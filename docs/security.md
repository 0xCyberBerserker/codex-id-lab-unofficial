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

The release workflow pins the official repository-key fingerprint and verifies `InRelease`, the package index, and the source package SHA-256 and size. The signing key is bootstrapped from the official HTTPS package, so HTTPS remains part of the initial trust boundary.

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

El workflow fija la huella de la clave del repositorio oficial y verifica `InRelease`, el índice, el SHA-256 y el tamaño del paquete. La clave se obtiene inicialmente desde el paquete oficial servido por HTTPS, por lo que HTTPS forma parte del límite de confianza inicial.

## Límite de publicación

Los binarios deben adjuntarse como assets generados por GitHub Actions. Usa el proceso privado de [SECURITY.md](../SECURITY.md) para informes y no publiques datos privados.
