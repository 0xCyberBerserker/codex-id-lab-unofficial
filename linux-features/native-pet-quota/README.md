# Experimental native pets

The `experimental-native-pets` profile enables the quota panel by default
on the reviewed upstream ASAR. This is a disposable build profile, not the
default release profile. The standard package still preserves the official
runtime byte-for-byte. The panel reads the same in-memory native usage query
as Codex and does not open a sidecar, copy credentials or cache quota data.

```bash
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/install-experimental-native-pets.mjs \
  --candidate /tmp/disposable-codex --profile /path/to/existing/test-profile
```

Run this as the desktop user. The installer needs the pinned ASAR development
dependency, a C++17 compiler, `pkg-config`, Qt 6 Gui with WebP support and
Python 3. It verifies the original ASAR digest, generates Null Pirate from the
local built-in sprite and places it in the selected profile. It never
selects the custom entry or replaces Null Signal. Use a fresh candidate and
a profile without an existing `null-signal-pirate` entry.

Select an existing local Codex profile and a PNG you are allowed to use. The
installed import command adds a separate `custom:` entry without selecting
it, replacing a built-in pet, or contacting a service:

```bash
/opt/codex-id-lab-unofficial/bin/codex-lab-pet-import \
  --profile "$CODEX_HOME" --id my-pet --name "My pet" /path/to/sprite.png
```

Reopen Settings → Pets to select it. Atlas format: 1536 × 1872 (v1) or
1536 × 2288 (v2), maximum 20 MiB. No atlas is bundled. Ordinary mouse gaze
and mixed-monitor drag are not accepted yet.

## Español

El perfil `experimental-native-pets` activa el consumo por defecto en el
ASAR revisado. Solo se aplica a copias desechables; el paquete normal
conserva el runtime oficial byte a byte. El panel reutiliza la consulta
nativa de Codex en memoria. No inicia otro proceso, copia credenciales ni
guarda el consumo.

```bash
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/install-experimental-native-pets.mjs \
  --candidate /tmp/disposable-codex --profile /ruta/al/perfil-de-prueba
```

Ejecuta el instalador como usuario del escritorio. Necesita la dependencia
ASAR fijada, un compilador C++17, `pkg-config`, Qt 6 Gui con WebP y
Python 3. Comprueba el hash del ASAR original, genera el PNG del pirata a
partir del sprite local y lo guarda en el perfil elegido. No selecciona la
mascota personalizada ni sustituye a Null Signal. Usa una copia nueva y
un perfil sin una entrada `null-signal-pirate` previa.

El importador instalado añade un PNG local como entrada `custom:` aparte,
sin seleccionarla, reemplazar una mascota integrada ni contactar un servicio.
Usa un perfil existente y un PNG cuyo uso esté autorizado:

```bash
/opt/codex-id-lab-unofficial/bin/codex-lab-pet-import \
  --profile "$CODEX_HOME" --id mi-mascota --name "Mi mascota" /ruta/al/sprite.png
```

Vuelve a abrir Ajustes → Mascotas para seleccionarla. Formatos: 1536 × 1872
(v1) o 1536 × 2288 (v2), máximo 20 MiB. No se incluye ningún atlas. La mirada
con ratón normal y el arrastre entre monitores distintos siguen pendientes
de aceptación.
