# Local AppImage candidate

This is an actual type-2 ELF/SquashFS recipe, not a renamed archive. The runtime
is fixed to AppImage/type2-runtime commit `75849dce7cc37e4319b633df1f116ca895c71a12`,
SHA-256 `1cc49bcf1e2ccd593c379adb17c9f85a36d619088296504de95b1d06215aebbf`.
Its detached GPG signature is checked with the key fixed from that source commit,
primary fingerprint `570C77ACEA40C0F1B758902CBF96CCA56490F695`, in a private keyring.
The script does not download or execute the runtime during building/validation.

```bash
python3 scripts/build-appimage-candidate \
  --app-dir /tmp/VERIFIED_LOCAL_CANDIDATE \
  --runtime /tmp/PINNED_RUNTIME/runtime-x86_64 \
  --output /tmp/codex-id-lab-unofficial-26.908.40834-2-x86_64.local-candidate.AppImage
```

The `.sig` must sit beside the runtime. The AppDir must be `/tmp`, base profile and
local-candidate. Existing output is never overwritten. Validation parses SquashFS
and checks the complete upstream payload file set, bytes, symlinks and modes.
The AppRun keeps Chromium's sandbox and separates its user-data path by default.
Root desktop metadata omits unavailable package-manager/companion actions.

A tiny real AppImage fixture executes through the signed runtime's documented
extract-and-run mode in an isolated namespace, without network, personal home,
desktop bus or application data. This proves format/entrypoint execution, not
real Codex GUI, authenticated voice, FUSE mount or cross-distribution portability.
System shared libraries are not yet bundled into a portable dependency closure.
The base release workflow/updater does not publish or install this format.

Redistribution remains BLOCKED pending the statically linked runtime libraries'
license/source obligations (including libfuse LGPL), and real GUI/dependency
acceptance. The runtime's MIT notice is preserved; it does not cover those libraries.
See [upstream runtime](https://github.com/AppImage/type2-runtime) and
[type-2 architecture](https://docs.appimage.org/reference/architecture.html).

## Español

Receta real type-2 ELF/SquashFS, con runtime, SHA y clave GPG fijados al commit
anterior. Se verifica la firma en un keyring privado. El builder no descarga ni
ejecuta el runtime al construir o validar. Exige candidato `/tmp`, perfil base y
local-candidate; no sobrescribe salidas. Comprueba todo el payload con el parser
SquashFS: conjunto de archivos, bytes, enlaces y permisos.

AppRun conserva el sandbox Chromium y separa por defecto su ruta de datos. El
desktop embebido omite acciones no disponibles del paquete/companion. Un fixture
AppImage real ejecuta su entrypoint mediante extract-and-run aislado, sin red,
home personal, D-Bus del escritorio ni datos. No acredita la GUI Codex, voz
autenticada, montaje FUSE ni portabilidad entre distribuciones. Falta cerrar las
dependencias compartidas del sistema. El workflow/updater base no publica ni
instala este formato.

La redistribución queda BLOCKED por las obligaciones de licencia/código fuente de
las bibliotecas estáticas del runtime —incluida libfuse LGPL— y por aceptación
GUI/dependencias pendiente. Se conserva su aviso MIT, que no cubre esas bibliotecas.
