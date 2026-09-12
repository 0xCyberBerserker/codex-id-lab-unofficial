# Publication And Release Policy

This repository is public automation for unofficial Linux packaging of Codex UI.

## Current State

- Repository visibility: public
- Release assets: public GitHub release assets
- AUR package: prepared, not published
- Upstream Codex binaries: not committed to git
- Personal, chat, credential, and runtime data: blocked by `scripts/privacy-audit`

## Publication Guardrails

1. Review upstream redistribution and trademark constraints.
2. Keep all project wording explicitly unofficial.
3. Run `scripts/privacy-audit` from a clean checkout.
4. Verify no local usernames, host-specific paths, Codex chats, Codex profiles, runtime databases, tokens, or private keys exist in tracked files.
5. Keep release assets generated only by GitHub Actions.
6. If AUR publication proceeds, update `packaging/aur` and regenerate `.SRCINFO`.
7. Do not imply official OpenAI support.

## Public Positioning

Use this project description when publishing:

```text
Unofficial Linux packaging automation for Codex UI. The project rebuilds upstream Codex UI release artifacts into Linux packages through auditable scripts and GitHub Actions. It is not affiliated with, endorsed by, or supported by OpenAI.
```

Avoid maintainer-specific language such as personal workstation details, private usage patterns, chat history, or local filesystem paths.

## Release Asset Policy

GitHub Actions is the only authoritative release builder. It always downloads the current upstream source archive, compares its SHA256 against the release manifest, rebuilds packages when needed, validates all artifacts, and runs the privacy audit.

Release assets must include:

- `chatgpt_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1-x86_64.pkg.tar.zst`
- `codex-ui-linux-port_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

If redistribution constraints change, remove public release assets and keep only the automation public.

## License Boundary

Repository-authored automation, Linux patches, packaging metadata, website material, and documentation use the PolyForm Noncommercial License 1.0.0. This license does not cover upstream software, application assets, release metadata, trademarks, or third-party dependencies. Generated packages retain `Custom` package-license metadata because they are aggregate artifacts.

---

# Política de publicación y releases

Este repositorio contiene automatización pública y no oficial para empaquetar Codex UI en Linux. Los assets son públicos; AUR está preparado, pero no publicado. GitHub Actions es el único builder autoritativo.

## Salvaguardas

1. Revisa las condiciones upstream de redistribución y marcas.
2. Mantén explícito el carácter no oficial.
3. Ejecuta `scripts/privacy-audit` desde un checkout limpio.
4. No publiques usuarios, rutas locales, chats, perfiles, bases runtime, tokens ni claves.
5. Genera los assets únicamente mediante GitHub Actions.
6. No sugieras soporte oficial de OpenAI.

## Assets requeridos

- `chatgpt_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1-x86_64.pkg.tar.zst`
- `codex-ui-linux-port_$VERSION_amd64.deb`
- `codex-ui-linux-port-$VERSION-1.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

Si cambian las condiciones de redistribución, deben retirarse los binarios públicos y conservarse sólo la automatización. PolyForm Noncommercial License 1.0.0 cubre únicamente el material original del repositorio; los componentes upstream conservan sus términos.
