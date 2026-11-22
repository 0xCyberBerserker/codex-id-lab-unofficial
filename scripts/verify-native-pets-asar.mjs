import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { pathToFileURL } from "node:url";
import * as asar from "../tools/asar-builder/node_modules/@electron/asar/lib/asar.js";
import patch from "../linux-features/native-pet-quota/patch.js";
import { readFile } from "node:fs/promises";

const bundle = "webview/assets/async/355340.2e31e7f34f.js";
const { lab } = JSON.parse(await readFile(new URL("../linux-features/native-pet-quota/feature.json", import.meta.url)));

export async function verifyNativePetsAsar(upstream, candidate, approved = lab.compatibility.asarSha256) {
  const hash = createHash("sha256");
  for await (const chunk of createReadStream(upstream)) hash.update(chunk);
  assert.ok(approved.includes(hash.digest("hex")), "Unreviewed upstream ASAR");
  const entries = file => asar.listPackage(file).map(value => value.slice(1)).sort();
  const paths = entries(upstream);
  assert.deepEqual(entries(candidate), paths, "ASAR path inventory changed");
  assert.ok(paths.includes(bundle), "Native pet bundle missing");

  for (const path of paths) {
    const source = asar.statFile(upstream, path, false);
    const target = asar.statFile(candidate, path, false);
    assert.equal(Boolean(source.files), Boolean(target.files), `Directory type drift: ${path}`);
    assert.equal(source.link, target.link, `Link drift: ${path}`);
    assert.equal(Boolean(source.unpacked), Boolean(target.unpacked), `Packing drift: ${path}`);
    assert.equal(Boolean(source.executable), Boolean(target.executable), `Mode drift: ${path}`);
    if (source.files || source.link) continue;
    const before = asar.extractFile(upstream, path);
    const after = asar.extractFile(candidate, path);
    if (path !== bundle) {
      assert.ok(before.equals(after), `Unauthorized content change: ${path}`);
      continue;
    }
    const input = before.toString("utf8");
    const expected = patch.applyNativePetQuota(input);
    assert.notEqual(expected, input, "Patch did not apply");
    assert.ok(after.equals(Buffer.from(expected)), "Native pet bundle differs from the reviewed patch");
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    if (process.argv.length !== 4) throw new Error("Usage: verify-native-pets-asar.mjs UPSTREAM CANDIDATE");
    await verifyNativePetsAsar(process.argv[2], process.argv[3]);
    console.log("verify-native-pets-asar: only the reviewed native usage patch changed");
  } catch (error) {
    console.error("verify-native-pets-asar: " + error.message);
    process.exitCode = 1;
  }
}
