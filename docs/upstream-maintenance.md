# Imported component maintenance

1. Resolve a proposed source revision once; record the immutable SHA and reason.
2. Compare only paths in `third-party/upstream.lock.json` against that revision.
   Preserve copyright, MIT license and explicit local adaptations. Do not merge
   the whole installer, floating model downloads or permission bypasses.
3. Review dependency/license changes before an isolated `npm ci --ignore-scripts`.
   Update the builder lock intentionally and run npm audit; no automatic upgrades.
4. Run imported framework tests, local runtime/feature tests and package fixtures.
   Probe the new verified upstream ASAR. A match is not authenticated acceptance.
5. Bump `packaging/revision` for recipe/profile changes. Produce a new immutable
   candidate, review the diff and repeat canary acceptance before promotion.

The scheduled release workflow discovers verified upstream releases; new native
features may be inherited from that runtime. It does not invent Linux support,
override account rollout or auto-merge incompatible community patches. Promotion
is disabled until the maintainer approves the live attestation gate.

## Español

Fija una revisión y su motivo; compara solo las rutas del inventario. Conserva
copyright, MIT y adaptaciones locales. No importes el instalador entero, descargas
flotantes ni bypass de permisos. Revisa dependencias/licencias antes de npm aislado
sin scripts; actualiza el lock deliberadamente y ejecuta la auditoría.

Ejecuta tests importados, módulos locales y fixtures de paquetes. Prueba el ASAR
upstream verificado: encajar no demuestra aceptación autenticada. Cambiar receta
o perfil requiere nueva revisión de empaquetado y candidato inmutable con canary.
El workflow programado descubre releases nativas verificadas, pero no crea soporte
Linux, concede rollouts ni fusiona parches incompatibles automáticamente. La
promoción espera autorización del gate de attestation real.
