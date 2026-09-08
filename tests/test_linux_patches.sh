#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT

app="$fixture/app-src"
mkdir -p "$app/.vite/build" "$app/webview/assets"
: > "$app/webview/assets/dictation-audio-worklet-fixture.js"
cat > "$app/package.json" <<'JSON'
{"codexBuildNumber":"test"}
JSON
cat > "$app/.vite/build/main-fixture.js" <<'JS'
const e={setPermissionRequestHandler(handler){this.request=handler},setPermissionCheckHandler(handler){this.check=handler}};e.setPermissionRequestHandler((e,t,n)=>{n(t===`clipboard-sanitized-write`)}),e.setPermissionCheckHandler((e,t)=>t===`clipboard-sanitized-write`);globalThis.testSession=e;globalThis.voiceEndpoint=`/codex/dictation-stream-connect-info`;
function G7(){return process.platform===`darwin`||process.platform===`win32`}
const z7=async()=>{};async function RIe(){switch(process.platform){case`darwin`:return;case`win32`:return;case`aix`:case`android`:case`cygwin`:case`freebsd`:case`haiku`:case`linux`:case`netbsd`:case`openbsd`:case`sunos`:throw Error(`Global dictation paste is not supported on this OS.`)}}
class TestDictation{isGateEnabled=true;configuredHotkey=`Ctrl+D`;createMutationFailure(error){return{success:false,error}}unregisterHotkey(){}registerHotkeyOrThrow(){}setHotkeyForMode(e,t){if(!G7()||!this.isGateEnabled)return this.createMutationFailure(`Not supported.`);return{success:true}}applyLifecycleOrThrow(){this.configuredHotkey==null?this.unregisterHotkey():this.registerHotkeyOrThrow(this.configuredHotkey,e)}}
globalThis.testGlobalDictationSupported=()=>G7();globalThis.testDictation=new TestDictation();
JS
cat > "$app/webview/assets/voice-settings-fixture.js" <<'JS'
const settings={children:[(0,Q.jsx)(Xt,{hotkeyState:r,mode:`hold`}),(0,Q.jsx)(Xt,{hotkeyState:r,mode:`toggle`})]};const message="settings.voice.dictation.unsupported";
JS

"$ROOT/scripts/apply-linux-patches" "$fixture" "test"
"$ROOT/scripts/apply-linux-patches" "$fixture" "test"

node - "$app/.vite/build/main-fixture.js" <<'NODE'
const assert = require("node:assert/strict");
require(process.argv[2]);

function request(permission, details) {
  let result = null;
  globalThis.testSession.request({}, permission, (allowed) => { result = allowed; }, details);
  return result;
}

assert.equal(globalThis.__codexUiLinuxAudioPermission, "audio-only");
assert.equal(request("media", {mediaTypes: ["audio"]}), true);
assert.equal(request("media", {mediaTypes: ["video"]}), false);
assert.equal(request("media", {mediaTypes: ["audio", "video"]}), false);
assert.equal(request("clipboard-sanitized-write", {}), true);
assert.equal(globalThis.testSession.check({}, "media", "app://codex", {mediaType: "audio"}), true);
assert.equal(globalThis.testSession.check({}, "media", "app://codex", {mediaType: "video"}), false);
assert.equal(globalThis.__codexUiLinuxGlobalDictation, "toggle-only");
assert.equal(globalThis.testGlobalDictationSupported(), true);
assert.match(globalThis.testDictation.setHotkeyForMode("hold", "Ctrl+D").error, /not supported on Linux/);
console.log("test_linux_patches: voice and Linux dictation patches passed");
NODE

grep -Fq 'children:[(0,Q.jsx)(Xt,{hotkeyState:r,mode:`toggle`})]' "$app/webview/assets/voice-settings-fixture.js"
! grep -Fq 'mode:`hold`' "$app/webview/assets/voice-settings-fixture.js"
grep -Fq 'process.platform===`linux`||this.configuredHotkey==null' "$app/.vite/build/main-fixture.js"
grep -Fq '"desktopName": "codex-ui-linux.desktop"' "$app/package.json"
grep -Fq -- '--enable-features=GlobalShortcutsPortal' "$fixture/bin/codex-ui-linux"

fake_bin="$fixture/fake-bin"
mkdir -p "$fake_bin"
cat > "$fake_bin/ydotool" <<'SH'
#!/usr/bin/env bash
printf '%s\n' "$*" > "$CODEXUI_TEST_PASTE_LOG"
SH
chmod 755 "$fake_bin/ydotool"
paste_log="$fixture/paste.log"
PATH="$fake_bin:$PATH" XDG_SESSION_TYPE=wayland CODEXUI_TEST_PASTE_LOG="$paste_log" "$fixture/bin/codex-ui-linux-paste"
grep -Fxq 'key 29:1 47:1 47:0 29:0' "$paste_log"
