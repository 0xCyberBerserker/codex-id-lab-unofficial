# Roadmap

## English

## Current State

- Public automation repository for unofficial Codex UI Linux packages.
- Arch/CachyOS package is the primary supported target.
- Debian and RPM packages are generated as experimental portability targets.
- Release workflow validates source version, checksums, package names, and artifact completeness.
- Packages ship an optional native companion for local usage, OCR, QR, and safe crash metadata.

## Next

- Keep the updater aligned with current GitHub release asset layout.
- Keep the official Linux runtime unmodified and track its signed repository.
- Continue separating local package validation from remote host version drift.
- Keep AUR metadata prepared until publication is explicitly approved.

## Later

- Expand package validation for Debian and RPM only after runtime compatibility is proven.
- Add narrowly scoped regression checks for launcher, desktop entry, and smoke startup behavior.

---

# Roadmap

## Español

## Estado actual

- Repositorio público de automatización para paquetes Linux no oficiales de Codex UI.
- El paquete Arch/CachyOS es el objetivo principal soportado.
- Los paquetes Debian y RPM se generan como objetivos experimentales de portabilidad.
- El workflow de release valida versión fuente, checksums, nombres de paquete e integridad de artefactos.
- Los paquetes incluyen un companion nativo opcional para consumo local, OCR, QR y metadatos seguros de fallos.

## Próximo

- Mantener el updater alineado con el layout actual de assets de GitHub Releases.
- Mantener sin modificar el runtime Linux oficial y seguir su repositorio firmado.
- Separar validación local de paquetes de drift de versión en hosts remotos.
- Mantener metadata AUR preparada hasta aprobación explícita de publicación.

## Más adelante

- Ampliar validación Debian y RPM sólo tras probar compatibilidad runtime.
- Añadir checks de regresión acotados para launcher, desktop entry y smoke startup.
