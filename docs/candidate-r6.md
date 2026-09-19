# Codex I+D Lab — local candidate revision 6

## English

Native identity: `26.908.40834-6`, built from
`fdeeb9c981547f22204c10befba0fb8802cbbc61`.
[Manifest](../dist/r6-current/manifest.json) and
[checksums](../dist/r6-current/checksums.txt) identify this exact local set.
Build recipe SHA-256:
`f5f79471b7c9ba20c331d95394832397fbda18fd7e5cf36a643a427c4a929a0f`.
Payload SHA-256:
`187b967e728ecab3b348ab3d5e125fc0783dfa3e94a85c1c6d77622a0861e500`.
The approved source was reverified against cached signed APT metadata.
`buildProfile: release` describes the recipe, **not** an attested/published release.
Own builder attestation and promotion remain NOT_RUN. No revision 6 AppImage is
claimed. Previous candidates and the revision 2 AppImage are preserved.

| Format | Package SHA-256 |
|---|---|
| Arch | 951d36e2977e7701839dc82c4a02a477bbae61a7b95ac45cf015bc72ee04c1ed |
| DEB | 66b727a8a2a9d80473b22c1b928eb9e95c16ed7397ad73da465255344d11ac7a |
| RPM | 46faea9b3a6ba6c55dbb653c067e078054fd1bdca5a7ae9fcf81659156d6fa48 |

### Changes and verification

Exact journal recovery reauthenticates the retained tuple; corrupt/ambiguous
journals and changed digests fail closed. Native manager inspection is read-only:
no lock removal, global repair, database restoration or automatic elevation.
The optional companion bridge shares one private Unix authority, lists loaded
thread metadata without turns, and presents generic task/attention counts in
English/Spanish/Catalan. Notifications are opt-in and transition-deduplicated.
It does not prove visibility of an authenticated desktop's actual tasks.

Computer Use's pinned native source was compiled/tested offline in isolation.
The local transport requires portal capture and system executable paths; browser
host/setup/global desktop tools remain excluded. Its native development binaries
are not shipped or activated. See [focused review](native-helper-review.md).
Agent Workspace's actual pinned backend was inspected, but its 718-package
GPUI dependency closure requires a reviewed build/dependency decision.
The [AppImage source review](appimage.md) records why static-library
corresponding-source/relinking and portability gates remain open.

Measured on 2026-09-12, without account access or personal desktop permissions:

- Python: 66 tests, 65 PASS, one native-fixture skip. Actual offscreen Qt panels
  cover locales, palettes, selector and shared-authority task counts.
- Node: 78 tests, 76 PASS, two explicit native-fixture skips, zero failures;
  `--test-concurrency=1` is also configured in read-only push/PR CI.
- `scripts/test-shared-authority VERIFIED_CLI`: eight PASS, zero skips.
- `scripts/test-companion-shared-authority VERIFIED_CLI`: six PASS, zero skips.
- `scripts/test-computer-use-isolated BINARY SHA256`: one PASS, zero skips.
  The skipped native cases above run separately through these isolated wrappers.
- Computer Use Rust: 278 PASS serially, zero ignored; release build PASS.
  Its checksum/VCS-bound notice collection covers 182 reachable registry packages,
  with 27 excluded lock entries. Dictation's existing 74-package notices remain.
- RPM extraction regression: padding accepted; decoder and extractor errors
  rejected (three cases within Python). Parser matrix PASS for all three formats:
  identity, dependencies, ownership, launchers, full payload digest and unchanged
  upstream bytes/modes/symlinks. Temporary extraction used disposable disk storage.
- AUR PKGBUILD/.SRCINFO now bind revision 6 and the validated Arch digest;
  optional WebSocket companion dependency is preserved. Metadata only, not published.
- ShellCheck, all three workflow YAML parsers, privacy and diff checks PASS.
  Argot NOT_RUN: scorer model absent;
  no automatic initialization. Remote Actions/actionlint are NOT_RUN.

