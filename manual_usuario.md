# User Manual

## English

Codex I+D Lab - Unofficial provides an unofficial Linux packaging and update path for Codex UI.

## Install Or Update

Fresh install, update, or migration from the former project name:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/0xCyberBerserker/codex-id-lab-unofficial/main/scripts/codex-lab-install)
```

After installation:

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

`codex-lab-update` is the short alias with the same flags. Former `codex-ui-*` commands remain temporarily available only for migration.

The smoke test launches Codex UI with a temporary profile and verifies that the native runtime remains active.

Voice and composer dictation are provided by the official Linux runtime and use the selected PipeWire microphone. Microphone access must also be allowed by the desktop portal or session policy.

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

Después de instalar:

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

`codex-lab-update` es el alias corto con los mismos flags. Los comandos anteriores `codex-ui-*` se mantienen temporalmente sólo para la migración.

El smoke test lanza Codex UI con un perfil temporal y comprueba que el runtime nativo permanece activo.

La voz y el dictado del compositor los proporciona el runtime Linux oficial y usan el micrófono PipeWire seleccionado. El portal del escritorio o la política de sesión también deben permitir el acceso al micrófono.

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
- Forks privados o entornos con rate limit pueden usar `GITHUB_TOKEN` o `GH_TOKEN`.
- No guardes chats, credenciales, perfiles, bases runtime ni material local de proyectos en este repositorio.

Consulta `docs/usage.md` para uso detallado.
