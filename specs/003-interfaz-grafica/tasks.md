---

description: "Task list for Interfaz Gráfica del Juego Tres en Raya"
---

# Tasks: Interfaz Gráfica del Juego Tres en Raya

**Input**: Design documents from `/specs/003-interfaz-grafica/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/ui-consumption-contract.md](./contracts/ui-consumption-contract.md), [research.md](./research.md)
**Feature dependency**: requiere que `001-motor-tres-en-raya` y
`002-agentes-de-juego` estén implementadas y expuestas (`/api/games`,
`/api/agents/{level}/move`); esta feature no añade endpoints propios.

**Tests**: Incluidas y obligatorias — el Principio III de la constitución
exige al menos un test automatizado por cada CA-I-* antes de cerrar la tarea
que lo cubre. Dado que la constitución fija Pytest como único framework de
pruebas (sin frameworks de testing JS), los tests de esta feature usan Pytest
con un navegador controlado (ver `research.md` Decisión 4).

**Organization**: Tareas agrupadas por historia de usuario (US1 =
Configurar Partida, US2 = Jugar Partida, US3 = Esperar Agente, US4 = Mover en
Modalidad Continua, US5 = Marcador y Reinicio, US6 = Teclado / Requisito
Excelente, US7 = Diseño Responsive).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: US1 a US7
- Cada tarea indica ruta de archivo exacta y los CA-I-* que cubre

## Recordatorio de gates de la constitución

- Ninguna tarea se cierra sin que sus tests asociados estén en verde
  (Principio III).
- Cada tarea corresponde a un commit único: `T-NNN: descripción (CA-I-XX)`
  (Principio IV).
- Ningún archivo bajo `frontend/js/` MUST implementar reglas de juego
  (victoria, empate, legalidad, heurística de agente); toda esa lógica vive
  en el backend de las specs 001/002.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Esqueleto estático del frontend y arnés de pruebas e2e

- [X] T001 Crear `frontend/index.html`, `frontend/css/styles.css` y los
      módulos vacíos `frontend/js/{api,state,board,config-screen,
      game-screen,scoreboard,keyboard}.js`, según `plan.md` → Project
      Structure
- [X] T002 [P] Montar `frontend/` como archivos estáticos en
      `backend/src/main.py` (`StaticFiles`), sirviendo `index.html` en `/`
- [X] T003 [P] Añadir dependencia de test de navegador controlado (p. ej.
      `pytest-playwright`) y crear `tests/e2e/` con configuración base para
      servir `frontend/` durante los tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cliente de API y estado de UI que todas las historias necesitan

**⚠️ CRITICAL**: Ninguna tarea de US1-US7 puede iniciarse hasta completar
esta fase

- [X] T004 [P] Implementar `frontend/js/api.js`: `crearPartida(mode)`,
      `obtenerPartida(gameId)`, `aplicarJugada(gameId, jugada)`,
      `obtenerJugadaAgente(nivel, solicitud)`, envolviendo `fetch` hacia los
      contratos de `001-motor-tres-en-raya/contracts/games-api.md` y
      `002-agentes-de-juego/contracts/agents-api.md` — único módulo que
      conoce URLs y forma de las peticiones HTTP
- [X] T005 [P] Implementar `frontend/js/state.js`: objeto `EstadoUI`
      (`pantalla`, `configuracion`, `game_state`, `foco_actual`,
      `casilla_seleccionada`) y `MarcadorSesion`, exactamente según
      `data-model.md`
- [X] T006 Implementar el esqueleto de `frontend/index.html` con los
      contenedores de las 4 pantallas (Configuración, En Juego/Esperando
      Agente, Terminada) y un estilo base de foco visible en
      `frontend/css/styles.css` (base para CA-I-17, refinado en US6)

**Checkpoint**: Cliente de API y estado de UI listos — el resto de historias
pueden implementarse en paralelo si hay más de una persona

---

## Phase 3: Configurar una Partida Nueva (Priority: P1) 🎯 MVP (parte 1)

**Goal**: Elegir modo, nivel de agente, fichas y modalidad, e iniciar la
partida

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k configuracion`

