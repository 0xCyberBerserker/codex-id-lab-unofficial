// SPDX-License-Identifier: MIT
// Copyright (c) 2025 ilysenko
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const parameters = {
  list_apps: [],
  get_app_state: ['include_screenshot', 'max_nodes', 'max_depth', 'max_width', 'max_height', 'max_bytes', 'scale', 'format', 'quality'],
  screenshot: ['max_width', 'max_height', 'max_bytes', 'scale', 'format', 'quality'],
  click: ['x', 'y', 'button', 'click_count', 'relative'],
  scroll: ['x', 'y', 'direction', 'pages', 'relative'],
  press_key: ['key'],
  type_text: ['text'],
};

function validateParameters(params) {
  const integer = (name, minimum, maximum) => {
    if (params[name] !== undefined && (!Number.isInteger(params[name]) || params[name] < minimum || params[name] > maximum)) {
      throw new Error(`Invalid native ${name} parameter`);
    }
  };
  if (params.include_screenshot !== undefined && typeof params.include_screenshot !== 'boolean') throw new Error('Invalid native include_screenshot parameter');
  integer('max_nodes', 1, 2000);
  integer('max_depth', 0, 64);
  integer('max_width', 1, 4096);
  integer('max_height', 1, 4096);
  integer('max_bytes', 1024, 4 * 1024 * 1024);
  integer('quality', 1, 95);
  if (params.scale !== undefined && (typeof params.scale !== 'number' || !Number.isFinite(params.scale) || params.scale <= 0 || params.scale > 1)) throw new Error('Invalid native scale parameter');
  if (params.format !== undefined && !['png', 'jpeg'].includes(params.format)) throw new Error('Invalid native format parameter');
  integer('x', 0, 1_000_000);
  integer('y', 0, 1_000_000);
  integer('click_count', 1, 3);
  if (params.relative !== undefined && params.relative !== true) throw new Error('Invalid native relative parameter');
  if (params.button !== undefined && !['left', 'middle', 'right'].includes(params.button)) throw new Error('Invalid native button parameter');
  if (params.direction !== undefined && !['up', 'down', 'left', 'right'].includes(params.direction)) throw new Error('Invalid native direction parameter');
  if (params.pages !== undefined && (!Number.isFinite(params.pages) || params.pages <= 0 || params.pages > 100)) throw new Error('Invalid native pages parameter');
  for (const [name, maximum] of [['text', 16384], ['key', 256]]) {
    if (params[name] !== undefined && (typeof params[name] !== 'string' || !params[name] || Buffer.byteLength(params[name]) > maximum)) throw new Error(`Invalid native ${name} parameter`);
  }
}

// This service runs in the official Node 24 code-mode host, which provides
// JSON source access and rawJSON. Keep u64 window IDs beyond JS's safe range as
// strings on the RPC side; only the Rust transport receives raw numeric tokens.
function parseBackendJson(text) {
  return JSON.parse(text, (key, value, context) =>
    key === 'window_id' && typeof value === 'number' && !Number.isSafeInteger(value)
      ? context.source : value);
}

