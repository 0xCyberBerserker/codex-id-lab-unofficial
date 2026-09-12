#!/usr/bin/env node
"use strict";

// Keep policy in this adapter; the imported framework retains its upstream contract.
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const framework = require("./lib/linux-features.js");

function fileSha(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function readProfile(profilePath) {
  const profile = JSON.parse(fs.readFileSync(profilePath, "utf8"));
  if (!Array.isArray(profile.enabled) || typeof profile.runtimePatches !== "boolean") {
    throw new Error("This integration requires an enabled array and an explicit runtimePatches boolean");
  }
  if (profile.settings == null || typeof profile.settings !== "object" || Array.isArray(profile.settings)) {
    throw new Error("Feature settings must be an object");
  }
  for (const [id, settings] of Object.entries(profile.settings)) {
    if (!profile.enabled.includes(id) || settings == null || typeof settings !== "object" || Array.isArray(settings)) {
      throw new Error(`Invalid or disabled feature settings: ${id}`);
    }
  }
  return profile;
}

function stage(appDir, profilePath, featuresRoot, allowRuntime = false) {
  const profile = readProfile(profilePath);
  if (profile.runtimePatches && !allowRuntime) throw new Error("Runtime patches require the explicit experimental-stage command");
  const options = { featuresRoot, featuresConfigPath: profilePath, strictConfig: true };
  const features = framework.loadEnabledLinuxFeatures(options);
  const featureMap = new Map(features.map(feature => [feature.id, feature]));
  const asarSha = fileSha(path.join(appDir, "resources", "app.asar"));
  const previousInfo = path.join(appDir, ".codex-linux", "build-info.json");
  if (fs.existsSync(previousInfo)) {
    const previous = JSON.parse(fs.readFileSync(previousInfo, "utf8"));
    if (previous.runtime && asarSha !== previous.upstreamAsarSha256) {
      throw new Error("Fresh upstream candidate required to disable or change runtime modules");
    }
  }
  for (const feature of features) {
    const sourceManifest = JSON.parse(fs.readFileSync(feature.manifestPath, "utf8"));
    const allowedKeys = new Set(["id", "title", "name", "description", "defaultEnabled", "internal", "requires", "conflicts", "resources", "lab", "entrypoints", "runtimeHooks", "packageResources", "packageDependencies", "packageHooks"]);
    for (const key of Object.keys(feature.manifest)) {
      if (!allowedKeys.has(key)) throw new Error(`Unknown feature manifest field: ${feature.id}.${key}`);
    }
    const metadata = feature.manifest.lab;
    if (metadata?.blockedReason) throw new Error(`Experimental feature blocked: ${feature.id}: ${metadata.blockedReason}`);
    if (path.basename(feature.dir) !== feature.id || sourceManifest.defaultEnabled !== false) {
      throw new Error(`Feature identity/default mismatch: ${feature.id}`);
    }
    if (!metadata || !Array.isArray(metadata.capabilities) || !Array.isArray(metadata.tests)
        || !["experimental", "tested"].includes(metadata.stability)
        || !Array.isArray(metadata.compatibility?.asarSha256)) {
      throw new Error(`Feature lacks explicit Lab capability, compatibility, stability or test metadata: ${feature.id}`);
    }
    if (!metadata.compatibility.asarSha256.includes(asarSha)) {
      throw new Error(`Upstream ASAR drift for enabled feature: ${feature.id}`);
    }
    const entrypoints = feature.manifest.entrypoints ?? {};
    const runtimeEntrypoint = profile.runtimePatches && ["appshots", "read-aloud", "global-dictation"].includes(feature.id)
      && Object.keys(entrypoints).length === 1 && typeof entrypoints.patchDescriptors === "string"
      && fs.realpathSync(feature.dir) === fs.realpathSync(path.join(__dirname, "../linux-features", feature.id));
    if ((Object.keys(entrypoints).length && !runtimeEntrypoint)
        || Object.keys(feature.manifest.runtimeHooks ?? {}).length
        || (feature.manifest.packageResources ?? []).length
        || Object.keys(feature.manifest.packageDependencies ?? {}).length
        || (feature.manifest.packageHooks ?? []).length) {
      throw new Error(`Feature requires a runtime/package adapter not yet accepted: ${feature.id}`);
    }
  }
  const plan = framework.enabledLinuxFeatureInstallPlan(options);
  for (const resource of plan.resources) {
    if (!resource.target.startsWith(`.codex-linux/features/${resource.id}/`)) {
      throw new Error(`Resource must stay in its feature namespace: ${resource.id}`);
    }
    if (!fs.lstatSync(resource.source).isFile()) {
      throw new Error(`This adapter accepts regular-file resources only: ${resource.id}`);
    }
    const featureRoot = fs.realpathSync(featureMap.get(resource.id).dir);
    if (!fs.realpathSync(resource.source).startsWith(featureRoot + path.sep)) {
      throw new Error(`Resource source escapes its feature directory: ${resource.id}`);
    }
    if (((resource.mode ?? fs.statSync(resource.source).mode) & 0o7000) !== 0) {
      throw new Error(`Special permission bits are forbidden: ${resource.id}`);
    }
  }
  framework.stageEnabledLinuxFeatureInstall(appDir, options);
  if (fileSha(path.join(appDir, "resources", "app.asar")) !== asarSha) {
    throw new Error("Base/declarative staging changed upstream app.asar");
  }
  const buildInfo = {
    schemaVersion: 1,
    upstreamAsarSha256: asarSha,
    featureConfigSha256: fileSha(profilePath),
    linuxFeatures: { enabled: features.map(feature => feature.id) },
    resources: plan.resources.map(resource => ({
      id: resource.id,
      target: resource.target,
      sha256: fileSha(path.join(appDir, resource.target)),
    })),
    features: features.map(feature => ({ id: feature.id, ...feature.manifest.lab, status: "staged-not-runtime-verified" })),
  };
  fs.mkdirSync(path.join(appDir, ".codex-linux"), { recursive: true });
  fs.writeFileSync(path.join(appDir, ".codex-linux", "build-info.json"), JSON.stringify(buildInfo, null, 2) + "\n");
  return buildInfo;
}

function diagnose(appDir) {
  const buildInfo = JSON.parse(fs.readFileSync(path.join(appDir, ".codex-linux", "build-info.json"), "utf8"));
  for (const resource of [...buildInfo.resources, ...(buildInfo.runtime?.nativeHelpers ?? []).map(helper => ({...helper, id: "global-dictation"}))]) {
    const target = path.resolve(appDir, resource.target);
    if (!target.startsWith(path.resolve(appDir) + path.sep)
        || !fs.realpathSync(target).startsWith(fs.realpathSync(appDir) + path.sep)
        || !fs.lstatSync(target).isFile() || fileSha(target) !== resource.sha256) {
      throw new Error(`Staged resource drift: ${resource.id}`);
    }
  }
  if (fileSha(path.join(appDir, "resources", "app.asar")) !== (buildInfo.runtime?.outputSha256 ?? buildInfo.upstreamAsarSha256)) {
    throw new Error("Installed upstream ASAR drift");
  }
  return buildInfo;
}

async function experimentalStage(appDir, profilePath, featuresRoot) {
  const profile = readProfile(profilePath);
  if (!profile.runtimePatches || !profile.enabled.length) throw new Error("Experimental staging requires explicit nonempty runtime selection");
  if (process.env.CODEX_LAB_EXPERIMENTAL_CANDIDATE !== "1") throw new Error("Set CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 for a disposable candidate, never an installed tree");
  const resolved = fs.realpathSync(appDir);
  if (resolved.startsWith("/opt/") || resolved.startsWith("/usr/")) throw new Error("Installed runtime trees are forbidden");
  const info = stage(appDir, profilePath, featuresRoot, true);
  const runtime = await require("./lab-runtime-features.js").stageRuntime(appDir, info.linuxFeatures.enabled);
  info.runtime = runtime;
  fs.writeFileSync(path.join(appDir, ".codex-linux", "build-info.json"), JSON.stringify(info, null, 2) + "\n");
  return info;
}

if (require.main === module) (async () => {
  try {
    const [command, appDir, profilePath, featuresRoot] = process.argv.slice(2);
    if (!appDir || !["stage", "experimental-stage", "diagnose"].includes(command) || (command !== "diagnose" && !profilePath)) {
      throw new Error("Usage: scripts/lab-features.js stage|experimental-stage APP PROFILE [FEATURES_ROOT] | diagnose APP");
    }
    const result = command === "stage" ? stage(appDir, profilePath, featuresRoot)
      : command === "experimental-stage" ? await experimentalStage(appDir, profilePath, featuresRoot) : diagnose(appDir);
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
  } catch (error) {
    console.error(`lab-features: ${error.message}`);
    process.exit(1);
  }
})();

module.exports = { stage, diagnose, experimentalStage };
