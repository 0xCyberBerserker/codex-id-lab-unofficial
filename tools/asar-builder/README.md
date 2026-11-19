# Isolated ASAR development dependency

`@electron/asar` 4.3.2 is pinned in package.json and the transitive lock. It is a
development parser/builder only, not a base runtime dependency. Upstream source:
https://github.com/electron/asar/releases/tag/v4.3.2

This version requires patched `glob` and `minimatch`. Use
`npm ci --ignore-scripts --no-fund` and `npm audit --audit-level=low` as in CI.
Registry integrity pins are not an absolute security guarantee.
Keep dependency notices if distributing this tool; do not distribute node_modules
in runtime packages or automatically upgrade the lock.

## Español

Parser de desarrollo fijado, sin dependencia para el runtime base. Esta versión
requiere las versiones corregidas de `glob` y `minimatch`. Usa
`npm ci --ignore-scripts --no-fund` y `npm audit --audit-level=low`, como en CI.
Los hashes del registro no garantizan seguridad absoluta. Conserva los avisos si
distribuyes la herramienta; no empaquetes `node_modules` ni actualices el lock
automáticamente.
