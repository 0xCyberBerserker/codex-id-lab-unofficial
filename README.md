<p align="center">
  <img src="docs/assets/codex-lab.svg" alt="Codex I+D Lab - Unofficial icon" width="132">
</p>

<p align="center">
  <strong>Codex I+D Lab - Unofficial</strong>
</p>

<p align="center">
  Unofficial Linux packaging automation for Codex UI.
</p>

<p align="center">
  <a href="https://github.com/0xCyberBerserker/codex-id-lab-unofficial/actions/workflows/release.yml"><img alt="Release workflow" src="https://img.shields.io/github/actions/workflow/status/0xCyberBerserker/codex-id-lab-unofficial/release.yml?branch=main&label=release%20build"></a>
  <a href="https://github.com/0xCyberBerserker/codex-id-lab-unofficial/releases"><img alt="Latest release" src="https://img.shields.io/github/v/release/0xCyberBerserker/codex-id-lab-unofficial?label=latest%20release"></a>
  <img alt="Targets" src="https://img.shields.io/badge/targets-Arch%20%7C%20Debian%20%7C%20RPM-ffb454">
  <img alt="Status" src="https://img.shields.io/badge/status-public%20automation-8fd18f">
  <img alt="Unofficial" src="https://img.shields.io/badge/OpenAI-unofficial-lightgrey">
</p>

<p align="center">
  <sub>Made with 🖤 in Barcelona City 🇪🇸</sub>
</p>

This repository repackages the official ChatGPT Linux runtime through auditable scripts and GitHub Actions, with targets for Arch, CachyOS, Debian, Ubuntu, and RPM-based distributions.

## Project Signal

| Area | Current signal |
| --- | --- |
| Release builder | GitHub Actions is authoritative |
| Source tracking | Signed official repository; builder-attestation implementation awaits its live promotion gate |
| Linux targets | Arch/CachyOS, Debian/Ubuntu, Fedora/RHEL-like |
| Public status | Public automation repository |
| Data boundary | No chats, credentials, runtime state, private data, or local paths |
| AUR status | Metadata prepared, not published |
| Validation | Real package parsers and disposable fixtures; desktop/session acceptance is separate |

The optional feature framework is selectively reused from [Ilysenko's MIT-licensed snapshot](https://github.com/ilysenko/codex-desktop-linux/tree/249cd4b64d42434f51417fec4a318750d461b676). See [import inventory](third-party/upstream.lock.json), [feature adapter](linux-features/README.md) and [validation boundaries](docs/validation.md).

The local development candidate adds a persistent QPalette quota companion,
English/Spanish/Catalan feature preferences, retained verified update candidates,
and opt-in AppShots/Read Aloud/Wayland dictation build adapters. A local-only
[AppImage recipe](docs/appimage.md) has real format/fixture tests, not GUI portability acceptance. These are not a published release
or a global parity claim. See [feature gates](docs/features.md),
[update recovery](docs/updater-recovery.md) and [import maintenance](docs/upstream-maintenance.md).
Revision 4 additionally provides exact retained-candidate recovery and an opt-in
shared-authority companion snapshot of loaded threads, without conversation reads
or a second server. Native Computer Use development builds and notice collection
are measured separately; runtime activation is still blocked. See
[helper review evidence](docs/native-helper-review.md).
Updates inherit native upstream features, but never autoimport unreviewed patches
or grant server/account entitlements.

El framework opcional se reutiliza selectivamente del snapshot MIT fijado de Ilysenko. El inventario conserva atribución y licencia; las pruebas de empaquetado no equivalen a aceptación de voz, dictado o sesión real.

El candidato local incorpora cuotas persistentes en Qt/QPalette, preferencias
en inglés/español/catalán, candidatos de actualización conservados y adaptadores
opt-in AppShots/Read Aloud/dictado Wayland. La receta AppImage pasa pruebas de
formato/fixture, no aceptación GUI/portabilidad. No está publicado ni demuestra paridad global.
Los gates funcionales y de recuperación se documentan por separado.
La revisión 4 añade recuperación del candidato exacto y snapshots opt-in de hilos
del mismo App Server, sin leer conversaciones ni iniciar otro servidor. Se probaron
builds nativos de Computer Use y avisos transitivos, no activación del escritorio.
La ingeniería del wrapper prepara actualizaciones; no autoimporta parches nuevos
sin licencia, compatibilidad y pruebas, ni concede funciones de cuenta del servidor.

## What It Builds

- Arch/CachyOS package: `.pkg.tar.zst`
- Debian/Ubuntu package: `.deb` (experimental)
- Fedora/RHEL-like package: `.rpm` (experimental)
- Verified official Linux source package: `chatgpt_$UPSTREAM_VERSION_amd64.deb`
- External release manifest with final artifact digests, plus an embedded build-identity manifest without self-hashes
- Native Qt companion for usage, OCR, private QR capture, and safe crash metadata
- Future AUR metadata under `packaging/aur`

## Why It Exists

Codex UI changes frequently. Linux users need a repeatable path that can:

- fetch the current upstream source archive
- preserve the official Linux-native Owl runtime and modules
- inherit upstream voice, dictation, app tools, plugins, and future features without patching minified bundles
- package the app for common Linux families
- verify artifacts before release
- keep private runtime data out of git

## Operational Rationale

This project covers a practical need that emerged from daily engineering work: Codex UI is part of the maintainer's regular Linux workstation workflow, and frequent upstream updates made manual repackaging wasteful and error-prone.

The automation was built to turn unavoidable waiting periods such as long builds, dependency installs, and CI feedback loops into useful maintenance time. The goal is straightforward: keep the workstation reliable, reduce repeated manual update work, and improve day-to-day engineering throughput without storing private runtime data, credentials, chats, or local project material.

## Install Or Update

Fresh install, update, or migration from the former project name:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/0xCyberBerserker/codex-id-lab-unofficial/main/scripts/codex-lab-install)
```

After installation, the command also refreshes the application-menu entry and desktop shortcut:

```bash
codex-lab-install
```

Check without installing:

```bash
codex-lab-install --check
```

Run a smoke test:

```bash
codex-lab-install --smoke
```

Public release downloads do not require authentication. GitHub CLI is required to verify build attestations. Private forks can use `GITHUB_TOKEN` or `GH_TOKEN`.

`codex-lab-update` is the short alias. Legacy `codex-ui-*` launchers are removed during migration.

## Release Pipeline

GitHub Actions is the authoritative builder.

Every scheduled or manual run verifies the pinned repository key, `InRelease`, the package index, and the selected source package. Releases use `$UPSTREAM_VERSION-$REVISION`, remain immutable after publication, and are promoted from a draft only after the complete asset set receives GitHub build-provenance attestations.
Promotion remains disabled until the maintainer approves the live signing identity with the repository variable `CODEX_LAB_RELEASE_PROMOTION_ENABLED=true`.

The identity also binds the architecture, base feature profile, build recipe, prepared payload, source archive, and final package digests.

### Pipeline de release

Cada ejecución verifica la clave fijada del repositorio, `InRelease`, el índice y el paquete fuente seleccionado. Las releases usan `$UPSTREAM_VERSION-$REVISION`, son inmutables tras publicarse y sólo se promocionan desde draft cuando el conjunto completo dispone de attestations de procedencia de GitHub.
La promoción permanece desactivada hasta que el responsable apruebe la identidad de firma en vivo mediante `CODEX_LAB_RELEASE_PROMOTION_ENABLED=true`.

La identidad también vincula arquitectura, perfil base de funciones, receta, payload preparado, paquete fuente y hashes finales de los paquetes.

### Automatic Feature Tracking

The base profile preserves the official Linux runtime unchanged and tracks its signed packages. Upstream voice, dictation, native app tools and plugins are inherited where that runtime, account and desktop support them; packaging tests do not establish feature parity. XWayland remains the default; native Wayland can be requested with `CODEX_LAB_OZONE_PLATFORM=wayland` and remains experimental upstream.

### Seguimiento automático de funciones

El perfil base conserva el runtime Linux oficial y sigue sus paquetes firmados. Hereda voz, dictado, herramientas y plugins cuando el runtime, la cuenta y el escritorio los soportan; las pruebas de paquetes no demuestran paridad. XWayland sigue siendo el modo predeterminado; Wayland nativo puede solicitarse con `CODEX_LAB_OZONE_PLATFORM=wayland` y continúa siendo experimental upstream.

Required release assets:

- `chatgpt_$UPSTREAM_VERSION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION-x86_64.pkg.tar.zst`
- `codex-id-lab-unofficial_$UPSTREAM_VERSION-$REVISION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

