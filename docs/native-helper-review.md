# Native helper review candidates

## English

These are source-pinned development experiments, not shipped or approved binaries.
The base profile and installed host are unchanged. A successful vulnerability query
or compilation is not a complete security or redistribution audit.

### Computer Use Linux

Source: `ilysenko/codex-desktop-linux`, commit
`249cd4b64d42434f51417fec4a318750d461b676`, `computer-use-linux/`, MIT.
The reviewed source lacked Cargo.lock; a disposable development lock resolves 209
registry dependencies, SHA-256
`649f0144a31c75e4383bb8ddfe81d92184e6e530e687ac6211585d6587c82af2`.
The 2026-09-12 OSV query reported zero known findings for those versions. Build
hooks were inspected before compilation; vendored C compilation and pkg-config
probes ran only in a read-only-source, offline bubblewrap namespace with no host
home, desktop bus, network or input device.

`cargo test --locked --offline -- --test-threads=1`: 278 PASS, zero ignored.
An earlier concurrent run had 277 PASS and one FAIL in the continuous-output
sub-second timing assertion; it did not reproduce serially, without source edits
or weaker assertions. `cargo build --locked --offline --release`: PASS.

| Development binary | SHA-256 |
|---|---|
| codex-computer-use-linux | f9902fa16b39895ac267151874ff9a35d083033de2ba18513494dcee0de05b72 |
| codex-chrome-extension-host | 73e5ea72290b1a9f47256e0615208a0b827ee71c2896fca4f6ad92b6b05797d7 |
| codex-computer-use-cosmic | 3a00edf847aeec875cdcc36cacc2d0c8b2392b76edcf857854e564680e613b9a |

`scripts/test-computer-use-isolated BINARY SHA256` verifies the digest and real
MCP initialization through our target-enforcing service, denial of unavailable
window/input capabilities, diagnostics and absence of input devices. This is
**not** a screenshot/accessibility/input acceptance test. The empty test namespace
has no compositor/portal and no wmctrl; no host permission is widened for a PASS.

The initial target-filtered collector rejected rmcp and rmcp-macros 1.8.0 because
their crates contain no license text. The exact upstream repository/commit notice
is now preserved and explicitly associated with each locked crate checksum,
declared license, VCS commit and text digest in
`third-party/computer-use/external-notices.json`. The collector never downloads a
fallback or modifies a crate. Wrong source/checksum/text/filename fails closed.
The reviewed Linux graph now collects 182 packages successfully (27 non-reachable
lock entries excluded). The original upstream notice preserves its Apache/MIT
licensing-transition statement and documentation terms; metadata alone was not
treated as a complete rights grant.

Native staging remains BLOCKED on a sandbox-preserving integration and controlled
positive screenshot/accessibility/input acceptance. Notice collection is not legal
certification or proof of those capabilities. Development binaries are not shipped.
Focused defensive review inspected command/process cancellation, target/PID
selection, portal denial and screenshot fallbacks. The local transport now fixes
`PATH=/usr/bin:/bin` and `CODEX_COMPUTER_USE_SCREENSHOT_BACKEND=portal`; a regression
proves ambient executable/capture overrides cannot select the CLI fallback. This
does not sandbox the backend automatically or grant desktop/input consent. Browser
host, setup and unrestricted desktop tools remain excluded. A sandbox-preserving
positive capability/permission harness is still required before activation.

On 2026-09-13, `tests/test-computer-use-accessibility BINARY SHA256` passed three
positive native CLI cases against real Qt/AT-SPI in English/Spanish/Catalan.
The wrapper verifies the reviewed binary digest before creating an offline
bubblewrap namespace with personal homes/runtime/input devices masked. Xvfb and
the session/accessibility D-Bus are private; no host service is enabled. Tests
discover exactly the fixture's PID and read its named editable field, text,
untruncated content, nonzero bounds and focus states. Qt uses the system palette.
CI checks the harness and records explicit skips when this native fixture is
not supplied; no remote Actions run is claimed.

