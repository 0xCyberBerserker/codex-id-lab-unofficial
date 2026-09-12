# Read Aloud (experimental)

The assistant-response button and webview bridge are selectively reused under MIT
from ilysenko/codex-desktop-linux at `249cd4b64d42434f51417fec4a318750d461b676`.
The host adapter is local code: it starts an already installed `espeak-ng`, sends
text through stdin and stops only its own player. No installer, pip command,
model download or paid API is included. Playback is an explicit button action.

The base profile has no speech dependency. Experimental staging requires an
explicit profile, known ASAR digest and `CODEX_LAB_EXPERIMENTAL_CANDIDATE=1`.
Activation/deactivation, patch drift, stdin and stop are fixture-tested.
Audible playback and the authenticated renderer roundtrip remain NOT_RUN.

## Español

Botón y puente webview reutilizados selectivamente bajo MIT del commit indicado.
El adaptador local arranca `espeak-ng` ya instalado, envía el texto por stdin y
detiene exclusivamente su reproductor. No incluye instalaciones, pip, descarga
de modelos ni APIs de pago. La reproducción exige una acción explícita.

El perfil base no depende de voz. El staging experimental requiere perfil
explícito, hash ASAR conocido y `CODEX_LAB_EXPERIMENTAL_CANDIDATE=1`.
Activación/desactivación, drift, stdin y parada se prueban con fixtures.
La reproducción audible y el recorrido del renderer autenticado siguen NOT_RUN.
