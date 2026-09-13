# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); package/release identities combine upstream version and the project's packaging revision.

## [Unreleased]

### Changed

- Native anonymous smoke retains Chromium sandbox with software X11; a visible splash/window is separate from loaded/authenticated UI acceptance.
- Computer Use imports the MIT client/transport and fixture tests with mandatory app targets, bounded framing and no input replay; native backend activation remains blocked.
- Feature build-profile export excludes disabled settings and unrelated preferences while preserving the original configuration.
- Companion quotas now use persistent initialized IPC, valid decimal percentages, notifications, stale cache and independent secondary metrics.
- Companion/OCR/QR dependencies are optional; the base runtime no longer requires screenshot and OCR tools.
- Build profile changes and data-risk downgrades require explicit updater flags; corrupt compatibility metadata fails closed.
- Local candidate builds record and re-verify signed APT provenance from cached metadata without downloading the same package again.
- Package identities now separate the upstream version from packaging revision `2` across Arch, Debian, RPM, manifests, tags, and updater decisions.
- External manifests now bind final package hashes and sizes, while embedded manifests bind the build recipe, feature profile, and prepared payload without self-hashes.
- Published releases are immutable drafts promoted only after the complete asset set receives GitHub build-provenance attestations.
- Packaging now uses the official Linux-native ChatGPT/Owl runtime instead of the macOS bundle on stock Electron.
- Scheduled releases verify the signed official Linux repository and inherit upstream voice, dictation, app tools, plugins, and later features without minified-code patches.
- Discord Rich Presence activities are now selected randomly without immediate repetition.
- Standardized the updater command as `codex-lab-install`; `codex-lab-update` remains available as a compatibility alias with identical flags.
- Renamed the project to Codex I+D Lab - Unofficial and standardized public commands under `codex-lab*`; legacy command aliases are removed during migration.
- The installer now refreshes the application-menu entry and desktop shortcut while preserving customized legacy launchers.
- Packages now expose only `codex-lab*` commands; migration removes obsolete per-user `codex-ui*` wrappers.

### Fixed

- RPM validation drains archive padding after the cpio trailer while retaining decoder and extractor failure checks.
- Computer Use transport pins system executable paths and portal-only capture instead of inheriting an ambient CLI fallback; runtime activation remains disabled.
- Recovery retries the journal's exact authenticated candidate, rejects changed digests and ambiguous journals, and does not remove native manager locks or perform global repair.
- RPM forced recovery uses installation when the package is absent instead of assuming a previous transaction completed.

- Native packages enforce root ownership; final payload digests cover updater files and exclude only the embedded identity manifest.
- RPM post-processing no longer strips bundled upstream native binaries; real package comparisons cover the preserved payload.
- Privacy scanning distinguishes the public `.codex-linux` namespace from private account directories while retaining secret/path detection.
- The updater authenticates manifests, checksums, and packages against the main-branch release workflow; identical tuples are skipped, newer revisions update, and downgrades require `--version`.
- Release freshness now includes the Linux build-recipe fingerprint, so integration changes rebuild an existing upstream version.
- Forced rebuilds of an already published identity are rejected and require a packaging-revision bump.
- Companion shutdown now cancels its temporary Codex CLI query before waiting for the worker.
- The companion now keeps its single-instance socket in the shared user runtime directory, including under `PrivateTmp`.
- `codex-lab-install --force` now genuinely reinstalls the current package on Arch, Debian, and RPM-based systems.
- Discord Rich Presence now clears immediately when Codex exits instead of leaving a stale activity visible.
- The updater now removes stale per-user desktop entry overrides after preserving customized copies, so package updates are visible in desktop menus.

### Added

- Digest-bound private KWin X11 MCP fixture: real PID-directed state, targeted keyboard input, wrong-target denial and portal-only capture denial. Wayland capture/consent and backend activation remain pending.

- Digest-bound offline Qt/AT-SPI native CLI accessibility harness with English/Spanish/Catalan positive cases; targeted MCP state, screenshot/input and real portal consent remain pending.
- Anonymous offline native-media probe with synthetic audio, private debugging pipe, settings-filter/MediaRecorder checks and CI-discovered transport regressions; actual microphone/transcription remain unverified.
- Explicit pinned-ASAR dictation adapter regression that validates syntax without executing upstream code or modifying the installed archive.
- Optional shared-authority companion transport with private Unix WebSocket framing, metadata-only loaded-thread snapshots, bounded polling and explicit sensitive-request denial.
- Opt-in private Unix shared authority transport with ordered configuration, owned cleanup, native CLI upgrade tests and reversible ASAR staging.
- Target-filtered Cargo license inventory for 74 reachable Linux dependencies; dictation candidates preserve and diagnose notices alongside the helper.

