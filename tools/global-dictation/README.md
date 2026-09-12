# Experimental Wayland dictation helper

Selected MIT portal helper and fake-portal tests from the pinned ilysenko snapshot.
It requests GlobalShortcuts and keyboard-only RemoteDesktop permission; it does
not open `/dev/input`, scrape credentials or implement speech recognition itself.
The official runtime remains responsible for dictation and account entitlements.
X11 input watchers and installer hooks are deliberately excluded.

The original lockfile used event-listener 5.4.1, affected by
[RUSTSEC-2026-0221](https://rustsec.org/advisories/RUSTSEC-2026-0221.html).
The lockfile now fixes 5.4.2. OSV queried all 90 locked registry dependencies on
2026-09-12: no reported advisories. This is not a complete source/security audit.
Build scripts were inspected and compiled offline with personal homes, desktop
bus and networking unavailable. Nine native tests pass against a private D-Bus.
Local adaptations close portal sessions on errors and best-effort release keys
after an interrupted paste chord. No personal desktop input was generated.

Development procedure, after reviewing locked dependency changes:

```bash
TASK_CARGO_CACHE=$(mktemp -d /tmp/codex-lab-cargo.XXXXXX)
CARGO_HOME="$TASK_CARGO_CACHE" cargo fetch --locked --manifest-path tools/global-dictation/Cargo.toml
python3 tools/global-dictation/audit-dependencies.py --query-osv
tools/global-dictation/test-isolated "$TASK_CARGO_CACHE"
# Use the printed target directory and its release executable, never a floating download.
export CODEX_LAB_GLOBAL_DICTATION_HELPER=/tmp/PRINTED_TARGET/release/codex-global-dictation-linux
export CODEX_LAB_GLOBAL_DICTATION_HELPER_SHA256=$(sha256sum "$CODEX_LAB_GLOBAL_DICTATION_HELPER" | cut -d ' ' -f 1)
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/lab-features.js experimental-stage \
  /tmp/FRESH_DISPOSABLE_APP packaging/profiles/experimental-wayland-dictation.json
node scripts/lab-features.js diagnose /tmp/FRESH_DISPOSABLE_APP
```

Staging copies only the explicitly hashed executable into the disposable tree;
it never launches it. Start from fresh verified upstream to disable/remove it.
Real portal denial/cancellation, microphone, authenticated transcription, focus
and paste acceptance remain NOT_RUN. The binary is not included in stable packages.
Before redistribution, vendor applicable dependency license texts/notices,
including Unicode-3.0 for unicode-ident, and complete the acceptance gates.

## Español

Helper MIT y tests seleccionados del snapshot fijado de ilysenko. Solicita permisos
GlobalShortcuts y RemoteDesktop sólo para teclado; no abre `/dev/input`, no copia
credenciales ni implementa reconocimiento de voz. El runtime oficial mantiene el
dictado y las concesiones de cuenta. Se excluyen watchers X11 y hooks de instalación.

Se corrigió event-listener 5.4.1 → 5.4.2 por RUSTSEC-2026-0221. OSV no detectó
avisos en las 90 dependencias fijadas el 12-09-2026; no es una auditoría completa.
Se inspeccionaron scripts de build y se compiló offline, sin home personal,
bus del escritorio ni red. Pasan nueve pruebas nativas contra un D-Bus privado.
Los cambios locales cierran sesiones al fallar y liberan teclas tras una pega
interrumpida. No se generó input sobre tu escritorio.

El procedimiento anterior sólo crea candidatos desechables: staging copia el
ejecutable con hash explícito y no lo ejecuta. Deshabilitar exige partir de upstream
fresco. Micrófono, permisos/cancelación reales, transcripción autenticada, foco y
pega siguen NOT_RUN. No se incluye el binario en paquetes estables. Su futura
redistribución exige textos/avisos de dependencias, incluido Unicode-3.0, y gates
de aceptación completos.
