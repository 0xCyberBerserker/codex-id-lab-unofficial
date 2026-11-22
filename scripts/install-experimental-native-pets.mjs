import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { lstat, mkdtemp, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { isAbsolute, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";
import lab from "./lab-features.js";
import runtime from "./lab-runtime-features.js";
import * as asar from "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js";

const approved = "6570177341c8a8b98c7036dcf95d008b48d8fbb0cf0961dc3e1aba137bc9e29a";
const asset = "webview/assets/null-signal-spritesheet-v7.e7af0b42f5.webp";
const root = fileURLToPath(new URL("../", import.meta.url));

async function install(candidate, profile) {
  runtime.assertDisposableCandidate(candidate);
  if (!isAbsolute(profile) || !(await lstat(profile)).isDirectory())
    throw new Error("An explicit, existing profile directory is required");
  profile = await realpath(profile);
  const output = join(profile, "pets", "null-signal-pirate");
  const existing = await lstat(output).catch(error => {
    if (error.code === "ENOENT") return null;
    throw error;
  });
  if (existing) throw new Error("Custom pet already exists; it was not overwritten");
  const archive = join(candidate, "resources", "app.asar");
  const hash = createHash("sha256");
  for await (const chunk of createReadStream(archive)) hash.update(chunk);
  if (hash.digest("hex") !== approved) throw new Error("Unsupported or modified upstream ASAR");
  const temp = await mkdtemp(join(tmpdir(), "codex-pet-install-"));
  try {
    const sprite = join(temp, "null-signal.webp");
    const compiler = join(temp, "export-pirate-sheet");
    const sheet = join(temp, "atlas.png");
    await writeFile(sprite, asar.extractFile(archive, asset), { mode: 0o600, flag: "wx" });
    const qt = execFileSync("pkg-config", ["--cflags", "--libs", "Qt6Gui"], { encoding: "utf8" }).trim();
    execFileSync("c++", ["-std=c++17", "-fPIC", join(root, "tools/native-pet-art/export-pirate-sheet.cpp"),
      "-o", compiler, ...qt.split(/\s+/)], { stdio: "inherit" });
    execFileSync(compiler, [sprite, sheet], { stdio: "inherit" });
    await lab.experimentalStage(candidate, join(root, "packaging/profiles/experimental-native-pets.json"));
    execFileSync("python3", [join(root, "scripts/codex_lab_pet.py"),
      "--profile", profile, "--id", "null-signal-pirate", "--name", "Null Pirate", sheet], { stdio: "inherit" });
  } finally {
    await rm(temp, { recursive: true, force: true });
  }
}

try {
  const { values } = parseArgs({ options: { candidate: { type: "string" }, profile: { type: "string" } } });
  if (process.env.CODEX_LAB_EXPERIMENTAL_CANDIDATE !== "1" || !values.candidate || !values.profile)
    throw new Error("Usage: CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/install-experimental-native-pets.mjs --candidate APP --profile PROFILE");
  await install(values.candidate, values.profile);
} catch (error) {
  console.error("install-experimental-native-pets: " + error.message);
  process.exitCode = 1;
}
