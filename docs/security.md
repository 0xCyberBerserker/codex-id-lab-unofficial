# Security And Privacy

This repository must not contain:

- Local usernames or absolute home paths
- Codex chats, profiles, sessions, or runtime databases
- Tokens, private keys, SSH material, or GitHub credentials
- Extracted upstream app bundles or dependency trees

Run before every commit and release:

```bash
scripts/privacy-audit
```

Release binaries should be attached as GitHub release assets, not committed to git.

Security reports must follow the private process in the repository root [SECURITY.md](../SECURITY.md). Do not include secrets or private runtime material in public issues.

## Build Source Verification

The release workflow stores the approved public key in the repository, rejects additional primary keys, accepts only its legitimate signing subkeys, and verifies the authenticated package index before downloading its concrete `Filename`. Published manifests, checksums, and packages must also carry GitHub build-provenance attestations from the main-branch release workflow.

## Release Boundary

Before publishing releases or changing release policy, review `docs/publication.md` and rerun:

```bash
scripts/privacy-audit
```

Do not publish local paths, Codex runtime state, chat data, tokens, credentials, or extracted app trees.

---

# Seguridad y privacidad

Este repositorio no debe contener usuarios o rutas locales, chats, perfiles, sesiones, bases runtime, tokens, claves, credenciales, árboles extraídos ni dependencias generadas. Ejecuta `scripts/privacy-audit` antes de cada commit y release.

## Verificación de la fuente

El workflow almacena la clave pública aprobada en el repositorio, rechaza claves primarias adicionales, acepta sólo sus subclaves de firma legítimas y verifica el índice autenticado antes de descargar su `Filename` concreto. Los manifiestos, checksums y paquetes publicados también deben incluir attestations de procedencia del workflow de release en la rama principal.

## Límite de publicación

Los binarios deben adjuntarse como assets generados por GitHub Actions. Usa el proceso privado de [SECURITY.md](../SECURITY.md) para informes y no publiques datos privados.
