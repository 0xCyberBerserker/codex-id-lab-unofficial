# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and release tags use the upstream Codex UI version packaged by this project.

## [Unreleased]

### Changed

- Packaging now uses the official Linux-native ChatGPT/Owl runtime instead of the macOS bundle on stock Electron.
- Scheduled releases verify the signed official Linux repository and inherit upstream voice, dictation, app tools, plugins, and later features without minified-code patches.
- Discord Rich Presence activities are now selected randomly without immediate repetition.
- Standardized the updater command as `codex-ui-update`; `codexui-update` remains available as a compatibility alias with identical flags.

### Fixed

- Release freshness now includes the Linux build-recipe fingerprint, so integration changes rebuild an existing upstream version.
- Companion shutdown now cancels its temporary Codex CLI query before waiting for the worker.
- The companion now keeps its single-instance socket in the shared user runtime directory, including under `PrivateTmp`.
- `codex-ui-update --force` now genuinely reinstalls the current package on Arch, Debian, and RPM-based systems.
- Discord Rich Presence now clears immediately when Codex exits instead of leaving a stale activity visible.
- The updater now removes stale per-user desktop entry overrides after preserving customized copies, so package updates are visible in desktop menus.

### Added

- Native Qt companion with local Codex usage, OCR, private QR capture, and metadata-only coredump notifications.
- English and Spanish companion UI, desktop actions, user service, and package dependencies.
- Optional Discord Rich Presence with rotating user-defined activities, artwork, elapsed session time, and HTTPS buttons. Private configuration remains under the user's XDG config directory.
- Repo-local Codex instructions.
- Standard project documentation set: user manual, architecture, and roadmap.

### Documentation

- Linked the standard documentation set from `README.md`.

---

# Registro de cambios

Todos los cambios relevantes del proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y los tags de release usan la versión upstream de Codex UI empaquetada por este proyecto.

## [Sin publicar]

### Cambiado

- El empaquetado usa ahora el runtime ChatGPT/Owl nativo oficial para Linux en lugar del bundle macOS sobre Electron estándar.
- Las releases programadas verifican el repositorio Linux oficial firmado y heredan voz, dictado, herramientas, plugins y funciones posteriores sin patches sobre código minificado.
- Las actividades de Discord Rich Presence ahora se eligen aleatoriamente sin repetición inmediata.
- Estandarizado el comando como `codex-ui-update`; `codexui-update` permanece como alias compatible con los mismos flags.

### Corregido

- La comprobación de vigencia de releases incluye ahora la huella de la receta de build para Linux, por lo que los cambios de integración reconstruyen una versión upstream ya existente.
- El cierre del companion cancela la consulta temporal a Codex CLI antes de esperar al worker.
- El companion mantiene ahora el socket de instancia única en el directorio runtime compartido del usuario, también con `PrivateTmp`.
- `codex-ui-update --force` ahora reinstala realmente el paquete actual en sistemas Arch, Debian y basados en RPM.
- Discord Rich Presence ahora se elimina al cerrar Codex en lugar de dejar una actividad obsoleta visible.
- El actualizador elimina overrides obsoletos del lanzador de usuario tras conservar una copia si estaba personalizado, por lo que las actualizaciones del paquete llegan al menú de aplicaciones.

### Añadido

- Companion Qt nativo con consumo local de Codex, OCR, captura QR privada y notificaciones de coredumps limitadas a metadatos.
- Interfaz del companion en inglés y español, acciones de escritorio, servicio de usuario y dependencias de paquete.
- Discord Rich Presence opcional con actividades configurables y rotatorias, imágenes, tiempo de sesión y botones HTTPS. La configuración privada permanece en el directorio XDG del usuario.
- Instrucciones repo-locales para Codex.
- Conjunto estándar de documentación: manual de usuario, arquitectura y roadmap.

### Documentación

- Enlazado el conjunto estándar de documentación desde `README.md`.
