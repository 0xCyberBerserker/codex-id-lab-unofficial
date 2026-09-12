// SPDX-License-Identifier: MIT
// Copyright (c) 2025 ilysenko
// Selected upstream transport and bundle fixtures; no hooks or orphan reaper.
const {EventEmitter}=require('node:events');
const {PassThrough}=require('node:stream');
const fs=require('node:fs');
const vm=require('node:vm');
const {sharedTransportClassSource}=require('../linux-features/shared-app-server-socket/patch.js');
function fakeChild() {
  const child = new EventEmitter();
  child.pid = process.pid;
  child.exitCode = null;
  child.signalCode = null;
  child.stdin = new PassThrough();
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  child.killed = false;
  child.kill = () => {
    child.killed = true;
    child.signalCode = "SIGTERM";
    queueMicrotask(() => child.emit("close", null, "SIGTERM"));
    return true;
  };
  return child;
}

function loadInjectedTransport({ spawnImpl, WebSocketImpl = null, fsImpl = fs, timeoutCapMs = null } = {}) {
  class DefaultWebSocket extends EventEmitter {
    constructor(_url, options) {
      super();
      this.stream = options.createConnection();
      queueMicrotask(() => this.emit("open"));
    }

    terminate() {
      this.terminated = true;
      this.stream?.destroy();
    }
  }
  class Adapter {
    constructor(socket) {
      this.socket = socket;
    }
  }
  const namespace = {
    WS: WebSocketImpl ?? DefaultWebSocket,
    keepAlive() {},
    Adapter,
  };
  const source = sharedTransportClassSource({
    namespace: "n",
    webSocketClass: "WS",
    webSocketUrl: "url",
    keepAlive: "keepAlive",
    adapterClass: "Adapter",
  });
  const context = {
    Buffer,
    n: namespace,
    url: "ws://localhost/rpc",
    process,
    console,
    require(id) {
      if (id === "node:child_process") return { spawn: spawnImpl };
      if (id === "node:fs") return fsImpl;
      return require(id);
    },
    setTimeout(callback, delay, ...args) {
      const timer = setTimeout(
        callback,
        timeoutCapMs == null ? delay : Math.min(delay, timeoutCapMs),
        ...args,
      );
      if (timeoutCapMs != null) timer.unref = () => timer;
      return timer;
    },
    clearTimeout,
  };
  vm.runInNewContext(`${source};globalThis.Transport=CodexLinuxSharedAppServerSocketTransport`, context);
  const InjectedTransport = context.Transport;
  class Transport extends InjectedTransport {
    constructor(socketPath, getConfigOverrides = async () => []) {
      super(socketPath, getConfigOverrides);
    }
  }
  return { InjectedTransport, Transport, namespace };
}

function syntheticBundle() {
  return [
    "var gC=class{options;kind=`websocket`;logger=i.i(`AppServerTransportSshWebsocket`);proxyStreams=new Set;hasConnected=!1;supportsReconnect(){return!0}",
    "async connect(){let t={current:null},r=new n.kn(qae,{perMessageDeflate:!1,createConnection:()=>",
    "(t.current=this.createSshProxyStream(),t.current)});r.once(`close`,()=>{t.current?.destroy()});try{await Xae(r)}catch(e){throw r.once(`error`,()=>void 0),t.current?.destroy(),r.terminate(),e}",
    "return n.Dn(r,{onPongTimeout:()=>{r.terminate()}}),this.hasConnected=!0,new n.On(r)}};",
    "function b5(e){let t=_C(e.hostConfig);if(t)return v5.info(`[ssh-websocket-v0] selected app-server transport`),new gC(t);",
    "if(e.transportKind===`remote-control`)return new Remote(e);",
    "if(n.no(e.hostConfig))return new hoe({hostConfig:e.hostConfig,repoRoot:e.repoRoot,resourcesPath:e.resourcesPath,defaultOriginator:e.defaultOriginator});",
    "let r=x5(e.hostConfig);if(r){e.desktopAuthAppServerClient;let t=vbe(e.hostConfig,r);return new n.Tn({hostConfig:e.hostConfig,websocketUrl:r,getWebsocketProtocols:void 0,...t==null?{}:{socksProxyUrl:t}})}",
    "return new n.Cn({hostConfig:e.hostConfig,repoRoot:e.repoRoot,resourcesPath:e.resourcesPath,defaultOriginator:e.defaultOriginator,getConfigOverrides:()=>Ope(e)})}function afterFactory(){}",
  ].join("");
}

module.exports={fakeChild,loadInjectedTransport,syntheticBundle};
