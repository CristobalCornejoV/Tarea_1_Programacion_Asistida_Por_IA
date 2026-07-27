# Feature Specification: Motor del Juego Tres en Raya

**Feature Branch**: `001-motor-tres-en-raya`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "Motor del juego tres en raya. Tablero de 3x3; X y O alternan turnos y X inicia. Reglas de victoria: Gana quien alinea tres fichas propias en fila, columna o diagonal. Modalidad clásica: se coloca una ficha por turno en casilla vacía; empate al llenarse el tablero sin ganador. Modalidad continua: cada jugador tiene exactamente 3 fichas. Primero fase de colocación en casillas vacías. Luego fase de movimiento, donde un jugador mueve una ficha propia a cualquier casilla vacía. Excluir: sin interfaz ni agentes en esta spec."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Partida en Modalidad Clásica (Priority: P1)

Dos jugadores (X y O) juegan una partida completa en modalidad clásica: colocan
fichas por turno en casillas vacías de un tablero 3x3 hasta que uno de los dos
alinea tres fichas propias, o el tablero se llena sin ganador.

**Why this priority**: Es el modo de juego fundamental y mínimo viable del
motor; sin esta capacidad no existe producto. Todo lo demás (modalidad
continua, agentes, interfaz) se apoya sobre estas reglas base.

**Independent Test**: Se puede probar por completo invocando el motor con una
secuencia de jugadas válidas en modalidad clásica y verificando que produce el
estado de tablero correcto, detecta el ganador (o empate) en el momento
correcto, y rechaza jugadas inválidas.

**Acceptance Scenarios** (notación EARS):

- **CA-M-01**: EL motor SHALL inicializar toda partida nueva con un tablero
  3x3 vacío y el turno asignado a la ficha X.
- **CA-M-02**: CUANDO un jugador coloca una ficha en una casilla vacía en su
  turno, EL motor SHALL registrar la ficha en esa casilla y SHALL ceder el
  turno al jugador contrario.
- **CA-M-03**: SI un jugador intenta colocar una ficha en una casilla ya
  ocupada, ENTONCES EL motor SHALL rechazar la jugada y SHALL mantener el
  turno del mismo jugador sin modificar el tablero.
- **CA-M-04**: SI un jugador intenta jugar fuera de su turno, ENTONCES EL
  motor SHALL rechazar la jugada sin modificar el tablero ni el turno.
- **CA-M-05**: CUANDO tras una jugada existen tres fichas iguales alineadas en
  una misma fila, columna o diagonal, EL motor SHALL declarar ganador al
  jugador dueño de esas fichas y SHALL finalizar la partida.
- **CA-M-06**: CUANDO las 9 casillas del tablero quedan ocupadas y ninguna
  alineación de tres fichas propias existe, EL motor SHALL declarar la
  partida empatada y SHALL finalizarla.
- **CA-M-07**: MIENTRAS la partida esté finalizada (con ganador o empate), EL
  motor SHALL rechazar cualquier jugada adicional.

---

### User Story 2 - Partida en Modalidad Continua (Priority: P2)

Dos jugadores (X y O), con exactamente 3 fichas cada uno, juegan una partida
en modalidad continua: primero colocan sus 3 fichas en casillas vacías (fase
de colocación) y luego, en la fase de movimiento, mueven una ficha propia a
cualquier casilla vacía del tablero en cada turno, hasta que alguien gane, o
el sistema detecte una repetición de posición que fuerce el empate.

**Why this priority**: Es una capacidad diferenciadora del motor respecto al
tres en raya clásico y depende de que la modalidad clásica (detección de
victoria, alternancia de turnos) ya esté implementada; por eso se ordena
después de US1.

**Independent Test**: Se puede probar por completo jugando una secuencia que
cubra la fase de colocación completa (6 jugadas), la transición a fase de
movimiento, y verificando victoria, movimientos inválidos, y la regla de
empate por repetición de posición.

**Acceptance Scenarios** (notación EARS):

- **CA-M-08**: EL motor SHALL iniciar toda partida en modalidad continua en
  fase de colocación, con 3 fichas disponibles para colocar por cada jugador.
