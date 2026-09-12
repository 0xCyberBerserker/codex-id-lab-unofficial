"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const {EventEmitter} = require("node:events");
const {patchSources} = require("../scripts/lab-runtime-features.js");
const fs = require("node:fs");
const os = require("node:os");
const crypto = require("node:crypto");
const {pathToFileURL} = require("node:url");
// MIT fixture adapted from the pinned ilysenko component; see upstream.lock.json.
function mainBundleFixture() {
  return [
    "var p=require(`node:fs`),u=require(`node:path`),h=require(`node:child_process`),c=require(`electron`),r={r:()=>({warning(){}})};",
    "function Kk(e,t){let n=``;e.stdout?.on(`data`,e=>{n+=e.toString(`utf8`);let r=n.indexOf(`\\n`);for(;r!==-1;)t(n.slice(0,r).trim()),n=n.slice(r+1),r=n.indexOf(`\\n`)})}",
    "function eA(e,t,n){let r=n?.ownership,i=t.onReleased,a=t.onCancelled,o=r==null?t:{onPressed:()=>{r.isOwner()&&t.onPressed()},onReleased:i==null?void 0:()=>{r.isOwner()&&i()},onCancelled:a==null?void 0:()=>{r.isOwner()&&a()}};if(Rk(e))return Lk(e)?Mk(e,o,n?.bareModifierTrigger):null;let s=oA(e),l=()=>{o.onPressed()},d=c.globalShortcut.register(s,l);return d?process.platform===`darwin`?sA({hotkey:e,onPressed:l,registrationHotkey:s}):{handlesRelease:!1,unregister:()=>{c.globalShortcut.unregister(s)}}:null}",
    "function fA(e){return nA(e)??(Lk(e)||bA(e,process.platform)?null:`Shortcut key is not supported for global dictation.`)}",
    "function pA(e,t){switch(process.platform){case`darwin`:{let n=Ik(mA(e),t);if(n==null)throw Error(`Global dictation hotkey release watching is not supported.`);return n}case`win32`:{let n=gA(e,process.platform);if(n==null)throw Error(`Global dictation hotkey release watching is not supported.`);return BA((0,h.spawn)(`powershell.exe`,[],{stdio:`ignore`}),t)}case`aix`:case`android`:case`cygwin`:case`freebsd`:case`haiku`:case`linux`:case`netbsd`:case`openbsd`:case`sunos`:throw Error(`Global dictation hotkey release watching is not supported.`)}}",
    "function mA(e){let t=[];for(let n of e.split(`+`)){let e=uA.get(n.trim().toLowerCase());e!=null&&!t.includes(e)&&t.push(e)}return t}",
    "function _A(){return [`/unrelated/native/path`]}",
    "function BA(e,t){let n=!1,i=e=>{n||(n=!0,e!=null&&r.r().warning(`Global dictation hotkey release watching failed`,{safe:{},sensitive:{error:e}}),t())};return e.once(`error`,i),e.once(`exit`,()=>i()),{dispose:()=>{n=!0,e.kill()}}}",
    "function bA(e,t){return t===`darwin`?mA(e).length>0:gA(e,t)!=null}",
    "function k7(e,t,n){return{x:e.centerX-n.x-t.width/2,y:e.centerY-n.y-t.height/2,...t}}var V7=async(...e)=>globalThis.__upstreamExecFile(...e);async function P7(){switch(process.platform){case`darwin`:await V7(`/usr/bin/osascript`,[]);return;case`win32`:return;case`aix`:case`android`:case`cygwin`:case`freebsd`:case`haiku`:case`linux`:case`netbsd`:case`openbsd`:case`sunos`:throw Error(`Global dictation paste is not supported on this OS.`)}}",
    "var H7=class{registeredHotkey=null;registeredHotkeyRegistration=null;registeredToggleHotkey=null;registeredToggleHotkeyRegistration=null;registerHotkeyOrThrow(e,t){if(this.registeredHotkey===e)return;let n=this.registeredHotkey,r=eA(e,{onPressed:()=>{this.handleHoldHotkeyPressed()},onReleased:()=>{this.handleHoldHotkeyReleased()},onCancelled:()=>{this.handleHoldHotkeyReleased()}},{ownership:t,bareModifierTrigger:`cancellablePress`});if(r==null)throw Error(`Unable to register global dictation hotkey: ${e}`);n!=null&&this.registeredHotkeyRegistration?.unregister(),this.registeredHotkey=e,this.registeredHotkeyRegistration=r}unregisterHotkey(){this.registeredHotkey!=null&&(this.registeredHotkeyRegistration?.unregister(),this.registeredHotkey=null,this.registeredHotkeyRegistration=null)}registerToggleHotkeyOrThrow(e,t){if(this.registeredToggleHotkey===e)return;let n=this.registeredToggleHotkey,r=eA(e,{onPressed:()=>{this.handleToggleHotkeyPressed()}},{bareModifierTrigger:`release`,ownership:t});if(r==null)throw Error(`Unable to register global dictation toggle hotkey: ${e}`);n!=null&&this.registeredToggleHotkeyRegistration?.unregister(),this.registeredToggleHotkey=e,this.registeredToggleHotkeyRegistration=r}unregisterToggleHotkey(){this.registeredToggleHotkey!=null&&(this.registeredToggleHotkeyRegistration?.unregister(),this.registeredToggleHotkey=null,this.registeredToggleHotkeyRegistration=null)}deactivateLifecycle(){this.unregisterHotkey(),this.unregisterToggleHotkey()}handleHoldHotkeyPressed(){}handleHoldHotkeyReleased(){}handleToggleHotkeyPressed(){}};",
    "function W7(){return process.platform===`darwin`||process.platform===`win32`}",
  ].join("");
}