- Experimental AppShots and Read Aloud ASAR adapters, selectively attributed MIT webview/patch reuse, local stdin speech and owned-player stop fixtures.
- Experimental Wayland global dictation adapter and MIT Rust portal helper, with corrected event-listener dependency, private D-Bus tests and fresh-build deactivation coverage.
- Local-only signed-runtime AppImage recipe, real SquashFS/payload validation and isolated fixture entrypoint execution; redistribution/GUI gates remain blocked.
- Native feature selector with preserved preferences, installed/requested/rebuild/incompatible states, and English/Spanish/Catalan UI.
- Single-owner updater lock, digest-keyed retained candidate, private transition journal, close deferral/`--wait`, and local `--status`/`--doctor` JSON.
- Read-only push/PR CI, real package-parser validation and disposable package-manager fixture install/update/smoke tests.
- Selectively imported MIT Linux feature framework and regression tests, with a resource-only base adapter and explicitly gated candidate runtime modules.
- Native Qt companion with local Codex usage, OCR, session QR capture, and metadata-only coredump notifications; clipboard privacy is not guaranteed.
- English and Spanish companion UI, desktop actions, user service, and package dependencies.
- Optional Discord Rich Presence with rotating user-defined activities, artwork, elapsed session time, and HTTPS buttons. Private configuration remains under the user's XDG config directory.
- Repo-local Codex instructions.
- Standard project documentation set: user manual, architecture, and roadmap.

### Documentation

- Linked the standard documentation set from `README.md`.

---

# Registro de cambios

Todos los cambios relevantes del proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); las identidades combinan versión upstream y revisión propia de empaquetado.

## [Sin publicar]

### Cambiado

- El smoke anónimo conserva el sandbox Chromium con X11 software; ventana/pantalla inicial no equivalen a GUI cargada o autenticada.
- Computer Use integra cliente/transporte MIT y pruebas MCP, con destino obligatorio, framing acotado y sin replay de entrada; el backend nativo sigue bloqueado.
- La exportación del perfil excluye ajustes deshabilitados y preferencias ajenas, conservando la configuración original.
- Cuotas persistentes con IPC inicializado, decimales válidos, eventos, caché stale y métricas secundarias independientes.
- Companion/OCR/QR pasan a dependencias opcionales; el runtime base no exige capturas ni OCR.
- Cambiar el perfil o aceptar riesgo de datos en downgrade exige flags explícitos; metadata corrupta bloquea la instalación.
- Los candidatos registran y reverifican procedencia APT firmada desde caché, sin repetir la descarga del paquete.

### Integración local experimental

- AppShots y Read Aloud reutilizan selectivamente parches/webview MIT con atribución; lectura por stdin y parada del reproductor propio se prueban con fixtures.
- Dictado global Wayland con helper Rust MIT, dependencia event-listener corregida, D-Bus privado y desactivación limpia desde un build fresco.
- Receta AppImage local con runtime firmado, parser SquashFS, conservación del payload y ejecución aislada de fixture; redistribución y GUI siguen bloqueadas.
- Selector Qt en inglés/español/catalán, conservando preferencias y distinguiendo instalado, solicitado, rebuild e incompatibilidad.
- Updater con flock, candidato por digest, journal privado, aplazamiento/`--wait` y JSON local `--status`/`--doctor`.
- RPM preserva binarios upstream sin strip. La auditoría distingue `.codex-linux` de directorios privados, manteniendo detección de secretos y rutas.
- Permisos/cuenta, voz audible y gates de publicación siguen separados de las pruebas locales.

### Cambiado (identidad y migración)

- Las identidades separan ahora la versión upstream de la revisión de empaquetado `2` en Arch, Debian, RPM, manifiestos, tags y decisiones del instalador.
- Los manifiestos externos vinculan hashes y tamaños finales; los embebidos vinculan receta, perfil de funciones y payload preparado sin autorreferencias.
- Las releases publicadas son inmutables y sólo se promocionan desde draft cuando el conjunto completo dispone de attestations de procedencia de GitHub.
- El empaquetado usa ahora el runtime ChatGPT/Owl nativo oficial para Linux en lugar del bundle macOS sobre Electron estándar.
- Las releases programadas verifican el repositorio Linux oficial firmado y heredan voz, dictado, herramientas, plugins y funciones posteriores sin patches sobre código minificado.
- Las actividades de Discord Rich Presence ahora se eligen aleatoriamente sin repetición inmediata.
- Estandarizado el comando como `codex-lab-install`; `codex-lab-update` permanece como alias compatible con los mismos flags.
- Renombrado el proyecto a Codex I+D Lab - Unofficial y estandarizados los comandos públicos bajo `codex-lab*`; los aliases antiguos se eliminan durante la migración.
- El instalador actualiza la entrada del menú de aplicaciones y el acceso directo del escritorio, conservando los lanzadores antiguos personalizados.
- Los paquetes exponen sólo comandos `codex-lab*`; la migración retira los wrappers de usuario `codex-ui*` obsoletos.

