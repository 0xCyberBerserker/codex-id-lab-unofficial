<p align="center">
  <img src="docs/assets/codex-ui-linux-port.svg" alt="Codex UI Linux Port icon" width="132">
</p>

<p align="center">
  <strong>Codex UI Linux Port</strong>
</p>

<p align="center">
  Unofficial Linux packaging automation for Codex UI.
</p>

<p align="center">
  <a href="https://github.com/0xCyberBerserker/codex-ui-linux-port/actions/workflows/release.yml"><img alt="Release workflow" src="https://img.shields.io/github/actions/workflow/status/0xCyberBerserker/codex-ui-linux-port/release.yml?branch=main&label=release%20build"></a>
  <a href="https://github.com/0xCyberBerserker/codex-ui-linux-port/releases"><img alt="Latest release" src="https://img.shields.io/github/v/release/0xCyberBerserker/codex-ui-linux-port?label=latest%20release"></a>
  <img alt="Targets" src="https://img.shields.io/badge/targets-Arch%20%7C%20Debian%20%7C%20RPM-ffb454">
  <img alt="Status" src="https://img.shields.io/badge/status-public%20automation-8fd18f">
  <img alt="Unofficial" src="https://img.shields.io/badge/OpenAI-unofficial-lightgrey">
</p>

<p align="center">
  <sub>Made with 🖤 in Barcelona City 🇪🇸</sub>
</p>

This repository rebuilds upstream Codex UI release artifacts into Linux packages for Codex UI through auditable scripts and GitHub Actions, with packaging targets for Arch, CachyOS, Debian, Ubuntu, and RPM-based distributions.

## Project Signal

| Area | Current signal |
| --- | --- |
| Release builder | GitHub Actions is authoritative |
| Source tracking | Upstream appcast, current source archive, SHA256 manifest |
| Linux targets | Arch/CachyOS, Debian/Ubuntu, Fedora/RHEL-like |
| Public status | Public automation repository |
| Data boundary | No chats, credentials, runtime state, private data, or local paths |
| AUR status | Metadata prepared, not published |

## What It Builds

- Arch/CachyOS package: `.pkg.tar.zst`
- Debian/Ubuntu package: `.deb` (experimental)
- Fedora/RHEL-like package: `.rpm` (experimental)
- Latest official macOS source asset: `Codex-$VERSION.dmg`
- Release manifest and checksums
- Native Qt companion for usage, OCR, private QR capture, and safe crash metadata
- Future AUR metadata under `packaging/aur`

## Why It Exists

Codex UI changes frequently. Linux users need a repeatable path that can:

- fetch the current upstream source archive
- rebuild native modules for Linux
- apply Linux desktop patches, including audio-only microphone access and toggle-style global dictation
- package the app for common Linux families
- verify artifacts before release
- keep private runtime data out of git

## Operational Rationale

This project covers a practical need that emerged from daily engineering work: Codex UI is part of the maintainer's regular Linux workstation workflow, and frequent upstream updates made manual repackaging wasteful and error-prone.

The automation was built to turn unavoidable waiting periods such as long builds, dependency installs, and CI feedback loops into useful maintenance time. The goal is straightforward: keep the workstation reliable, reduce repeated manual update work, and improve day-to-day engineering throughput without storing private runtime data, credentials, chats, or local project material.

## Install Or Update

```bash
codex-ui-update
```

Check without installing:

```bash
codex-ui-update --check
```

Run a smoke test:

```bash
codex-ui-update --smoke
```

Public release downloads do not require authentication. Private forks can use `GITHUB_TOKEN` or `GH_TOKEN`.

The legacy `codexui-update` command remains available as a compatibility alias and accepts the same flags.

## Release Pipeline

GitHub Actions is the authoritative builder.

Every scheduled or manual run reads the latest version from the official appcast, downloads the current official `Codex.dmg`, verifies its internal application version, computes its SHA256, compares the source and Linux build-recipe fingerprints with the existing release manifest, and verifies every existing asset against `checksums.txt`. It rebuilds only when needed. If the same version tag exists but the source, Linux patches, packaging inputs, or any published artifact changed, release assets are refreshed with `--clobber`.

### Automatic Feature Tracking

Each run preserves upstream features and applies only the Linux compatibility patches. On Wayland, global dictation uses Electron's shortcut portal and a toggle shortcut. Automatic paste uses `ydotool`; X11 can also use `xdotool`. Hold-to-dictate stays hidden because Electron does not expose the global key-release event on Linux.

### Seguimiento automático de funciones

Cada ejecución programada o manual obtiene el bundle oficial más reciente, conserva sus funciones upstream y aplica sólo los patches de compatibilidad necesarios para Linux, incluido el permiso exclusivo de audio para voz y dictado. La huella de la receta de build obliga a reconstruir una versión existente cuando cambian esos patches o sus inputs de empaquetado.

En Wayland, el dictado global usa el portal de atajos de Electron y un atajo de tipo alternar. El pegado automático usa `ydotool`; en X11 también admite `xdotool`. El modo de mantener pulsado permanece oculto en Linux porque Electron no expone el evento global de liberación de tecla.

Required release assets:

- `Codex-$VERSION.dmg`
- `codex-ui-linux-port-$VERSION-1-x86_64.pkg.tar.zst`
- `codex-ui-linux-port_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

Local builds are supported for bootstrap and debugging:

```bash
scripts/build-from-dmg --source /path/to/Codex.dmg
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