// The process owns the Rust backend's state. Failed or interrupted requests are
// never retried: input may already have reached the desktop.
export function createNativeService({
  command = fileURLToPath(new URL('../bin/codex-computer-use-linux', import.meta.url)),
  args = ['mcp'], timeoutMs = 120_000,
} = {}) {
  let child, ready, failure, sequence = 0;
  const pending = new Map();
  function stop(error) {
    failure ??= error;
    for (const { reject, timer } of pending.values()) {
      clearTimeout(timer);
      reject(failure);
    }
    pending.clear();
    child?.kill();
  }
  const shutdown = () => stop(new Error('Linux Computer Use backend shut down'));
  function send(message) {
    child.stdin.write(`${JSON.stringify(message)}\n`, error => { if (error) stop(error); });
  }
  function request(method, params) {
    if (failure) return Promise.reject(failure);
    if (pending.size >= 32) return Promise.reject(new Error('Linux Computer Use request limit reached'));
    return new Promise((resolve, reject) => {
      const id = ++sequence;
      const timer = setTimeout(() => stop(new Error(`Linux Computer Use ${method} timed out; not replayed`)), timeoutMs);
      pending.set(id, { resolve, reject, timer });
      send({ jsonrpc: '2.0', id, method, params });
    });
  }
  async function start() {
    if (failure) throw failure;
    if (!ready) ready = (async () => {
      child = spawn(command, args, { stdio: ['pipe', 'pipe', 'pipe'] });
      child.on('error', error => stop(new Error(`Linux Computer Use backend: ${error.message}`)));
      child.on('exit', (code, signal) => stop(new Error(`Linux Computer Use backend exited (${signal ?? code}); not replayed`)));
      child.stdin.on('error', error => stop(error));
      // Drain diagnostics without leaking application text into the RPC channel.
      child.stderr.resume();
      const handleLine = line => {
        let message;
        try { message = parseBackendJson(line); }
        catch { stop(new Error('Linux Computer Use backend returned invalid JSON')); return; }
        if (!message || typeof message !== 'object' || Array.isArray(message) || message.jsonrpc !== '2.0') {
          stop(new Error('Linux Computer Use backend returned invalid JSON-RPC')); return;
        }
        const call = pending.get(message.id);
        if (!call) {
          if (message.method && message.id !== undefined) send({ jsonrpc: '2.0', id: message.id, error: { code: -32601, message: 'Client requests are unsupported' } });
          return;
        }
        if (Object.hasOwn(message, 'result') === Object.hasOwn(message, 'error')) {
          stop(new Error('Linux Computer Use backend returned ambiguous JSON-RPC')); return;
        }
        pending.delete(message.id);
        clearTimeout(call.timer);
        if (message.error) call.reject(new Error(message.error.message || 'Linux Computer Use RPC error'));
        else call.resolve(message.result);
      };
      let buffer = Buffer.alloc(0);
      const maximumFrameBytes = 8 * 1024 * 1024;
      child.stdout.on('data', chunk => {
        if (failure) return;
        buffer = Buffer.concat([buffer, chunk]);
        let newline;
        while ((newline = buffer.indexOf(10)) !== -1) {
          if (newline > maximumFrameBytes) { stop(new Error('Linux Computer Use backend frame limit exceeded')); return; }
          const line = buffer.subarray(0, newline).toString('utf8');
          buffer = buffer.subarray(newline + 1);
          handleLine(line);
          if (failure) return;
        }
        if (buffer.length > maximumFrameBytes) stop(new Error('Linux Computer Use backend frame limit exceeded'));
      });
      const initialization = await request('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'linux-unified-computer-use', version: '1' } });
      if (initialization?.protocolVersion !== '2024-11-05' || !initialization.capabilities || typeof initialization.capabilities !== 'object') {
        const error = new Error('Linux Computer Use initialization contract drift');
        stop(error); throw error;
      }
      send({ jsonrpc: '2.0', method: 'notifications/initialized' });
    })();
    await ready;
  }
  async function handleRpc(input) {
    const { method, app, params = {} } = input ?? {};
    if (!Object.hasOwn(parameters, method)) throw new Error('This native Linux Computer Use operation is not supported');
    if (!params || typeof params !== 'object' || Array.isArray(params) || Object.keys(params).some(key => !parameters[method].includes(key))) throw new Error('Unsupported native operation parameter');
    validateParameters(params);
    // Lab forbids untargeted native observation/input; there is no desktop fallback.
    if (method !== 'list_apps' && app === undefined) throw new Error('A non-empty native app id is required');
    if (['click', 'scroll'].includes(method) && (!Number.isInteger(params.x) || !Number.isInteger(params.y))) throw new Error('Invalid native coordinates');
    if (['type_text', 'press_key'].includes(method) && params[method === 'type_text' ? 'text' : 'key'] === undefined) throw new Error('Invalid native input parameter');
    let target = {};
    if (app !== undefined) {
      if (typeof app !== 'string' || !app.trim() || Buffer.byteLength(app) > 1024) throw new Error('A non-empty native app id is required');
      if (app.startsWith('linux-window:')) {
        const id = app.slice('linux-window:'.length);
        if (!/^\d+$/.test(id) || BigInt(id) > 18446744073709551615n) throw new Error('Invalid native window id');
        target = { window_id: JSON.rawJSON(BigInt(id).toString()) };
      } else target = { app_id: app };
    }
    await start();
    const result = await request('tools/call', { name: method === 'list_apps' ? 'list_windows' : method, arguments: { ...params, ...target } });
    const message = result?.content?.filter(item => item.type === 'text').map(item => item.text).join('\n');
    if (result?.isError) throw new Error(message || 'Linux Computer Use tool failed');
    let data = result?.structuredContent;
    if (data === undefined) {
      try { data = parseBackendJson(message); }
      catch { throw new Error('Linux Computer Use backend returned no structured result'); }
    }
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Linux Computer Use backend returned invalid structured result');
    if (method === 'get_app_state' && data.window_error) throw new Error(data.window_error);
    if (data.ok === false) throw new Error(data.message || 'Linux Computer Use action failed');
    if (method === 'screenshot') {
      const images = result?.content?.filter(item => item.type === 'image') ?? [];
      if (data.cropped_to_window !== true || images.length !== 1 || !images[0].data || !['image/png', 'image/jpeg'].includes(images[0].mimeType)
          || !/^[A-Za-z0-9+/]+={0,2}$/.test(images[0].data) || Buffer.byteLength(images[0].data, 'base64') > (params.max_bytes ?? 4 * 1024 * 1024)) {
        throw new Error('Linux Computer Use backend returned no valid targeted screenshot');
      }
      return { screenshot: { ...data, data_url: `data:${images[0].mimeType};base64,${images[0].data}` } };
    }
    if (method === 'list_apps') {
      if (data.error) throw new Error(data.error);
      if (!Array.isArray(data.windows) || data.windows.length > 2000) throw new Error('Linux Computer Use backend returned invalid window inventory');
      return data.windows.map(window => ({ id: `linux-window:${window.window_id}`, displayName: window.app_id || window.wm_class || window.title || 'Linux app', title: window.title, isRunning: true, focused: window.focused }));
    }
    return data;
  }
  return { handleRpc, shutdown };
}
const service = createNativeService();
export const handleRpc = service.handleRpc;
export const shutdown = service.shutdown;
process.once('exit', shutdown);
