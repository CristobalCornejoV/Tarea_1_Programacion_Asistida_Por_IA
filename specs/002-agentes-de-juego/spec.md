# Feature Specification: Agentes de Juego

**Feature Branch**: `002-agentes-de-juego`

**Created**: 2026-07-26

**Status**: Complete

**Input**: User description: "Agentes de juego. Existen 3 niveles distinguibles: Sencillo (jugada legal al azar, sin memoria), Medio (memoria de la partida en curso, heurística ganar/bloquear/azar), Complejo (juego óptimo, nunca pierde en modalidad clásica, memoria persistente entre partidas). Incluir criterio estadístico CA-A-07: Sencillo vs Complejo, 100 partidas, el Complejo no pierde ninguna. Sin detalles de motor ni de interfaz."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agente Sencillo (Priority: P1)

Un jugador enfrenta a un agente de nivel Sencillo, que en cada uno de sus
turnos elige al azar una casilla legal del tablero, sin considerar el
historial de la partida.

**Why this priority**: Es el agente más simple y la base mínima para que el
juego pueda jugarse contra la máquina en cualquier modalidad; los niveles
Medio y Complejo se comparan y validan contra este agente.

**Independent Test**: Se puede probar por completo solicitando repetidamente
una jugada al agente Sencillo sobre distintos estados de tablero y
verificando que toda jugada devuelta es legal y que, sobre un número grande de
repeticiones, la distribución de casillas elegidas cubre todas las opciones
legales disponibles.

**Acceptance Scenarios** (notación EARS):

- **CA-A-01**: EL agente Sencillo SHALL seleccionar su jugada únicamente entre
  las casillas legales disponibles en el estado de tablero actual.
- **CA-A-02**: CUANDO el agente Sencillo debe jugar, EL agente SHALL elegir la
  casilla mediante selección aleatoria uniforme entre las casillas legales, sin
  utilizar ninguna información de turnos anteriores de la misma partida.

---

### User Story 2 - Agente Medio (Priority: P2)

Un jugador enfrenta a un agente de nivel Medio, que recuerda el desarrollo de
la partida en curso y en cada turno intenta primero ganar, luego bloquear una
victoria inminente del rival, y solo si ninguna de esas condiciones aplica,
juega una casilla legal al azar.

**Why this priority**: Introduce comportamiento estratégico básico y depende
de que exista ya un agente de referencia (Sencillo) contra el cual contrastar
su comportamiento; se ordena antes del agente Complejo por ser una heurística
más simple de verificar.

**Independent Test**: Se puede probar por completo colocando el tablero en
estados donde exista una jugada ganadora propia, estados donde exista una
amenaza de victoria del rival sin jugada ganadora propia, y estados sin
ninguna de las dos condiciones, verificando en cada caso la jugada elegida por
el agente Medio.

**Acceptance Scenarios** (notación EARS):

- **CA-A-03**: CUANDO el agente Medio debe jugar y existe al menos una
  casilla legal que le otorga la victoria inmediata, EL agente SHALL jugar en
  esa casilla.
- **CA-A-04**: SI el agente Medio no tiene ninguna jugada ganadora inmediata Y
  el rival cuenta con una casilla legal que le otorgaría la victoria en su
  próximo turno, ENTONCES EL agente Medio SHALL jugar en esa casilla para
  bloquear al rival.
- **CA-A-05**: SI el agente Medio no tiene jugada ganadora inmediata ni
  necesita bloquear una amenaza de victoria del rival, ENTONCES EL agente
  SHALL elegir una casilla legal mediante selección aleatoria uniforme.
- **CA-A-06**: MIENTRAS dure la partida en curso, EL agente Medio SHALL
  mantener memoria de las jugadas ya realizadas en esa partida, de forma que
  su evaluación de jugada ganadora propia y de amenaza de victoria del rival
  en cada turno sea consistente con el historial completo de esa partida.

---

### User Story 3 - Agente Complejo (Priority: P3)

