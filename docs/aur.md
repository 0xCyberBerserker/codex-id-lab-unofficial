# AUR Preparation

The repository includes future AUR metadata under `packaging/aur`.

Package name:

```text
codex-id-lab-unofficial-bin
```

The AUR package is not published yet.

Before AUR publication:

1. Review redistribution and trademark implications.
2. Decide whether release assets may be publicly accessible.
3. Confirm release asset URLs and checksums.
4. Review `docs/publication.md`.
5. Run:

```bash
scripts/update-aur-metadata
```

6. Regenerate `.SRCINFO`.
7. Build locally with:

```bash
makepkg -sf
```

---

# Preparación para AUR

El repositorio incluye metadata futura en `packaging/aur` para `codex-id-lab-unofficial-bin`. El paquete todavía no está publicado.

Antes de publicarlo:

1. Revisa redistribución y marcas.
2. Confirma que los assets pueden ser públicos.
3. Verifica URLs y checksums.
4. Revisa `docs/publication.md`.
5. Ejecuta `scripts/update-aur-metadata`.
6. Regenera `.SRCINFO`.
7. Compila localmente con `makepkg -sf`.
