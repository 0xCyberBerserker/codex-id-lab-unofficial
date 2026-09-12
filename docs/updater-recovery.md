# Update recovery

The package manager remains the only authority for installed paths. The updater
authenticates the manifest and package first, caches the candidate by SHA-256, takes
a single-owner flock and records sanitized transitions under the user's state
directory. `codex-lab-update --status` and `--doctor` return local JSON without
contacting GitHub. `--wait` waits for the installed runtime executable to close;
without it an open runtime defers installation and retains the verified candidate.
A second check before installation catches reopening; this is not a universal
process-launch interlock or an atomic filesystem transaction.

Cancellation/failure in the manager retains the candidate and requires explicit
retry. A process interruption leaves its last transition for inspection; the
next attempt re-authenticates the manifest and cached package before any install.
The transition journal is local, private and not a power-loss-proof transaction
log. A failed package transaction must be inspected/repaired through pacman,
dpkg/apt or rpm/dnf; the updater does not rename manager-owned trees.

Rollback is an explicit previously authenticated release via `--version`; the
previous package may need downloading. User data is not rolled back or deleted.
Changed installed build feature profiles require `--allow-profile-change`;
explicit downgrades also require `--accept-data-downgrade-risk`. Neither flag
restores, deletes or inspects personal data. Unknown upstream data schemas cannot
be declared compatible. Automatic rollback, data-schema detection and interrupted-manager
repair remain PENDING. Beta, ARM64 and AppImage publication are blocked until
their source authentication and runtime acceptance are measured. No second
updater or unattended elevation service is installed.

OCR/QR dependencies and PySide6 are optional package metadata. Removing those
tools does not remove the runtime; the corresponding companion command reports
its missing prerequisite. Existing optional tools are not uninstalled.

## Español

El gestor de paquetes es la única autoridad sobre rutas instaladas. Primero se
autentican manifiesto y paquete; el candidato se conserva por SHA-256, se usa un
flock de instancia y se registran transiciones saneadas en el estado del usuario.
`--status` y `--doctor` devuelven JSON local sin contactar GitHub. `--wait` espera
el cierre del ejecutable instalado; sin él, la app abierta aplaza la instalación.
Se vuelve a comprobar antes de instalar, pero no es un interlock universal ni
una transacción atómica de archivos.

Cancelar o fallar en el gestor conserva el candidato y requiere reintento
explícito. Interrumpir el proceso deja su última transición; el reintento vuelve
a autenticar manifiesto y paquete. El journal privado no garantiza persistencia
frente a pérdida eléctrica. Una transacción del gestor interrumpida debe revisarse
con pacman, dpkg/apt o rpm/dnf, sin renombrar sus árboles desde este updater.

Rollback significa seleccionar una release anterior autenticada con `--version`;
puede requerir descarga. No restaura ni borra datos personales. Cambiar el perfil
de build exige `--allow-profile-change`; un downgrade exige además
`--accept-data-downgrade-risk`. No se inspeccionan datos privados ni se presupone
compatibilidad de schemas upstream. Rollback automático, detección de schemas
de datos y reparación del gestor siguen PENDING. Beta, ARM64
y publicación AppImage esperan autenticación y aceptación real. No se instala
otro updater ni un servicio de elevación desatendida.

OCR/QR y PySide6 son dependencias opcionales. Quitar esos extras no elimina el
runtime; el comando correspondiente informa del requisito ausente. Los extras
ya instalados no se desinstalan.