These three cases are **CLI accessibility acceptance only**. A subsequent private
KWin X11 test now provides positive targeted MCP state and keyboard acceptance:
`tests/test-computer-use-accessibility BINARY SHA256 kwin`. Actual KWin scripting
resolves the unique fixture window to its PID; AT-SPI reads its editable text.
Real Ctrl+A and typing change only that fixture, and a nonexistent target is
rejected without changing the text. Accessibility is enabled on the private bus
only. Capture must fail without a portal, preserving the portal-only policy.
Evidence: `build/qa/native-kwin-mcp-r5.log` (one PASS, zero skips). This does not
accept Wayland capture/input consent or activate/ship the helper.
The CLI `apps` uses AT-SPI directly; CLI `state APP_NAME` has no PID argument, so
the test verifies the discovered PID/unique app before filtering the snapshot by
name. MCP `get_app_state` and input first resolve/focus a window target. The generic
X11 window backend requires wmctrl, absent on this host; Xvfb/AT-SPI alone do not
provide a working capture/input portal. No fake window inventory or permission
approval is substituted. KWin supplies the real alternative to the missing generic
wmctrl backend. Positive screenshot and actual Wayland portal consent remain
BLOCKED; the backend is still unshipped/disabled.

Evidence: `build/qa/native-accessibility-r2.log` (three PASS, zero skips).
The first run had two PASS and one English fixture failure because its custom
translator returned empty text; the fixture fallback was fixed without weaker
assertions. This tests-only harness and CI/docs changes do not alter revision 6's
recipe, payload or installed package.

### Agent Workspace

External backend source: `agent-sh/agent-workspace-linux`, tag v0.3.2, resolved
commit `6c7691e817e4409be1eee508dad7cf165dd68171`; source archive SHA-256
`3bdd30de20b14c41b3e21b53fee334af701cea426f3942ae528589bb1db517e7`.
Cargo.lock SHA-256:
`c0b5e94fb888a02ea33b803e516e0e143debef4dade8de4b447c9e003bcfae73`.
The package license is MIT; the lock contains 718 packages and 29 Git-sourced
packages. GPUI and gpui_platform are unconditional dependencies on Zed, locked
to `9bde578ef5afa84920c4300af25f9dee31c96fcf`, despite the branch-based manifest.
There is no Cargo feature that separates a minimal headless/MCP build from this
viewer closure. Offline metadata fails because that Git checkout is absent.

The integration attempt resolved and inspected the actual backend instead of
trusting the wrapper's license. No npm postinstall, global installation, skill
write, browser-profile/cookie copy or sandbox-disabling option was executed or
imported. Without explicit permissions, its MCP has no independent permission
ceiling. Integration is BLOCKED on a reviewed source/dependency/notice closure and
a sandbox-preserving, explicit-permission controlled runtime; it is not discarded.
Splitting/optionalizing the upstream viewer is a larger dependency decision, not
silently performed in this candidate.

## Español

Son experimentos de desarrollo fijados por fuente, no binarios distribuidos ni
aprobados. Perfil base y host no cambian. Compilar o consultar vulnerabilidades no
equivale a una auditoría completa de seguridad/licencias.

Computer Use usa el commit MIT de Ilysenko indicado arriba. Se resolvieron 209
dependencias con lock desechable fijado por SHA; OSV no informó de hallazgos el
12-09-2026. Los hooks revisados se ejecutaron únicamente dentro de bubblewrap,
sin red, home, bus del desktop ni dispositivos de entrada. Pasan 278 pruebas en
serie; un fallo temporal bajo concurrencia no se reprodujo, sin aflojar assertions.
Los tres binarios release se compilaron y tienen los hashes de la tabla.

