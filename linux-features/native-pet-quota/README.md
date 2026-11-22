# Native Pet Quota / Consumo de la mascota

Revision `26.1117.41037-9` adds Codex's native usage and reset times to the
existing pet overlay. It uses the signed-in account's existing read-only
query, without a sidecar or persisted quota data. The panel is independent of
the selected pet. No custom artwork, generator or startup hook is packaged.

The base profile and its hash remain unchanged for the `-8` updater. The
additive manifest entry is `runtimeExtensions.nativePetQuota = "native-query-v1"`.
The release workflow's `stage_quota_rev9` input stages an attested draft from
`main` without promoting it. Before promotion, check the isolated upgrade,
clean-profile startup and authenticated usage/reset display. Anonymous tests
do not establish authenticated quota behavior.

To check that only the reviewed renderer code changed:

```bash
node scripts/verify-native-pets-asar.mjs UPSTREAM_ASAR CANDIDATE_ASAR
```

Optional: import a private sprite sheet into an existing local Codex profile.
This neither uploads nor selects the pet.

```bash
/opt/codex-id-lab-unofficial/bin/codex-lab-pet-import \
  --profile /absolute/path/to/profile --id my-pet --name "My Pet" /absolute/path/to/atlas.png
```

## Español

La revisión `26.1117.41037-9` añade el consumo y los reinicios de Codex al
flotante de la mascota existente. Usa la consulta nativa de solo lectura de
la cuenta con sesión iniciada, sin procesos auxiliares ni datos de consumo
persistidos. El panel no depende de la mascota seleccionada. No se distribuye
arte personalizado, generadores ni tareas de primer arranque.

El perfil base y su hash no cambian para el actualizador del `-8`. La
extensión se declara como `runtimeExtensions.nativePetQuota = "native-query-v1"`.
La opción `stage_quota_rev9` del workflow prepara un borrador con attestations
desde `main` sin promocionarlo. Antes de publicar, comprueba la actualización
aislada, el inicio con un perfil limpio y el consumo con sesión iniciada.
Una prueba anónima no acredita el consumo real.

El verificador ASAR comprueba que solo cambió el renderer revisado. El
importador opcional permite añadir un atlas propio a un perfil local existente:
no sube ni selecciona la mascota.