### Corregido

- La validación RPM drena el padding posterior al cierre cpio y conserva la comprobación de errores del decodificador y del extractor.
- El transporte Computer Use fija rutas del sistema y captura exclusivamente por portal; no hereda fallbacks CLI ambientales ni activa el runtime.
- Recuperación del candidato exacto autenticado del journal, con rechazo de digests cambiados y registros ambiguos; sin borrar locks ni reparar globalmente el gestor.
- Recuperación RPM forzada instala cuando el paquete está ausente, sin presuponer que terminó la transacción anterior.

- Los paquetes nativos fuerzan propiedad root; el digest del payload incluye el updater y excluye sólo el manifiesto de identidad embebido.
- El instalador autentica manifiestos, checksums y paquetes contra el workflow de release de la rama principal; omite tuplas idénticas, aplica revisiones nuevas y exige `--version` para downgrades.
- La comprobación de vigencia de releases incluye ahora la huella de la receta de build para Linux, por lo que los cambios de integración reconstruyen una versión upstream ya existente.
- Las reconstrucciones forzadas de una identidad ya publicada se rechazan y exigen incrementar la revisión de empaquetado.
- El cierre del companion cancela la consulta temporal a Codex CLI antes de esperar al worker.
- El companion mantiene ahora el socket de instancia única en el directorio runtime compartido del usuario, también con `PrivateTmp`.
- `codex-lab-install --force` ahora reinstala realmente el paquete actual en sistemas Arch, Debian y basados en RPM.
- Discord Rich Presence ahora se elimina al cerrar Codex en lugar de dejar una actividad obsoleta visible.
- El actualizador elimina overrides obsoletos del lanzador de usuario tras conservar una copia si estaba personalizado, por lo que las actualizaciones del paquete llegan al menú de aplicaciones.

### Añadido

- Fixture MCP privado KWin X11 ligado a digest: estado dirigido al PID real, teclado dirigido, rechazo de destino inexistente y captura sin portal. Captura/consentimiento Wayland y activación del backend siguen pendientes.

- Harness offline de accesibilidad CLI nativa Qt/AT-SPI, ligado a digest y con casos positivos en inglés/español/catalán; MCP dirigido, captura/input y consentimiento real del portal siguen pendientes.
- Prueba multimedia nativa anónima y offline con audio sintético, pipe privado, filtro del selector/MediaRecorder y regresiones de transporte descubiertas por CI; micrófono y transcripción reales siguen sin verificar.
- Regresión del adaptador de dictado contra ASAR fijado explícito, validando sintaxis sin ejecutar código upstream ni modificar el archivo instalado.
- Transporte opcional del companion hacia la misma autoridad, WebSocket Unix privado, snapshots de hilos sin conversaciones, polling acotado y rechazo de peticiones sensibles.
- Transporte Unix privado opt-in de autoridad compartida, con configuración ordenada, limpieza propia, prueba nativa y staging ASAR reversible.
- Inventario de licencias de las 74 dependencias Linux alcanzables; los candidatos de dictado adjuntan avisos y detectan su manipulación.

- CI de push/PR sin publicación, validación mediante parsers reales y pruebas desechables de instalación, actualización y smoke de fixtures.
- Framework Linux MIT y tests reutilizados selectivamente, con perfil base limitado a recursos y módulos runtime explícitos para candidatos.
- Companion Qt nativo con consumo local, OCR, captura QR de sesión y coredumps limitados a metadatos; no garantiza privacidad del portapapeles.
- Interfaz del companion en inglés y español, acciones de escritorio, servicio de usuario y dependencias de paquete.
- Discord Rich Presence opcional con actividades configurables y rotatorias, imágenes, tiempo de sesión y botones HTTPS. La configuración privada permanece en el directorio XDG del usuario.
- Instrucciones repo-locales para Codex.
- Conjunto estándar de documentación: manual de usuario, arquitectura y roadmap.

### Documentación

- Enlazado el conjunto estándar de documentación desde `README.md`.
