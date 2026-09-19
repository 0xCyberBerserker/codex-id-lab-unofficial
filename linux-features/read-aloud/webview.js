// SPDX-License-Identifier: MIT
// Copyright (c) 2025 ilysenko; selective Lab integration.
"use strict";
const HELPER_MARKER="codexLinuxReadAloudClick";
const SETUP_MARKER="codexLinuxReadAloudSetup";
const HANDLER_NAME="linux-read-aloud";
const RUNTIME_VERSION="lab-native-v1";
const ASSISTANT_RENDER_CANDIDATE_PATTERN=/\.(?:jsx|jsxs)\)\([A-Za-z_$][\w$]*,\{(?=[^{}]{0,2500}\bitem:)(?=[^{}]{0,2500}\bassistantCopyText:)(?=[^{}]{0,2500}\bconversationId:)/u;
function warn(message,patchName){console.warn(`WARN: ${message} - ${patchName}`)}
function readAloudRuntimeSource() {
  return [
    `;(()=>{const VERSION=${JSON.stringify(RUNTIME_VERSION)};if(globalThis.codexLinuxReadAloudVersion===VERSION)return;globalThis.codexLinuxReadAloudVersion=VERSION;try{globalThis.speechSynthesis?.cancel?.()}catch{}`,
    `const METHOD=${JSON.stringify(HANDLER_NAME)};let seq=0,pending=new Map,currentButton=null,currentSpeakTimer=null;`,
    `function onMessage(e){let t=e?.data;if(!t||typeof t!="object"||t.type!=="fetch-response")return;let n=pending.get(t.requestId);if(!n)return;pending.delete(t.requestId);if(t.responseType==="success"){let e=null;try{e=t.bodyJsonString?JSON.parse(t.bodyJsonString):null}catch{}n.resolve({status:t.status,body:e})}else n.reject(Error(t.error||"fetch failed"))}`,
    `window.addEventListener("message",onMessage);`,
    `function dispatch(payload){let bridge=window.electronBridge,event=new CustomEvent("codex-message-from-view",{detail:payload});if(bridge?.sendMessageFromView){event.__codexForwardedViaBridge=!0;bridge.sendMessageFromView(payload).catch(()=>{})}window.dispatchEvent(event)}`,
    `function log(message,tags={}){dispatch({type:"log-message",level:"info",message,tags:{safe:tags,sensitive:{}}})}`,
    `function hostPost(method,body,timeoutMs=4000){let requestId="codex-linux-read-aloud-"+ ++seq;let payload={type:"fetch",hostId:"local",requestId,method:"POST",url:"vscode://codex/"+method,body:JSON.stringify(body??{})};return new Promise((resolve,reject)=>{pending.set(requestId,{resolve,reject});setTimeout(()=>{pending.delete(requestId);reject(Error("timeout"))},timeoutMs);dispatch(payload)})}`,
    `function post(params,timeoutMs=4000){return hostPost(METHOD,params,timeoutMs)}`,
    `function clean(text){return String(text||"").replace(/\\r\\n/g,"\\n").replace(/\`\`\`[\\s\\S]*?\`\`\`/g," code block. ").replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g,"$1").replace(/[*_#>~]/g,"").replace(/\\n{3,}/g,"\\n\\n").trim().slice(0,8e3)}`,
    `function buttonLabel(state,label){return label??(state==="speaking"?"Stop read aloud":state==="loading"?"Loading voice":state==="error"?"No voice available":"Read assistant response aloud")}`,
    `function setButton(button,state,label){if(!button)return;let title=buttonLabel(state,label);button.dataset.codexLinuxReadAloudState=state;button.title=title;button.setAttribute("aria-label",title);button.disabled=state==="loading"}`,
    `function flash(button,label){setButton(button,"error",label);setTimeout(()=>setButton(button,"ready"),1500)}`,
    `function resetButton(button=currentButton){if(currentSpeakTimer!=null){clearTimeout(currentSpeakTimer);currentSpeakTimer=null}if(button)setButton(button,"ready");if(button===currentButton)currentButton=null}`,
    `function stopSpeech(){resetButton();post({action:"stop"}).catch(()=>{})}`,
    `function estimateMs(text){let words=text.split(/\\s+/).filter(Boolean).length;return Math.max(3000,Math.min(120000,words*360))}`,
    `function failureLabel(result){let reason=result?.reason;if(reason==="disabled")return"Enable Read aloud in settings";if(reason==="kokoro-unavailable")return"Install Read aloud voice model";if(reason==="empty")return"Nothing to read";return"No voice available"}`,
    `async function click(item,copyText,conversationId,button){try{button?.blur?.();if(globalThis.codexLinuxConversationIsSpeaking?.()){globalThis.codexLinuxConversationStopSpeaking?.();resetButton(button);return}if(button?.dataset.codexLinuxReadAloudState==="speaking"){stopSpeech();return}let text=clean(copyText||item?.content||"");if(text.length<2)return;setButton(button,"loading","Starting voice");let result=await post({action:"speak",source:"button",text}).then(e=>e.body).catch(()=>({spoken:!1,reason:"request-failed"}));log("[linux-read-aloud] click",{conversationId:conversationId||null,textLength:text.length,spoken:result?.spoken===!0,engine:result?.engine||null,reason:result?.reason||null,missing:Array.isArray(result?.missing)?result.missing.join(","):null});if(result?.spoken){currentButton=button;setButton(button,"speaking");currentSpeakTimer=setTimeout(()=>resetButton(button),estimateMs(text));return}flash(button,failureLabel(result))}catch{flash(button,"No voice available")}}`,
    `function setupLabel(result){let reason=result?.reason;if(reason==="cancelled")return"Cancelled";if(reason==="missing-files")return"Folder is missing model files";if(reason==="python-unavailable")return"Python 3.10-3.13 required";if(reason==="voice-unavailable")return"Voice backend missing";return result?.ok?"Voice ready":"Setup failed"}`,
    `async function setup(mode,button){let original=button?.dataset.codexLinuxReadAloudOriginalLabel||button?.textContent||"";if(button&&!button.dataset.codexLinuxReadAloudOriginalLabel)button.dataset.codexLinuxReadAloudOriginalLabel=original;try{button&&(button.disabled=!0,button.textContent=mode==="download"?"Downloading...":"Choosing...");let result=await post({action:"setup",mode},mode==="download"?9e5:6e4).then(e=>e.body).catch(()=>({ok:!1,reason:"request-failed"}));button&&(button.textContent=setupLabel(result));setTimeout(()=>{button&&(button.textContent=original,button.disabled=!1)},1800);return result}catch{button&&(button.textContent="Setup failed",setTimeout(()=>{button.textContent=original,button.disabled=!1},1800))}}`,
    `function installStyle(){if(document.getElementById("codex-linux-read-aloud-style"))return;let e=document.createElement("style");e.id="codex-linux-read-aloud-style";e.textContent=".codex-linux-read-aloud-row{display:flex;align-items:center;margin-top:4px}.codex-linux-read-aloud-button{width:28px;height:24px;display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--token-border);background:transparent;color:var(--text-secondary,var(--token-description-foreground));border-radius:6px;padding:0;cursor:pointer}.codex-linux-read-aloud-icon{width:15px;height:15px}.codex-linux-read-aloud-button:hover{background:var(--token-list-hover-background,rgba(127,127,127,.12));color:var(--text-primary,var(--token-foreground))}.codex-linux-read-aloud-button:disabled{opacity:.65;cursor:default}.codex-linux-read-aloud-button[data-codex-linux-read-aloud-state=speaking]{background:var(--token-list-hover-background,rgba(127,127,127,.14));color:var(--text-primary,var(--token-foreground))}.codex-linux-read-aloud-button[data-codex-linux-read-aloud-state=error]{color:var(--token-error-foreground,#c00);border-color:currentColor}";document.head.appendChild(e)}`,
    `installStyle();globalThis.${HELPER_MARKER}=click;globalThis.${SETUP_MARKER}=setup;globalThis.codexLinuxReadAloudGetSetting=key=>hostPost("get-global-state",{params:{key}}).then(e=>e.body?.value);globalThis.codexLinuxReadAloudSetSetting=(key,value)=>hostPost("set-global-state",{params:{key,value}}).then(e=>e.body);})();`,
  ].join("");
}

function readAloudIconButtonSource(jsxVar, itemVar, copyVar, conversationVar, eventVar) {
  return `(0,${jsxVar}.jsx)("button",{type:"button",className:"codex-linux-read-aloud-button",title:"Read assistant response aloud","aria-label":"Read assistant response aloud",onClick:${eventVar}=>{${eventVar}.stopPropagation(),globalThis.${HELPER_MARKER}?.(${itemVar},${copyVar},${conversationVar},${eventVar}.currentTarget)},children:(0,${jsxVar}.jsxs)("svg",{"aria-hidden":"true",viewBox:"0 0 24 24",className:"codex-linux-read-aloud-icon",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round",children:[(0,${jsxVar}.jsx)("path",{d:"M11 5 6 9H3v6h3l5 4V5z"}),(0,${jsxVar}.jsx)("path",{d:"M15 9a5 5 0 0 1 0 6"}),(0,${jsxVar}.jsx)("path",{d:"M18 6a9 9 0 0 1 0 12"})]})})`;
}

function readAloudButtonRowSource(jsxVar, itemVar, copyVar, conversationVar, eventVar) {
  return `(0,${jsxVar}.jsx)("div",{className:"codex-linux-read-aloud-row",children:${readAloudIconButtonSource(jsxVar, itemVar, copyVar, conversationVar, eventVar)}})`;
}

function applyIndexRuntimePatch(source) {
  return ensureReadAloudRuntime(source);
}

function ensureReadAloudRuntime(source) {
  if (source.includes(RUNTIME_VERSION)) {
    return source;
  }
  return `${source}\n${readAloudRuntimeSource()}`;
}

function applyAssistantRenderPatch(source) {
  if (source.includes(`globalThis.${HELPER_MARKER}?.(`)) {
    return source;
  }
  const jsxCallPattern =
    /\(0,([A-Za-z_$][\w$]*)\.jsx\)\(([A-Za-z_$][\w$]*),\{(?=[^{}]*\bitem:)(?=[^{}]*\bassistantCopyText:)(?=[^{}]*\bconversationId:)([^{}]*)\}\)/g;
  const readProp = (props, name) =>
    new RegExp(`(?:^|,)${name}:([A-Za-z_$][\\w$]*)`).exec(props)?.[1] ?? null;
  const patched = source.replace(
    jsxCallPattern,
    (match, jsxVar, _component, props) => {
      const itemVar = readProp(props, "item");
      const copyVar = readProp(props, "assistantCopyText");
      const conversationVar = readProp(props, "conversationId");
      if (itemVar == null || copyVar == null || conversationVar == null) {
        return match;
      }
      return `(0,${jsxVar}.jsxs)(${jsxVar}.Fragment,{children:[${match},${readAloudButtonRowSource(jsxVar, itemVar, copyVar, conversationVar, "e")}]})`;
    },
  );
  if (patched !== source) {
    return patched;
  }

  if (ASSISTANT_RENDER_CANDIDATE_PATTERN.test(source)) {
    warn("Could not find assistant message render call", "read aloud assistant render patch");
  }
  return source;
}


module.exports={applyAssistantRenderPatch,applyIndexRuntimePatch};

