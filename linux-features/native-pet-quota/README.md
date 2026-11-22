# Experimental native pets

This prerelease is a verified **source setup bundle**, not a stable package or
an automatic update. Start with the installed Codex Lab 26.1117.41037-8 and
verify the downloaded archive against its published checksum and provenance.
Prepare a fresh copy in `/tmp`; do not point the setup at the installed app.

The `experimental-native-pets` profile enables the quota panel by default
on the reviewed upstream ASAR. This is a disposable build profile, not the
default release profile. The standard package still preserves the official
runtime byte-for-byte. The panel reads the same in-memory native usage query
as Codex and does not open a sidecar, copy credentials or cache quota data.

```bash
npm --prefix tools/asar-builder ci --ignore-scripts --no-fund
npm --prefix tools/asar-builder audit --audit-level=low
candidate=$(mktemp -d /tmp/codex-native-pets.XXXXXX)
cp -a /opt/codex-id-lab-unofficial/. "$candidate/"
profile="${XDG_DATA_HOME:-$HOME/.local/share}/codex-lab-native-pets"
electron_profile="$profile/electron"
install -d -m 700 "$profile/codex" "$electron_profile"
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/install-experimental-native-pets.mjs \
  --candidate "$candidate" --profile "$profile/codex"
CODEX_HOME="$profile/codex" CODEX_ELECTRON_USER_DATA_PATH="$electron_profile" \
  "$candidate/ChatGPT"
```

Run this as the desktop user. The installer needs the pinned ASAR development
dependency, a C++17 compiler, `pkg-config`, Qt 6 Gui with WebP support and
Python 3. It verifies the original ASAR digest, generates Pirate Null from the
local built-in sprite and places it in the selected profile. It never
selects the custom entry or replaces Null Signal. Use a fresh candidate and
a profile without an existing `null-signal-pirate` entry.

Launch the prepared copy with that profile after setup and pick Pirate Null in
Settings → Pets. Do not run two Desktop processes on the same profile.

From the repository checkout, `--first-launch` may replace `--profile` at
setup. Run the prepared candidate's `bin/codex-lab-native-pets` with
`CODEX_HOME` set to an existing disposable profile to create the entry on
first launch. To use a PNG cleared for packaging rather than Qt generation,
add `--atlas /path/to/pet.png` to the setup command. In both cases an existing
entry is left untouched.

The packaging candidate is separate from the stable update channel. Build it
with `CODEX_LAB_BUILD_PROFILE=local-candidate CODEX_LAB_NATIVE_PETS_CANDIDATE=1`
and the pinned source package. It carries the native generator, not the PNG.
The launch hook uses Python 3 and the generator needs Qt 6 Gui and its WebP
plugin. The stable release validator still rejects this experimental profile.

For packaging review, verify a candidate against the untouched, pinned source
with `node scripts/verify-native-pets-asar.mjs UPSTREAM CANDIDATE`. It checks
that only the reviewed renderer patch changed. This check is not a stable
package or an updater migration.

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

Esta prerelease es un **paquete de preparación desde código**, no un paquete
estable ni una actualización automática. Parte de Codex Lab 26.1117.41037-8,
verifica la suma y la procedencia del archivo descargado y prepara una copia
nueva en `/tmp`. No apuntes el instalador a la app instalada.

El perfil `experimental-native-pets` activa el consumo por defecto en el
ASAR revisado. Solo se aplica a copias desechables; el paquete normal
conserva el runtime oficial byte a byte. El panel reutiliza la consulta
nativa de Codex en memoria. No inicia otro proceso, copia credenciales ni
guarda el consumo.

```bash
npm --prefix tools/asar-builder ci --ignore-scripts --no-fund
npm --prefix tools/asar-builder audit --audit-level=low
candidate=$(mktemp -d /tmp/codex-native-pets.XXXXXX)
cp -a /opt/codex-id-lab-unofficial/. "$candidate/"
profile="${XDG_DATA_HOME:-$HOME/.local/share}/codex-lab-native-pets"
electron_profile="$profile/electron"
install -d -m 700 "$profile/codex" "$electron_profile"
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/install-experimental-native-pets.mjs \
  --candidate "$candidate" --profile "$profile/codex"
CODEX_HOME="$profile/codex" CODEX_ELECTRON_USER_DATA_PATH="$electron_profile" \
  "$candidate/ChatGPT"
```

Ejecuta el instalador como usuario del escritorio. Necesita la dependencia
ASAR fijada, un compilador C++17, `pkg-config`, Qt 6 Gui con WebP y
Python 3. Comprueba el hash del ASAR original, genera el PNG del pirata a
partir del sprite local y lo guarda en el perfil elegido. No selecciona la
mascota personalizada ni sustituye a Null Signal. Usa una copia nueva y
un perfil sin una entrada `null-signal-pirate` previa.

Después, abre la copia con el perfil indicado y elige Pirate Null en Ajustes
→ Mascotas. No abras dos procesos de Desktop con el mismo perfil.

Desde el repositorio, puedes usar `--first-launch` en lugar de `--profile`
al preparar la copia. Ejecuta su `bin/codex-lab-native-pets` con
`CODEX_HOME` apuntando a un perfil desechable existente para crear la
mascota al primer arranque. Para usar un PNG autorizado en vez de generarlo
con Qt, añade `--atlas /ruta/al/sprite.png`. Las entradas existentes no
se sobrescriben.

El candidato empaquetado va separado del actualizador estable. Compílalo
con `CODEX_LAB_BUILD_PROFILE=local-candidate CODEX_LAB_NATIVE_PETS_CANDIDATE=1`
y el paquete fuente fijado. Incluye el generador, no el PNG. El lanzador usa
Python 3 y el generador necesita Qt 6 Gui con el plugin WebP. El validador de
releases estables sigue rechazando este perfil experimental.

Para revisar el empaquetado, compara un candidato con el ASAR original
mediante `node scripts/verify-native-pets-asar.mjs ORIGINAL CANDIDATO` desde
el repositorio. Comprueba que solo cambió el parche revisado del flotante.
No genera un paquete estable ni migra el actualizador.

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