### Tests para US1 (escribir primero, deben fallar)

- [X] T007 [P] [US1] Test e2e en `tests/e2e/test_ui_flows.py::test_configuracion_inicial`:
      la pantalla inicial es Configuración (CA-I-01), permite elegir modo,
      fichas, modalidad y nivel de agente cuando corresponde (CA-I-02),
      confirma el inicio con selección completa (CA-I-03), y rechaza el
      inicio con selección incompleta permaneciendo en Configuración
      (CA-I-04)

### Implementación para US1

- [X] T008 [US1] Implementar `frontend/js/config-screen.js`: renderiza los
      controles de modo, ficha, modalidad y nivel de agente (visible solo
      si `modo = "humano_vs_agente"`) sobre `EstadoUI.configuracion`
      (CA-I-01, CA-I-02)
- [X] T009 [US1] Implementar en `frontend/js/config-screen.js` la
      validación de selección completa antes de habilitar "iniciar", y el
      aviso visual de qué falta si se intenta confirmar incompleto
      (CA-I-04)
- [X] T010 [US1] Conectar el botón "iniciar" en `frontend/js/config-screen.js`
      a `api.crearPartida(configuracion.modalidad)` y transicionar
      `EstadoUI.pantalla` a `"en_juego"` con la respuesta (CA-I-03)
- [X] T011 [US1] Ejecutar `pytest tests/e2e/test_ui_flows.py -k
      configuracion` y confirmar que T007 está en verde

**Checkpoint**: Configuración inicial completamente funcional y testeada de
forma independiente

---

## Phase 4: Jugar una Partida (Priority: P1) 🎯 MVP (parte 2)

**Goal**: Ver turno y ficha, jugar sobre el tablero, ver victoria/empate
resaltados y bloqueo del tablero, recibir aviso ante jugada ilegal

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k partida`

### Tests para US2 (escribir primero, deben fallar)

- [X] T012 [P] [US2] Test e2e en `tests/e2e/test_ui_flows.py::test_jugar_partida`:
      se indica turno y ficha durante la partida (CA-I-05); al ganar se
      resalta la línea ganadora y se bloquea el tablero (CA-I-06); al
      empatar se indica el empate y se bloquea el tablero (CA-I-07); una
      jugada ilegal muestra aviso visual sin alterar el estado (CA-I-08)

### Implementación para US2

- [X] T013 [US2] Implementar `frontend/js/board.js`: renderiza el tablero
      3x3 a partir de `game_state.board` e indica de quién es el turno y
      su ficha a partir de `game_state.turn` (CA-I-05)
- [X] T014 [US2] Implementar en `frontend/js/board.js` el resaltado de
      `game_state.winning_line` y el bloqueo de interacción cuando
      `game_state.status != "en_curso"` (CA-I-06, CA-I-07)
- [X] T015 [US2] Implementar en `frontend/js/game-screen.js` el manejador de
      clic sobre una casilla: construye la `Jugada` y llama
      `api.aplicarJugada`; en `200 OK` actualiza `EstadoUI.game_state`; en
      `422` muestra el aviso visual de error usando el campo `error` de la
      respuesta sin modificar `EstadoUI.game_state` (CA-I-08)
- [X] T016 [US2] Ejecutar `pytest tests/e2e/test_ui_flows.py -k partida` y
      confirmar que T012 está en verde

**Checkpoint**: Ciclo completo de partida (clásica, contra otro humano)
jugable de principio a fin — MVP entregable (US1+US2)

---

## Phase 5: Esperar la Jugada del Agente (Priority: P2)

**Goal**: Indicar visualmente que el agente está calculando y deshabilitar
el tablero mientras tanto

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k espera_agente`

### Tests para US3 (escribir primero, deben fallar)

- [X] T017 [P] [US3] Test e2e en
      `tests/e2e/test_ui_flows.py::test_espera_agente`: al llegar el turno
      de un agente se muestra la indicación de espera y se deshabilita el
      tablero (CA-I-09); al recibir la jugada del agente se oculta la
      espera, se aplica la jugada y se retorna a En Juego o Terminada
      (CA-I-10)