Un jugador enfrenta a un agente de nivel Complejo, que juega de forma óptima
en modalidad clásica —de modo que nunca pierde una partida— y que conserva
memoria persistente entre partidas para reutilizar resultados ya calculados de
posiciones de tablero conocidas.

**Why this priority**: Es el nivel más exigente y depende de que exista ya el
agente Sencillo para poder validarse estadísticamente contra él (CA-A-07); se
implementa al final por ser el de mayor complejidad de verificación.

**Independent Test**: Se puede probar por completo (a) verificando, sobre
todos los estados de tablero alcanzables en modalidad clásica, que la jugada
elegida por el agente Complejo nunca permite una victoria del rival cuando
existía una alternativa que la evitaba, y (b) enfrentando al agente Complejo
contra el agente Sencillo durante 100 partidas completas y verificando que el
Complejo no pierde ninguna (CA-A-07).

**Acceptance Scenarios** (notación EARS):

- **CA-A-07** *(criterio estadístico obligatorio)*: CUANDO el agente Sencillo
  y el agente Complejo disputan 100 partidas completas en modalidad clásica
  (alternando cuál de los dos agentes inicia como X), EL agente Complejo
  SHALL no perder ninguna de esas 100 partidas.
- **CA-A-08**: CUANDO el agente Complejo debe jugar en modalidad clásica, EL
  agente SHALL seleccionar siempre una jugada que garantice su mejor
  resultado posible frente a cualquier respuesta del rival: victoria si es
  alcanzable de forma forzada, o empate si la victoria no es alcanzable ante
  un rival que también juega de forma óptima.
- **CA-A-09**: EL agente Complejo SHALL conservar memoria persistente entre
  partidas de los resultados ya evaluados para cada posición de tablero
  encontrada, y CUANDO una posición ya evaluada vuelve a presentarse en una
  partida posterior, EL agente SHALL reutilizar el resultado memorizado en
  lugar de recalcularlo.
- **CA-A-10**: CUANDO el agente Complejo debe jugar en modalidad continua,
  tanto en fase de colocación como de movimiento, EL agente SHALL devolver
  una jugada legal en menos de 1 segundo mediante una estrategia táctica
  acotada; la garantía de juego óptimo de CA-A-08 permanece limitada a la
  modalidad clásica.

---

### Edge Cases

- ¿Qué ocurre si se solicita una jugada a cualquier agente sobre un tablero
  sin casillas legales disponibles (tablero lleno) o sobre una partida ya
  finalizada? El agente SHALL rechazar la solicitud sin devolver una jugada.
- ¿Qué ocurre si el agente Medio tiene simultáneamente más de una casilla que
  le otorgaría la victoria inmediata? El agente SHALL jugar cualquiera de
  ellas, priorizando siempre ganar sobre bloquear o jugar al azar.
- ¿Qué ocurre si el agente Medio detecta simultáneamente una jugada ganadora
  propia y una amenaza de victoria del rival? El agente SHALL priorizar
  siempre ganar (CA-A-03) sobre bloquear (CA-A-04).
- ¿Qué ocurre si el agente Complejo enfrenta una posición para la que ya
  existe un resultado memorizado de una partida anterior distinta? El agente
  SHALL reutilizar ese resultado (CA-A-09) sin recalcular la jugada óptima
  desde cero.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST ofrecer exactamente tres niveles de agente
  seleccionables: Sencillo, Medio y Complejo.
- **FR-002**: El agente Sencillo MUST elegir su jugada por selección aleatoria
  uniforme entre las casillas legales del estado de tablero recibido, sin
  emplear información de turnos previos.
- **FR-003**: El agente Medio MUST aplicar, en este orden estricto de
  prioridad en cada turno: (1) jugar una victoria inmediata propia si existe,
  (2) bloquear una victoria inmediata del rival si existe y no hay victoria
  propia disponible, (3) jugar una casilla legal al azar si ninguna de las
  anteriores aplica.