- **CA-M-09**: CUANDO un jugador coloca una de sus fichas disponibles en una
  casilla vacía durante la fase de colocación, EL motor SHALL descontar una
  ficha disponible de ese jugador y SHALL ceder el turno al contrario.
- **CA-M-10**: CUANDO ambos jugadores han colocado sus 3 fichas (0 fichas
  disponibles para colocar en ambos), EL motor SHALL transicionar la partida a
  fase de movimiento.
- **CA-M-11**: MIENTRAS la partida esté en fase de movimiento, CUANDO un
  jugador mueve una ficha propia desde su casilla actual hacia cualquier
  casilla vacía del tablero, EL motor SHALL reubicar la ficha en la casilla
  destino, SHALL vaciar la casilla de origen y SHALL ceder el turno al
  contrario. [Resuelto: la casilla destino no requiere ser adyacente a la
  casilla de origen.]
- **CA-M-12**: SI un jugador en fase de movimiento intenta mover una ficha que
  no le pertenece, o mover hacia una casilla ocupada, ENTONCES EL motor SHALL
  rechazar la jugada sin modificar el tablero ni el turno.
- **CA-M-13**: CUANDO tras colocar o mover una ficha existen tres fichas
  iguales alineadas en una misma fila, columna o diagonal, EL motor SHALL
  declarar ganador al jugador dueño de esas fichas y SHALL finalizar la
  partida, tanto en fase de colocación como en fase de movimiento.
- **CA-M-14**: MIENTRAS la partida esté en fase de movimiento, SI la misma
  posición exacta del tablero (mismas fichas en las mismas casillas) se
  repite un total de 3 veces a lo largo de la partida, ENTONCES EL motor
  SHALL declarar la partida empatada y SHALL finalizarla. [Resuelto: regla
  introducida específicamente para evitar bucles infinitos de movimientos.]
- **CA-M-15**: MIENTRAS la partida esté finalizada (con ganador o empate), EL
  motor SHALL rechazar cualquier colocación o movimiento adicional.

---

### Edge Cases

- ¿Qué ocurre si se intenta colocar o mover una ficha fuera de los límites del
  tablero (coordenadas inválidas)? El motor SHALL rechazar la jugada sin
  modificar el estado.
- ¿Qué ocurre si en modalidad continua un jugador intenta mover una ficha
  antes de que ambos jugadores hayan completado la fase de colocación? El
  motor SHALL rechazar la jugada por estar en la fase incorrecta.
- ¿Qué ocurre si se alcanza simultáneamente una alineación ganadora y una
  repetición de posición? La detección de victoria SHALL evaluarse primero;
  la partida termina en victoria, no en empate por repetición.
- ¿Qué ocurre si una posición repetida es distinta a la inicial pero ya se
  vio dos veces antes? El conteo de repeticiones SHALL acumularse por
  posición exacta de tablero, no solo respecto a la posición inicial.

## Resolved Clarifications

Estas ambigüedades fueron identificadas durante el análisis de la
especificación y resueltas por decisión explícita del equipo antes de cerrar
esta spec (ver CA-M-11 y CA-M-14 arriba):

- **[NEEDS CLARIFICATION: ¿En modalidad continua, una ficha puede moverse a
  cualquier casilla vacía o solo a casillas adyacentes?]** — **RESUELTO**: una
  ficha puede moverse a cualquier casilla vacía del tablero, sin restricción
  de adyacencia. Decisión tomada para simplificar el flujo del motor y de las
  reglas que deberán validar los agentes en tareas futuras.
- **[NEEDS CLARIFICATION: ¿Qué ocurre si una posición del tablero se repite
  indefinidamente durante la fase de movimiento?]** — **RESUELTO**: si la
  misma posición exacta del tablero se repite 3 veces a lo largo de la fase
  de movimiento, el sistema declara la partida empatada, para evitar bucles
  infinitos entre los dos jugadores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El motor MUST representar el tablero como una cuadrícula de 3x3
  casillas, cada una vacía o con una ficha X u O.
- **FR-002**: El motor MUST alternar el turno entre los dos jugadores (X y O)
  después de cada jugada válida, comenzando siempre por X.
- **FR-003**: El motor MUST soportar dos modalidades de partida configurables
  al crearla: clásica y continua.
