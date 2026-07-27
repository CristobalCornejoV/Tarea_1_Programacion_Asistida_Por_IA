---

description: "Task list for Agentes de Juego"
---

# Tasks: Agentes de Juego

**Input**: Design documents from `/specs/002-agentes-de-juego/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/agents-api.md](./contracts/agents-api.md), [research.md](./research.md)
**Feature dependency**: requiere que `001-motor-tres-en-raya` esté implementada
(reutiliza `backend/src/models/game_state.py` y
`backend/src/engine/{rules.py,win_detection.py}` sin modificarlos)

**Tests**: Incluidas y obligatorias — el Principio III de la constitución
exige al menos un test automatizado por cada CA-A-* antes de cerrar la tarea
que lo cubre.

**Organization**: Tareas agrupadas por historia de usuario (US1 = Agente
Sencillo, US2 = Agente Medio, US3 = Agente Complejo) para permitir
implementación y prueba independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: US1, US2 o US3
- Cada tarea indica ruta de archivo exacta y los CA-A-* que cubre

## Recordatorio de gates de la constitución

- Ninguna tarea se cierra sin que sus tests asociados estén en verde
  (Principio III).
- Cada tarea corresponde a un commit único: `T-NNN: descripción (CA-A-XX)`
  (Principio IV).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estructura de directorios y registro del router de agentes

- [X] T001 Crear `backend/src/agents/` y
      `backend/tests/integration/` (directorios nuevos sobre la estructura
      ya existente de `001-motor-tres-en-raya`), según `plan.md` → Project
      Structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Utilidades compartidas por los tres niveles de agente

**⚠️ CRITICAL**: Ninguna tarea de US1/US2/US3 puede iniciarse hasta completar
esta fase

- [X] T002 [P] Implementar `listar_jugadas_legales(estado: GameState) ->
      list[Jugada]` en `backend/src/agents/shared.py`, reutilizando
      `backend/src/models/game_state.py` de la spec 001 (colocar en modo
      clásico/fase colocación, mover en fase movimiento) — base de CA-A-01,
      CA-A-02, CA-A-03, CA-A-05, CA-A-08
- [X] T003 [P] Implementar `simular_jugada(estado: GameState, jugada:
      Jugada) -> GameState` en `backend/src/agents/shared.py`, como envoltorio
      de solo lectura sobre `aplicar_jugada` del motor (spec 001) — base de
      CA-A-03, CA-A-04, CA-A-08
- [X] T004 Crear el router FastAPI `backend/src/api/agents.py` con
      `POST /api/agents/{level}/move` (despacho por `level` a
      `sencillo`/`medio`/`complejo`, 404 si el nivel no existe) y montarlo en
      `backend/src/main.py`

**Checkpoint**: Utilidades y endpoint base listos — US1, US2 y US3 pueden
implementarse en paralelo si hay más de una persona (aunque US3 depende
conceptualmente de que exista US1 para su validación estadística, CA-A-07)

---

## Phase 3: Agente Sencillo (Priority: P1) 🎯 MVP

**Goal**: Un agente que juega, sobre cualquier tablero, una casilla legal
elegida al azar, sin usar información de turnos anteriores

**Independent Test**: `pytest backend/tests/unit/test_agent_simple.py
backend/tests/contract/test_agents_api.py`

### Tests para Agente Sencillo (escribir primero, deben fallar)

- [X] T005 [P] [US1] Test unitario en
      `backend/tests/unit/test_agent_simple.py`: toda jugada devuelta es
      legal para el tablero dado (CA-A-01), y sobre múltiples llamadas al
      mismo estado la distribución de casillas elegidas cubre todas las
      opciones legales sin depender de llamadas anteriores (CA-A-02)
- [X] T006 [P] [US1] Test de contrato en
      `backend/tests/contract/test_agents_api.py -k sencillo`:
      `POST /api/agents/sencillo/move` devuelve 200 con una `Jugada` legal
      para distintos estados de tablero (CA-A-01, CA-A-02)

### Implementación para Agente Sencillo

- [X] T007 [US1] Implementar `decidir_jugada(estado: GameState) -> Jugada`
      en `backend/src/agents/simple.py` usando `random.choice` sobre
      `listar_jugadas_legales(estado)` (T002), sin leer ni escribir ningún
      estado propio entre llamadas (CA-A-01, CA-A-02)
- [X] T008 [US1] Conectar `POST /api/agents/sencillo/move` en
      `backend/src/api/agents.py` a `simple.decidir_jugada` (CA-A-01,
      CA-A-02)
- [X] T009 [US1] Ejecutar `pytest backend/tests/unit/test_agent_simple.py
      backend/tests/contract/test_agents_api.py` y confirmar
      que T005/T006 están en verde

**Checkpoint**: Agente Sencillo completamente funcional y testeado de forma
independiente — MVP entregable

---

## Phase 4: Agente Medio (Priority: P2)

**Goal**: Un agente que gana si puede, bloquea si el rival puede ganar, y
si no juega al azar

**Independent Test**: `pytest backend/tests/unit/test_agent_medium.py
backend/tests/contract/test_agents_api.py`

### Tests para Agente Medio (escribir primero, deben fallar)

- [X] T010 [P] [US2] Test unitario en
      `backend/tests/unit/test_agent_medium.py`: juega la victoria
      inmediata cuando existe (CA-A-03), bloquea al rival cuando no tiene
      victoria propia y el rival amenaza ganar (CA-A-04), juega al azar
      cuando ninguna condición aplica (CA-A-05), y produce la misma
      decisión sin importar cómo se llegó al tablero actual —solo a partir
      del estado recibido— demostrando que no requiere estado propio entre
      llamadas (CA-A-06)
- [X] T011 [P] [US2] Test de contrato en
      `backend/tests/contract/test_agents_api.py -k medio`:
      `POST /api/agents/medio/move` sobre tableros con amenaza de victoria
      propia, amenaza del rival, y ninguna de las dos, verificando la
      jugada devuelta en cada caso (CA-A-03 a CA-A-06)

### Implementación para Agente Medio

- [X] T012 [US2] Implementar
      `detectar_jugada_ganadora(estado: GameState, jugador: str) ->
      Jugada | None` en `backend/src/agents/shared.py`, usando
      `simular_jugada` (T003) y `comprobar_victoria` del motor (spec 001) —
      utilidad reutilizada también por el Agente Complejo (CA-A-03,
      CA-A-04, CA-A-08)
- [X] T013 [US2] Implementar `decidir_jugada(estado: GameState) -> Jugada`
      en `backend/src/agents/medium.py` aplicando en orden: victoria propia
      (CA-A-03) → bloqueo de victoria del rival (CA-A-04) → azar sobre
      `listar_jugadas_legales` (CA-A-05)
- [X] T014 [US2] Verificar y documentar en
      `backend/src/agents/medium.py` que la función no lee ni escribe
      ningún estado propio entre llamadas: toda la "memoria de la partida
      en curso" exigida por CA-A-06 queda satisfecha por el `GameState`
      completo recibido en cada solicitud (ver `research.md` Decisión 1)
- [X] T015 [US2] Conectar `POST /api/agents/medio/move` en
      `backend/src/api/agents.py` a `medium.decidir_jugada` (CA-A-03 a
      CA-A-06)
- [X] T016 [US2] Ejecutar `pytest backend/tests/unit/test_agent_medium.py
      backend/tests/contract/test_agents_api.py` y confirmar que
      T010/T011 están en verde

**Checkpoint**: Agentes Sencillo y Medio completamente funcionales y
testeados de forma independiente

---

## Phase 5: Agente Complejo (Priority: P3)

**Goal**: Un agente que nunca pierde en modalidad clásica (juego óptimo vía
minimax con poda alfa-beta) y reutiliza memoria persistente entre partidas

**Independent Test**: `pytest backend/tests/unit/test_agent_complex.py
backend/tests/contract/test_agents_api.py
backend/tests/integration/test_simple_vs_complex_100_games.py`

### Tests para Agente Complejo (escribir primero, deben fallar)

- [X] T017 [P] [US3] Test unitario en
      `backend/tests/unit/test_agent_complex.py`: sobre un conjunto
      representativo de tableros de modalidad clásica (incluyendo
      posiciones donde solo el empate es alcanzable ante juego óptimo
      rival), el agente Complejo nunca elige una jugada que permita una
      derrota evitable (CA-A-08); y una segunda llamada sobre la misma
      posición ya evaluada reutiliza el resultado memorizado en lugar de
      recalcularlo (CA-A-09, verificable p. ej. instrumentando/mockeando el
      contador de invocaciones a minimax)
- [X] T018 [P] [US3] Test de contrato en
      `backend/tests/contract/test_agents_api.py -k complejo`:
      `POST /api/agents/complejo/move` responde 200 con una `Jugada` válida
      sobre distintos estados de modalidad clásica
- [X] T019 [P] [US3] Test de integración estadístico obligatorio en
      `backend/tests/integration/test_simple_vs_complex_100_games.py`:
      simula 100 partidas completas en modalidad clásica entre el agente
      Sencillo y el agente Complejo (alternando quién inicia como X),
      aplicando cada jugada a través del motor (spec 001), y verifica que
      el agente Complejo termina con 0 derrotas en las 100 partidas
      (**CA-A-07**, criterio estadístico obligatorio)

### Implementación para Agente Complejo

- [X] T020 [US3] Implementar la representación canónica de `(board, turn)`
      como clave de caché en `backend/src/agents/complex.py` (base de
      CA-A-09)
- [X] T021 [US3] Implementar `minimax(estado: GameState, jugador: str) ->
      tuple[Jugada, int]` con poda alfa-beta en `backend/src/agents/complex.py`,
      usando `listar_jugadas_legales` y `simular_jugada` (T002, T003),
      garantizando jugada óptima (victoria forzada si existe, empate en
      caso contrario) en modalidad clásica (CA-A-08)

      **Nota de implementación**: se usó negamax (formulación equivalente a
      minimax de un solo parámetro, valor siempre relativo a `estado.turn`)
      en lugar de una función `minimax(estado, jugador)` con parámetro de
      jugador explícito. Se detectó que el motor deja `turn` sin alternar
      tras una jugada ganadora (queda igual al ganador), lo que rompe la
      suposición de "el turno siempre alterna" en la que se apoyaría una
      memoización ingenua combinada con poda alfa-beta; la caché de
      transposición (T022) requirió además distinguir valores exactos de
      cotas (superior/inferior) para no reutilizar incorrectamente un valor
      podado bajo una ventana alfa-beta distinta. Ver docstrings de
      `complex.py` para el detalle.
- [X] T022 [US3] Añadir la caché de memoización
      `memo: dict[str, tuple[Jugada, int]]` en `backend/src/agents/complex.py`,
      consultada antes de invocar `minimax` y actualizada tras cada
      evaluación nueva, persistente en memoria de proceso entre partidas
      (CA-A-09)
- [X] T023 [US3] Implementar `decidir_jugada(estado: GameState) -> Jugada`
      en `backend/src/agents/complex.py` como punto de entrada público que
      usa la caché (T022) y `minimax` (T021)
- [X] T024 [US3] Conectar `POST /api/agents/complejo/move` en
      `backend/src/api/agents.py` a `complex.decidir_jugada` (CA-A-07,
      CA-A-08, CA-A-09)
- [X] T025 [US3] Ejecutar `pytest backend/tests/unit/test_agent_complex.py
      backend/tests/contract/test_agents_api.py
      backend/tests/integration/test_simple_vs_complex_100_games.py` y
      confirmar que T017/T018/T019 están en verde, incluyendo el criterio
      estadístico CA-A-07

**Checkpoint**: Los tres niveles de agente completamente funcionales,
testeados de forma independiente, y validados estadísticamente entre sí

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Requisitos transversales a los tres niveles de agente

- [X] T026 [P] Test de rendimiento en
      `backend/tests/contract/test_agents_api.py -k tiempo`: cada nivel
      (`sencillo`, `medio`, `complejo`) responde en menos de 1 segundo sobre
      cualquier estado de tablero válido (SC-004, Principio VI de la
      constitución)
- [X] T027 [P] Añadir rechazo (`422`) de solicitudes de jugada sobre
      tableros sin casillas legales disponibles o partidas ya finalizadas,
      compartido por los tres niveles, en `backend/src/agents/shared.py`
      (edge case de `spec.md`)

      **Nota**: al implementar esta tarea se detectó que `simple.decidir_jugada`
      (y por extensión los otros niveles) lanzaba `IndexError` sin capturar
      (`random.choice([])`) en vez de un 422 limpio cuando no había jugadas
      legales — exactamente el bug que esta tarea existe para corregir.
      Se agregó `asegurar_jugada_disponible` (shared.py) y se conectó en el
      router antes de invocar cualquier agente.
- [X] T028 Ejecutar manualmente la validación end-to-end de
      `quickstart.md` (bloqueo del rival, simulación de 100 partidas, y
      verificación de tiempos de respuesta)

      **Nota importante**: durante T025 (ejecución repetida de la suite
      completa) se detectó una falla intermitente real en
      `test_simple_vs_complex_100_games.py` (Complejo perdía en ~1 de cada
      5-15 corridas). Se aisló y corrigió un bug en `complex.py`: la caché
      de memoización guardaba también cotas (no solo valores exactos) de
      búsquedas podadas por alfa-beta; una cota obsoleta de un turno
      anterior de la misma partida se usaba para acotar alpha/beta de un
      turno posterior con una ventana distinta, provocando un corte
      prematuro que nunca llegó a evaluar la respuesta ganadora real del
      rival — llevando al agente Complejo a perder una partida que debía
      ganar. Corregido memoizando únicamente valores exactos (búsquedas no
      podadas: `alpha_original < mejor_valor < beta`); se agregó un test de
      regresión (`test_no_pierde_una_partida_previamente_reproducida_con_cache_persistente`
      en `test_agent_complex.py`) que reproduce el seed exacto que falló.
      Verificado con más de 5000 partidas simuladas sin ninguna derrota del
      Complejo tras la corrección.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Depende de que `001-motor-tres-en-raya` esté
  implementada (reutiliza sus modelos y motor)
- **Foundational (Phase 2)**: Depende de Setup — bloquea las tres historias
- **US1 (Phase 3)**: Depende de Foundational — sin dependencia de US2/US3
- **US2 (Phase 4)**: Depende de Foundational; reutiliza
  `detectar_jugada_ganadora` (T012) que también usa US3
- **US3 (Phase 5)**: Depende de Foundational; su test estadístico
  obligatorio (T019, CA-A-07) requiere que US1 (Agente Sencillo) ya exista
- **Polish (Phase 6)**: Depende de que US1, US2 y US3 estén completas

### Parallel Opportunities

- T002 y T003 en paralelo dentro de Foundational
- T005 y T006 en paralelo (tests de US1)
- T010 y T011 en paralelo (tests de US2)
- T017, T018 y T019 en paralelo (tests de US3)
- T026 y T027 en paralelo dentro de Polish

---

## Parallel Example: Agente Complejo (US3)

```bash
# Lanzar juntos los tests de US3 (deben fallar antes de implementar):
Task: "Test unitario de optimalidad y memoización en backend/tests/unit/test_agent_complex.py"
Task: "Test de contrato en backend/tests/contract/test_agents_api.py -k complejo"
Task: "Test estadístico obligatorio CA-A-07 en backend/tests/integration/test_simple_vs_complex_100_games.py"
```

---

## Implementation Strategy

### MVP First (Agente Sencillo)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (bloquea todo lo demás)
3. Completar Phase 3: Agente Sencillo (US1)
4. **Detener y validar**: correr `quickstart.md` con el agente Sencillo
5. Commitear cada tarea según Principio IV: `T-00N: descripción (CA-A-XX)`

### Entrega Incremental

1. Setup + Foundational → base lista
2. US1 (Agente Sencillo) → MVP jugable, demo posible
3. US2 (Agente Medio) → añade heurística sin romper Sencillo
4. US3 (Agente Complejo) → añade juego óptimo y valida CA-A-07 contra US1
5. Polish → rendimiento y casos límite transversales
