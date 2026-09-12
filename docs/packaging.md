# Packaging

The package bundles the official Linux-native ChatGPT runtime without modifying its application bundle.

Installed paths:

- `/opt/codex-ui-linux-port`
- `/usr/bin/codex-ui-linux`
- `/usr/bin/codex-ui-update`
- `/usr/bin/codexui-update` (compatibility alias)
- `/usr/bin/codex-ui-tools`
- `/usr/lib/systemd/user/codex-ui-companion.service`
- `/usr/share/applications/codex-ui-linux.desktop`
- `/usr/share/applications/codex-ui-tools.desktop`
- `/usr/share/icons/hicolor/scalable/apps/codex-ui-linux.svg`

Runtime dependencies:

- GTK 3 and the shared libraries required by the official runtime
- Node.js
- curl
- jq
- desktop-file-utils
- PySide6
- Spectacle
- Tesseract with English and Spanish language data
- zbar

The Arch/CachyOS package is the primary supported target. Debian and Fedora packages are experimental portability targets. All packages carry the upstream runtime and require compatible host libraries.

Generated packages use `Custom` license metadata because they aggregate repository-authored material and upstream components governed by separate terms. Project license files are installed under `/usr/share/licenses/codex-ui-linux-port`.

## Release Build Authority

GitHub Actions is the authoritative builder for release artifacts. Generated releases are public GitHub release assets and must remain clearly marked as unofficial.

A release run must generate and validate:

- `chatgpt_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1-x86_64.pkg.tar.zst`
- `codex-ui-linux-port_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

The workflow verifies the pinned OpenAI repository-key fingerprint, the signed `InRelease` metadata, the package-index hash, and the Linux DEB hash and size. If a release for the same version exists, it also verifies every asset listed in `checksums.txt`. Any source, recipe, or artifact mismatch rebuilds the packages and refreshes release assets with `--clobber`.

`manifest.json` records the upstream source URL, source archive filename, SHA256, package version, and UTC generation timestamp.

The workflow fails before release creation or refresh if any required package is missing, empty, has an unexpected name, has a stale source archive hash, or fails checksum validation.

Local package builds remain supported for bootstrap, debugging, and smoke testing. They are not the source of truth for future releases.

---

# Empaquetado

El paquete incluye el runtime Linux nativo oficial de ChatGPT sin modificar su bundle de aplicación.

Rutas instaladas:

- `/opt/codex-ui-linux-port`
- `/usr/bin/codex-ui-linux`
- `/usr/bin/codex-ui-update`
- `/usr/bin/codexui-update` (alias de compatibilidad)
- `/usr/bin/codex-ui-tools`
- `/usr/lib/systemd/user/codex-ui-companion.service`
- `/usr/share/applications/codex-ui-linux.desktop`
- `/usr/share/applications/codex-ui-tools.desktop`
- `/usr/share/icons/hicolor/scalable/apps/codex-ui-linux.svg`

Dependencias de ejecución:

- GTK 3 y las bibliotecas compartidas requeridas por el runtime oficial
- Node.js
- curl
- jq
- desktop-file-utils
- PySide6
- Spectacle
- Tesseract con datos de idioma inglés y español
- zbar

El paquete Arch/CachyOS es el objetivo principal. Los paquetes Debian y Fedora son objetivos experimentales de portabilidad. Todos incluyen el runtime upstream y requieren bibliotecas compatibles del host.

Los paquetes generados usan metadatos de licencia `Custom` porque agregan material propio del repositorio y componentes upstream sometidos a términos distintos. Las licencias se instalan bajo `/usr/share/licenses/codex-ui-linux-port`.

## Autoridad del build de release

GitHub Actions es el builder autoritativo de los artefactos publicados. Cada ejecución valida la huella de la clave, el índice firmado, el SHA-256 del DEB oficial, el manifiesto, los nombres y la integridad de todos los paquetes antes de crear o actualizar una release.

Los builds locales sirven para bootstrap, depuración y smoke tests; no son la fuente de verdad de releases futuras.
