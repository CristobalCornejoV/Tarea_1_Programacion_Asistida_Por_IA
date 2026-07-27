# Implementation Plan: Motor del Juego Tres en Raya

**Branch**: `001-motor-tres-en-raya` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-motor-tres-en-raya/spec.md`

**Note**: This plan is shared architecturally with `002-agentes-de-juego` and
`003-interfaz-grafica` — the three features form a single system (motor +
agentes en FastAPI, interfaz en Vanilla JS). El estado del tablero y los
contratos JSON definidos aquí son la fuente de verdad que consumen los otros
dos planes; ver [`data-model.md`](./data-model.md) y
[`contracts/`](./contracts/) para el detalle referenciado desde ellos.

## Summary

Implementar el motor de reglas del tres en raya (modalidad clásica y
continua) como un conjunto de funciones puras de Python, expuestas mediante
endpoints FastAPI independientes de cualquier lógica de agentes o de
interfaz. El estado del tablero se modela como una estructura inmutable:
cada jugada produce un nuevo `GameState` en lugar de mutar el anterior. La
comunicación con el frontend (y con los agentes de la spec 002) se realiza
exclusivamente mediante JSON serializado a partir de ese `GameState`.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript ES2020+ sin
transpilación (frontend, ver spec 003)

**Primary Dependencies**: FastAPI + Uvicorn (servidor ASGI), Pydantic (modelos
inmutables/validación), ninguna librería de UI en el frontend

**Storage**: En memoria del proceso (diccionario `game_id -> GameState`); no
se requiere base de datos ni persistencia en disco para esta spec

**Testing**: Pytest (`tests/unit` para el motor puro, `tests/contract` para
los endpoints FastAPI vía `TestClient`)

**Target Platform**: Servidor backend (Linux/Windows) sirviendo una API HTTP
local; frontend estático servido por el propio backend o un servidor de
archivos simple

**Project Type**: Web application (backend + frontend, un solo repositorio)

**Performance Goals**: Cada respuesta de la API del motor (crear partida,
aplicar jugada, consultar estado) SHALL completarse en menos de 1 segundo
(alineado con el Principio VI de la constitución, que aplica en rigor a los
agentes pero se adopta aquí también como techo superior para toda la API)

**Constraints**: El motor MUST ser un conjunto de funciones puras (Principio
II): dado un `GameState` y una jugada, el resultado es siempre el mismo;
ningún endpoint MUST depender de estado oculto no representado en el
`GameState` devuelto

**Scale/Scope**: Un único proceso backend, partidas concurrentes acotadas al
uso de un curso (decenas de partidas simultáneas como máximo, sin requisitos
de alta disponibilidad)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| I. Stack Tecnológico Fijo | PASS — FastAPI (Python) + Pytest; sin frameworks de UI (el frontend de la spec 003 es Vanilla JS) |
| II. Motor y Agentes como Funciones/Endpoints Puros | PASS — el motor se diseña como funciones puras (`aplicar_jugada(estado, jugada) -> nuevo_estado`); los endpoints son una capa delgada sobre esas funciones |
| III. Test-First con Cobertura de CA-* | PASS (gate de proceso) — cada CA-M-01..15 tendrá al menos un test Pytest antes de cerrar su tarea en `tasks.md` |
| IV. Disciplina de Commits Atómicos | PASS (gate de proceso) — se aplicará al ejecutar `tasks.md`, no afecta al diseño técnico |
| V. Corrección de Bugs Dirigida por la Especificación | PASS (gate de proceso) — no aplica en fase de diseño inicial |
| VI. Rendimiento en Tiempo Real (<1s) | PASS — el motor no realiza búsqueda combinatoria (eso es responsabilidad de los agentes, spec 002); cada operación es O(1) sobre un tablero de 9 casillas |

Sin violaciones. No se requiere `Complexity Tracking`.

## Project Structure

### Documentation (this feature)

```text
specs/001-motor-tres-en-raya/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output — GameState compartido por las 3 specs
├── quickstart.md         # Phase 1 output
└── contracts/            # Phase 1 output — contratos HTTP del motor
    └── games-api.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── game_state.py      # GameState, Board, Move (Pydantic, inmutables)
│   ├── engine/
│   │   ├── rules.py           # aplicar_jugada, validar_jugada (funciones puras)
│   │   ├── win_detection.py   # comprobar_victoria (8 alineaciones)
│   │   └── repetition.py      # conteo de posiciones (modalidad continua)
│   ├── api/
│   │   └── games.py           # Router FastAPI: POST/GET /api/games...
│   └── main.py                # App FastAPI, monta routers de motor y agentes
└── tests/
    ├── unit/
    │   └── test_engine_rules.py
    └── contract/
        └── test_games_api.py

frontend/
├── index.html
├── css/
└── js/
    └── api.js                 # Cliente fetch hacia /api/games (consumido por spec 003)
```

**Structure Decision**: Aplicación web de un solo repositorio con `backend/`
(FastAPI, motor y agentes) y `frontend/` (Vanilla JS). El motor vive en
`backend/src/engine/` como funciones puras sin dependencia de FastAPI; el
router `backend/src/api/games.py` es la única capa que conoce HTTP. Esta
misma estructura de repositorio es compartida por las specs 002 y 003 (ver
sus planes), que añaden `backend/src/agents/`, `backend/src/api/agents.py`, y
el resto de `frontend/js/` respectivamente.

## Complexity Tracking

*Sin violaciones del Constitution Check; tabla omitida intencionalmente.*
