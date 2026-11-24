"use strict";

const { nativeQuotaPanel, quotaPanelLayout, quotaRows } = require("./quota.mjs");
const variants = [
  ['},"pet"):null]})}),aY?null:', 'aY', 'u.Ul', 'aG', 'eb', 'ef?eb.tray:null'],
  ['},"pet"):null]})}),az?null:', 'az', 'a("Q840").Ul', 'a$', 'ex', 'ex.tray??null'],
];
const boundary = "function iN(e){";
const marker = "const codexLabNativeQuotaPanel=";

function applyNativePetQuota(source) {
  if (source.includes(marker)) return source;
  const matches = variants.filter(([slot]) => source.split(slot).length === 2);
  if (source.split(boundary).length !== 2 || matches.length !== 1) return source;
  const [slot, hidden, queryHook, showsPet, layout, tray] = matches[0];
  const panel = `${marker}(${nativeQuotaPanel})(g,i.jsx,${queryHook},a("gPv1").Ix,(${quotaRows}),(${quotaPanelLayout}));`;
  return source.replace(boundary, () => panel + boundary).replace(slot, () =>
    `},"pet"):null,${showsPet}?(0,i.jsx)(codexLabNativeQuotaPanel,{mascot:a8,visibleBounds:${layout}.visibleBounds,tray:${tray}},"codex-lab-quota"):null]})}),${hidden}?null:`);
}

module.exports = { applyNativePetQuota, descriptors: [] };
