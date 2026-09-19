"use strict";

// The upstream webview renderer is reused; the host adapter has no installer or downloader.
const webview = require("./webview.js");

function nativeHelperSource() {
  return `
let codexLabSpeechChild=null;
function codexLabSpeechStop(){let child=codexLabSpeechChild;codexLabSpeechChild=null;if(!child)return{stopped:false,reason:"idle"};try{child.kill("SIGTERM")}catch{}return{stopped:true}}
function codexLabSpeechSpeak(input){
 if(process.platform!=="linux")return{spoken:false,reason:"not-linux"};
 let text=typeof input==="string"?input.trim().slice(0,8000):"";
 if(!text)return{spoken:false,reason:"empty"};
 const cp=require("node:child_process"),fs=require("node:fs"),path=require("node:path");
 let binary=String(process.env.PATH||"").split(path.delimiter).filter(Boolean).map(p=>path.join(p,"espeak-ng")).find(p=>{try{fs.accessSync(p,fs.constants.X_OK);return fs.statSync(p).isFile()}catch{return false}});
 if(!binary)return{spoken:false,reason:"voice-unavailable"};
 codexLabSpeechStop();
 let language=String(process.env.CODEX_LAB_LANG||process.env.LANG||"en").slice(0,2),voice=["en","es","ca"].includes(language)?language:"en";
 try{let child=cp.spawn(binary,["--stdin","-v",voice],{stdio:["pipe","ignore","ignore"]});codexLabSpeechChild=child;
 child.on("error",()=>{if(codexLabSpeechChild===child)codexLabSpeechChild=null});
 child.on("exit",()=>{if(codexLabSpeechChild===child)codexLabSpeechChild=null});
 child.stdin.on("error",()=>{});child.stdin.end(text);return{spoken:true,engine:"espeak-ng"};
 }catch{return{spoken:false,reason:"voice-unavailable"}}
}
process.once?.("exit",()=>codexLabSpeechStop());
`;
}

function applyMainBundlePatch(source) {
  if (source.includes("function codexLabSpeechSpeak(")) return source;
  const marker = '"native-desktop-apps":async';
  if (source.split(marker).length !== 2) throw new Error("Read Aloud host handler drift");
  const handler = '"linux-read-aloud":async e=>{if(e?.action==="stop")return codexLabSpeechStop();if(e?.action==="speak"&&e?.source==="button")return codexLabSpeechSpeak(e.text);return{spoken:false,reason:"not-explicit"}},';
  return source.replace(marker, handler + marker) + nativeHelperSource();
}

function applyIndexRuntimePatch(source) {
  const patched = webview.applyIndexRuntimePatch(source);
  if (patched === source) return source;
  const labels = {
    es: {"Read assistant response aloud": "Leer respuesta en voz alta", "Stop read aloud": "Detener lectura", "Loading voice": "Cargando voz", "No voice available": "Voz no disponible", "Starting voice": "Iniciando voz", "Enable Read aloud in settings": "Activa la lectura en ajustes", "Install Read aloud voice model": "Falta el modelo de voz", "Nothing to read": "No hay texto para leer"},
    ca: {"Read assistant response aloud": "Llegir resposta en veu alta", "Stop read aloud": "Aturar lectura", "Loading voice": "Carregant veu", "No voice available": "Veu no disponible", "Starting voice": "Iniciant veu", "Enable Read aloud in settings": "Activa la lectura als ajustos", "Install Read aloud voice model": "Falta el model de veu", "Nothing to read": "No hi ha text per llegir"},
  };
  const translation = `;globalThis.codexLabSpeechLabel=text=>{const language=String(globalThis.navigator?.language||"en").slice(0,2),labels=${JSON.stringify(labels)};return labels[language]?.[text]||text};\n`;
  return translation + patched.replace("let title=buttonLabel(state,label);", "let title=globalThis.codexLabSpeechLabel(buttonLabel(state,label));")
    .replace("conversationId:conversationId||null,", "")
    .replace("globalThis.codexLinuxReadAloudSetup=setup;", "");
}

function applyAssistantRenderPatch(source) {
  const patched = webview.applyAssistantRenderPatch(source);
  if (patched === source) return source;
  return patched.replaceAll('title:"Read assistant response aloud","aria-label":"Read assistant response aloud"', 'title:globalThis.codexLabSpeechLabel?.("Read assistant response aloud")||"Read assistant response aloud","aria-label":globalThis.codexLabSpeechLabel?.("Read assistant response aloud")||"Read assistant response aloud"');
}

module.exports = { applyMainBundlePatch, applyIndexRuntimePatch, applyAssistantRenderPatch, nativeHelperSource };
