# Shared authority bridge — experimental

English

Opt-in adaptation of ilysenko's MIT shared-app-server transport. A disposable build
routes the desktop's local transport through the bundled CLI's Unix WebSocket
server. The base profile leaves ASAR unchanged. Runtime staging only accepts `/tmp`
candidates with regular, non-symlink resources.

The bridge uses a same-user private runtime directory (0700), a Unix socket, and an
owned lock/discovery record (0600). It preserves opaque configuration overrides,
drains stderr without retaining it, and stops only its own backend. No SSH hook,
global orphan reaper, attached CLI command, network exposure or account discovery
is imported. `CODEX_CLI_PATH`, if specified, must be absolute; normally the signed,
bundled CLI is used.

Select `packaging/profiles/experimental-shared-authority.json` with the existing
explicit `experimental-stage` candidate command. Disable by building a fresh
verified upstream candidate with the base profile, not by reverse-patching an
installed tree.

Tests cover staging/ASAR integrity/disable, ownership and configuration ordering.
An isolated native CLI test verifies the real `/rpc` HTTP 101 WebSocket upgrade.
Authenticated desktop factory integration and companion task visibility remain
NOT_RUN. This module does not yet make the companion observe desktop tasks.

Español

Adaptación opt-in del transporte MIT de ilysenko. Un build desechable conecta el
transporte local del desktop al servidor Unix WebSocket del CLI incluido. El perfil
base conserva ASAR intacto; el staging sólo acepta candidatos `/tmp` sin enlaces
simbólicos en sus recursos.

Usa un directorio privado del mismo usuario (0700), socket Unix y registro/lock
propios (0600). Conserva overrides opacos, drena stderr sin guardarlo y detiene
únicamente su backend. No incorpora SSH, limpieza global de procesos, comando CLI
adjunto, exposición de red ni descubrimiento de cuentas.

Selecciona el perfil experimental indicado mediante `experimental-stage`.
Desactivar exige un build nuevo desde upstream verificado con el perfil base;
nunca desparchea la instalación existente.

Las pruebas verifican staging, integridad ASAR, desactivación, propiedad y orden de
configuración. El CLI real aislado responde HTTP 101 en `/rpc`. La integración
autenticada del desktop y la observación de tareas desde el companion siguen
NOT_RUN: el puente no demuestra todavía esas capacidades.
