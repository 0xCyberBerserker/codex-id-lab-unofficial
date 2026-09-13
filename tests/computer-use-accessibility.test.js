const assert = require('node:assert/strict');
const {test} = require('node:test');
const {spawn, spawnSync} = require('node:child_process');
const path = require('node:path');
const {setTimeout: delay} = require('node:timers/promises');

const backend = process.env.CODEX_LAB_TEST_ACCESSIBILITY_BACKEND;
const isolated = process.env.CODEX_LAB_TEST_NATIVE_ISOLATED === '1';
const labels = {en: 'Fixture input', es: 'Entrada de prueba', ca: 'Entrada de prova'};

function readReady(child) {
  return new Promise((resolve, reject) => {
    let buffer = '';
    const timer = setTimeout(() => reject(new Error('Qt fixture readiness timed out')), 8000);
    child.once('error', error => { clearTimeout(timer); reject(error); });
    child.once('exit', () => { clearTimeout(timer); reject(new Error('Qt fixture exited before readiness')); });
    child.stdout.on('data', chunk => {
      buffer += chunk.toString('utf8');
      if (buffer.length > 4096) { clearTimeout(timer); reject(new Error('Qt fixture readiness exceeded bound')); return; }
      const newline = buffer.indexOf('\n');
      if (newline !== -1) {
        clearTimeout(timer);
        try { resolve(JSON.parse(buffer.slice(0, newline))); }
        catch (error) { reject(error); }
      }
    });
  });
}

function call(args) {
  const result = spawnSync(backend, args, {encoding: 'utf8', timeout: 12000, maxBuffer: 2 * 1024 * 1024});
  assert.ifError(result.error);
  assert.equal(result.status, 0, `Native accessibility call failed: ${result.stderr}`);
  return JSON.parse(result.stdout);
}

for (const language of ['en', 'es', 'ca']) {
  test(`real native CLI discovers and reads only the isolated Qt ${language} fixture`, {skip: !isolated || !backend}, async () => {
    assert.equal(spawnSync('/usr/bin/test', ['-e', '/run/user']).status, 1, 'Personal desktop runtime must be masked before starting');
    assert.equal(spawnSync('/usr/bin/test', ['-e', '/dev/input']).status, 1);
    assert.equal(spawnSync('/usr/bin/test', ['-e', '/dev/uinput']).status, 1);
    const fixture = spawn('/usr/bin/python3', [path.join(__dirname, 'computer_use_accessibility_fixture.py'), language],
      {stdio: ['ignore', 'pipe', 'pipe']});
    fixture.stderr.resume();
    try {
      const ready = await readReady(fixture);
      assert.equal(ready.pid, fixture.pid);
      assert.equal(ready.inputLabel, labels[language]);
      let apps, selected;
      const deadline = Date.now() + 8000;
      do {
        apps = call(['apps']);
        assert.ok(Array.isArray(apps));
        selected = apps.find(app => app.pid === fixture.pid);
        if (selected) break;
        await delay(200);
      } while (Date.now() < deadline);
      assert.ok(selected, 'Fixture PID must be discoverable through actual AT-SPI');
      assert.equal(apps.length, 1, 'No unrelated accessibility application may be visible');
      assert.equal(selected.name, 'codex-lab-accessibility-fixture');
      const tree = call(['state', selected.name]);
      assert.ok(Array.isArray(tree) && tree.length > 0);
      const editor = tree.find(node => node.name === labels[language] && node.supports_editable_text);
      assert.ok(editor, 'Named editable Qt input must be present in the actual tree');
      assert.equal(editor.text?.content, 'lab-fixture-only');
      assert.equal(editor.text?.truncated, false);
      assert.ok(editor.bounds?.width > 0 && editor.bounds?.height > 0);
      assert.ok(editor.states.some(state => /focus/i.test(state)), 'Fixture input must expose focus state');
    } finally {
      fixture.kill('SIGTERM');
      if (fixture.exitCode === null && fixture.signalCode === null) {
        await new Promise(resolve => fixture.once('exit', resolve));
      }
    }
    assert.equal(spawnSync('/usr/bin/test', ['-e', '/dev/input']).status, 1);
    assert.equal(spawnSync('/usr/bin/test', ['-e', '/dev/uinput']).status, 1);
    assert.equal(spawnSync('/usr/bin/test', ['-e', '/run/user']).status, 1);
  });
}
