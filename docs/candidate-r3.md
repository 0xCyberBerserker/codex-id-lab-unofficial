# Codex I+D Lab — local candidate revision 3

## English

Native package identity: `26.908.40834-3`, built from commit
`d66b55ddd5e169bc2d6228e6530fe2e29b5fd562`.
The [manifest](../dist/r3-current/manifest.json) and
[checksums](../dist/r3-current/checksums.txt) describe this exact local set.
Its `buildProfile: release` identifies the build recipe, not a published or
attested release. Own builder attestation and promotion remain NOT_RUN.
Revision 2 packages/AppImage are preserved separately; no revision 3 AppImage
or authenticated GUI acceptance is claimed.

Verified on 2026-09-12:

- Python: 48 tests PASS, zero skips (including isolated Qt cases).
- Node: 75 PASS, one explicit native-fixture skip, zero failures.
- `bash scripts/test-shared-authority VERIFIED_CLI`: eight PASS, zero skips,
  including actual anonymous Unix `/rpc` HTTP 101, with home/network/desktop masked.
- Known official ASAR: shared-authority staging and diagnosis PASS; original
  SHA-256 remains `6c371cc96c2cf201c0777ddd54085f156efbb5347cbb21667cd8e67ec1bb36d3`.
- `scripts/validate-release-artifacts dist/r3-current 26.908.40834 3`: PASS
  for real Arch/DEB/RPM parsers, dependencies, identity, desktop entries, ownership,
  symlinks, executable modes and preserved upstream bytes/payload hashes.
- Cargo notices: 74 Linux registry dependencies collected from checksum-verified
  crates; 16 unreachable lock packages explicitly excluded. Candidate staging
  copies notices; tampering fails diagnosis. Not legal/security certification.
- Privacy, YAML, ShellCheck and diff whitespace: PASS. Original third-party notice
  whitespace is preserved. Argot NOT_RUN: repository scorer model missing.

Remaining gates: authenticated voice/dictation/microphone and portals; desktop
factory/task subscription; audited Computer Use/Agent Workspace helpers;
interrupted-manager inspection/recovery; unknown data-schema rollback;
AppImage static-library source/license and portability closure. No host migration,
account access, service changes, push, remote Actions or publication was performed.

## Español

Candidato nativo local `26.908.40834-3`, construido desde el commit indicado.
Manifiesto y checksums identifican este conjunto exacto; `buildProfile: release`
describe la receta, no una release publicada o firmada por nuestro builder.
Se conservan los paquetes/AppImage de revisión 2; no se declara AppImage 3 ni
aceptación autenticada de la GUI.

Pasan 48 tests Python, 75 Node y ocho nativos aislados. El skip nativo de la suite
Node se ejecuta aparte mediante el wrapper. Pasan staging/diagnóstico del ASAR
conocido, parsers reales Arch/DEB/RPM, identidad/dependencias/permisos y preservación
de bytes upstream. El dictado adjunta avisos de 74 dependencias Linux y registra
16 exclusiones del lockfile; detecta manipulación. No es certificación legal ni
auditoría completa. Privacidad/YAML/ShellCheck/diff pasan; falta preparar Argot.

Siguen pendientes voz/dictado autenticados y permisos, tareas reales del desktop,
helpers auditados, recuperación del gestor y schemas desconocidos, obligaciones
estáticas/portabilidad AppImage y firma/promoción en vivo. No se ha instalado,
desinstalado, accedido a cuentas, cambiado servicios, enviado al remoto ni publicado.
