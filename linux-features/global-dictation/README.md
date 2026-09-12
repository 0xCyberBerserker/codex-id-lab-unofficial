# global-dictation — experimental Wayland candidate

Known-ASAR patch and explicitly hashed Rust helper stage in a disposable candidate.
Nine native fake-portal tests and JavaScript activation/paste/cleanup tests pass.
Actual microphone, portal consent, release/cancellation, focus and authenticated
dictation acceptance remain NOT_RUN. X11 is intentionally unavailable.

Reference source/commit/license are in `feature.json` and the import inventory.
No installer hook or global input watcher is imported. Disabled fresh builds add
no helper, permissions or activity. See [the isolated build procedure](../../tools/global-dictation/README.md).

## Español

El parche ASAR conocido y el helper Rust con hash explícito se prueban en un
candidato desechable. Pasan nueve tests nativos de portales simulados y pruebas
JavaScript de activación, pega y cierre. Micrófono, consentimiento, cancelación,
foco y dictado autenticado siguen NOT_RUN. X11 queda excluido.

La referencia está fijada en `feature.json` y el inventario. No se importan
instaladores ni watchers globales. Un build fresco deshabilitado no añade helper,
permisos ni actividad. El procedimiento anterior conserva el aislamiento.
