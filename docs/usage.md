# Usage

## Update

Fresh install, update, or migration:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/0xCyberBerserker/codex-id-lab-unofficial/main/scripts/codex-lab-install)
```

After installation:

```bash
codex-lab-install
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
codex-lab-install --smoke
```

`codex-lab-update` is the short alias with the same flags. Former `codex-ui-*` commands remain temporarily available only for migration.

The smoke test launches Codex UI with a temporary profile and verifies that the native runtime remains active.

## Voice And Dictation

Voice chat and dictation come from the official Linux runtime and use the microphone selected under Codex UI settings. The desktop portal or session policy must also allow microphone access.

Update to the latest rebuilt package before testing:

```bash
codex-lab-install
```

If no input is listed, confirm that PipeWire exposes a default source, then reopen Codex UI after selecting it.

## Runtime Overrides

The launcher follows the host locale and the official runtime's display backend selection. Optional overrides:

```bash
CODEX_LAB_LANG=es-ES codex-lab
CODEX_LAB_OZONE_PLATFORM=x11 codex-lab
CODEX_LAB_ELECTRON_FLAGS="--disable-vulkan --force-device-scale-factor=1" codex-lab
```

No language, X11 backend, Vulkan mode, or scale factor is forced by default.

## Local Companion

The package ships `codex-lab-tools`, a native Qt companion for local usage status, OCR, private QR capture, and metadata-only coredump notifications. Enable it with:

```bash
systemctl --user enable --now codex-lab-companion.service
```

This service is independent from the Codex UI process. Enabling or restarting it does not restart Codex UI. See [companion.md](companion.md) for its privacy boundaries and commands.

## Discord Rich Presence

Copy `docs/discord-rich-presence.example.json` to
`~/.config/codex-id-lab-unofficial/discord-rich-presence.json`, then set the public
Discord Application ID and your own activities. The application name is the
bold title shown by Discord. Asset fields accept keys configured in the Discord
Developer Portal. Restart Codex UI after editing the file.

No client secret or API key is required.

## Voz y dictado (Español)

El chat por voz y el dictado proceden del runtime Linux oficial y usan el micrófono seleccionado en los ajustes de Codex UI. El portal del escritorio o la política de sesión también deben permitir el acceso al micrófono.

Actualiza al último paquete reconstruido antes de probar:

```bash
codex-lab-install
```

Si no aparece ninguna entrada, confirma que PipeWire expone una fuente predeterminada y vuelve a abrir Codex UI después de seleccionarla.

## Companion local (Español)

El paquete incluye `codex-lab-tools`, un companion Qt nativo para consultar el consumo local, capturar OCR y QR privados y notificar coredumps usando solo metadatos. Se habilita con:

```bash
systemctl --user enable --now codex-lab-companion.service
```

Este servicio es independiente del proceso de Codex UI. Habilitarlo o reiniciarlo no reinicia Codex UI. Consulta [companion.md](companion.md) para ver sus límites de privacidad y comandos.

## Discord Rich Presence (Español)

Copia `docs/discord-rich-presence.example.json` en
`~/.config/codex-id-lab-unofficial/discord-rich-presence.json` y configura el ID
público de la aplicación de Discord y tus propias actividades. El nombre de la
aplicación es el título en negrita que muestra Discord. Los campos de imágenes
aceptan claves configuradas en el portal de desarrolladores de Discord. Reinicia
Codex UI después de editar el archivo.

No hace falta ningún secreto de cliente ni API key.
