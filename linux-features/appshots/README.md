# AppShots (experimental)

Selective MIT reuse from ilysenko/codex-desktop-linux at
`249cd4b64d42434f51417fec4a318750d461b676`. The composer availability and capture
patches are reused; the global-hotkey descriptor and keyboard monitor are not staged.
The empty base profile remains unchanged. No capture runs while disabled.

Only the pinned ASAR hash in `feature.json` is accepted. The adapter verifies each
patch contract and preserves unrelated ASAR content and metadata. A compatible
patch is not proof of capture permission, cancellation or authenticated insertion.
Those gates remain NOT_RUN; this module cannot be promoted as stable.

Requires the official Linux Computer Use backend already installed and desktop
capture permission. No backend, models or permissions are installed automatically.
Captured pixels may temporarily cover a full output before cropping; accessibility
text is sensitive. Do not enable on a personal desktop to approve a fixture test.

## Español

Reutilización selectiva MIT del commit indicado. Se conservan los parches del
composer y de captura, pero no el descriptor de hotkey ni el monitor del teclado.
Deshabilitado, no captura nada. El perfil base no cambia.

Solo se admite el hash ASAR declarado. El adaptador comprueba contratos y preserva
contenido y metadatos ajenos. Permisos, cancelación e inserción autenticada siguen
NOT_RUN: compatibilidad del parche no demuestra funcionamiento completo.

Requiere el backend oficial Linux Computer Use previamente instalado y permiso
de captura. No instala nada automáticamente. Puede capturar temporalmente una
salida completa antes de recortarla; el texto de accesibilidad también es sensible.