test("pinned native ASAR accepts the dictation adapter without executing upstream code", {skip: !process.env.CODEX_LAB_TEST_DICTATION_ASAR}, async () => {
  const archive = process.env.CODEX_LAB_TEST_DICTATION_ASAR;
  const compatibility = require("../linux-features/global-dictation/feature.json").lab.compatibility.asarSha256;
  const digest = crypto.createHash("sha256").update(fs.readFileSync(archive)).digest("hex");
  assert.ok(compatibility.includes(digest), "ASAR must match the reviewed compatibility identity");
  const asar = await import(pathToFileURL(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js")));
  const names = asar.listPackage(archive).map(name => name.replace(/^\//, "")).filter(name => /^\.vite\/build\/main-[^/]+\.js$/.test(name));
  assert.equal(names.length, 1);
  const name = names[0];
  const original = asar.extractFile(archive, name).toString("utf8");
  const files = {[name]: original};
  assert.deepEqual(patchSources({...files}, []), []);
  const changes = patchSources(files, ["global-dictation"]);
  assert.equal(changes.length, 1);
  assert.notEqual(files[name], original);
  assert.doesNotThrow(() => new vm.Script(files[name]));
  assert.equal(crypto.createHash("sha256").update(fs.readFileSync(archive)).digest("hex"), digest);
});


function context(child, session = "wayland") {
  let spawned = 0;
  const result = {
    process: {platform: "linux", resourcesPath: "/fixture/resources", env: {XDG_SESSION_TYPE: session}},
    console: {warn() {}}, clearTimeout, setTimeout,
    require(name) {
      if (name === "node:fs") return {constants: {X_OK: 1}, accessSync() {}, lstatSync: () => ({isFile: () => true, mode: 0o755})};
      if (name === "node:path") return path;
      if (name === "node:child_process") return {spawn() { spawned++; return child; }, execFile() {throw Error("No X11 process allowed");}};
      if (name === "electron") return {globalShortcut: {register() {throw Error("No fallback global input allowed");}}};
      throw Error("Unexpected import: " + name);
    },
    spawned: () => spawned,
  };
  const source = {".vite/build/main-fixture.js": mainBundleFixture()};
  assert.equal(patchSources(source, ["global-dictation"]).length, 1);
  assert.deepEqual(patchSources({".vite/build/main-fixture.js": mainBundleFixture()}, []), []);
  assert.doesNotThrow(() => new vm.Script(source[".vite/build/main-fixture.js"]));
  vm.runInNewContext(source[".vite/build/main-fixture.js"], result);
  return result;
}

test("dictation candidate is Wayland-only and rejects contract drift", () => {
  const c = context(null, "x11");
  assert.equal(c.W7(), false);
  assert.equal(c.eA("Ctrl+Space", {onPressed() {}}, {}), null);
  assert.equal(c.spawned(), 0);
  assert.throws(() => patchSources({".vite/build/main-fixture.js": "changed contract"}, ["global-dictation"]), /missing or non-idempotent/);
});

test("portal adapter frames events, deduplicates presses, pastes explicitly and closes only its child", async () => {
  const child = new EventEmitter();
  child.stdout = new EventEmitter(); child.stderr = new EventEmitter();
  child.stdin = {writes: [], write(text, callback) {this.writes.push(text); callback?.();}};
  child.kill = () => {child.killed = true;};
  const c = context(child);
  let down = 0, up = 0, unavailable = 0;
  const registration = c.eA("Ctrl+Space", {onPressed() {down++;}, onReleased() {up++;}, onUnavailable() {unavailable++;}}, {});
  await new Promise(setImmediate);
  assert.equal(c.spawned(), 1);
  child.stdout.emit("data", Buffer.from("rea")); child.stdout.emit("data", Buffer.from("dy\n"));
  assert.equal(registration.ready(), true);
  child.stdout.emit("data", Buffer.from("down\ndown\nup\n"));
  assert.equal(down, 1); assert.equal(up, 1);
  const pasted = registration.paste();
  assert.deepEqual(child.stdin.writes, ["paste\n"]);
  child.stdout.emit("data", Buffer.from("paste-ok\n")); await pasted;
  child.stdout.emit("data", Buffer.from("down\n"));
  child.emit("exit", 1);
  await new Promise(resolve => setTimeout(resolve, 5));
  assert.equal(up, 2); assert.equal(unavailable, 1);
  assert.equal(registration.ready(), false); assert.equal(child.killed, true);
  registration.unregister(); assert.equal(up, 2);
});

test("actual candidate stages a hashed helper and disabling in a fresh build leaves no residue", {skip: !fs.existsSync(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js"))}, async () => {
  const asar = await import(pathToFileURL(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js")));
  const {stageRuntime} = require("../scripts/lab-runtime-features.js");
  const {diagnose} = require("../scripts/lab-features.js");
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "codex-lab-dictation-test-"));
  const oldPath = process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER, oldDigest = process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256;
  try {
    const source = path.join(temporary, "source"), app = path.join(temporary, "app"), fresh = path.join(temporary, "fresh");
    fs.mkdirSync(path.join(source, ".vite/build"), {recursive: true});
    fs.writeFileSync(path.join(source, ".vite/build/main-fixture.js"), mainBundleFixture());
    fs.mkdirSync(path.join(app, "resources"), {recursive: true});
    fs.mkdirSync(path.join(fresh, "resources"), {recursive: true});
    await asar.createPackage(source, path.join(app, "resources/app.asar"));
    const original = fs.readFileSync(path.join(app, "resources/app.asar"));
    fs.writeFileSync(path.join(fresh, "resources/app.asar"), original);
    const helper = path.join(temporary, "helper");
    fs.writeFileSync(helper, "fixture executable, never launched", {mode: 0o755});
    process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER = helper;
    process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256 = "0".repeat(64);
    await assert.rejects(stageRuntime(app, ["global-dictation"]), /identity or permissions/);
    assert.deepEqual(fs.readFileSync(path.join(app, "resources/app.asar")), original);
    process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256 = crypto.createHash("sha256").update(fs.readFileSync(helper)).digest("hex");
    const runtime = await stageRuntime(app, ["global-dictation"]);
    assert.equal(runtime.nativeHelpers.length, 1);
    assert.equal(runtime.nativeResources.length, 75);
    fs.mkdirSync(path.join(app, ".codex-linux"));
    fs.writeFileSync(path.join(app, ".codex-linux/build-info.json"), JSON.stringify({resources: [], runtime}));
    diagnose(app);
    const notice = path.join(app, runtime.nativeResources[0].target);
    const noticeBytes = fs.readFileSync(notice);
    fs.appendFileSync(notice, "tampered");
    assert.throws(() => diagnose(app), /Staged resource drift/);
    fs.writeFileSync(notice, noticeBytes);
    fs.appendFileSync(path.join(app, runtime.nativeHelpers[0].target), "tampered");
    assert.throws(() => diagnose(app), /Staged resource drift/);
    await stageRuntime(fresh, []);
    assert.equal(fs.existsSync(path.join(fresh, "resources/native/codex-global-dictation-linux")), false);
    assert.equal(asar.extractFile(path.join(fresh, "resources/app.asar"), ".vite/build/main-fixture.js").toString(), mainBundleFixture());
  } finally {
    if (oldPath === undefined) delete process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER; else process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER = oldPath;
    if (oldDigest === undefined) delete process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256; else process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256 = oldDigest;
    fs.rmSync(temporary, {recursive: true, force: true});
  }
});
