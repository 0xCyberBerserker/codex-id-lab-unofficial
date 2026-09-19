const assert = require('node:assert/strict');
const {test} = require('node:test');
const {spawnSync} = require('node:child_process');

const isolated = process.env.CODEX_LAB_TEST_NATIVE_ISOLATED === '1';
const backend = process.env.CODEX_LAB_TEST_COMPUTER_USE_BACKEND;

test('real native Computer Use MCP rejects unavailable capabilities in a private namespace', {skip: !isolated || !backend}, async () => {
  const {createNativeService} = await import('../linux-features/computer-use-linux/native-service.mjs');
  const service = createNativeService({command: backend, timeoutMs: 5000});
  try {
    await assert.rejects(service.handleRpc({method: 'list_apps'}), /session bus|X11 session/);
    await assert.rejects(service.handleRpc({method: 'screenshot'}), /non-empty native app id/);
    await assert.rejects(service.handleRpc({method: 'click', app: 'isolated-missing-app', params: {x: 0, y: 0}}), /target|window|match|accessib/i);
  } finally {
    service.shutdown();
  }
  const doctor = spawnSync(backend, ['doctor'], {encoding: 'utf8', timeout: 5000});
  assert.equal(doctor.status, 0);
  const report = JSON.parse(doctor.stdout);
  assert.ok(report && typeof report === 'object');
  assert.equal(spawnSync('/usr/bin/test', ['-e', '/dev/uinput']).status, 1);
  assert.equal(spawnSync('/usr/bin/test', ['-e', '/dev/input']).status, 1);
});
