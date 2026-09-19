# User Manual

## English

Codex I+D Lab - Unofficial provides an unofficial Linux packaging and update path for Codex UI.

## Install Or Update

Fresh install, update, or migration from the former project name:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/0xCyberBerserker/codex-id-lab-unofficial/main/scripts/codex-lab-install)
```

After installation, the command also refreshes the application-menu entry and desktop shortcut:

```bash
codex-lab-install
```

## Check Latest Available Version

```bash
codex-lab-install --check
```

## Smoke Test

```bash
codex-lab-install --smoke
```

`codex-lab-update` is the short alias with the same flags. Legacy `codex-ui-*` launchers are removed during migration.

The smoke test launches Codex UI with a temporary profile and verifies that the native runtime remains active.

Voice and composer dictation are inherited where the official runtime/account support them; packaging does not grant microphone permission or server capabilities. Real authenticated voice/dictation are NOT_RUN in the local development candidate.

`codex-lab-tools features` opens feature preferences; saving requests a future
rebuild, not installation. `codex-lab-tools features-json`,
`codex-lab-update --status` and `--doctor` expose sanitized local state.
`--wait` defers elevation until the runtime closes. Changed build profiles require
`--allow-profile-change`; explicit downgrades also require
`--accept-data-downgrade-risk`. No flag restores or deletes user data.
See [features](docs/features.md), [recovery](docs/updater-recovery.md) and
[local AppImage limits](docs/appimage.md).

## Local Companion

The package includes `codex-lab-tools`. It shows local Codex usage, captures text and QR codes, and records safe crash metadata. Enable its tray service with:

```bash
systemctl --user enable --now codex-lab-companion.service
```

The companion is a separate process and does not restart Codex UI. Detailed commands and privacy limits are documented in `docs/companion.md`.

## Supported Systems

- Arch/CachyOS through `pacman`
- Debian/Ubuntu through `apt-get` experimental packages
- Fedora/RHEL-like systems through `dnf` experimental packages

## Security Notes

- Public release downloads do not require authentication.
- GitHub CLI (`gh`) verifies the manifest and package build provenance.
- Private forks or rate-limited environments can use `GITHUB_TOKEN` or `GH_TOKEN`.
- Do not store chats, credentials, profiles, runtime databases, or local project material in this repository.

See `docs/usage.md` for detailed usage.

---

# Manual de usuario

## Español

Codex I+D Lab - Unofficial proporciona una vía no oficial para empaquetar y actualizar Codex UI en Linux.

## Instalar o actualizar

Instalación desde cero, actualización o migración desde el nombre anterior:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/0xCyberBerserker/codex-id-lab-unofficial/main/scripts/codex-lab-install)
```

Después de instalar, el comando también actualiza la entrada del menú de aplicaciones y el acceso directo del escritorio:

```bash
codex-lab-install
```

## Comprobar última versión disponible

```bash
codex-lab-install --check
```

## Smoke test

```bash
codex-lab-install --smoke
```

`codex-lab-update` es el alias corto con los mismos flags. Los lanzadores antiguos `codex-ui-*` se eliminan durante la migración.

El smoke test lanza Codex UI con un perfil temporal y comprueba que el runtime nativo permanece activo.

Voz y dictado se heredan cuando el runtime oficial y la cuenta los permiten; el empaquetado no concede permisos de micrófono ni capacidades del servidor. Voz y dictado autenticados siguen NOT_RUN en el candidato local.

`codex-lab-tools features` abre preferencias para un rebuild futuro, sin instalar.
`features-json`, `codex-lab-update --status` y `--doctor` muestran estado local
saneado. `--wait` espera al cierre antes de elevar privilegios. Cambiar el perfil
exige `--allow-profile-change`; un downgrade exige además
`--accept-data-downgrade-risk`. Ningún flag restaura ni borra datos personales.
Consulta funciones, recuperación y límites AppImage en los enlaces anteriores.

## Companion local

El paquete incluye `codex-lab-tools`. Muestra el consumo local de Codex, captura texto y códigos QR y registra metadatos seguros de fallos. Su servicio de bandeja se habilita con:

```bash
systemctl --user enable --now codex-lab-companion.service
```

El companion es un proceso independiente y no reinicia Codex UI. Los comandos y límites de privacidad se documentan en `docs/companion.md`.

## Sistemas soportados

- Arch/CachyOS mediante `pacman`
- Debian/Ubuntu mediante paquetes experimentales con `apt-get`
- Sistemas tipo Fedora/RHEL mediante paquetes experimentales con `dnf`

## Notas de seguridad

- Las descargas públicas de release no requieren autenticación.
- GitHub CLI (`gh`) verifica la procedencia de build del manifiesto y del paquete.
- Forks privados o entornos con rate limit pueden usar `GITHUB_TOKEN` o `GH_TOKEN`.
- No guardes chats, credenciales, perfiles, bases runtime ni material local de proyectos en este repositorio.

Consulta `docs/usage.md` para uso detallado.
