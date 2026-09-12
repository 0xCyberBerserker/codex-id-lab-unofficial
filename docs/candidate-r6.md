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

### Remaining gates

Phase 1 engineering and phase 3 framework/package work have local evidence.
Phases 2 and 4–7 must not be represented as fully accepted: live builder trust,
desktop factory/authenticated tasks, voice/dictation/microphone, real capture/
insertion/playback, positive Computer Use capabilities, remote pairing/revocation,
Agent Workspace closure, unknown data-schema rollback, global manager repair,
AppImage source/portability and actual host migration remain blocked or NOT_RUN.
Unknown schema rollback and host-wide manager repair are not silently implemented.
Upstream updates inherit delivered native functions; unreviewed patches are never
autoimported and account/server entitlements are never fabricated.

No host installation/uninstallation, private account/data access, personal service
changes, app termination, push, PR, remote Actions or publication was performed.
The protected checkout's pre-existing changes are preserved; there is no automatic
merge into it. The private Git checkpoint records exact results and the next gates.

## Español

Candidato nativo local `26.908.40834-6`, identificado por el commit, receta,
payload, manifiesto y hashes indicados arriba. Origen APT firmado reverificado;
nuestro builder sigue sin attestation ni promoción. No es una release publicada,
aunque el perfil de receta se llame `release`. Se conservan los candidatos
anteriores y el AppImage 2; no se declara AppImage 6.

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
migración del host y firma/promoción necesitan sus gates. No se instaló,
desinstaló, accedió a cuentas/datos, cambió servicios, cerró apps ni publicó nada.
El WIP protegido queda intacto y el checkpoint privado conserva la continuidad.

Made with 🖤 in Barcelona City 🇪🇸
