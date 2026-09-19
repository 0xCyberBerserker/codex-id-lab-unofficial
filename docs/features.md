# Linux features

The base profile preserves upstream ASAR exactly. The official runtime owns voice,
native dictation and browser/account functionality; packaging does not grant server
entitlements or microphone permission. Authenticated voice/dictation remain NOT_RUN
in this autonomous execution.

`codex-lab-tools features` opens the native QPalette feature selector;
`features-json` reports requested/installed state and rebuild/incompatibility.
Saving preserves preferences and does not rebuild, install or grant permissions.
`codex-lab-tools feature-profile-json` exports build-only JSON without changing
preferences; disabled settings and unrelated private preferences are excluded.
New builds must start from the verified upstream archive; disabling cannot unpatch
an existing installed runtime in place.

| Module | Measured local state | Remaining gate |
|---|---|---|
| AppShots | MIT patches; known-ASAR staging and roundtrip; hotkeys excluded | Controlled capture, cancellation, insertion and backend permission |
| Read Aloud | MIT webview + local espeak adapter; stdin/owned-stop fixture; actual ASAR | Authenticated renderer and audible playback |
| Global dictation | Wayland-only ASAR adapter; native Rust helper; private D-Bus tests; 74 dependency notice texts | Real portal permission, microphone and authenticated dictation |
| Computer Use | Five main contracts; MIT client/transport, 26 MCP fixtures; isolated native build, 278 serial tests, 182 notices; no backend staged | Focused backend review and positive capture/accessibility/input permission tests |
| Shared authority | Opt-in MIT transport; private Unix ownership; real CLI initialization and loaded-thread list; companion metadata-only snapshots; known-ASAR staging | Authenticated desktop factory and real nonempty-thread events |
| Remote/mobile | Two main contracts match; no remote flags/network exposure | Account entitlement, keychain, consent, pairing and revocation |
| Agent Workspace | Main bridge; pinned external v0.3.2 backend inspected; no skill/installer hook | 718-package/GPUI source closure review and explicit-permission controlled acceptance |

AppShots, Read Aloud and Wayland global dictation have candidate runtime adapters. All modules are disabled
by default. Experimental staging is local, explicitly gated and cannot be promoted
by the base release workflow. Example for a **fresh disposable** upstream tree:

```bash
cd tools/asar-builder
npm ci --ignore-scripts --no-fund
npm audit
cd ../..
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/lab-features.js experimental-stage \
  /tmp/YOUR_DISPOSABLE_APP packaging/profiles/experimental-capture-speech.json
node scripts/lab-features.js diagnose /tmp/YOUR_DISPOSABLE_APP
```

ASAR builder 4.3.0 is pinned with transitive integrity digests; MIT/BlueOak notices
remain in development dependencies. The local audit found no reported npm
vulnerabilities on 2026-09-12. This is not a security guarantee. Never use floating
npx or invoke an imported install hook. Third-party binary/model rights remain
separate from the wrapper's MIT license.

See [the portal helper procedure](../tools/global-dictation/README.md) for isolated
dependency audit/build and explicit candidate staging. No helper is automatically
compiled, downloaded, launched or installed by the base profile.

## Español

El puente de autoridad compartida es opt-in: valida socket privado, propiedad y
overrides; el CLI real aislado completa inicialización y listado en `/rpc`.
El companion añade snapshots acotados sin turnos, pero no demuestra aún
visibilidad de todas las tareas del desktop. Consulta
[el contrato y límites](../linux-features/shared-app-server-socket/README.md).

El perfil base preserva ASAR upstream. Voz, dictado nativo y funciones de
navegador/cuenta pertenecen al runtime oficial; empaquetarlo no concede privilegios
del servidor ni permiso de micrófono. Voz y dictado autenticados siguen NOT_RUN.

`codex-lab-tools features` abre el selector Qt/QPalette; `features-json` informa de
estado solicitado/instalado, rebuild e incompatibilidad. Guardar conserva
preferencias, sin instalar, reconstruir ni conceder permisos. Deshabilitar requiere
un build nuevo desde upstream verificado; no desparchea el runtime instalado.
`feature-profile-json` exporta sólo entradas de build, excluyendo ajustes
deshabilitados y preferencias privadas ajenas, sin modificar el archivo original.

AppShots, Read Aloud y dictado global Wayland tienen adaptador experimental y pruebas ASAR reales.
Captura/cancelación/inserción, renderer autenticado y reproducción audible siguen
pendientes. El helper Rust de dictado pasa pruebas de portales en un D-Bus privado,
pero faltan micrófono, permisos reales y dictado autenticado; X11 queda excluido.
Computer Use, remote/mobile y Agent Workspace pasan probes de contratos, pero
activarlos se rechaza antes de mutar: faltan helpers auditados y aceptación
controlada de permisos, cuenta, keychain o sandbox.
Computer Use incorpora además cliente/transporte MIT y 26 pruebas MCP, con destino
obligatorio y framing acotado; no acreditan captura ni entrada real.
No añaden hooks, exposición de red ni actividad deshabilitados.
Computer Use añade build nativo aislado, 278 pruebas en serie y 182 avisos Linux;
la prueba real rechaza capacidades ausentes, sin acreditar permisos positivos.
Agent Workspace fija e inspecciona el backend externo v0.3.2, pero su viewer GPUI
incondicional exige una cadena de 718 paquetes todavía no revisada.
Consulta [la evidencia de helpers](native-helper-review.md).

El ejemplo anterior solo admite un árbol desechable fresco. El builder ASAR está
fijado con hashes transitivos, sin ejecutar scripts npm. La auditoría local del
12-09-2026 no detectó vulnerabilidades npm reportadas; no garantiza seguridad.
No uses npx flotante ni hooks de instalación importados. Los derechos sobre
binarios/modelos son independientes de la licencia MIT del wrapper.

Consulta [el procedimiento del helper](../tools/global-dictation/README.md).
El perfil base no compila, descarga, ejecuta ni instala el helper automáticamente.
