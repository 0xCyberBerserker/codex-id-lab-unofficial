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
console.log("test_linux_patches: audio-only permission passed");
NODE
