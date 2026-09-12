const assert = require('node:assert/strict');
const {test} = require('node:test');

test('native transport pins system PATH and portal-only capture despite ambient overrides', async () => {
  const {createNativeService} = await import('../linux-features/computer-use-linux/native-service.mjs');
  const originalPath = process.env.PATH;
  const originalBackend = process.env.CODEX_COMPUTER_USE_SCREENSHOT_BACKEND;
  const source = `
    require('node:readline').createInterface({input:process.stdin}).on('line', line => {
      const message = JSON.parse(line);
      if (!message.id) return;
      const result = message.method === 'initialize'
        ? {protocolVersion:'2024-11-05', capabilities:{tools:{}}}
        : {structuredContent:{ok:true,path:process.env.PATH,backend:process.env.CODEX_COMPUTER_USE_SCREENSHOT_BACKEND}};
      console.log(JSON.stringify({jsonrpc:'2.0',id:message.id,result}));
    });`;
  process.env.PATH = '/tmp/untrusted-executables';
  process.env.CODEX_COMPUTER_USE_SCREENSHOT_BACKEND = 'gnome-screenshot';
  const service = createNativeService({command:process.execPath,args:['-e',source],timeoutMs:1000});
  try {
    const result = await service.handleRpc({method:'press_key',app:'fixture',params:{key:'ESC'}});
    assert.equal(result.path, '/usr/bin:/bin');
    assert.equal(result.backend, 'portal');
  } finally {
    service.shutdown();
    if (originalPath === undefined) delete process.env.PATH; else process.env.PATH = originalPath;
    if (originalBackend === undefined) delete process.env.CODEX_COMPUTER_USE_SCREENSHOT_BACKEND;
    else process.env.CODEX_COMPUTER_USE_SCREENSHOT_BACKEND = originalBackend;
  }
});