Failure history is retained, not hidden: revision 4 parsing exhausted tmpfs;
revision 5 RPM decoding succeeded to a file but its extraction pipeline returned
SIGPIPE after cpio's trailer. Revision 6 drains padding without hiding failures.
An earlier concurrent Rust test failed a sub-second timing assertion, then passed
serially without code/assertion changes. A Qt fixture's 600 ms quit preceded IPC
completion under package compression; only that fixture's wait budget increased,
with identical content/privacy assertions. Production deadlines are unchanged.

### Native Arch lifecycle follow-up

After explicit installation/removal test authorization, real pacman installed and
removed revision 6 successfully in a rootless UID/GID-mapped namespace. Dependency
checks used a private copy of installed host package metadata, excluding this app;
this is not an independent clean-distribution image. Host paths were read-only,
home/runtime/network masked, and pacman's download sandbox was not disabled.
The installed payload digest, original ASAR and launcher presence matched before
removal; package registration and app/launcher absence were checked afterwards.
Evidence: `build/qa/r6-arch-native-lifecycle-rootless.log`.

Initial harness attempts exposed a missing mountpoint, omitted ALPM version file,
and single-UID mapping incompatible with pacman's download user. The corrected
harness uses the existing subordinate UID/GID mappings, without host database
upgrade, signature override, dependency-check bypass or new tool installation.
At that checkpoint host mutation was NOT_RUN due active UI/tasks and required
administrative authentication. The authorized follow-up below supersedes that gate.

### Authorized host lifecycle follow-up

After the user closed the UI and authorized continuation, native pacman upgraded
revision 1 to 6, removed revision 6, and reinstalled the exact verified revision 6
archive successfully. Administrative authentication used the system's pkexec
dialog; no password was collected. No new dependencies were installed, no signature
or sandbox policy was overridden, and removal did not recursively remove dependencies.

Final state: `codex-id-lab-unofficial 26.908.40834-6`; pacman reports 6,868 files and
zero missing. Installed manifest/build identity, full payload digest and original
ASAR digest match this candidate. Native CLI reports `0.154.0-alpha.6.2`.
All four `codex-lab*` launcher targets and system desktop entries validate; the
existing executable desktop shortcut already uses the correct command/icon.
The companion remains inactive; no personal service was enabled or stopped.
Normal distro transaction hooks refreshed caches/user-manager configuration and
created their configured Snapper snapshots.

A private non-recursive archive of revision 1's package-owned files and package
description was preserved before upgrade; SHA-256
`22edb78c1a09bc76eca09531796368a0f8cf368c2e53a740a0f1f4eef386c643`.
This is not automatic data-schema rollback or a raw package-database restore.
Evidence: `build/qa/r6-host-install.log`, `r6-host-uninstall.log`,
`r6-host-reinstall.log`, and `r6-host-runtime-anonymous-smoke.log`.
A disposable copy of the installed runtime passed actual anonymous software-X11
window startup with home/network isolated and Chromium sandbox retained. No host
account/profile, microphone, playback or authenticated voice functionality was tested.

### Native media follow-up

The installed revision 6 passed `tests/native_media_probe.py` on 2026-09-12:
secure application context, three labeled synthetic audio inputs, two inputs
accepted by the actual settings filter before/after capture, one audio track,
zero video tracks, and a non-empty MediaRecorder recording. The probe uses
Chromium fake devices and a private debugging pipe in an anonymous offline
namespace without `/dev/snd`, personal homes or desktop sockets. It does not
override permission handlers or use fake permission approval. No recording is
saved and no actual microphone/account/backend is used.

Reproduce with the verified installed path and ASAR digest:

```bash
python3 tests/native_media_probe.py /opt/codex-id-lab-unofficial \
  6c371cc96c2cf201c0777ddd54085f156efbb5347cbb21667cd8e67ec1bb36d3
CODEX_LAB_TEST_DICTATION_ASAR=/opt/codex-id-lab-unofficial/resources/app.asar \
  node --test tests/global-dictation.test.js
```

