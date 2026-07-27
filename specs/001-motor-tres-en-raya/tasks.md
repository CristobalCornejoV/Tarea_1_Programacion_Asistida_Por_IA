---

description: "Task list for Motor del Juego Tres en Raya"
---

# Tasks: Motor del Juego Tres en Raya

**Input**: Design documents from `/specs/001-motor-tres-en-raya/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/games-api.md](./contracts/games-api.md), [research.md](./research.md)

**Tests**: Incluidas y obligatorias — el Principio III de la constitución exige
al menos un test automatizado por cada CA-M-* antes de cerrar la tarea que lo
cubre; cada fase de historia de usuario abajo escribe sus tests primero.

**Organization**: Tareas agrupadas por historia de usuario (US1 = Modalidad
Clásica, US2 = Modalidad Continua) para permitir implementación y prueba
independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: US1 o US2
- Cada tarea indica ruta de archivo exacta y los CA-M-* que cubre

## Recordatorio de gates de la constitución

- Ninguna tarea se cierra (ni se commitea) sin que sus tests asociados estén
  en verde (Principio III).
- Cada tarea corresponde a un commit único: `T-NNN: descripción (CA-M-XX)`
  (Principio IV).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto backend compartido por las tres specs

- [X] T001 Crear la estructura de directorios `backend/src/{models,engine,api}`,
      `backend/tests/{unit,contract}` y `frontend/{css,js}` según
      `plan.md` → Project Structure
- [ ] T002 [P] Inicializar el proyecto Python en `backend/pyproject.toml` (o
      `requirements.txt`) con dependencias `fastapi`, `uvicorn`, `pydantic`,
      `pytest`, `httpx`
- [ ] T003 [P] Configurar `pytest.ini` (o sección `[tool.pytest.ini_options]`)
      apuntando a `backend/tests/` como raíz de descubrimiento de pruebas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estructuras de datos y esqueleto de API que ambas historias
necesitan

**⚠️ CRITICAL**: Ninguna tarea de US1/US2 puede iniciarse hasta completar esta fase

- [ ] T004 [P] Definir los modelos Pydantic inmutables (`frozen=True`)
      `GameState`, `Jugada` (colocar/mover) y `ErrorJugada` en
      `backend/src/models/game_state.py`, exactamente según el esquema de
      `data-model.md` (base estructural para todo CA-M-01 a CA-M-15)
- [ ] T005 [P] Implementar `comprobar_victoria(board)` evaluando las 8 líneas
      fijas (3 filas, 3 columnas, 2 diagonales) en
      `backend/src/engine/win_detection.py` (usado por CA-M-05, CA-M-06,
      CA-M-13)
- [ ] T006 Crear el almacén en memoria (`dict[str, GameState]`) y el
      esqueleto de la app FastAPI en `backend/src/main.py`, montando un
      router vacío `backend/src/api/games.py` (base de infraestructura para
      todos los endpoints de US1/US2)

**Checkpoint**: Modelos y esqueleto de API listos — US1 y US2 pueden
implementarse en paralelo si hay más de una persona

---

## Phase 3: Modalidad Clásica (Priority: P1) 🎯 MVP

**Goal**: Partida completa jugable en modalidad clásica vía API: alternancia
de turnos, validación de jugadas y detección de victoria/empate

**Independent Test**: Ejecutar `pytest backend/tests/unit/test_engine_rules.py
backend/tests/contract/test_games_api.py -k classic` y validar
manualmente con `quickstart.md` (sección "partida clásica hasta victoria")

### Tests para Modalidad Clásica (escribir primero, deben fallar)

- [ ] T007 [P] [US1] Tests unitarios del motor en modalidad clásica en
      `backend/tests/unit/test_engine_rules.py`: estado inicial (CA-M-01),
      colocar en turno válido (CA-M-02), rechazo de casilla ocupada
      (CA-M-03), rechazo fuera de turno (CA-M-04), detección de las 8
      líneas ganadoras (CA-M-05), empate por tablero lleno (CA-M-06),
      rechazo de jugada tras finalizar (CA-M-07)
- [ ] T008 [P] [US1] Tests de contrato para `POST /api/games` (mode
      "clasica"), `GET /api/games/{game_id}` y
      `POST /api/games/{game_id}/moves` en
      `backend/tests/contract/test_games_api.py` vía `TestClient`,
      cubriendo los mismos CA-M-01 a CA-M-07 a nivel HTTP (incluyendo el
      cuerpo `ErrorJugada` de las respuestas 422)

### Implementación para Modalidad Clásica

- [ ] T009 [US1] Implementar `crear_partida(mode)` en
      `backend/src/engine/rules.py` produciendo el `GameState` inicial con
      tablero vacío y turno "X" (CA-M-01)
- [ ] T010 [US1] Implementar `colocar_ficha(estado, jugada)` en
      `backend/src/engine/rules.py`: valida turno y casilla vacía, coloca la
      ficha y alterna el turno (CA-M-02, CA-M-03, CA-M-04)
- [ ] T011 [US1] Integrar `comprobar_victoria` y detección de empate por
      tablero lleno dentro de `aplicar_jugada(estado, jugada)` en
      `backend/src/engine/rules.py` (CA-M-05, CA-M-06)
- [ ] T012 [US1] Añadir rechazo de cualquier jugada cuando
      `estado.status != "en_curso"` en `aplicar_jugada` en
      `backend/src/engine/rules.py` (CA-M-07)
- [ ] T013 [US1] Implementar `POST /api/games` (creación con `mode:
      "clasica"`) en `backend/src/api/games.py`, devolviendo 201 con el
      `GameState` inicial (CA-M-01)
- [ ] T014 [US1] Implementar `GET /api/games/{game_id}` en
      `backend/src/api/games.py`, devolviendo 404 si no existe
- [ ] T015 [US1] Implementar `POST /api/games/{game_id}/moves` en
      `backend/src/api/games.py`, traduciendo excepciones de
      `aplicar_jugada` a respuestas 422 con el `ErrorJugada` correspondiente
      (CA-M-02 a CA-M-07)
- [ ] T016 [US1] Ejecutar `pytest backend/tests/unit/test_engine_rules.py
      backend/tests/contract/test_games_api.py -k classic` y confirmar que
      T007/T008 están en verde

**Checkpoint**: Modalidad clásica completamente jugable y testeada de forma
independiente — MVP entregable

---

## Phase 4: Modalidad Continua (Priority: P2)

**Goal**: Partida completa jugable en modalidad continua: fase de
colocación, transición a fase de movimiento, movimiento libre a cualquier
casilla vacía, y empate por repetición de posición

**Independent Test**: Ejecutar `pytest backend/tests/unit/test_engine_rules.py
backend/tests/contract/test_games_api.py -k continuous` y validar
manualmente con `quickstart.md` (sección "modalidad continua completa")

### Tests para Modalidad Continua (escribir primero, deben fallar)

- [ ] T017 [P] [US2] Tests unitarios del motor en modalidad continua en
      `backend/tests/unit/test_engine_rules.py`: estado inicial con 3
      fichas por jugador (CA-M-08), descuento de fichas al colocar
      (CA-M-09), transición a fase de movimiento (CA-M-10), movimiento a
      casilla no adyacente (CA-M-11), rechazo de ficha ajena o casilla
      ocupada en movimiento (CA-M-12), victoria en cualquier fase
      (CA-M-13), empate por repetición de posición 3 veces (CA-M-14),
      rechazo de jugada tras finalizar (CA-M-15)
- [ ] T018 [P] [US2] Tests de contrato para `POST /api/games` (mode
      "continua") y `POST /api/games/{game_id}/moves` (colocar y mover) en
      `backend/tests/contract/test_games_api.py`, cubriendo CA-M-08 a
      CA-M-15 a nivel HTTP

### Implementación para Modalidad Continua

- [ ] T019 [US2] Extender `crear_partida(mode)` en
      `backend/src/engine/rules.py` para inicializar `phase: "colocacion"`
      y `fichas_disponibles: {"X": 3, "O": 3}` cuando `mode = "continua"`
      (CA-M-08)
- [ ] T020 [US2] Extender `colocar_ficha` en `backend/src/engine/rules.py`
      para decrementar `fichas_disponibles` del jugador y alternar turno
      durante `phase = "colocacion"` (CA-M-09)
- [ ] T021 [US2] Implementar la transición automática de `phase:
      "colocacion"` a `phase: "movimiento"` cuando ambos jugadores llegan a
      0 fichas disponibles, en `backend/src/engine/rules.py` (CA-M-10)
- [ ] T022 [US2] Implementar `mover_ficha(estado, jugada)` en
      `backend/src/engine/rules.py`: mueve una ficha propia desde `from` a
      cualquier `to` vacío sin restricción de adyacencia (CA-M-11)
- [ ] T023 [US2] Añadir validación en `mover_ficha` que rechace mover una
      ficha ajena o mover hacia una casilla ocupada, en
      `backend/src/engine/rules.py` (CA-M-12)
- [ ] T024 [US2] Extender la integración de `comprobar_victoria` para que se
      evalúe tras cada `colocar_ficha` y `mover_ficha` en ambas fases, en
      `backend/src/engine/rules.py` (CA-M-13)
- [ ] T025 [US2] Implementar el contador interno `posiciones_vistas` y la
      regla de empate al alcanzar 3 repeticiones de la misma posición
      exacta durante `phase = "movimiento"`, en
      `backend/src/engine/repetition.py`, integrado en `aplicar_jugada`
      (CA-M-14)
- [ ] T026 [US2] Añadir rechazo de movimientos antes de completar la fase de
      colocación (`fase_incorrecta`) y de cualquier jugada tras
      `status != "en_curso"` en modalidad continua, en
      `backend/src/engine/rules.py` (CA-M-15)
- [ ] T027 [US2] Conectar `mode: "continua"` en `POST /api/games` y en
      `POST /api/games/{game_id}/moves` (tipo `"mover"`) en
      `backend/src/api/games.py` (CA-M-08 a CA-M-15 expuestos vía HTTP)
- [ ] T028 [US2] Ejecutar `pytest backend/tests/unit/test_engine_rules.py
      backend/tests/contract/test_games_api.py -k continuous` y confirmar
      que T017/T018 están en verde

**Checkpoint**: Ambas modalidades (clásica y continua) completamente
funcionales y testeadas de forma independiente

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Casos límite transversales a ambas modalidades

- [ ] T029 [P] Añadir validación de coordenadas fuera de rango
      (`fuera_de_rango`) compartida por `colocar_ficha` y `mover_ficha` en
      `backend/src/engine/rules.py` (edge case de `spec.md`)
- [ ] T030 [P] Ejecutar manualmente la validación end-to-end de
      `quickstart.md` (ambas modalidades) contra el servidor levantado con
      `uvicorn`
- [ ] T031 Revisar que `GET /api/games/{game_id}` refleja siempre el
      `GameState` completo y consistente tras cualquier combinación de
      tareas anteriores (T004-T028), en `backend/src/api/games.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciarse de inmediato
