# Packaging

The package bundles the official Linux-native ChatGPT runtime without modifying its application bundle.

Installed paths:

- `/opt/codex-id-lab-unofficial`
- `/usr/bin/codex-lab`
- `/usr/bin/codex-lab-install`
- `/usr/bin/codex-lab-update` (compatibility alias)
- `/usr/bin/codex-lab-tools`
- `/usr/lib/systemd/user/codex-lab-companion.service`
- `/usr/share/applications/codex-lab.desktop`
- `/usr/share/applications/codex-lab-tools.desktop`
- `/usr/share/icons/hicolor/scalable/apps/codex-lab.svg`

Runtime dependencies:

- GTK 3 and the shared libraries required by the official runtime
- Node.js
- curl
- jq
- GitHub CLI (`gh`) for build-attestation verification
- desktop-file-utils
- PySide6
- Spectacle
- Tesseract with English and Spanish language data
- zbar

The Arch/CachyOS package is the primary supported target. Debian and Fedora packages are experimental portability targets. All packages carry the upstream runtime and require compatible host libraries.

Generated packages use `Custom` license metadata because they aggregate repository-authored material and upstream components governed by separate terms. Project license files are installed under `/usr/share/licenses/codex-id-lab-unofficial`.

## Release Build Authority

GitHub Actions is the authoritative builder for release artifacts. Generated releases are public GitHub release assets and must remain clearly marked as unofficial.

A release run must generate and validate:

- `chatgpt_$UPSTREAM_VERSION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION-x86_64.pkg.tar.zst`
- `codex-id-lab-unofficial_$UPSTREAM_VERSION-$REVISION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

The workflow verifies the pinned repository key, signed `InRelease`, package-index hash, and selected Linux DEB. Package identities use `$UPSTREAM_VERSION-$REVISION`; published tags and assets are immutable. A complete draft is attested and only then promoted.

The manifest embedded in each package records upstream and package versions separately, packaging revision, architecture, build and feature profiles, commit, recipe hash, prepared-payload hash, source hash, and UTC generation timestamp. The external `manifest.json` adds the final package hashes and sizes; the embedded copy intentionally has no self-hash.

The workflow fails before draft promotion if any required package is missing, empty, has an unexpected name, has a stale source archive hash, or fails checksum validation.

Release promotion additionally requires `CODEX_LAB_RELEASE_PROMOTION_ENABLED=true`; it remains blocked until the signing identity has been accepted through a controlled live test.

Local package builds remain supported for bootstrap, debugging, and smoke testing. They are not the source of truth for future releases.

---

# Empaquetado

El paquete incluye el runtime Linux nativo oficial de ChatGPT sin modificar su bundle de aplicación.

Rutas instaladas:

- `/opt/codex-id-lab-unofficial`
- `/usr/bin/codex-lab`
- `/usr/bin/codex-lab-install`
- `/usr/bin/codex-lab-update` (alias de compatibilidad)
- `/usr/bin/codex-lab-tools`
- `/usr/lib/systemd/user/codex-lab-companion.service`
- `/usr/share/applications/codex-lab.desktop`
- `/usr/share/applications/codex-lab-tools.desktop`
- `/usr/share/icons/hicolor/scalable/apps/codex-lab.svg`

Dependencias de ejecución:

- GTK 3 y las bibliotecas compartidas requeridas por el runtime oficial
- Node.js
- curl
- jq
- GitHub CLI (`gh`) para verificar attestations de build
- desktop-file-utils
- PySide6
- Spectacle
- Tesseract con datos de idioma inglés y español
- zbar

El paquete Arch/CachyOS es el objetivo principal. Los paquetes Debian y Fedora son objetivos experimentales de portabilidad. Todos incluyen el runtime upstream y requieren bibliotecas compatibles del host.

Los paquetes generados usan metadatos de licencia `Custom` porque agregan material propio del repositorio y componentes upstream sometidos a términos distintos. Las licencias se instalan bajo `/usr/share/licenses/codex-id-lab-unofficial`.

## Autoridad del build de release

GitHub Actions es el builder autoritativo. La identidad usa `$UPSTREAM_VERSION-$REVISION`; cada formato conserva su revisión nativa. Los assets publicados son inmutables: el workflow crea un draft completo, genera attestations y sólo entonces lo promociona.

El manifiesto embebido registra por separado versión upstream, revisión de empaquetado, arquitectura, perfiles de build y funciones, commit, receta, payload preparado y paquete fuente. El `manifest.json` externo añade hashes y tamaños finales; la copia embebida no contiene autorreferencias.

Los builds locales sirven para bootstrap, depuración y smoke tests; no son la fuente de verdad de releases futuras.

La promoción requiere además `CODEX_LAB_RELEASE_PROMOTION_ENABLED=true`; permanece bloqueada hasta aceptar la identidad de firma mediante una prueba controlada en vivo.
