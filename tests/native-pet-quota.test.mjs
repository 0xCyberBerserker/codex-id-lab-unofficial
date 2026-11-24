import { test } from "node:test";
import assert from "node:assert/strict";
import { nativeQuotaPanel, quotaPanelLayout, quotaRows } from "../linux-features/native-pet-quota/quota.mjs";
import runtime from "../scripts/lab-runtime-features.js";

test("experimental profile patches only the exact pet bundle, preserving the avatar and main process", () => {
  const bundle = "webview/assets/async/355340.2e31e7f34f.js";
  const fixture = 'function iN(e){return {items:[{node:jsx(A,{skin:em},"pet"):null]})}),aY?null:';
  const baseline = { [bundle]: fixture, ".vite/build/main-fixture.js": "baseline" };
  assert.deepEqual(runtime.patchSources(structuredClone(baseline), []), []);
  const candidate = structuredClone(baseline);
  assert.equal(runtime.patchSources(candidate, ["native-pet-quota"])[0].file, bundle);
  assert.match(candidate[bundle], /codexLabNativeQuotaPanel/);
  assert.match(candidate[bundle], /skin:em/);
  assert.equal(candidate[".vite/build/main-fixture.js"], "baseline");
  assert.throws(() => runtime.patchSources({ [bundle]: "upstream changed" }, ["native-pet-quota"]), /missing/);
});

test("native snapshots render only valid windows and update from new data", () => {
  const now = Date.parse("2026-11-22T10:00:00Z");
  const window = { used_percent: 0, reset_at: now / 1000 + 90 };
  const usage = { secondary_window: window };
  const [row] = quotaRows(usage, now, "es-ES", "Europe/Madrid");
  assert.equal(row.key, "secondary_window");
  assert.equal(row.percent, 0);
  assert.match(row.reset, /domingo.*11:01/);
  assert.equal(row.left, "2 min");
  assert.equal(quotaRows(usage, now + 60_000, "en-GB", "UTC")[0].left, "1 min");
  const [updated] = quotaRows({ secondary_window: { ...window, used_percent: 85 } },
    now + 90_000, "en-GB", "UTC");
  assert.equal(updated.left, "Awaiting refresh");
  assert.equal(updated.percent, 85);
  assert.deepEqual(quotaRows({ primary_window: { used_percent: null } }, now, "en"), []);
  assert.deepEqual(quotaRows(null, now, "en"), []);
});

test("reviewed 26.1120 renderer uses its live query and layout bindings", () => {
  const bundle = "webview/assets/async/268134.9d35b4d545.js";
  const fixture = 'function iN(e){return {items:[{node:jsx(A,{skin:em},"pet"):null]})}),az?null:';
  const files = { [bundle]: fixture };
  assert.equal(runtime.patchSources(files, ["native-pet-quota"])[0].file, bundle);
  assert.match(files[bundle], /a\("Q840"\)\.Ul,a\("gPv1"\)\.Ix/);
  assert.match(files[bundle], /a\$\?\(0,i\.jsx\)\(codexLabNativeQuotaPanel/);
  assert.match(files[bundle], /visibleBounds:ex\.visibleBounds,tray:ex\.tray\?\?null/);
});

test("panel reacts to query updates and does not retain unavailable data", t => {
  t.mock.method(Date, "now", () => Date.parse("2026-11-22T10:00:00Z"));
  Object.defineProperty(globalThis, "document", {
    configurable: true, value: { documentElement: { lang: "es-ES" } },
  });
  t.after(() => { delete globalThis.document; });
  let result;
  const query = {};
  const render = nativeQuotaPanel(
    { useState: fn => [fn()], useEffect() {} },
    (tag, props) => ({ tag, ...props }),
    source => { assert.equal(source, query); return result; },
    query, quotaRows, quotaPanelLayout,
  );
  const panel = () => render({
    mascot: { left: 300, top: 200, width: 112, height: 120 },
    visibleBounds: { left: 0, top: 0, width: 800, height: 600 },
  });
  const window = { used_percent: 42, reset_at: Date.now() / 1000 + 60 };
  result = { data: { rate_limit: { primary_window: window } }, dataUpdatedAt: Date.now() };
  assert.equal(panel().children[0].children[0].children, "42%");
  assert.equal(panel().style.width, 320);
  assert.equal(panel()["data-codex-lab-quota-updated-at"], Date.now());
  assert.equal(panel().style.pointerEvents, "none");
  result = { data: { rate_limit: { secondary_window: { ...window, used_percent: 80 } } } };
  assert.equal(panel().children[0].children[0].children, "80%");
  result = { ...result, isError: true, dataUpdatedAt: Date.now() };
  assert.equal(panel().children.children, "Sin datos de uso");
  assert.equal(panel()["data-codex-lab-quota-updated-at"], undefined);
});

test("panel scales with the mascot and selects space away from the activity stack", () => {
  const bounds = { left: 0, top: 0, width: 740, height: 500 };
  const pet = { left: 300, top: 220, width: 112, height: 120 };
  const above = quotaPanelLayout(pet, bounds, null, 2);
  assert.equal(above.width, 320);
  assert.ok(above.top + above.height < 0);
  const closer = quotaPanelLayout(pet, bounds, null, 2, 49 / 208);
  assert.equal(closer.top - above.top, 14);
  assert.equal(closer.width, above.width);
  assert.ok(closer.top + closer.height < pet.height * 49 / 208);
  assert.ok(quotaPanelLayout({ ...pet, width: 180 }, bounds, null, 2).width > above.width);
  const corner = { ...pet, left: 580, top: 5 };
  const side = quotaPanelLayout(corner, bounds, null, 2);
  assert.ok(side.left + side.width < 0);
  const blocked = { left: 0, top: 0, width: 570, height: 160 };
  const below = quotaPanelLayout(corner, bounds, blocked, 2);
  assert.ok(below.top > corner.height);
  assert.equal(quotaPanelLayout(corner, { ...bounds, width: 50 }, null, 2), null);
});
