# Isolated ASAR development dependency

`@electron/asar` 4.3.0 is fixed in package.json and the transitive lock. It is a
development parser/builder only, not a base runtime dependency. Upstream source:
https://github.com/electron/asar/releases/tag/v4.3.0

Before use, package scripts and MIT/BlueOak notices were inspected. The
2026-09-12 npm audit returned zero reported vulnerabilities across eight
dependencies. Only `npm ci --ignore-scripts --no-fund` was used in this isolated
worktree. Registry integrity pins are not an absolute security guarantee.
Keep dependency notices if distributing this tool; do not distribute node_modules
in runtime packages or automatically upgrade the lock.

## Español

Parser/builder de desarrollo fijado, sin dependencia para el runtime base.
Se inspeccionaron scripts y avisos MIT/BlueOak; npm audit del 12-09-2026 no reportó
vulnerabilidades en ocho dependencias. La instalación fue aislada y sin ejecutar
scripts. Los hashes del registro no garantizan seguridad absoluta. Conserva avisos
si distribuyes el tool; no empaquetes node_modules ni actualices el lock automáticamente.
