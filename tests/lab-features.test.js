"use strict";

const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { stage, diagnose } = require("../scripts/lab-features.js");

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "codex-lab-features-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const app = path.join(root, "app");
  const featuresRoot = path.join(root, "features");
  const profile = path.join(root, "profile.json");
  fs.mkdirSync(path.join(app, "resources"), { recursive: true });
  fs.mkdirSync(featuresRoot);
  const asar = Buffer.from("unchanged upstream fixture");
  fs.writeFileSync(path.join(app, "resources", "app.asar"), asar);
  const asarSha = crypto.createHash("sha256").update(asar).digest("hex");
  const writeProfile = enabled => fs.writeFileSync(profile, JSON.stringify({ id: "fixture", enabled, settings: {}, runtimePatches: false }));
  const addFeature = (id, extra = {}) => {
    const featureDir = path.join(featuresRoot, id);
    fs.mkdirSync(featureDir);
    fs.writeFileSync(path.join(featureDir, "README.md"), `# ${id}\n`);
    fs.writeFileSync(path.join(featureDir, "resource.json"), '{"fixture":true}\n');
    const manifest = {
      id,
      title: id,
      defaultEnabled: false,
      resources: [{ source: "resource.json", target: `.codex-linux/features/${id}/resource.json`, mode: "0644" }],
      lab: { capabilities: ["declarative-resource"], compatibility: { asarSha256: [asarSha] }, stability: "experimental", tests: ["tests/lab-features.test.js"] },
      ...extra,
    };
    fs.writeFileSync(path.join(featureDir, "feature.json"), JSON.stringify(manifest));
  };
  writeProfile([]);
  return { root, app, featuresRoot, profile, asar, asarSha, writeProfile, addFeature };
}

test("base profile leaves upstream ASAR intact and has no extra resources", t => {
  const f = fixture(t);
  const result = stage(f.app, f.profile, f.featuresRoot);
  assert.deepEqual(result.linuxFeatures.enabled, []);
  assert.deepEqual(result.resources, []);
  assert.deepEqual(fs.readFileSync(path.join(f.app, "resources", "app.asar")), f.asar);
  assert.deepEqual(diagnose(f.app).linuxFeatures.enabled, []);
});

test("selection stages into an artifact, diagnoses and disables without residual resources", t => {
  const f = fixture(t);
  f.addFeature("diagnostic-fixture");
  f.writeProfile(["diagnostic-fixture"]);
  stage(f.app, f.profile, f.featuresRoot);
  const archive = path.join(f.root, "candidate.tar");
  execFileSync("bsdtar", ["-cf", archive, "-C", f.app, "."]);
  const extracted = path.join(f.root, "extracted");
  fs.mkdirSync(extracted);
  execFileSync("bsdtar", ["-xf", archive, "-C", extracted]);
  const diagnostic = diagnose(extracted);
  assert.deepEqual(diagnostic.linuxFeatures.enabled, ["diagnostic-fixture"]);
  assert.equal(diagnostic.features[0].status, "staged-not-runtime-verified");
  const resource = path.join(extracted, ".codex-linux/features/diagnostic-fixture/resource.json");
  const original = fs.readFileSync(resource);
  fs.writeFileSync(resource, "tampered");
  assert.throws(() => diagnose(extracted), /resource drift/);
  fs.writeFileSync(resource, original);
  f.writeProfile([]);
  stage(extracted, f.profile, f.featuresRoot);
  assert.equal(fs.existsSync(resource), false);
  assert.deepEqual(diagnose(extracted).linuxFeatures.enabled, []);
  assert.deepEqual(fs.readFileSync(path.join(extracted, "resources", "app.asar")), f.asar);
});

test("unknown IDs, conflicts and upstream drift reject candidates before mutation", t => {
  const f = fixture(t);
  f.writeProfile(["unknown"]);
  assert.throws(() => stage(f.app, f.profile, f.featuresRoot), /not found.*unknown/);
  f.addFeature("first", { conflicts: ["second"] });
  f.addFeature("second");
  f.writeProfile(["first", "second"]);
  assert.throws(() => stage(f.app, f.profile, f.featuresRoot), /conflicts/);
  const manifestPath = path.join(f.featuresRoot, "first", "feature.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.conflicts = [];
  manifest.lab.compatibility.asarSha256 = ["0".repeat(64)];
  fs.writeFileSync(manifestPath, JSON.stringify(manifest));
  f.writeProfile(["first"]);
  assert.throws(() => stage(f.app, f.profile, f.featuresRoot), /ASAR drift/);
  assert.deepEqual(fs.readFileSync(path.join(f.app, "resources", "app.asar")), f.asar);
  assert.equal(fs.existsSync(path.join(f.app, ".codex-linux")), false);
});
