# Local Companion

## English

`codex-lab-tools` is the native Qt companion shipped by this port. It follows the active `QPalette` and provides:

- persistent local quota status through a fully initialized Codex App Server connection
- region OCR with Tesseract and Spectacle
- QR capture with a KDE clipboard-history hint (other clipboard clients may retain it)
- metadata-only notifications for new user coredumps

It does not scan session archives, persist account responses, read core bytes, or include command lines and environment variables in crash reports. Quotas are kept in memory while running.

Quota notifications update the panel automatically. Opening uses a 45-second cache;
idle polling is approximately five minutes with jitter and reconnect backoff.
Secondary usage failure preserves valid quotas; disconnection preserves the last
snapshot with its age and stale status. Account changes invalidate old data.
Missing/null/invalid percentages stay unknown, and a passed reset timestamp does
not imply replenishment. IDs, real window duration and server reset classification
are preserved. See the [official App Server contract](https://learn.chatgpt.com/docs/app-server).

This independent provider does **not** observe desktop tasks. The pinned upstream
shared-socket bridge requires an opt-in ASAR transport patch plus a verified
WebSocket byte-stream adapter, not the standalone JSON-lines connection used here.
Task status, approvals, Stop and prompt dispatch therefore remain unavailable.
No conversation is started merely to read quotas.

The approximately 400-logical-pixel panel follows QPalette and supports English,
Spanish and Catalan. It is a compatible Qt dialog, not a native Wayland flyout.
Without a tray, the manual panel remains available. Offscreen GUI tests cover all
three languages in light/dark palettes; live Plasma SNI, Wayland focus/outside-click,
X11 and physical multi-monitor/DPI acceptance remain NOT_RUN.

Install from a checkout without replacing or restarting Codex UI:

```bash
scripts/install-codex-lab-companion --enable --desktop-shortcut
```

Packaged installations can enable it with:

```bash
systemctl --user enable --now codex-lab-companion.service
```

Commands:

```bash
codex-lab-tools panel
codex-lab-tools usage-json
codex-lab-tools ocr
codex-lab-tools qr
codex-lab-tools crashes
```

OCR requires Spectacle, Tesseract, English and Spanish language data. QR capture requires `zbarimg`. Crash reports are created with mode `0600` under `~/.local/state/codex-id-lab-unofficial/crashes`.

---

## Español

`codex-lab-tools` es el companion Qt nativo incluido por este port. Respeta la `QPalette` activa y ofrece:

- límites persistentes mediante una conexión App Server completamente inicializada
- OCR de región con Tesseract y Spectacle
- captura QR con una indicación para el historial de KDE; otros clientes pueden conservarla
- notificaciones de nuevos coredumps del usuario limitadas a metadatos

No escanea sesiones, no persiste respuestas de cuenta, no lee los bytes del core y
excluye argumentos y variables de entorno de los informes. Las cuotas solo se
mantienen en memoria durante la ejecución.

Los eventos actualizan el panel automáticamente. Al abrir, la caché dura 45 s;
en reposo consulta aproximadamente cada cinco minutos, con jitter y backoff.
Un fallo secundario no borra los límites. La desconexión conserva el último dato
con antigüedad y estado stale; cambiar de cuenta lo invalida. Valores ausentes,
null o inválidos son desconocidos. Pasar la hora de reset no inventa saldo.
Se conservan IDs, duración real y clasificación del servidor.

El provider independiente **no** observa tareas del desktop. El puente compartido
upstream necesita un parche ASAR opt-in y un adaptador WebSocket de bytes verificado;
no usa el framing JSON-lines de esta conexión. Tareas, aprobaciones, Stop y envío
de prompts siguen indisponibles. Consultar cuotas no inicia una conversación.

El panel de unos 400 píxeles lógicos respeta QPalette y ofrece inglés, español y
catalán. Es un diálogo Qt compatible, no un flyout Wayland nativo. Sin tray queda
la apertura manual. Se prueban los tres idiomas con paletas clara/oscura offscreen;
SNI real, foco/click exterior Wayland, X11 y DPI/multimonitor físicos siguen NOT_RUN.

Puede instalarse desde el checkout sin reemplazar ni reiniciar Codex UI:

```bash
scripts/install-codex-lab-companion --enable --desktop-shortcut
```

En una instalación empaquetada se habilita con:

```bash
systemctl --user enable --now codex-lab-companion.service
```

Comandos:

```bash
codex-lab-tools panel
codex-lab-tools usage-json
codex-lab-tools ocr
codex-lab-tools qr
codex-lab-tools crashes
```

El OCR necesita Spectacle, Tesseract y los datos de idioma inglés y español. La captura QR necesita `zbarimg`. Los informes se crean con modo `0600` bajo `~/.local/state/codex-id-lab-unofficial/crashes`.
