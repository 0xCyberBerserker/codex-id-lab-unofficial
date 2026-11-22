# Experimental native pets

The `experimental-native-pets` profile enables the quota panel by default
on the reviewed upstream ASAR. This is a disposable build profile, not the
default release profile. The standard package still preserves the official
runtime byte-for-byte. The panel reads the same in-memory native usage query
as Codex and does not open a sidecar, copy credentials or cache quota data.

```bash
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/lab-features.js experimental-stage \
  /tmp/disposable-codex packaging/profiles/experimental-native-pets.json
```

Select an existing local Codex profile and a PNG you are allowed to use. The
installed import command adds a separate `custom:` entry without selecting
it, replacing a built-in pet, or contacting a service:

```bash
/opt/codex-id-lab-unofficial/bin/codex-lab-pet-import \
  --profile "$CODEX_HOME" --id my-pet --name "My pet" /path/to/sprite.png
```

Reopen Settings → Pets to select it. Atlas format: 1536 × 1872 (v1) or
1536 × 2288 (v2), maximum 20 MiB. No atlas is bundled. A preinstalled custom
pet needs artwork cleared for redistribution before release. Ordinary mouse
gaze and mixed-monitor drag are not accepted yet.

## Español

El perfil `experimental-native-pets` activa el consumo por defecto en el
ASAR revisado. Solo se aplica a copias desechables; el paquete normal
conserva el runtime oficial byte a byte. El panel reutiliza la consulta
nativa de Codex en memoria. No inicia otro proceso, copia credenciales ni
guarda el consumo.

```bash
CODEX_LAB_EXPERIMENTAL_CANDIDATE=1 node scripts/lab-features.js experimental-stage \
  /tmp/disposable-codex packaging/profiles/experimental-native-pets.json
```

El importador instalado añade un PNG local como entrada `custom:` aparte,
sin seleccionarla, reemplazar una mascota integrada ni contactar un servicio.
Usa un perfil existente y un PNG cuyo uso esté autorizado:

```bash
/opt/codex-id-lab-unofficial/bin/codex-lab-pet-import \
  --profile "$CODEX_HOME" --id mi-mascota --name "Mi mascota" /ruta/al/sprite.png
```

Vuelve a abrir Ajustes → Mascotas para seleccionarla. Formatos: 1536 × 1872
(v1) o 1536 × 2288 (v2), máximo 20 MiB. No se incluye ningún atlas. Para
preinstalar una mascota personalizada hace falta verificar que su arte se
puede redistribuir. La mirada con ratón normal y el arrastre entre monitores
distintos siguen pendientes de aceptación.
