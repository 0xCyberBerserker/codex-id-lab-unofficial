# Optional Linux features

The framework library is selectively reused from the pinned MIT-licensed Ilysenko snapshot listed in `third-party/upstream.lock.json`. These Linux extensions are not official Codex plugins. No feature is enabled by default.

The base Lab adapter accepts declared regular-file resources within `.codex-linux/features/<id>/`. A separate explicitly gated experimental adapter supports AppShots and Read Aloud ASAR contracts in disposable candidates. Generic runtime/package hooks remain rejected. The base profile leaves upstream ASAR and native binaries unchanged. See [module acceptance](../docs/features.md).

Each feature must declare its ID, disabled default, dependencies/conflicts and a `lab` object containing `capabilities`, `compatibility.asarSha256`, `stability` and `tests`. Unknown IDs, conflicts and upstream hash drift reject the candidate before staging. Private selections/settings and local modules must remain outside tracked release profiles.

Run `node --test scripts/lib/linux-features.test.js tests/lab-features.test.js`.

---

# Funciones Linux opcionales

La biblioteca del framework se reutiliza selectivamente desde el snapshot MIT de Ilysenko fijado en `third-party/upstream.lock.json`. Estas extensiones Linux no son plugins oficiales de Codex. Ninguna función se activa por defecto.

El adaptador base acepta ficheros regulares dentro de `.codex-linux/features/<id>/`. Un adaptador experimental separado admite los contratos ASAR de AppShots y Read Aloud en candidatos desechables, con gate explícito. Los hooks genéricos de runtime/paquetes siguen rechazados. El perfil base conserva ASAR y binarios nativos upstream. Consulta la aceptación por módulo en `docs/features.md`.

Cada módulo declara ID, desactivación predeterminada, dependencias/conflictos y un objeto `lab` con `capabilities`, `compatibility.asarSha256`, `stability` y `tests`. IDs desconocidos, conflictos o drift del hash upstream rechazan el candidato antes del staging. Las opciones privadas y módulos locales no deben entrar en perfiles de release versionados.

Ejecuta `node --test scripts/lib/linux-features.test.js tests/lab-features.test.js`.
