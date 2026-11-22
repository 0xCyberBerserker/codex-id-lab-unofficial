export function quotaRows(usage, now, locale, timeZone) {
  const spanish = /^es(?:-|$)/i.test(locale);
  const format = new Intl.DateTimeFormat(locale, {
    weekday: "long", day: "numeric", hour: "2-digit", minute: "2-digit", timeZone,
  });
  return ["primary_window", "secondary_window"].flatMap((key, index) => {
    const window = usage?.[key];
    if (!Number.isFinite(window?.used_percent)
      || window.used_percent < 0 || window.used_percent > 100) return [];
    const date = window.reset_at * 1000;
    const valid = Number.isFinite(window.reset_at) && date > 0 && date <= 8.64e15;
    const minutes = Math.ceil((date - now) / 60_000);
    const hours = Math.floor(minutes / 60);
    return [{
      key, percent: Math.round(window.used_percent),
      label: (spanish ? ["Principal", "Secundario"] : ["Primary", "Secondary"])[index],
      reset: valid ? format.format(date) : null,
      left: !valid ? null : minutes <= 0
        ? spanish ? "Pendiente de actualizar" : "Awaiting refresh"
        : hours ? `${hours} h ${minutes % 60} min` : `${minutes} min`,
    }];
  });
}

export function quotaPanelLayout(mascot, bounds, tray, rows, headroom = 0) {
  if (!mascot || !bounds || mascot.width <= 0 || bounds.width < 176) return null;
  const clamp = (value, min, max) => Math.max(min, Math.min(value, max));
  const scale = clamp(mascot.width / 112, 0.86, 1.3);
  const edge = 8;
  const gap = 8;
  const rowHeight = Math.round(52 * scale);
  const width = Math.min(Math.round(320 * scale), bounds.width - 2 * edge);
  const height = rowHeight * rows + gap * (rows - 1);
  const left = bounds.left + edge, top = bounds.top + edge;
  const right = bounds.left + bounds.width - edge, bottom = bounds.top + bounds.height - edge;
  const centered = clamp(mascot.left + (mascot.width - width) / 2, left, right - width);
  const beside = clamp(mascot.top, top, bottom - height);
  const clearance = gap * 2;
  const inset = clamp(Math.floor(mascot.height * headroom / 2), 0, 14);
  const candidates = [
    [centered, mascot.top - height - gap + inset],
    [mascot.left - width - gap, beside],
    [mascot.left + mascot.width + gap, beside],
    [centered, mascot.top + mascot.height + 52 * scale + gap],
  ];
  for (const [x, y] of candidates) {
    if (x < left || x + width > right || y < top || y + height > bottom) continue;
    if (tray && x < tray.left + tray.width + clearance && x + width > tray.left - clearance
      && y < tray.top + tray.height + clearance && y + height > tray.top - clearance) continue;
    return { left: x - mascot.left, top: y - mascot.top, width, height, rowHeight, gap, scale };
  }
  return null;
}

// Serialized into the pinned native renderer, with its existing React and query modules.
export function nativeQuotaPanel(React, jsx, useQuery, usageQuery, rowsFor, layoutFor) {
  return function NativeQuotaPanel({ mascot, visibleBounds, tray, headroom }) {
    const { data, isError, dataUpdatedAt } = useQuery(usageQuery);
    const [now, setNow] = React.useState(Date.now);
    React.useEffect(() => {
      const id = setInterval(() => setNow(Date.now()), 1000);
      return () => clearInterval(id);
    }, []);
    const locale = document.documentElement.lang || navigator.language;
    const rows = rowsFor(isError ? null : data?.rate_limit, now, locale);
    const noData = /^es(?:-|$)/i.test(locale) ? "Sin datos de uso" : "Usage unavailable";
    const layout = layoutFor(mascot, visibleBounds, tray, Math.max(1, rows.length), headroom);
    if (!layout) return null;
    const ring = Math.round(34 * layout.scale);
    const surface = "var(--color-background-elevated-secondary, Canvas)";
    const rowStyle = {
      display: "grid", alignItems: "center", gap: 10,
      gridTemplateColumns: rows.length ? `${ring}px minmax(0, 1fr)` : "minmax(0, 1fr)",
      boxSizing: "border-box", minHeight: layout.rowHeight, padding: "5px 12px",
      borderRadius: 999, border: "1px solid var(--color-border, GrayText)",
      background: surface, color: "var(--color-text, CanvasText)",
      fontSize: Math.round(13 * layout.scale), lineHeight: 1.18,
    };
    return jsx("div", {
      "data-codex-lab-native-quota": "",
      "data-codex-lab-quota-updated-at": !isError && dataUpdatedAt > 0 ? dataUpdatedAt : undefined,
      style: {
        position: "absolute", left: layout.left, top: layout.top,
        pointerEvents: "none", zIndex: 2, width: layout.width, display: "grid", gap: layout.gap,
      },
      children: rows.length === 0 ? jsx("div", { style: rowStyle, children: noData }) : rows.map(row => jsx("div", {
        style: rowStyle,
        children: [
          jsx("span", {
            "aria-label": `${row.label}: ${row.percent}%`,
            style: {
              display: "grid", placeItems: "center", width: ring, height: ring,
              borderRadius: "50%", fontWeight: 600, whiteSpace: "nowrap",
              background: `radial-gradient(circle, ${surface} 57%, transparent 61%), conic-gradient(#5abf85 ${row.percent}%, #80808040 0)`,
            },
            children: `${row.percent}%`,
          }),
          jsx("span", {
            style: { minWidth: 0, overflowWrap: "anywhere" },
            children: [
              jsx("strong", { style: { display: "block" }, children: row.reset || row.label }),
              row.left ? jsx("span", {
                style: { color: "var(--color-text-secondary, GrayText)" }, children: row.left,
              }) : null,
            ],
          }),
        ],
      }, row.key)),
    });
  };
}
