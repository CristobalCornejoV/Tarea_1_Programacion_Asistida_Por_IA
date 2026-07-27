# Research: Agentes de Juego

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Decisión 1: Cómo el agente Medio usa "memoria de la partida en curso"

- **Decision**: El agente Medio se implementa como una función pura
  `decidir_jugada(estado: GameState) -> Jugada` que **no** requiere estado
  persistido entre llamadas: la evaluación "¿tengo una jugada ganadora?" y
  "¿el rival puede ganar en su próximo turno?" es completamente derivable del
  `board` recibido en cada llamada. La "memoria de la partida en curso" que
  describe la spec (CA-A-06) se satisface porque el backend siempre envía el
  `GameState` completo y actualizado de la partida en cada solicitud; el
  agente no necesita guardar nada entre turnos.
- **Rationale**: Preserva el Principio II (funciones puras/sin estado
  oculto) de la constitución sin sacrificar el comportamiento especificado:
  el resultado es idéntico a si el agente "recordara" la partida, porque el
  tablero recibido ya refleja todo lo relevante del historial.
- **Alternatives considered**: Mantener un objeto de sesión por partida en el
  backend con el historial de jugadas (más estado para gestionar, mayor
  riesgo de desincronización con el `GameState` real del motor, sin beneficio
  funcional ya que el tablero actual es suficiente).

## Decisión 2: Algoritmo del agente Complejo

- **Decision**: Minimax con poda alfa-beta sobre el espacio de estados de la
  modalidad clásica. El espacio de un tablero 3x3 clásico tiene como máximo
  9! ≈ 362,880 secuencias (mucho menor con poda y simetrías), por lo que un
  cálculo completo desde cero SHALL resolverse muy por debajo de 1 segundo
  incluso sin memoización; la memoización (Decisión 3) es una optimización
  adicional, no un requisito para cumplir CA-A-10/SC-004.
- **Rationale**: Minimax con poda alfa-beta es el enfoque estándar y
  demostrablemente óptimo para tres en raya clásico, y es el mecanismo más
  simple que garantiza matemáticamente CA-A-07/CA-A-08 (nunca perder).
- **Alternatives considered**: Tablas de apertura precalculadas a mano (frágil
  y difícil de verificar exhaustivamente); Monte Carlo Tree Search (MCTS)
  (innecesariamente probabilístico para un juego con espacio de estados tan
  pequeño que admite solución exacta).

## Decisión 3: Memoria persistente entre partidas del agente Complejo

- **Decision**: Un diccionario en memoria de proceso
  `memo: dict[str, ResultadoEvaluado]`, con clave la representación canónica
  del tablero + turno, poblado incrementalmente por cada llamada a minimax y
  reutilizado en llamadas futuras (incluso de partidas distintas) mientras el
  proceso backend siga vivo.
- **Rationale**: Cumple literalmente CA-A-09 ("memoria persistente entre
  partidas... reutilizar resultados memorizados") sin introducir
  dependencias externas (base de datos, archivo); al ser una función
  determinista de `(board, turno) -> resultado`, la memoización no cambia el
  resultado observable, solo evita recomputar — compatible con el Principio
  II.
- **Alternatives considered**: Persistir la memoización en disco (JSON o
  SQLite) para sobrevivir a reinicios del servidor — fuera de alcance de esta
  spec, que no exige persistencia entre *procesos*, solo entre *partidas*
  dentro del mismo proceso (ver Assumptions de `spec.md`).

## Decisión 4: Modalidad continua y el agente Complejo

- **Decision**: Las garantías de optimalidad (CA-A-07, CA-A-08, SC-002,
  SC-005) se acotan explícitamente a la modalidad clásica, tal como ya
  documentan las Assumptions de `spec.md`. En modalidad continua, el agente
  Complejo reutiliza el mismo mecanismo de minimax con poda, pero sin
  garantía formal de invencibilidad (el espacio de estados con fase de
  movimiento y repetición de posiciones es más complejo y no forma parte del
  criterio estadístico obligatorio).
- **Rationale**: Evita prometer una garantía no solicitada ni verificada por
  la especificación; mantiene el alcance de esta fase de diseño ceñido a lo
  que CA-A-07 realmente exige.
- **Alternatives considered**: Extender minimax a modalidad continua con
  profundidad acotada y detección de ciclos para garantizar también
  invencibilidad ahí — de mayor complejidad y no requerido por ningún CA-A-*;
  queda como posible mejora futura fuera de esta spec.

## Decisión 5: Endpoint de agentes independiente del motor

- **Decision**: `POST /api/agents/{level}/move` recibe el estado necesario
  para decidir (no el `game_id`) y responde una `Jugada` con el mismo
  esquema que `POST /api/games/{game_id}/moves` del motor (spec 001), de
  forma que el frontend pueda reenviarla sin transformación.
- **Rationale**: El agente no necesita ni debe conocer la existencia de
  partidas persistidas en el motor (Principio II: función pura, sin
  dependencia de almacenamiento ajeno); recibir el estado explícitamente en
  el cuerpo de la petición hace el contrato autocontenido y fácil de testear
  con Pytest sin necesidad de crear una partida real.
- **Alternatives considered**: `POST /api/games/{game_id}/agent-move`
  (acoplaría el router de agentes al almacenamiento de partidas del motor,
  violando la separación de responsabilidades exigida por el Principio II).
