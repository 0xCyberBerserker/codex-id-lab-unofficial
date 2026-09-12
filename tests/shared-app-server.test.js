"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const net = require("node:net");
const path = require("node:path");
const {spawn} = require("node:child_process");
const {once} = require("node:events");
const crypto = require("node:crypto");
const {pathToFileURL} = require("node:url");
const {fakeChild, loadInjectedTransport, syntheticBundle} = require("./shared-app-server.fixture.js");
const {applySharedAppServerSocketPatch} = require("../linux-features/shared-app-server-socket/patch.js");

function fixture(t) {
  const root = fs.mkdtempSync("/tmp/lab-rpc-");
  const previous = {XDG_RUNTIME_DIR: process.env.XDG_RUNTIME_DIR, CODEX_CLI_PATH: process.env.CODEX_CLI_PATH};
  process.env.XDG_RUNTIME_DIR = root;
  process.env.CODEX_CLI_PATH = "/fake/codex";
  t.after(() => {
    for (const [key, value] of Object.entries(previous)) {
      if (value === undefined) delete process.env[key]; else process.env[key] = value;
    }
    fs.rmSync(root, {recursive: true, force: true});
  });
  return {root, socket: path.join(root, "app-server.sock")};
}

test("shared authority selection stages an ASAR artifact, diagnoses drift and disables in a fresh build", async t => {
  const asar = await import(pathToFileURL(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js")));
  const {experimentalStage, stage, diagnose} = require("../scripts/lab-features.js");
  const root = fs.mkdtempSync("/tmp/lab-shared-stage-");
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  const source = path.join(root, "source"), app = path.join(root, "app"), features = path.join(root, "features");
  const file = ".vite/build/main-fixture.js";
  fs.mkdirSync(path.dirname(path.join(source, file)), {recursive: true});
  fs.writeFileSync(path.join(source, file), syntheticBundle());
  fs.writeFileSync(path.join(source, "unchanged.txt"), "upstream bytes");
  fs.mkdirSync(path.join(app, "resources"), {recursive: true});
  const archive = path.join(app, "resources/app.asar");
  await asar.createPackage(source, archive);
  const baseline = fs.readFileSync(archive);
  const sha = crypto.createHash("sha256").update(baseline).digest("hex");
  fs.cpSync(path.join(__dirname, "../linux-features/shared-app-server-socket"), path.join(features, "shared-app-server-socket"), {recursive: true});
  const manifestPath = path.join(features, "shared-app-server-socket/feature.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  // A copied fixture cannot claim the trusted repository descriptor entrypoint.
  delete manifest.entrypoints;
  manifest.lab.compatibility.asarSha256 = [sha];
  fs.writeFileSync(manifestPath, JSON.stringify(manifest));
  const profile = path.join(root, "profile.json");
  fs.writeFileSync(profile, JSON.stringify({enabled: ["shared-app-server-socket"], settings: {}, runtimePatches: true}));
  const previous = process.env.CODEX_LAB_EXPERIMENTAL_CANDIDATE;
  process.env.CODEX_LAB_EXPERIMENTAL_CANDIDATE = "1";
  t.after(() => {if (previous === undefined) delete process.env.CODEX_LAB_EXPERIMENTAL_CANDIDATE; else process.env.CODEX_LAB_EXPERIMENTAL_CANDIDATE = previous;});
  const info = await experimentalStage(app, profile, features);
  assert.equal(info.runtime.changes.length, 1);
  assert.equal(asar.extractFile(archive, "unchanged.txt").toString(), "upstream bytes");
  assert.deepEqual(diagnose(app).linuxFeatures.enabled, ["shared-app-server-socket"]);
  fs.appendFileSync(archive, "tampered");
  assert.throws(() => diagnose(app), /ASAR drift/);
  // Disabling is a fresh upstream build, never a reverse patch of an installed app.
  fs.writeFileSync(archive, baseline); asar.uncache(archive);
  fs.writeFileSync(profile, JSON.stringify({enabled: [], settings: {}, runtimePatches: false}));
  stage(app, profile, features);
  assert.deepEqual(diagnose(app).linuxFeatures.enabled, []);
  assert.equal(diagnose(app).runtime, undefined);
  assert.deepEqual(fs.readFileSync(archive), baseline);
});

test("runtime staging rejects non-disposable and symlinked candidates before writing", t => {
  const {assertDisposableCandidate} = require("../scripts/lab-runtime-features.js");
  assert.throws(() => assertDisposableCandidate("/usr"), /disposable/);
  const root = fs.mkdtempSync("/tmp/lab-shared-unsafe-");
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  fs.mkdirSync(path.join(root, "real"));
  fs.symlinkSync(path.join(root, "real"), path.join(root, "resources"));
  assert.throws(() => assertDisposableCandidate(root), /symlinks/);
});

test("shared transport patch is opt-in, idempotent and drift fails without mutation", () => {
  const baseline = syntheticBundle();
  const output = applySharedAppServerSocketPatch(baseline);
  assert.notEqual(output, baseline);
  assert.equal(applySharedAppServerSocketPatch(output), output);
  assert.match(output, /privateSocketPath/);
  assert.match(output, /BRIDGE_SOCKET\?\?`auto`/);
  const drift = baseline.replace("getConfigOverrides:()=>Ope(e)", "unknownCallback:()=>Ope(e)");
  assert.equal(applySharedAppServerSocketPatch(drift), drift);
});

test("private runtime root, containment, modes and symlinks are checked", t => {
  const {root, socket} = fixture(t);
  const {Transport} = loadInjectedTransport({spawnImpl: () => assert.fail("unsafe path launched backend")});
  const automatic = new Transport("auto");
  assert.equal(automatic.socketPath, path.join(root, "codex-id-lab-unofficial/app-server-bridge/app-server.sock"));
  assert.equal(fs.statSync(path.dirname(automatic.socketPath)).mode & 0o777, 0o700);
  assert.throws(() => new Transport("/tmp/escaped.sock"), /escapes/);
  assert.throws(() => new Transport(socket + "\n"), /unsafe/);
  fs.mkdirSync(path.join(root, "public"), {mode: 0o755});
  assert.throws(() => new Transport(path.join(root, "public/a.sock")), /unsafe/);
  fs.symlinkSync(root, path.join(root, "linked"));
  assert.throws(() => new Transport(path.join(root, "linked/a.sock")), /unsafe/);
  fs.chmodSync(root, 0o755);
  assert.throws(() => new Transport(socket), /unsafe/);
});

test("ownership rejects live owner and only removes its own lock inode", async t => {
  const {socket} = fixture(t);
  const {Transport} = loadInjectedTransport({spawnImpl: () => assert.fail("ownership probe spawned backend")});
  const first = new Transport(socket), second = new Transport(socket);
  await first.acquireOwnership();
  await assert.rejects(second.acquireOwnership(), /already owned/);
  fs.renameSync(first.lockPath, first.lockPath + ".old");
  fs.writeFileSync(first.lockPath, "replacement", {mode: 0o600});
  first.releaseOwnedPaths();
  assert.equal(fs.readFileSync(first.lockPath, "utf8"), "replacement");
});

test("one authority preserves opaque ordered overrides and owned cleanup", async t => {
  const {socket} = fixture(t);
  const children = [], calls = [];
  let server;
  const {Transport} = loadInjectedTransport({spawnImpl(command, args) {
    const child = fakeChild(); children.push(child); calls.push({command, args});
    queueMicrotask(() => {
      server = net.createServer(); server.listen(socket);
      child.kill = () => {
        child.killed = true; child.signalCode = "SIGTERM";
        server.close(() => {child.emit("exit", 0); child.emit("close", 0);});
        return true;
      };
    });
    return child;
  }});
  let overridesRead = 0;
  const transport = new Transport(socket, async () => {overridesRead++; return ["alpha=opaque", "beta=opaque"];});
  const stop = async () => {
    if (!children[0] || children[0].signalCode !== null) return;
    const closed = once(children[0], "close"); transport.dispose(); await closed;
  };
  t.after(stop);
  await Promise.all([transport.ensureAuthority(), transport.ensureAuthority()]);
  assert.equal(children.length, 1); assert.equal(overridesRead, 1);
  assert.deepEqual(Array.from(calls[0].args), ["-c", "alpha=opaque", "-c", "beta=opaque", "app-server", "--listen", `unix://${socket}`]);
  const record = path.join(process.env.XDG_RUNTIME_DIR, "codex-id-lab-unofficial/app-server-bridge/attached-cli-v1");
  assert.equal(fs.statSync(record).mode & 0o777, 0o600);
  await stop();
  assert.equal(fs.existsSync(socket), false);
  assert.equal(fs.existsSync(transport.lockPath), false);
});

test("disposed startup cannot spawn while overrides resolve", async t => {
  const {socket} = fixture(t);
  const {Transport} = loadInjectedTransport({spawnImpl: () => assert.fail("disposed transport spawned backend")});
  let release;
  const transport = new Transport(socket, () => new Promise(resolve => {release = resolve;}));
  const starting = transport.ensureAuthority();
  transport.dispose(); release([]);
  await assert.rejects(starting, /disposed/);
  assert.equal(fs.existsSync(transport.lockPath), false);
});

test("real bundled CLI proxy upgrades /rpc in isolated anonymous namespace", {timeout: 15000}, async t => {
  const cli = process.env.CODEX_LAB_TEST_NATIVE_CLI;
  if (!cli || process.env.CODEX_LAB_TEST_NATIVE_ISOLATED !== "1") {
    t.skip("explicit isolated native CLI fixture required"); return;
  }
  const root = fs.mkdtempSync("/tmp/lab-real-rpc-"), socket = path.join(root, "app-server.sock");
  const env = {PATH: "/usr/bin", HOME: root, CODEX_HOME: path.join(root, "codex")};
  fs.mkdirSync(env.CODEX_HOME, {mode: 0o700});
  const authority = spawn(cli, ["app-server", "--listen", `unix://${socket}`], {env, stdio: "ignore"});
  let proxy;
  async function stop(child) {
    if (!child || child.exitCode !== null || child.signalCode !== null) return;
    const closed = once(child, "close");
    child.stdin?.end();
    child.kill();
    const timer = setTimeout(() => child.kill("SIGKILL"), 1500);
    try {await closed;} finally {clearTimeout(timer);}
  }
  t.after(async () => {await Promise.all([stop(proxy), stop(authority)]); fs.rmSync(root, {recursive: true, force: true});});
  for (let i = 0; i < 100 && !fs.existsSync(socket); i++) {
    assert.equal(authority.exitCode, null); await new Promise(resolve => setTimeout(resolve, 50));
  }
  assert.equal(fs.statSync(socket).isSocket(), true);
  assert.equal(fs.statSync(socket).mode & 0o077, 0);
  proxy = spawn(cli, ["app-server", "proxy", "--sock", socket], {env, stdio: ["pipe", "pipe", "ignore"]});
  const reply = new Promise((resolve, reject) => {
    let response = "";
    const timer = setTimeout(() => reject(Error("stock proxy upgrade timed out")), 5000);
    proxy.once("error", error => {clearTimeout(timer); reject(error);});
    proxy.stdout.on("data", chunk => {
      response += chunk.toString();
      if (response.length > 65536) {clearTimeout(timer); reject(Error("oversized upgrade"));}
      if (response.includes("\r\n\r\n")) {clearTimeout(timer); resolve(response);}
    });
  });
  proxy.stdin.write(["GET /rpc HTTP/1.1", "Host: localhost", "Upgrade: websocket", "Connection: Upgrade", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==", "Sec-WebSocket-Version: 13", "", ""].join("\r\n"));
  assert.match(await reply, /^HTTP\/1\.1 101 /);
});
