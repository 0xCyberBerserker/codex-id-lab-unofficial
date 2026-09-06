# Usage

## Update

```bash
codex-ui-update
```

The updater detects the host OS, downloads the latest compatible package from the GitHub release, verifies checksums, installs the package, and checks the installed command.

## Supported Systems

- CachyOS and Arch-like systems using `pacman`
- Debian and Ubuntu-like systems using `apt-get` (experimental)
- Fedora and RHEL-like systems using `dnf` (experimental)

## Authentication

Public releases do not require authentication.

Private forks or rate-limited environments can authenticate with `GITHUB_TOKEN` or `GH_TOKEN`. Public GitHub releases use the unauthenticated Releases API and do not require GitHub CLI.

## Smoke Test

```bash
codex-ui-update --smoke
```

`codexui-update` remains available as a compatibility alias with the same flags.

The smoke test launches Codex UI with a temporary profile and checks for a successful startup log.

## Runtime Overrides

The launcher follows the host locale and Electron's native display backend selection. Optional overrides:

```bash
CODEXUI_LANG=es-ES codex-ui-linux
CODEXUI_OZONE_PLATFORM=x11 codex-ui-linux
CODEXUI_ELECTRON_FLAGS="--disable-vulkan --force-device-scale-factor=1" codex-ui-linux
```

No language, X11 backend, Vulkan mode, or scale factor is forced by default.

## Local Companion

The package ships `codex-ui-tools`, a native Qt companion for local usage status, OCR, private QR capture, and metadata-only coredump notifications. Enable it with:

```bash
systemctl --user enable --now codex-ui-companion.service
```

This service is independent from the Codex UI process. Enabling or restarting it does not restart Codex UI. See [companion.md](companion.md) for its privacy boundaries and commands.

## Discord Rich Presence

Copy `docs/discord-rich-presence.example.json` to
`~/.config/codex-ui-linux-port/discord-rich-presence.json`, then set the public
Discord Application ID and your own activities. The application name is the
bold title shown by Discord. Asset fields accept keys configured in the Discord
Developer Portal. Restart Codex UI after editing the file.

No client secret or API key is required.

## Companion local (Español)

El paquete incluye `codex-ui-tools`, un companion Qt nativo para consultar el consumo local, capturar OCR y QR privados y notificar coredumps usando solo metadatos. Se habilita con:

```bash
systemctl --user enable --now codex-ui-companion.service
```

Este servicio es independiente del proceso de Codex UI. Habilitarlo o reiniciarlo no reinicia Codex UI. Consulta [companion.md](companion.md) para ver sus límites de privacidad y comandos.

## Discord Rich Presence (Español)

Copia `docs/discord-rich-presence.example.json` en
`~/.config/codex-ui-linux-port/discord-rich-presence.json` y configura el ID
público de la aplicación de Discord y tus propias actividades. El nombre de la
aplicación es el título en negrita que muestra Discord. Los campos de imágenes
aceptan claves configuradas en el portal de desarrolladores de Discord. Reinicia
Codex UI después de editar el archivo.

No hace falta ningún secreto de cliente ni API key.