The latter also checks the opt-in Wayland adapter against this actual pinned
ASAR, validates syntax without executing upstream code, and leaves the archive
unchanged. Native global hold/release is unsupported in the unmodified Linux
bundle; the experimental portal adapter remains disabled in the installed base.
The restrictive clipboard permission handler belongs to the integrated browser,
not the main UI; it was not widened. Composer dictation additionally depends on
the server feature and ChatGPT authentication, neither of which this test grants.
Actual hardware audio, transcription and voice playback are still NOT_RUN.

Three transport regressions pass and are automatically discovered by existing
read-only push/PR CI. The actual-ASAR case requires an explicit reviewed fixture;
the synthetic runtime probe is a local/manual check, not a remote Actions result.
Evidence: `build/qa/native-media-probe-r3.log` and
`build/qa/native-dictation-contract.log`. The first probe failed on pipe descriptor
inheritance; the harness was corrected without changing runtime permissions.
Tests/docs do not change revision 6's build recipe or installed payload.

### Remaining gates

Follow-up on 2026-09-13: three positive native CLI accessibility cases pass in a
private Qt/Xvfb/AT-SPI session (en/es/ca). The fixture PID, editable text, bounds and
focus are verified. See [native helper review](native-helper-review.md) and
`tests/test-computer-use-accessibility BINARY SHA256`. This does not close targeted
MCP state, screenshot/input or portal-consent gates; the CLI name filter is not a
PID-capable MCP target. No helper activation or installed package change occurred.

Phase 1 engineering and phase 3 framework/package work have local evidence.
Phases 2 and 4–7 must not be represented as fully accepted: live builder trust,
desktop factory/authenticated tasks, voice/dictation/microphone, real capture/
insertion/playback, positive Computer Use capabilities, remote pairing/revocation,
Agent Workspace closure, unknown data-schema rollback, global manager repair,
AppImage source/portability and authenticated host acceptance remain blocked or NOT_RUN.
Unknown schema rollback and host-wide manager repair are not silently implemented.
Upstream updates inherit delivered native functions; unreviewed patches are never
autoimported and account/server entitlements are never fabricated.

Host package lifecycle is now verified as described above. No private account/data
access, personal service enablement/termination, push, PR, remote Actions or
publication was performed. The user closed the original UI before the host test.
The protected checkout's pre-existing changes are preserved; there is no automatic
merge into it. The private Git checkpoint records exact results and the next gates.

## Español

Seguimiento 13-09-2026: pasan tres casos positivos de accesibilidad del CLI nativo
en sesión Qt/Xvfb/AT-SPI privada (en/es/ca), verificando PID, texto editable,
geometría y foco. El harness está descrito en `native-helper-review.md`; no
acredita MCP dirigido, captura/input ni consentimiento del portal. No se activa
el helper ni cambia el paquete instalado. Receta/payload de revisión 6 intactos.

Candidato nativo local `26.908.40834-6`, identificado por el commit, receta,
payload, manifiesto y hashes indicados arriba. Origen APT firmado reverificado;
nuestro builder sigue sin attestation ni promoción. No es una release publicada,
aunque el perfil de receta se llame `release`. Se conservan los candidatos
anteriores y el AppImage 2; no se declara AppImage 6.

La prueba multimedia del runtime instalado pasa con audio sintético: contexto
seguro, tres entradas etiquetadas, dos aceptadas por el selector antes/después
de capturar, una pista de audio, ninguna de vídeo y grabación MediaRecorder no
vacía. Usa dispositivos falsos de Chromium, pipe privado y namespace anónimo sin
red, `/dev/snd`, homes personales ni sockets del escritorio. No amplía permisos,
guarda audio ni utiliza micrófono, cuenta o backend reales. Los comandos anteriores
permiten repetirla. Tres regresiones del transporte entran automáticamente en el
CI push/PR existente; no se han ejecutado Actions remotas.

El adaptador Wayland también acepta el ASAR real fijado y conserva su archivo
intacto; sólo se compila su sintaxis, sin ejecutar código upstream. El dictado
global al mantener/liberar el atajo no está soportado por la base Linux sin
parches; el adaptador experimental sigue deshabilitado. El handler restrictivo
de portapapeles pertenece al navegador integrado y se conserva: ampliarlo no
arreglaría la UI principal. Dictado del composer depende además del flag servidor
y autenticación ChatGPT. Audio físico, transcripción y reproducción siguen NOT_RUN.
Tests y documentación no cambian la receta ni el payload instalado de revisión 6.

