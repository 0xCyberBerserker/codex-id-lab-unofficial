"use strict";

const { nativeQuotaPanel, quotaPanelLayout, quotaRows } = require("./quota.mjs");
const slot = '},"pet"):null]})}),aY?null:';
const boundary = "function iN(e){";
const marker = "const codexLabNativeQuotaPanel=";

function applyNativePetQuota(source) {
  if (source.includes(marker)) return source;
  if (source.split(boundary).length !== 2 || source.split(slot).length !== 2) return source;
  const panel = `${marker}(${nativeQuotaPanel})(g,i.jsx,u.Ul,a("gPv1").Ix,(${quotaRows}),(${quotaPanelLayout}));`;
  return source.replace(boundary, () => panel + boundary).replace(slot, () =>
    '},"pet"):null,aG?(0,i.jsx)(codexLabNativeQuotaPanel,{mascot:a8,visibleBounds:eb.visibleBounds,tray:ef?eb.tray:null},"codex-lab-quota"):null]})}),aY?null:');
}

module.exports = { applyNativePetQuota, descriptors: [] };
