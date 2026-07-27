# Research: Interfaz Gráfica del Juego Tres en Raya

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Decisión 1: Orquestación de turnos de agente sin lógica de reglas

- **Decision**: Tras cada respuesta del motor (`GameState`), la interfaz
  inspecciona únicamente `turn` y la configuración local (¿es agente o
  humano quien controla esa ficha?) para decidir si debe: (a) esperar
  entrada del usuario, o (b) llamar automáticamente a
  `POST /api/agents/{level}/move` y reenviar la `Jugada` resultante a
  `POST /api/games/{game_id}/moves`. Ninguna de estas decisiones evalúa
  reglas del juego (victoria, legalidad): solo lee campos ya resueltos por
  el backend.
- **Rationale**: Satisface la exigencia explícita del usuario ("la interfaz
  solo debe consumir la API; no debe tener lógica de reglas de juego") sin
  perder la experiencia de "modo Humano vs Agente": secuenciar llamadas HTTP
  no es lógica de negocio, es orquestación de presentación.
- **Alternatives considered**: Un endpoint de backend que orqueste
  automáticamente motor+agente en una sola llamada (mezclaría las
  responsabilidades separadas de las specs 001 y 002 en un tercer
  componente no especificado; se descarta para mantener el acoplamiento
  mínimo ya decidido en `002-agentes-de-juego/research.md` Decisión 5).

## Decisión 2: Navegación e interacción por teclado (CA-I-16 a CA-I-18)

- **Decision**: Las 9 casillas del tablero se implementan como una única
  parada de tabulación (`tabindex="0"` en el tablero) con navegación interna
  por flechas de dirección (patrón ARIA "grid"/"roving tabindex"): el foco
  se mueve entre casillas con las flechas y se envuelve dentro de los
  límites del tablero (no sale de la cuadrícula 3x3, ver Edge Cases de
  `spec.md`); Enter o Espacio confirman la jugada sobre la casilla enfocada.
  El resto de controles (Configuración, botón de reinicio) son elementos
  nativos (`select`, `button`, `input[type=radio]`) que ya son
  accesibles por teclado por defecto en HTML.
- **Rationale**: Reutilizar elementos HTML nativos donde sea posible
  minimiza el código de accesibilidad a mano (menos superficie de bugs); el
  patrón "roving tabindex" es el estándar documentado para grids
  interactivos y resuelve directamente CA-I-16 a CA-I-18 sin dependencias
  externas.
- **Alternatives considered**: Hacer cada casilla un elemento tabulable por
  separado (`tabindex="0"` en las 9) — funcionalmente válido pero obliga a
  9 pulsaciones de Tab para atravesar el tablero, peor experiencia que
  navegar con flechas dentro de una única parada de tabulación.

## Decisión 3: Servido del frontend sin build step

- **Decision**: `frontend/` son archivos estáticos servidos directamente
  (HTML/CSS/JS sin transpilar) montados por FastAPI (`StaticFiles`) en la
  misma app que expone `/api/games` y `/api/agents`. No hay paso de
  compilación ni empaquetado.
- **Rationale**: Cumple el Principio I (sin frameworks de UI) de la forma
  más directa; servir desde el mismo proceso evita configurar CORS para el
  desarrollo local del curso.
- **Alternatives considered**: Servidor de desarrollo aparte (p. ej.
  `http-server` en otro puerto) — añade una pieza móvil adicional (CORS,
  dos procesos que levantar) sin beneficio para el alcance de esta spec.

## Decisión 4: Verificación automatizada de la interfaz con Pytest

- **Decision**: Dado que la constitución exige Pytest como único framework
  de pruebas (sin permitir un framework de testing JS dedicado), los CA-I-*
  críticos que requieren interacción real de navegador (resaltado de línea
  ganadora, bloqueo de tablero, navegación por teclado) se verifican con
  Pytest orquestando un navegador controlado (p. ej. Playwright para
  Python) contra el `frontend/` servido localmente. Los aspectos puramente
  visuales/estéticos (color exacto, disposición) se validan manualmente
  siguiendo `quickstart.md`, tal como indican las guías del proyecto para
  cambios de UI.
- **Rationale**: Mantiene el gate de "cada CA-* tiene al menos un test
  automatizado" (Principio III) sin introducir un segundo framework de
  pruebas no autorizado por la constitución (Principio I).
- **Alternatives considered**: Tests unitarios de funciones JS aisladas con
  un framework tipo Jest/Vitest — quedaría fuera del "Pytest como único
  framework de pruebas" fijado por la constitución; se descarta.

## Decisión 5: Representación del marcador de sesión

- **Decision**: El marcador (`{ victoriasX: int, victoriasO: int, empates:
  int }`) vive como una variable de módulo en `frontend/js/state.js`,
  incrementada localmente cuando la interfaz observa `status: "victoria"` o
  `status: "empate"` en un `GameState`. Se reinicia únicamente al recargar
  la página completa (no hay persistencia entre sesiones, ver Assumptions
  de `spec.md`).
- **Rationale**: Es un dato puramente de presentación de sesión, sin
  relación con las reglas del juego; mantenerlo en el backend obligaría a
  introducir un concepto de "sesión" ajeno al motor y a los agentes,
  ampliando su alcance sin necesidad.
- **Alternatives considered**: Persistir el marcador en el backend
  asociado a un identificador de sesión — sobre-ingeniería para un
  requisito explícitamente volátil y de un solo cliente (curso, sin
  multiusuario concurrente sobre el mismo marcador).