### Implementación para US3

- [X] T018 [US3] Implementar en `frontend/js/game-screen.js` la detección
      de turno de agente (a partir de `game_state.turn` y
      `EstadoUI.configuracion`), transicionando `EstadoUI.pantalla` a
      `"esperando_agente"` y deshabilitando el tablero (CA-I-09)
- [X] T019 [US3] Implementar en `frontend/js/game-screen.js` la llamada a
      `api.obtenerJugadaAgente(nivel, subconjuntoEstado)` seguida de
      `api.aplicarJugada` con la jugada recibida, ocultando la indicación
      de espera y retornando a `"en_juego"` o `"terminada"` según la
      respuesta (CA-I-10)
- [X] T020 [US3] Ejecutar `pytest tests/e2e/test_ui_flows.py -k
      espera_agente` y confirmar que T017 está en verde

**Checkpoint**: Partidas Humano vs Agente completamente jugables con
indicación de espera

---

## Phase 6: Mover Fichas en Modalidad Continua (Priority: P2)

**Goal**: Señalar fichas propias movibles y casillas destino disponibles
durante la fase de movimiento

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k continua`

### Tests para US4 (escribir primero, deben fallar)

- [X] T021 [P] [US4] Test e2e en
      `tests/e2e/test_ui_flows.py::test_modalidad_continua_movimiento`: en
      fase de movimiento se señalan las fichas propias movibles (CA-I-11);
      al seleccionar una, se señalan las casillas vacías disponibles como
      destino (CA-I-12)

### Implementación para US4

- [X] T022 [US4] Implementar en `frontend/js/board.js` el cálculo y
      resaltado de las fichas propias del jugador humano cuando
      `game_state.mode = "continua"`, `game_state.phase = "movimiento"` y
      es su turno (CA-I-11)
- [X] T023 [US4] Implementar en `frontend/js/board.js` /
      `frontend/js/game-screen.js` el resaltado de casillas vacías
      disponibles al seleccionar una ficha movible, y la construcción de la
      `Jugada` tipo `"mover"` (`from`/`to`) hacia la casilla elegida
      (CA-I-12)
- [X] T024 [US4] Ejecutar `pytest tests/e2e/test_ui_flows.py -k continua` y
      confirmar que T021 está en verde

**Checkpoint**: Modalidad continua completamente jugable con señalización
visual de movimientos válidos

---

## Phase 7: Marcador de Sesión y Reinicio (Priority: P3)

**Goal**: Marcador acumulado de victorias/empates y reinicio de partida sin
perderlo

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k marcador`

### Tests para US5 (escribir primero, deben fallar)

- [X] T025 [P] [US5] Test e2e en
      `tests/e2e/test_ui_flows.py::test_marcador_y_reinicio`: el marcador
      se mantiene visible y acumula victorias/empates tras cada partida
      (CA-I-13, CA-I-14); "reiniciar" inicia una nueva partida con la misma
      configuración y conserva el marcador (CA-I-15)

### Implementación para US5

- [X] T026 [US5] Implementar `frontend/js/scoreboard.js`: renderiza
      `MarcadorSesion` de forma visible en toda pantalla de juego, y lo
      incrementa exactamente una vez por cada `GameState` recibido con
      `status != "en_curso"` (CA-I-13, CA-I-14)
- [X] T027 [US5] Implementar en `frontend/js/scoreboard.js` el control de
      "reiniciar": repite la secuencia de creación de partida con
      `EstadoUI.configuracion` vigente sin modificar `MarcadorSesion`
      (CA-I-15)
- [X] T028 [US5] Ejecutar `pytest tests/e2e/test_ui_flows.py -k marcador` y
      confirmar que T025 está en verde

**Checkpoint**: Marcador de sesión y reinicio completamente funcionales

---

## Phase 8: Operación Completa por Teclado — Requisito Excelente (Priority: P3)