- **FR-004**: En modalidad clásica, el motor MUST permitir únicamente
  colocar una ficha por turno en una casilla vacía.
- **FR-005**: En modalidad continua, el motor MUST limitar a exactamente 3
  fichas por jugador y MUST distinguir explícitamente entre fase de
  colocación y fase de movimiento.
- **FR-006**: En modalidad continua, el motor MUST permitir mover una ficha
  propia a cualquier casilla vacía del tablero una vez iniciada la fase de
  movimiento, sin restricción de adyacencia.
- **FR-007**: El motor MUST detectar victoria evaluando las 8 alineaciones
  posibles de tres casillas (3 filas, 3 columnas, 2 diagonales) tras cada
  jugada válida.
- **FR-008**: En modalidad clásica, el motor MUST declarar empate cuando las 9
  casillas estén ocupadas sin ninguna alineación ganadora.
- **FR-009**: En modalidad continua, el motor MUST llevar un registro de las
  posiciones de tablero ya vistas durante la fase de movimiento y MUST
  declarar empate cuando una misma posición exacta se repita 3 veces.
- **FR-010**: El motor MUST rechazar toda jugada inválida (casilla ocupada,
  fuera de turno, ficha ajena, fase incorrecta, coordenadas fuera de rango)
  sin alterar el estado de la partida ni el turno vigente.
- **FR-011**: El motor MUST rechazar cualquier jugada una vez que la partida
  ha finalizado (con ganador o empate).
- **FR-012**: El motor MUST exponer el estado completo de la partida en todo
  momento: tablero, turno actual, modalidad, fase (si aplica), fichas
  disponibles por jugador (si aplica) y resultado (en curso, ganador, empate).

### Key Entities

- **Partida**: Representa una partida en curso o finalizada. Atributos:
  identificador, modalidad (clásica/continua), tablero, turno actual, fase
  (colocación/movimiento, solo en modalidad continua), fichas disponibles por
  jugador (solo en modalidad continua), resultado (en curso/ganador/empate) e
  historial de posiciones vistas (solo en modalidad continua, para la regla
  de repetición).
- **Tablero**: Cuadrícula de 3x3 casillas; cada casilla está vacía o contiene
  una ficha X u O.
- **Jugada**: Acción de un jugador sobre el tablero: colocar una ficha en una
  casilla vacía, o mover una ficha propia desde una casilla de origen hacia
  una casilla de destino vacía (solo en fase de movimiento de modalidad
  continua).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El motor determina el resultado (victoria o empate) de
  cualquier partida completa, en cualquiera de las dos modalidades, de forma
  100% consistente con las reglas descritas (verificado mediante pruebas
  automatizadas exhaustivas de los 8 patrones de alineación).
- **SC-002**: El 100% de las jugadas inválidas descritas en los criterios de
  aceptación (casilla ocupada, fuera de turno, ficha ajena, fase incorrecta,
  fuera de rango) son rechazadas sin corromper el estado de la partida.
- **SC-003**: En modalidad continua, toda partida en la que se repite 3 veces
  la misma posición exacta durante la fase de movimiento termina en empate,
  sin requerir un número máximo de turnos configurado externamente.
- **SC-004**: El estado completo de cualquier partida (tablero, turno, fase,
  fichas disponibles y resultado) puede consultarse en cualquier momento sin
  ambigüedad sobre qué modalidad o fase está activa.

## Assumptions

- La modalidad y el número de jugadores (siempre 2: X y O) se determinan al
  crear la partida y no cambian durante su transcurso.
- No existe límite de tiempo por turno ni por partida; el único mecanismo de
  finalización forzada es la regla de repetición de posición en modalidad
  continua (CA-M-14).
- Esta especificación cubre exclusivamente el motor de reglas del juego. Los
  agentes automáticos (aleatorio, heurístico, minimax, etc.) y cualquier
  interfaz de usuario quedan fuera de alcance y se especificarán en tareas
  posteriores.
- El registro de posiciones para la regla de repetición (CA-M-14, FR-009)
  inicia junto con la fase de movimiento; las posiciones vistas únicamente
  durante la fase de colocación no cuentan para esta regla, dado que en esa
  fase el tablero nunca puede repetir una posición ya vista (cada colocación
  añade una ficha nueva).
