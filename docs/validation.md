# Validation boundaries

Run locally:

```bash
python3 -m unittest discover -s tests -v
node --test scripts/lib/linux-features.test.js tests/lab-features.test.js tests/runtime-features.test.js tests/global-dictation.test.js linux-features/computer-use-linux/native.test.js
scripts/privacy-audit
git diff --check
```

Push/PR CI has read-only repository permissions and never publishes. Package fixtures exercise the real Arch, Debian and RPM parsers, metadata, dependency declarations, executable modes, launcher symlinks, desktop entries and unchanged upstream files. Arbitrary bytes with a valid package filename are rejected.

Disposable package-manager tests install and update a tiny known fixture from revision 2 to 3. Debian uses an isolated root/database; RPM and Arch use an isolated root inside a user namespace where available. Fixture dependencies/signatures/scripts are intentionally bypassed in these tests only. Production downloads still require the approved GitHub builder attestation, authenticated manifest and matching artifact digests.

The fixture launcher smoke is not an official-runtime startup, authenticated session, microphone, voice, dictation or desktop-control acceptance test. Missing managers or user-namespace support produce explicit skips. Real runtime/desktop and live GitHub signing gates remain separate.

`scripts/smoke-linux-candidate /tmp/FRESH_CANDIDATE` separately starts the real native client in bubblewrap with an anonymous profile, no access to network, home or personal desktop, and software X11 (GLX disabled, Chromium sandbox retained). Its PASS means a visible window survived 20 seconds, not that the application loaded. The measured screenshot shows the initial OpenAI splash only; loaded/authenticated UI remains NOT_RUN. An optional existing private `/tmp` directory in `CODEX_LAB_SMOKE_EVIDENCE_DIR` receives only the isolated display capture. Computer Use transport tests similarly prove MCP framing/target binding, not native desktop permissions.

The imported framework tests remain MIT-licensed. The Lab integration test exercises selection → staging → candidate archive → integrity diagnosis → disabling, with unchanged baseline ASAR and explicit unknown-ID/conflict/drift failures. The base slice accepts resources only. Explicit local candidates additionally accept the fixed AppShots/Read Aloud/Wayland dictation adapters; ASAR roundtrips preserve unrelated source bytes and metadata. Native portal tests use a private D-Bus, not the personal desktop. The [AppImage fixture](appimage.md) uses a real signed type-2 runtime and parser, without claiming real GUI acceptance.

---

# Límites de validación

Ejecuta localmente los comandos anteriores. CI de push/PR sólo tiene lectura y no publica. Los fixtures ejercitan parsers reales de Arch, Debian y RPM, metadatos, dependencias declaradas, permisos ejecutables, enlaces, entradas de escritorio y conservación de archivos upstream. Un fichero arbitrario con un nombre de paquete válido se rechaza.

Las pruebas desechables instalan y actualizan un fixture conocido de revisión 2 a 3. Debian usa root y base de datos aislados; RPM y Arch añaden un namespace de usuario cuando está disponible. Sólo estos fixtures omiten dependencias, firma y scripts. Las descargas de producción siguen exigiendo attestation del builder aprobado, manifiesto autenticado y hashes concordantes.

El smoke del launcher fixture no demuestra arranque del runtime oficial, sesión autenticada, micrófono, voz, dictado ni control del escritorio. La ausencia de gestores o namespaces produce skips explícitos. Los gates runtime/desktop y de firma GitHub en vivo se registran por separado.

El smoke nativo separado ejecuta el cliente real con perfil anónimo y X11 software, sin red, home ni escritorio personal; deshabilita GLX, no el sandbox Chromium. PASS significa ventana visible durante 20 segundos, no aplicación cargada. La captura medida sólo muestra la pantalla inicial de OpenAI; GUI cargada/autenticada sigue NOT_RUN. El directorio opcional de evidencias sólo recibe la captura del display aislado. Las pruebas MCP de Computer Use tampoco demuestran permisos de control nativo.

Los tests importados conservan MIT. La integración propia prueba selección → staging → archivo candidato → diagnóstico de integridad → desactivación, con ASAR intacto y errores explícitos para ID desconocido, conflicto o drift. El perfil base sólo acepta recursos. Los candidatos locales explícitos admiten adaptadores fijados de AppShots/Read Aloud/dictado Wayland, preservando bytes y metadata no modificados. Los tests de portales usan un D-Bus privado, no el escritorio personal. El fixture AppImage utiliza runtime firmado y parser reales, sin acreditar aceptación de la GUI Codex.
