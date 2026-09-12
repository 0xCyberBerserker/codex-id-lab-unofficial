"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const crypto = require("node:crypto");

function sha(file) { return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"); }

function patchSources(files, enabled) {
  const changes = [];
  function apply(id, pattern, patch) {
    const matches = Object.keys(files).filter(file => pattern.test(file));
    if (matches.length !== 1) throw new Error(`${id}: expected one upstream bundle, found ${matches.length}`);
    const file = matches[0], before = files[file], after = patch(before);
    if (after === before || patch(after) !== after) throw new Error(`${id}: missing or non-idempotent patch contract`);
    files[file] = after;
    changes.push({ id, file, beforeSha256: crypto.createHash("sha256").update(before).digest("hex"), afterSha256: crypto.createHash("sha256").update(after).digest("hex") });
  }
  for (const feature of enabled) {
    if (feature === "appshots") {
      const module = require("../linux-features/appshots/patch.js");
      apply("appshots-main", /^\.vite\/build\/main-[^/]+\.js$/, module.applyLinuxAppshotMainProcessPatch);
      apply("appshots-availability", /^webview\/assets\/app-initial-[^/]+\.js$/, module.applyLinuxAppshotAvailabilityPatch);
      // No hotkey descriptor, bare-modifier helper, runtime hook or implicit input permission.
    } else if (feature === "read-aloud") {
      const module = require("../linux-features/read-aloud/runtime.js");
      apply("read-aloud-main", /^\.vite\/build\/main-[^/]+\.js$/, module.applyMainBundlePatch);
      apply("read-aloud-webview", /^webview\/assets\/app-initial-[^/]+\.js$/, module.applyIndexRuntimePatch);
      apply("read-aloud-assistant", /^webview\/assets\/local-conversation-turn-[^/]+\.js$/, module.applyAssistantRenderPatch);
    } else if (feature === "global-dictation") {
      const module = require("../linux-features/global-dictation/patch.js");
      apply("global-dictation-main", /^\.vite\/build\/main-[^/]+\.js$/, module.applyLinuxGlobalDictationMainProcessPatch);
    } else throw new Error(`Runtime adapter unavailable: ${feature}`);
  }
  return changes;
}

async function stageRuntime(appDir, enabled) {
  let nativeHelper = null;
  if (enabled.includes("global-dictation")) {
    const source = process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER;
    const expected = process.env.CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256;
    if (!source || !path.isAbsolute(source) || !/^\/tmp\//.test(fs.realpathSync(source))
        || !/^[a-f0-9]{64}$/.test(expected ?? "")) throw new Error("Explicit temporary native helper and SHA-256 are required");
    const stat = fs.lstatSync(source);
    if (!stat.isFile() || (stat.mode & 0o022) || !(stat.mode & 0o111) || sha(source) !== expected) {
      throw new Error("Native dictation helper identity or permissions rejected");
    }
    nativeHelper = { source, sha256: expected };
  }
  const archive = path.join(appDir, "resources", "app.asar");
  const asar = await import(pathToFileURL(path.join(__dirname, "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js")));
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "codex-lab-asar-"));
  try {
    const sources = {};
    const files = asar.listPackage(archive).map(file => file.replace(/^\//, ""));
    const unpacked = [];
    for (const file of files) {
      const metadata = asar.statFile(archive, file, false);
      if (metadata.unpacked && !metadata.files) unpacked.push("**/" + file.replace(/([*?{}()[\]\\])/g, "\\$1"));
      if (/^(\.vite\/build\/main-|webview\/assets\/(app-initial-|local-conversation-turn-)).*\.js$/.test(file)) {
        sources[file] = asar.extractFile(archive, file).toString("utf8");
      }
    }
    // All contracts must pass before extraction or replacing the candidate archive.
    const changes = patchSources(sources, enabled);
    const extracted = path.join(temporary, "extracted");
    asar.extractAll(archive, extracted);
    for (const file of new Set(changes.map(change => change.file))) fs.writeFileSync(path.join(extracted, file), sources[file]);
    const candidate = path.join(temporary, "candidate.asar");
    const unpack = unpacked.length === 1 ? unpacked[0] : unpacked.length ? `{${unpacked.join(",")}}` : undefined;
    await asar.createPackageWithOptions(extracted, candidate, { unpack });
    for (const file of new Set(changes.map(change => change.file))) {
      if (asar.extractFile(candidate, file).toString("utf8") !== sources[file]) throw new Error(`ASAR roundtrip failed: ${file}`);
    }
    const changed = new Set(changes.map(change => change.file));
    for (const file of files) {
      const before = asar.statFile(archive, file, false), after = asar.statFile(candidate, file, false);
      if (before.files) continue;
      if (before.link !== after.link || !!before.executable !== !!after.executable || !!before.unpacked !== !!after.unpacked) {
        throw new Error(`ASAR metadata preservation failed: ${file}`);
      }
      if (!before.link && !changed.has(file) && !asar.extractFile(archive, file).equals(asar.extractFile(candidate, file))) {
        throw new Error(`Unexpected upstream content change: ${file}`);
      }
    }
    const outputSha256 = sha(candidate);
    if (nativeHelper) {
      const directory = path.join(appDir, "resources", "native");
      fs.mkdirSync(directory, { recursive: true });
      if (fs.realpathSync(directory) !== path.resolve(directory)) throw new Error("Native resource directory must not contain symlinks");
      const target = path.join(directory, "codex-global-dictation-linux");
      if (fs.existsSync(target)) throw new Error("Fresh candidate without a native dictation helper is required");
      fs.copyFileSync(nativeHelper.source, target, fs.constants.COPYFILE_EXCL);
      fs.chmodSync(target, 0o755);
      if (sha(target) !== nativeHelper.sha256) throw new Error("Native helper copy digest mismatch");
    }
    // Candidate-only API. Installed package-manager trees must never be passed here.
    fs.copyFileSync(candidate, archive + ".candidate");
    if (fs.existsSync(candidate + ".unpacked")) fs.cpSync(candidate + ".unpacked", archive + ".unpacked", { recursive: true });
    fs.renameSync(archive + ".candidate", archive);
    asar.uncache(archive);
    return { outputSha256, changes, ...(nativeHelper ? {nativeHelpers: [{target: "resources/native/codex-global-dictation-linux", sha256: nativeHelper.sha256}]} : {}), status: "patched-not-runtime-verified" };
  } finally { fs.rmSync(temporary, { recursive: true, force: true }); }
}

module.exports = { patchSources, stageRuntime };
