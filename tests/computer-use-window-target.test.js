const assert = require('node:assert/strict');
const {test} = require('node:test');
const {spawn, spawnSync} = require('node:child_process');
const path = require('node:path');
const {setTimeout: delay} = require('node:timers/promises');
const {createInterface} = require('node:readline');
const {once} = require('node:events');

const backend = process.env.CODEX_LAB_TEST_ACCESSIBILITY_BACKEND;
const isolated = process.env.CODEX_LAB_TEST_NATIVE_ISOLATED === '1'
  && process.env.CODEX_LAB_TEST_WINDOW_MODE === 'kwin';

test('real native MCP targets and types only in a private KWin X11 fixture', {skip: !isolated || !backend}, async () => {
  for (const target of ['/run/user', '/dev/input', '/dev/uinput']) {
    assert.equal(spawnSync('/usr/bin/test', ['-e', target]).status, 1, `${target} must be masked before launch`);
  }
  const {createNativeService} = await import('../linux-features/computer-use-linux/native-service.mjs');
  const service = createNativeService({command: backend, timeoutMs: 12000});
  const fixture = spawn('/usr/bin/python3', [path.join(__dirname, 'computer_use_accessibility_fixture.py'), 'en'],
    {stdio: ['ignore', 'pipe', 'pipe']});
  const lines = createInterface({input: fixture.stdout});
  fixture.stderr.resume();
  try {
    const [line] = await once(lines, 'line', {signal: AbortSignal.timeout(8000)});
    assert.equal(JSON.parse(line).pid, fixture.pid);
    lines.close();
    fixture.stdout.resume();
    let selected;
    const deadline = Date.now() + 8000;
    do {
      let apps;
      try { apps = await service.handleRpc({method: 'list_apps'}); }
      catch (error) {
        if (!/KWin returned no windows/.test(error.message)) throw error;
        await delay(200);
        continue;
      }
      selected = apps.find(app => app.title === 'Accessibility fixture');
      if (selected) { assert.equal(apps.length, 1); break; }
      await delay(200);
    } while (Date.now() < deadline);
    assert.ok(selected, 'Real KWin inventory must contain the fixture');
    const read = () => service.handleRpc({method: 'get_app_state', app: selected.id,
      params: {include_screenshot: false, max_nodes: 100}});
    const initial = await read();
    assert.equal(initial.window_context.pid, fixture.pid);
    assert.equal(initial.accessibility_error, null);
    const editor = state => state.accessibility_tree.find(node => node.name === 'Fixture input' && node.supports_editable_text);
    assert.equal(editor(initial)?.text?.content, 'lab-fixture-only');
    await service.handleRpc({method: 'press_key', app: selected.id, params: {key: 'Ctrl+A'}});
    await service.handleRpc({method: 'type_text', app: selected.id, params: {text: 'lab-mcp-private-input'}});
    const changed = await read();
    assert.equal(changed.window_context.pid, fixture.pid);
    assert.equal(editor(changed)?.text?.content, 'lab-mcp-private-input');
    assert.equal(changed.screenshot, null);
    const missing = selected.id === 'linux-window:0' ? 'linux-window:1' : 'linux-window:0';
    await assert.rejects(service.handleRpc({method: 'type_text', app: missing,
      params: {text: 'must-not-reach-fixture'}}), /target|window|match/i);
    assert.equal(editor(await read())?.text?.content, 'lab-mcp-private-input');
    // Capture must fail without the private portal; no CLI fallback is accepted.
    await assert.rejects(service.handleRpc({method: 'screenshot', app: selected.id,
      params: {max_width: 420, max_height: 120}}), /portal|ScreenCast|desktop.*capture|service.*provided/i);
  } finally {
    lines.close();
    service.shutdown();
    fixture.kill('SIGTERM');
    if (fixture.exitCode === null && fixture.signalCode === null) {
      await new Promise(resolve => fixture.once('exit', resolve));
    }
  }
});