Local builds are supported for bootstrap and debugging:

```bash
scripts/build-from-linux --source /path/to/chatgpt_amd64.deb
```

## Repository Boundary

Committed files must be limited to automation, patches, package metadata, and documentation. Upstream binaries, extracted app bundles, Codex chats, Codex profiles, runtime databases, local paths, tokens, and private keys must not be committed.

Before every commit and release:

```bash
scripts/privacy-audit
```

## Public Status

- Repository visibility: public
- Release visibility: public
- AUR package: prepared, not published

Publication and redistribution notes live in [docs/publication.md](docs/publication.md).

## Documentation

- [Usage](docs/usage.md)
- [Local Companion](docs/companion.md)
- [Packaging](docs/packaging.md)
- [Security And Privacy](docs/security.md)
- [Changelog](CHANGELOG.md)
- [User Manual](manual_usuario.md)
- [Architecture](arquitectura.md)
- [Roadmap](roadmap.md)
- [Codex Instructions](AGENTS.md)
- [AUR Preparation](docs/aur.md)
- [Publication Checklist](docs/publication.md)
- [Security Policy](SECURITY.md)
- [Disclaimer](DISCLAIMER.md)

## Documentación

- [Uso](docs/usage.md)
- [Companion local](docs/companion.md)
- [Empaquetado](docs/packaging.md)
- [Seguridad y privacidad](docs/security.md)
- [Registro de cambios](CHANGELOG.md)
- [Manual de usuario](manual_usuario.md)
- [Arquitectura](arquitectura.md)
- [Roadmap](roadmap.md)
- [Instrucciones para Codex](AGENTS.md)

## Companion tools

- [`token-rat-esp`](https://github.com/0xCyberBerserker/token-rat-esp): Spanish Codex skill for shorter answers, cleaner patches and token-efficient developer workflows.

## License

Original automation scripts, Linux patches, packaging metadata, website material, and documentation in this repository are licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

This is a source-available, noncommercial license. It does not grant rights over Codex, Codex UI, OpenAI software, upstream binaries, application assets, release metadata, trademarks, or third-party dependencies. See [NOTICE.md](NOTICE.md) for the exact scope.

## Disclaimer

This is an unofficial automation wrapper and packaging toolkit. Codex, Codex UI, OpenAI trademarks, upstream binaries, release metadata, and application assets belong to OpenAI or their respective owners. This repository is not affiliated with, endorsed by, or supported by OpenAI.
