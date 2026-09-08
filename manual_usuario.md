# User Manual

## English

Codex UI Linux Port provides an unofficial Linux packaging and update path for Codex UI.

## Install Or Update

```bash
codex-ui-update
```

## Check Latest Available Version

```bash
codex-ui-update --check
```

## Smoke Test

```bash
codex-ui-update --smoke
```

The legacy `codexui-update` command remains available as a compatibility alias with the same flags.

The smoke test launches Codex UI with a temporary profile and checks for a startup marker.

Voice and composer dictation use the selected PipeWire microphone. Global dictation on Linux supports the toggle shortcut: press once to start and again to stop. Automatic paste requires `ydotool` on Wayland or `xdotool` on X11.

## Local Companion

The package includes `codex-ui-tools`. It shows local Codex usage, captures text and QR codes, and records safe crash metadata. Enable its tray service with:

```bash
systemctl --user enable --now codex-ui-companion.service
```

The companion is a separate process and does not restart Codex UI. Detailed commands and privacy limits are documented in `docs/companion.md`.

## Supported Systems

- Arch/CachyOS through `pacman`
- Debian/Ubuntu through `apt-get` experimental packages
- Fedora/RHEL-like systems through `dnf` experimental packages

## Security Notes

- Public release downloads do not require authentication.
- Private forks or rate-limited environments can use `GITHUB_TOKEN` or `GH_TOKEN`.
- Do not store chats, credentials, profiles, runtime databases, or local project material in this repository.

See `docs/usage.md` for detailed usage.

---

# Manual de usuario

## Español

Codex UI Linux Port proporciona una vía no oficial para empaquetar y actualizar Codex UI en Linux.

## Instalar o actualizar

```bash
codex-ui-update
```

## Comprobar última versión disponible

```bash
codex-ui-update --check
```

## Smoke test

```bash
codex-ui-update --smoke
```

El comando anterior `codexui-update` permanece disponible como alias compatible con los mismos flags.

El smoke test lanza Codex UI con un perfil temporal y comprueba una marca de arranque correcto.

La voz y el dictado del compositor usan el micrófono PipeWire seleccionado. El dictado global en Linux admite el atajo alternable: púlsalo una vez para iniciar y otra para detener. El pegado automático requiere `ydotool` en Wayland o `xdotool` en X11.

## Companion local

El paquete incluye `codex-ui-tools`. Muestra el consumo local de Codex, captura texto y códigos QR y registra metadatos seguros de fallos. Su servicio de bandeja se habilita con:

```bash
systemctl --user enable --now codex-ui-companion.service
```

El companion es un proceso independiente y no reinicia Codex UI. Los comandos y límites de privacidad se documentan en `docs/companion.md`.

## Sistemas soportados

- Arch/CachyOS mediante `pacman`
- Debian/Ubuntu mediante paquetes experimentales con `apt-get`
- Sistemas tipo Fedora/RHEL mediante paquetes experimentales con `dnf`

## Notas de seguridad

- Las descargas públicas de release no requieren autenticación.
- Forks privados o entornos con rate limit pueden usar `GITHUB_TOKEN` o `GH_TOKEN`.
- No guardes chats, credenciales, perfiles, bases runtime ni material local de proyectos en este repositorio.

Consulta `docs/usage.md` para uso detallado.
