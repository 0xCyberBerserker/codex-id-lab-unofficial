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
| Source tracking | Signed official Linux repository, package SHA256 manifest |
| Linux targets | Arch/CachyOS, Debian/Ubuntu, Fedora/RHEL-like |
| Public status | Public automation repository |
| Data boundary | No chats, credentials, runtime state, private data, or local paths |
| AUR status | Metadata prepared, not published |

## What It Builds

- Arch/CachyOS package: `.pkg.tar.zst`
- Debian/Ubuntu package: `.deb` (experimental)
- Fedora/RHEL-like package: `.rpm` (experimental)
- Verified official Linux source package: `chatgpt_$VERSION_amd64.deb`
- Release manifest and checksums
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

Public release downloads do not require authentication. Private forks can use `GITHUB_TOKEN` or `GH_TOKEN`.

`codex-lab-update` is the short alias. Former `codex-ui-*` commands remain temporarily available only for migration.

## Release Pipeline

GitHub Actions is the authoritative builder.

Every scheduled or manual run downloads the current official Linux package, pins and validates the repository signing-key fingerprint, verifies `InRelease`, checks the package against the signed index, and compares source and build-recipe fingerprints with the existing release. It rebuilds only when needed and refreshes changed assets with `--clobber`.

### Automatic Feature Tracking

Each run preserves the official Linux runtime unchanged. Voice, dictation, native app tools, plugins, and later upstream features arrive with the next signed official package. XWayland remains the default; native Wayland can be requested with `CODEX_LAB_OZONE_PLATFORM=wayland` and remains experimental upstream.

### Seguimiento automático de funciones

Cada ejecución conserva sin modificar el runtime Linux oficial. Voz, dictado, herramientas nativas, plugins y funciones upstream posteriores llegan con el siguiente paquete oficial firmado. XWayland sigue siendo el modo predeterminado; Wayland nativo puede solicitarse con `CODEX_LAB_OZONE_PLATFORM=wayland` y continúa siendo experimental upstream.

Required release assets:

- `chatgpt_$VERSION_amd64.deb`
- `codex-id-lab-unofficial-$VERSION-1-x86_64.pkg.tar.zst`
- `codex-id-lab-unofficial_$VERSION_amd64.deb`
- `codex-id-lab-unofficial-$VERSION-1.x86_64.rpm`
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
