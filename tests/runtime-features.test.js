"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const { EventEmitter } = require("node:events");
const { patchSources } = require("../scripts/lab-runtime-features.js");
const { nativeHelperSource } = require("../linux-features/read-aloud/runtime.js");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

// Adapted MIT fixture contracts from ilysenko's AppShots tests, pinned in upstream.lock.json.
function fixture() {
  return {
    ".vite/build/main-fixture.js": 'var h={handlers:{"native-desktop-apps":async()=>({apps:[]}),"computer-use-frontmost-window":async({origin:e,signal:t})=>process.platform===`win32`?bridge(e,t):process.platform===`darwin`?Xo():null,"computer-use-start-capture":async({animationDestination:e,animationPresentationStyle:s,bundleIdentifier:t,origin:n,requestId:r,signal:i})=>{if(process.platform!==`darwin`&&process.platform!==`win32`)return null;return a}}};function send(){windowManager.sendInlineMessageForView(origin,{})}',
    "webview/assets/app-initial-fixture.js": 'function allowed(e){return e.requirements?.allowAppshots!==!1}function platform(e){return e===`macOS`||e===`windows`}',
    "webview/assets/local-conversation-turn-fixture.js": '(0,R.jsx)(Message,{item:i,assistantCopyText:c,conversationId:d})',
    "unchanged.txt": "upstream",
  };
}

test("selected modules patch only declared bundles and preserve the baseline when disabled", () => {
  const source = fixture(), baseline = structuredClone(source);
  assert.deepEqual(patchSources(source, []), []);
  assert.deepEqual(source, baseline);
  const changes = patchSources(source, ["appshots", "read-aloud"]);
  assert.equal(changes.length, 5);
  assert.equal(source["unchanged.txt"], "upstream");
  assert.match(source["webview/assets/local-conversation-turn-fixture.js"], /codexLinuxReadAloudClick/);
  assert.doesNotMatch(source[".vite/build/main-fixture.js"], /function codexLinuxReadAloudInstallRuntime|DownloadFile|bare-modifier-monitor/);
  assert.doesNotThrow(() => new Function(source[".vite/build/main-fixture.js"]));
});

test("unknown module, ambiguous bundle and contract drift fail closed", () => {
  assert.throws(() => patchSources(fixture(), ["unknown"]), /unavailable/);
  const duplicate = fixture(); duplicate[".vite/build/main-other.js"] = duplicate[".vite/build/main-fixture.js"];
  assert.throws(() => patchSources(duplicate, ["read-aloud"]), /expected one/);
  const drift = fixture(); drift["webview/assets/local-conversation-turn-fixture.js"] = "changed contract";
  assert.throws(() => patchSources(drift, ["read-aloud"]), /missing or non-idempotent/);
});

test("read aloud uses stdin, stops only its owned player and rejects unrelated setup", () => {
  const spawned = [], process = { platform: "linux", env: { PATH: "/fixture/bin", LANG: "es_ES.UTF-8" }, once() {} };
  const cp = { spawn(command, args) {
    const child = new EventEmitter(); child.stdin = new EventEmitter();
    child.stdin.end = text => { child.text = text; }; child.kill = signal => { child.signal = signal; };
    spawned.push({ command, args, child }); return child;
  } };
  const requireFixture = name => name === "node:child_process" ? cp : name === "node:fs" ? { constants: {X_OK: 1}, accessSync() {}, statSync: () => ({isFile: () => true}) } : require(name);
  const runtime = new Function("require", "process", nativeHelperSource() + ';return {speak:codexLabSpeechSpeak,stop:codexLabSpeechStop}')(requireFixture, process);
  assert.deepEqual(runtime.stop(), {stopped: false, reason: "idle"});
  assert.equal(runtime.speak("Sensitive fixture text").spoken, true);
  assert.deepEqual(spawned[0].args, ["--stdin", "-v", "es"]);
  assert.equal(spawned[0].child.text, "Sensitive fixture text");
  assert.equal(runtime.stop().stopped, true);
  assert.equal(spawned[0].child.signal, "SIGTERM");
  assert.equal(runtime.speak(null).reason, "empty");
});

test("AppShots does not discover floating private-cache helpers and requires approved override digest", () => {
  const {applyLinuxAppshotMainProcessPatch} = require("../linux-features/appshots/patch.js");
  const source = applyLinuxAppshotMainProcessPatch(fixture()[".vite/build/main-fixture.js"]);
  const helper = source.slice(source.indexOf(";function codexLinuxAppshotRequire"));
  let mode = 0o755, regular = true;
  const fakeFs = {constants: {X_OK: 1}, accessSync() {}, lstatSync: () => ({mode, isFile: () => regular}), readFileSync: () => Buffer.from("approved fixture")};
  const process = {env: {HOME: "/fixture/home", CODEX_HOME: "/fixture/private-cache"}};
  const backendPath = new Function("require", "process", helper + ";return codexLinuxAppshotBackendPath")(name => name === "node:fs" ? fakeFs : require(name), process);
  assert.equal(backendPath(), null);
  process.env.CODEX_LAB_APPROVED_COMPUTER_USE_BACKEND = "/fixture/backend";
  assert.equal(backendPath(), null);
  process.env.CODEX_LAB_APPROVED_COMPUTER_USE_BACKEND_SHA256 = require("node:crypto").createHash("sha256").update("approved fixture").digest("hex");
  assert.equal(backendPath(), "/fixture/backend");
  mode = 0o777; assert.equal(backendPath(), null);
  mode = 0o755; regular = false; assert.equal(backendPath(), null);
});

test("actual ASAR staging preserves unpacked native file content and flags", { skip: !fs.existsSync(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js")) }, async () => {
  const asar = await import(pathToFileURL(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js")));
  const { stageRuntime } = require("../scripts/lab-runtime-features.js");
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "codex-lab-asar-fixture-"));
  try {
    const source = path.join(temporary, "source"), app = path.join(temporary, "app");
    for (const [file, text] of Object.entries(fixture())) {
      fs.mkdirSync(path.dirname(path.join(source, file)), {recursive: true}); fs.writeFileSync(path.join(source, file), text);
    }
    const native = "node_modules/native-fixture/watcher.node";
    fs.mkdirSync(path.dirname(path.join(source, native)), {recursive: true}); fs.writeFileSync(path.join(source, native), "native fixture");
    fs.mkdirSync(path.join(app, "resources"), {recursive: true});
    const archive = path.join(app, "resources/app.asar");
    await asar.createPackageWithOptions(source, archive, {unpack: "**/" + native});
    assert.equal(asar.statFile(archive, native).unpacked, true);
    const result = await stageRuntime(app, ["appshots", "read-aloud"]);
    assert.equal(result.changes.length, 5);
    assert.equal(asar.statFile(archive, native).unpacked, true);
    assert.equal(asar.extractFile(archive, native).toString(), "native fixture");
    assert.equal(asar.extractFile(archive, "unchanged.txt").toString(), "upstream");
  } finally { fs.rmSync(temporary, {recursive: true, force: true}); }
});