Se implementó recuperación del candidato exacto autenticado, sin borrar locks ni
reparar/restaurar el host. El companion puede compartir una autoridad Unix opt-in,
consultar metadatos sin conversaciones y mostrar tareas/atención en tres idiomas;
las notificaciones genéricas son opcionales y deduplicadas. No acredita todavía
las tareas reales de un desktop autenticado. Computer Use compila y pasa pruebas
nativas aisladas, fuerza portal y PATH del sistema, pero no se distribuye ni activa.
Agent Workspace y las obligaciones estáticas AppImage tienen bloqueos concretos,
no una declaración de paridad ni un descarte sin intentar integración.

Pasan 65 tests Python y 76 Node; los skips nativos se ejecutan aparte con wrappers
aislados: ocho del transporte, seis del companion y uno de Computer Use. Rust pasa
278 en serie. Avisos transitivos: 182 paquetes Computer Use y 74 del dictado.
La matriz de parsers 6 pasa en los tres formatos, incluidos permisos, launchers,
hashes y bytes upstream intactos. ShellCheck/YAML/privacidad/diff pasan; falta preparar
Argot y no se han ejecutado Actions remotas. Se conserva el historial de fallos:
tmpfs lleno, SIGPIPE del parser y fixtures sensibles a carga. Se corrigió el parser
y se ajustó solo la espera de fixtures, sin relajar assertions ni límites reales.
PKGBUILD/.SRCINFO AUR fijan revisión 6 y su checksum validado; no se publicaron.

Fases 1/3 con evidencia local; aceptación completa de 2 y 4–7 pendiente. Voz y
dictado autenticados, micrófono/portales, tareas reales, captura/input/reproducción,
emparejamiento remoto, closures de helpers/AppImage, schemas desconocidos,
aceptación autenticada del host y firma/promoción necesitan sus gates. La prueba
autorizada del paquete en el host se completó; no se accedió a cuentas/datos,
habilitó/detuvo servicios personales ni publicó nada.
El WIP protegido queda intacto y el checkpoint privado conserva la continuidad.

Tras autorizar las pruebas de instalación/desinstalación, pacman real instaló y
eliminó revisión 6 dentro de un namespace rootless con mapeo UID/GID completo.
Se comprobaron payload, ASAR y launcher antes; ausencia de paquete/app/launcher
después. Las dependencias se validaron contra una copia privada de metadata del
host: no equivale a una imagen limpia independiente. Sin red ni acceso al home del
usuario ni desactivar sandbox, firmas o comprobación de dependencias. El harness
inicial necesitó corregir mountpoint, versión ALPM y mapeo del usuario de descarga;
no se actualizó la base del host ni se instalaron herramientas. En aquel checkpoint
el host permanecía en revisión 1, pendiente de cierre y autenticación.

Después del cierre de la UI por el usuario y su autorización de continuación,
pacman actualizó 1 → 6, desinstaló 6 y reinstaló el mismo archivo verificado: PASS.
La autenticación se realizó mediante pkexec, sin recoger contraseñas. Queda revisión
6 instalada: 6.868 archivos, ninguno ausente, manifiesto/payload/ASAR correctos y
CLI `0.154.0-alpha.6.2`. Lanzadores, entradas de menú e icono existente del escritorio
validan; no se añadieron dependencias ni se habilitaron/detuvieron servicios.
Los hooks normales de la distro actualizaron caches/configuración y sus snapshots.
Se conserva un backup privado no recursivo de archivos del paquete 1 y descripción,
con el SHA indicado arriba; no es rollback automático de datos ni restauración de DB.
Una copia desechable del runtime instalado pasó arranque de ventana anónima X11,
sin cuenta/red/directorios personales y conservando sandbox. Voz, dictado y permisos
reales del micrófono siguen sin aceptación autenticada.

Made with 🖤 in Barcelona City 🇪🇸