La prueba real MCP comprueba inicialización, rechazo de capacidades ausentes,
diagnóstico y ausencia de dispositivos; no acredita captura, accesibilidad ni
input positivos. No se amplían permisos para aprobarla. Redistribución y staging
siguen BLOCKED por integración que preserve el sandbox y aceptación controlada positiva,
no por una declaración de paridad. Tras detectar ausencia de texto en rmcp y
rmcp-macros 1.8.0, se conservó el aviso del commit exacto y se vinculó a checksum,
licencia declarada, VCS y digest del texto. El colector recoge 182 paquetes Linux
y excluye 27 no alcanzables; no descarga fallbacks ni modifica crates. Rechaza
origen, checksum, texto o ruta incorrectos. Se preserva la declaración upstream de
transición Apache/MIT y términos documentales, sin considerarla certificación legal.
Los binarios de desarrollo no se distribuyen.
La revisión defensiva acotada examinó cancelación/procesos, destino/PID, denegación
de portal y fallbacks. El transporte fija PATH del sistema y backend portal, con
regresión frente a overrides ambientales. No concede permisos ni crea sandbox
automático; browser host, setup y herramientas globales siguen fuera. Falta un
harness positivo de capacidades/permisos que conserve la frontera de aislamiento.

El 13-09-2026 pasan tres casos positivos del CLI nativo contra Qt/AT-SPI reales
en inglés/español/catalán. `tests/test-computer-use-accessibility BINARIO SHA256`
verifica el digest revisado y crea namespace offline sin homes/runtime personal
ni dispositivos de entrada. Xvfb y los buses de sesión/accesibilidad son privados;
no activa servicios del host. Descubre exclusivamente el PID del fixture y lee
campo editable, texto íntegro, geometría y foco reales. Qt conserva la QPalette.
CI valida el harness y declara skips si falta el fixture nativo; no se han
ejecutado Actions remotas. Evidencia: `build/qa/native-accessibility-r2.log`.

Los tres casos acreditan accesibilidad del CLI. La prueba posterior
`tests/test-computer-use-accessibility BINARIO SHA256 kwin` acredita estado MCP
dirigido al PID y teclado reales contra un único fixture KWin X11 privado.
Ctrl+A y escritura cambian su campo; un destino inexistente se rechaza sin cambiar
el texto. Se habilita accesibilidad únicamente en el bus privado. Sin portal se
rechaza la captura, sin fallback CLI. Evidencia: `build/qa/native-kwin-mcp-r5.log`
(un PASS, cero skips). No acredita consentimiento/captura/input Wayland ni activa
o distribuye el helper. KWin es una alternativa real al backend genérico wmctrl.

El caso CLI por sí solo no acredita control del desktop por MCP.
CLI `state NOMBRE_APP` no admite PID; se comprueba PID/app única antes del filtro.
MCP exige resolver/enfocar WindowTarget; el backend X11 genérico requiere wmctrl,
ausente, pero la prueba privada usa KWin real.
Xvfb/AT-SPI no suministran portal funcional de captura/input. No se falsifica
inventario de ventanas ni aprobación de permisos. Captura positiva y consentimiento
Wayland siguen BLOCKED; backend sin distribuir/activar. Se corrigió
el fallback inglés del traductor del fixture tras un fallo, sin aflojar aserciones.
Este lote de tests/CI/docs no cambia receta, payload ni paquete instalado.

Agent Workspace se resolvió a v0.3.2/commit y archive SHA anteriores. Su lock
incluye 718 paquetes, 29 de Git; GPUI/Zed es incondicional y no hay feature Cargo
para compilar sólo MCP/headless. Metadata offline falla por faltar ese checkout.
Se inspeccionó la fuente real, sin postinstall npm, instaladores globales, escritura
de skills, cookies/perfiles privados ni opciones que desactiven sandbox. Sin
permisos explícitos, MCP carece de techo propio. Sigue BLOCKED por revisión de
fuente/dependencias/avisos y aceptación aislada con permisos explícitos, no
descartado. Separar el viewer exige una decisión mayor que no se aplica a escondidas.
