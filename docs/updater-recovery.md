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
`codex-lab-install --recover` selects the exact retained journal identity/digest,
not the latest release. Corrupt, ambiguous or symlink journals and changed remote
digests are rejected. It re-verifies builder attestations and cannot be combined
with `--version` or a diagnostic mode. No recovery action is automatic.
The transition journal is local, private and not a power-loss-proof transaction
log. A failed package transaction must be inspected/repaired through pacman,
dpkg/apt or rpm/dnf; the updater does not rename manager-owned trees.
Before recovery requests privileges, it refuses an observed pacman lock or a
nonempty/failed/timed-out targeted `dpkg --audit` result. It never removes a lock,
runs global configuration repair or restores data. `--doctor` reports recovery
availability and sanitized manager status. This observation is not a manager-lock
acquisition or proof that the database is healthy; the native manager validates
the actual retry. See [pacman locking](https://wiki.archlinux.org/title/Pacman)
and [targeted dpkg audit](https://manpages.debian.org/trixie/dpkg/dpkg.1.en.html).

Rollback is an explicit previously authenticated release via `--version`; the
previous package may need downloading. User data is not rolled back or deleted.
Changed installed build feature profiles require `--allow-profile-change`;
explicit downgrades also require `--accept-data-downgrade-risk`. Neither flag
restores, deletes or inspects personal data. Unknown upstream data schemas cannot
be declared compatible. Exact retained-candidate retry is implemented and fixture-tested;
global manager/database repair remains an explicit native-administrator action.
Automatic data rollback is BLOCKED: no approved upstream data-schema compatibility
contract is available; no personal database is inspected to guess one.
Beta, ARM64 and AppImage publication are blocked until
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

`codex-lab-install --recover` fija identidad y digest al candidato retenido, no a
la última release. Rechaza journal corrupto/ambiguo/enlazado y digest remoto cambiado;
vuelve a verificar attestations. No admite `--version` ni modos de diagnóstico.
Antes de elevar privilegios rechaza locks pacman observados o auditoría dpkg del
paquete pendiente/fallida/con timeout. Nunca borra locks ni reconfigura globalmente
el sistema. `--doctor` informa de disponibilidad y estado saneado; no demuestra
salud completa del gestor ni adquiere su lock. No se ejecutó reparación en el host.

Rollback significa seleccionar una release anterior autenticada con `--version`;
puede requerir descarga. No restaura ni borra datos personales. Cambiar el perfil
de build exige `--allow-profile-change`; un downgrade exige además
`--accept-data-downgrade-risk`. No se inspeccionan datos privados ni se presupone
compatibilidad de schemas upstream. Está implementado/probado el reintento exacto
del candidato; reparar globalmente la base del gestor exige actuación nativa
explícita del administrador. Rollback automático de datos queda BLOCKED por falta
de contrato upstream aprobado de compatibilidad; no se inspecciona tu base privada
para inferirlo. Beta, ARM64
y publicación AppImage esperan autenticación y aceptación real. No se instala
otro updater ni un servicio de elevación desatendida.

OCR/QR y PySide6 son dependencias opcionales. Quitar esos extras no elimina el
runtime; el comando correspondiente informa del requisito ausente. Los extras
ya instalados no se desinstalan.