**Goal**: Configurar, jugar y reiniciar una partida completa usando
exclusivamente el teclado

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k teclado`

### Tests para US6 (escribir primero, deben fallar)

- [ ] T029 [P] [US6] Test e2e en
      `tests/e2e/test_ui_flows.py::test_operacion_por_teclado`: completa,
      solo con teclado, el flujo de Configuración → partida completa
      (incluyendo una jugada rechazada por ilegal) → reinicio, verificando
      en cada paso indicación visual de foco (CA-I-17) y que una entrada de
      teclado sobre el tablero deshabilitado se ignora sin cambios
      (CA-I-18)

### Implementación para US6

- [ ] T030 [US6] Implementar en `frontend/js/keyboard.js` el patrón "roving
      tabindex" sobre las 9 casillas del tablero: navegación con flechas de
      dirección, foco acotado dentro de los límites del tablero sin salir
      de las 9 casillas (CA-I-16, edge case de `spec.md`)
- [ ] T031 [US6] Implementar en `frontend/js/keyboard.js` la confirmación
      de selección/jugada con Enter o Espacio sobre la casilla enfocada, y
      verificar que los controles de Configuración y el botón de reinicio
      son operables por Tab/Enter/Espacio de forma nativa (CA-I-16)
- [ ] T032 [US6] Refinar en `frontend/css/styles.css` la indicación visual
      de foco (`:focus-visible`) para todo control de Configuración,
      casilla del tablero y botón de reinicio (CA-I-17)
- [ ] T033 [US6] Implementar en `frontend/js/keyboard.js` el rechazo
      silencioso de una selección de teclado sobre el tablero cuando
      `EstadoUI.pantalla` es `"esperando_agente"` o `"terminada"`, sin
      alterar estado ni foco (CA-I-18)
- [ ] T034 [US6] Ejecutar `pytest tests/e2e/test_ui_flows.py -k teclado` y
      confirmar que T029 está en verde

**Checkpoint**: Interfaz completamente operable por teclado (Requisito
Excelente) sin romper la operación por mouse

---

## Phase 9: Uso en Pantallas de Distinto Tamaño — Responsive (Priority: P3)

**Goal**: Tablero, marcador y controles de Configuración permanecen
visibles y operables, sin scroll horizontal ni zoom manual, en anchos de
viewport de ~320px a 1920px (móvil, tablet, escritorio)

**Independent Test**: `pytest tests/e2e/test_ui_flows.py -k responsive`

### Tests para US7 (escribir primero, deben fallar)

- [ ] T035 [P] [US7] Test e2e en
      `tests/e2e/test_ui_flows.py::test_responsive_sin_scroll_horizontal`:
      en tres anchos de viewport representativos (móvil ~375px, tablet
      ~768px, escritorio ~1440px), el tablero, el marcador y los controles
      de Configuración son visibles y no aparece scroll horizontal
      (CA-I-19, CA-I-20)
- [ ] T036 [P] [US7] Test e2e en
      `tests/e2e/test_ui_flows.py::test_responsive_objetivo_tactil`: en el
      ancho móvil, cada casilla del tablero mide al menos ~44x44px CSS
      (CA-I-21)
- [ ] T037 [P] [US7] Test e2e en
      `tests/e2e/test_ui_flows.py::test_responsive_resize_preserva_estado`:
      con una partida en curso y foco de teclado activo, redimensionar el
      viewport SHALL preservar el tablero, turno, fase, marcador y foco
      vigente (CA-I-22)

### Implementación para US7

- [ ] T038 [US7] Añadir `<meta name="viewport"
      content="width=device-width, initial-scale=1">` en
      `frontend/index.html` y un reset CSS base "mobile-first" en
      `frontend/css/styles.css`
- [ ] T039 [US7] Implementar en `frontend/css/styles.css` la disposición
      responsive de tablero, marcador y controles de Configuración con
      Flexbox/Grid y unidades relativas, reordenando mediante media
      queries sin provocar scroll horizontal en ningún ancho del rango
      320px-1920px (CA-I-19, CA-I-20)
- [ ] T040 [US7] Asegurar en `frontend/css/styles.css` que cada casilla del
      tablero mantiene un tamaño mínimo de objetivo táctil (~44x44px CSS)
      en todos los anchos soportados (CA-I-21)
- [ ] T041 [US7] Confirmar que ningún dato de `EstadoUI` (tablero, turno,
      fase, marcador, foco) se deriva de o se ve alterado por el tamaño de
      viewport — el layout responsive es puramente CSS (CA-I-22)
- [ ] T042 [US7] Ejecutar `pytest tests/e2e/test_ui_flows.py -k responsive`
      y confirmar que T035/T036/T037 están en verde

**Checkpoint**: Interfaz completamente utilizable en móvil, tablet y
escritorio sin scroll horizontal ni pérdida de estado al redimensionar

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Validación manual final transversal a todas las historias

- [ ] T043 [P] Ejecutar manualmente la validación completa de
      `quickstart.md` (flujo con mouse, flujo exclusivamente por teclado, y
      diseño responsive en los tres anchos de referencia)
- [ ] T044 [P] Revisar que ningún archivo bajo `frontend/js/` contiene
      lógica de reglas de juego (victoria, empate, legalidad, heurística de
      agente), confirmando que toda decisión de negocio proviene de
      `api.js` (Principio II de la constitución)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Depende de que `001-motor-tres-en-raya` y
  `002-agentes-de-juego` estén implementadas y sirviendo sus endpoints
- **Foundational (Phase 2)**: Depende de Setup — bloquea las seis historias
- **US1 (Phase 3)** y **US2 (Phase 4)**: Dependen de Foundational; forman el
  MVP conjunto (sin Configuración no hay partida que jugar)
- **US3 (Phase 5)**: Depende de Foundational y de US2 (reutiliza el manejo
  de `GameState` de `board.js`/`game-screen.js`)
- **US4 (Phase 6)**: Depende de Foundational y de US2; independiente de US3
- **US5 (Phase 7)**: Depende de Foundational y de US2 (necesita resultados
  de partida ya finalizada para acumular marcador)
- **US6 (Phase 8)**: Depende de que US1-US5 ya funcionen por mouse; añade
  una capa de accesibilidad sobre ellas sin modificarlas
- **US7 (Phase 9)**: Depende de Foundational y de US1/US2 (necesita una
  Configuración y una partida jugable para validar el layout en distintos
  anchos); es independiente de US3-US6, ya que solo modifica CSS
- **Polish (Phase 10)**: Depende de que todas las historias estén completas

### Parallel Opportunities

- T002 y T003 en paralelo tras T001
- T004 y T005 en paralelo dentro de Foundational
- T035, T036 y T037 en paralelo dentro de US7 (tests)
- T043 y T044 en paralelo dentro de Polish

---

## Parallel Example: MVP (US1 + US2)

```bash
# Tests de ambas historias del MVP pueden escribirse en paralelo:
Task: "Test e2e de configuración en tests/e2e/test_ui_flows.py::test_configuracion_inicial"
Task: "Test e2e de partida completa en tests/e2e/test_ui_flows.py::test_jugar_partida"
```

---

## Implementation Strategy

### MVP First (Configurar + Jugar Partida)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (bloquea todo lo demás)
3. Completar Phase 3 (US1) y Phase 4 (US2)
4. **Detener y validar**: correr `quickstart.md` sección "flujo completo con
   mouse", pasos 1-5
5. Commitear cada tarea según Principio IV: `T-00N: descripción (CA-I-XX)`

### Entrega Incremental

1. Setup + Foundational → base lista
2. US1 + US2 → MVP: partida Humano vs Humano jugable de principio a fin
3. US3 → añade soporte Humano vs Agente
4. US4 → añade modalidad continua
5. US5 → añade continuidad entre partidas (marcador y reinicio)
6. US6 → añade accesibilidad completa por teclado (Requisito Excelente)
7. US7 → añade diseño responsive (móvil/tablet/escritorio)
8. Polish → validación manual final y revisión de separación de
   responsabilidades
