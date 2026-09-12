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

GitHub Actions is the only authoritative release builder. It verifies the source, builds `$UPSTREAM_VERSION-$REVISION`, validates all artifacts, creates provenance attestations, and promotes a complete draft. Published tags and assets are not replaced.

Promotion is disabled by default. It requires the repository variable `CODEX_LAB_RELEASE_PROMOTION_ENABLED=true` after the maintainer has approved the GitHub Actions identity and completed a controlled attestation test.

The authenticated external manifest binds the final package names, formats, architectures, sizes, and SHA-256 digests. Package-embedded manifests bind the same build identity and prepared payload without attempting to hash their own package.

Release assets must include:

- `chatgpt_$UPSTREAM_VERSION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION-x86_64.pkg.tar.zst`
- `codex-id-lab-unofficial_$UPSTREAM_VERSION-$REVISION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

If redistribution constraints change, remove public release assets and keep only the automation public.

## License Boundary

Repository-authored automation, Linux patches, packaging metadata, website material, and documentation use the PolyForm Noncommercial License 1.0.0. This license does not cover upstream software, application assets, release metadata, trademarks, or third-party dependencies. Generated packages retain `Custom` package-license metadata because they are aggregate artifacts.

---

# Política de publicación y releases

Este repositorio contiene automatización pública y no oficial para empaquetar Codex UI en Linux. Los assets son públicos; AUR está preparado, pero no publicado. GitHub Actions es el único builder autoritativo.

Las releases usan `$UPSTREAM_VERSION-$REVISION`. El workflow valida el conjunto completo, genera attestations y promociona un draft; no sustituye tags ni assets ya publicados.

La promoción está desactivada por defecto. Requiere la variable de repositorio `CODEX_LAB_RELEASE_PROMOTION_ENABLED=true` después de aprobar la identidad de GitHub Actions y completar una prueba controlada de attestations.

El manifiesto externo autenticado vincula nombres, formatos, arquitecturas, tamaños y SHA-256 finales. Los manifiestos embebidos conservan la misma identidad y el hash del payload preparado sin intentar calcular el hash del paquete que los contiene.

## Salvaguardas

1. Revisa las condiciones upstream de redistribución y marcas.
2. Mantén explícito el carácter no oficial.
3. Ejecuta `scripts/privacy-audit` desde un checkout limpio.
4. No publiques usuarios, rutas locales, chats, perfiles, bases runtime, tokens ni claves.
5. Genera los assets únicamente mediante GitHub Actions.
6. No sugieras soporte oficial de OpenAI.

## Assets requeridos

- `chatgpt_$UPSTREAM_VERSION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION-x86_64.pkg.tar.zst`
- `codex-id-lab-unofficial_$UPSTREAM_VERSION-$REVISION_amd64.deb`
- `codex-id-lab-unofficial-$UPSTREAM_VERSION-$REVISION.x86_64.rpm`
- `manifest.json`
- `checksums.txt`

Si cambian las condiciones de redistribución, deben retirarse los binarios públicos y conservarse sólo la automatización. PolyForm Noncommercial License 1.0.0 cubre únicamente el material original del repositorio; los componentes upstream conservan sus términos.