- **FR-004**: El agente Medio MUST mantener memoria del historial de jugadas
  de la partida en curso mientras esta no finalice, y MUST descartar esa
  memoria al finalizar la partida.
- **FR-005**: El agente Complejo MUST elegir, en modalidad clásica, una
  jugada que garantice el mejor resultado posible ante cualquier respuesta
  del rival (victoria forzada si existe, empate en caso contrario), de forma
  que nunca pierda una partida.
- **FR-006**: El agente Complejo MUST mantener memoria persistente entre
  partidas de los resultados ya evaluados por posición de tablero, y MUST
  reutilizar un resultado memorizado en lugar de recalcularlo cuando la misma
  posición vuelva a presentarse.
- **FR-007**: Todo agente, en cualquier nivel, MUST rechazar una solicitud de
  jugada cuando no existan casillas legales disponibles o la partida ya haya
  finalizado.
- **FR-008**: El sistema MUST permitir enfrentar entre sí a dos agentes de
  cualquier nivel (incluyendo el mismo nivel contra sí mismo) durante una
  serie de partidas completas, para fines de validación estadística
  (CA-A-07).
- **FR-009**: En modalidad continua, el agente Complejo MUST utilizar una
  estrategia acotada que priorice victoria inmediata, bloqueo y una jugada
  legal determinista, sin ejecutar una búsqueda potencialmente cíclica del
  árbol completo de movimientos.

### Key Entities

- **Agente**: Entidad que, dado el estado actual de una partida, produce una
  jugada legal. Atributos: nivel (Sencillo, Medio o Complejo), y —según el
  nivel— memoria de la partida en curso (Medio) o memoria persistente entre
  partidas (Complejo).
- **Memoria de Partida**: Historial de jugadas de una partida en curso,
  utilizado únicamente por el agente Medio y descartado al finalizar la
  partida.
- **Memoria Persistente**: Conjunto de resultados ya evaluados para
  posiciones de tablero conocidas, utilizado y actualizado únicamente por el
  agente Complejo, y conservado entre partidas distintas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las jugadas devueltas por cualquier agente, en
  cualquier nivel, son legales para el estado de tablero recibido.
- **SC-002**: En una muestra de al menos 100 partidas completas entre el
  agente Sencillo y el agente Complejo en modalidad clásica, el agente
  Complejo obtiene victoria o empate en el 100% de los casos (0 derrotas).
- **SC-003**: El agente Medio juega una victoria inmediata disponible o
  bloquea una amenaza de victoria del rival en el 100% de los estados de
  tablero donde dicha condición se presenta.
- **SC-004**: Cualquier agente, en cualquier nivel, responde con su jugada en
  menos de 1 segundo desde que se le solicita.
- **SC-005**: Al enfrentar al agente Complejo contra sí mismo en modalidad
  clásica en repetidas partidas, el resultado es empate en el 100% de los
  casos, evidenciando juego óptimo por ambos lados.

## Assumptions

- Esta especificación cubre exclusivamente el comportamiento observable de
  los agentes (nivel, jugada producida, uso de memoria); las reglas del
  tablero, turnos y detección de victoria/empate corresponden al motor del
  juego, ya especificado por separado, y no se redefinen aquí.
- El criterio estadístico CA-A-07 y el éxito SC-002 se evalúan sobre la
  modalidad clásica, dado que es la modalidad para la que el agente Complejo
  garantiza juego óptimo sin derrota; el comportamiento del agente Complejo en
  modalidad continua garantiza legalidad y tiempo de respuesta, pero no
  optimalidad ni invencibilidad (CA-A-10).
- La "memoria persistente entre partidas" del agente Complejo (CA-A-09,
  FR-006) se limita a resultados de evaluación de posiciones de tablero; no
  implica ningún requisito de almacenamiento, formato o tecnología, que queda
  fuera de alcance de esta especificación.
- No se especifica ninguna interfaz de usuario ni forma de selección del
  nivel de agente por parte del jugador; ambos aspectos quedan fuera de
  alcance de esta especificación.