- **Foundational (Phase 2)**: Depende de Setup — bloquea ambas historias
- **US1 (Phase 3)**: Depende de Foundational — sin dependencia de US2
- **US2 (Phase 4)**: Depende de Foundational; reutiliza `colocar_ficha` y la
  integración de victoria creadas en US1 (T010, T011), por lo que en la
  práctica se implementa después de US1 aunque no dependa de sus endpoints
- **Polish (Phase 5)**: Depende de que US1 y US2 estén completas

### Parallel Opportunities

- T002 y T003 en paralelo tras T001
- T004 y T005 en paralelo dentro de Foundational
- T007 y T008 en paralelo (tests de US1)
- T017 y T018 en paralelo (tests de US2)
- T029 y T030 en paralelo dentro de Polish

---

## Parallel Example: Modalidad Clásica (US1)

```bash
# Lanzar juntos los tests de US1 (deben fallar antes de implementar):
Task: "Tests unitarios del motor en modalidad clásica en backend/tests/unit/test_engine_rules.py"
Task: "Tests de contrato para /api/games en backend/tests/contract/test_games_api.py"
```

---

## Implementation Strategy

### MVP First (Modalidad Clásica)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (bloquea todo lo demás)
3. Completar Phase 3: Modalidad Clásica (US1)
4. **Detener y validar**: correr `quickstart.md` sección clásica
5. Commitear cada tarea según Principio IV: `T-00N: descripción (CA-M-XX)`

### Entrega Incremental

1. Setup + Foundational → base lista
2. US1 (Modalidad Clásica) → MVP jugable, demo posible
3. US2 (Modalidad Continua) → añade la segunda modalidad sin romper la
   primera
4. Polish → casos límite transversales
