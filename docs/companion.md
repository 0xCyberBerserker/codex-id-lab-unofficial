# Local Companion

## English

`codex-lab-tools` is the native Qt companion shipped by this port. It follows the active `QPalette` and provides:

- local Codex usage and rate-limit status through the bundled Codex CLI
- region OCR with Tesseract and Spectacle
- QR capture with clipboard history suppression on KDE
- metadata-only notifications for new user coredumps

It does not scan session archives, retain account responses, read core bytes, or include command lines and environment variables in crash reports.

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

- estado local de consumo y límites de Codex mediante el CLI incluido
- OCR de región con Tesseract y Spectacle
- captura QR sin conservar el contenido en el historial de KDE
- notificaciones de nuevos coredumps del usuario limitadas a metadatos

No escanea archivos de sesiones, no conserva respuestas de cuenta, no lee los bytes del core y excluye argumentos de ejecución y variables de entorno de los informes.

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
