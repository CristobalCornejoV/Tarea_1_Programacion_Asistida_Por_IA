# Implementation Plan: Agentes de Juego

**Branch**: `002-agentes-de-juego` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-agentes-de-juego/spec.md`

**Note**: Este plan se apoya en el `GameState` y los contratos ya definidos en
[`../001-motor-tres-en-raya/data-model.md`](../001-motor-tres-en-raya/data-model.md)
y [`../001-motor-tres-en-raya/contracts/games-api.md`](../001-motor-tres-en-raya/contracts/games-api.md).
Los agentes son consumidores de solo lectura de ese estado; no redefinen
reglas de tablero, turnos ni victoria/empate.

## Summary

Implementar tres agentes de juego (Sencillo, Medio, Complejo) como funciones
puras de Python, expuestas mediante un endpoint FastAPI independiente del
motor: dado un `GameState` (o el subconjunto necesario de él), cada agente
devuelve una `Jugada` con el mismo esquema JSON que consume
`POST /api/games/{game_id}/moves` (spec 001), de modo que el frontend (spec
003) puede reenviar la respuesta del agente directamente al motor sin
transformarla.

## Technical Context

**Language/Version**: Python 3.11 (mismo backend que la spec 001)

**Primary Dependencies**: FastAPI + Uvicorn, Pydantic (reutiliza los modelos
de `backend/src/models/game_state.py` de la spec 001); `random` de la
librería estándar para los componentes aleatorios de los agentes Sencillo y
Medio

**Storage**: En memoria de proceso; el agente Complejo mantiene una caché de
memoización (`dict` posición canónica -> resultado óptimo) que persiste
mientras el proceso backend esté vivo (memoria persistente *entre partidas*,
no entre reinicios del servidor — ver `research.md` Decisión 3)

**Testing**: Pytest (`tests/unit` para la lógica de cada agente,
`tests/contract` para el endpoint, y un test de simulación estadística para
CA-A-07: 100 partidas Sencillo vs. Complejo)

**Target Platform**: Mismo proceso backend que el motor (spec 001); los
agentes se registran como un router adicional en la misma app FastAPI

**Project Type**: Web application (backend + frontend, comparte repositorio
con las specs 001 y 003)

**Performance Goals**: Cada respuesta de jugada de cualquier agente, en
cualquier nivel, SHALL completarse en menos de 1 segundo (Principio VI de la
constitución, y SC-004/CA-A-10 de esta spec) — condiciona directamente la
elección del algoritmo del agente Complejo (ver `research.md` Decisión 2)

**Constraints**: Los agentes MUST comportarse como funciones puras desde la
perspectiva del llamador (Principio II): misma entrada (estado de tablero +
jugador) produce la misma decisión determinista, salvo los componentes
explícitamente aleatorios de Sencillo y de la rama de azar de Medio, cuya
aleatoriedad es una propiedad especificada del comportamiento, no un efecto
colateral oculto

**Scale/Scope**: Tres niveles de agente, un endpoint por jugada; sin
requisitos de escalabilidad más allá de servir una partida interactiva y
ejecutar simulaciones de validación de 100 partidas en tiempo de test

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| I. Stack Tecnológico Fijo | PASS — mismo backend FastAPI/Pytest que la spec 001; sin dependencias nuevas de UI |
| II. Motor y Agentes como Funciones/Endpoints Puros | PASS — cada agente es `decidir_jugada(estado) -> Jugada`; la memoización del agente Complejo es una optimización interna determinista, no estado oculto que cambie el resultado |
| III. Test-First con Cobertura de CA-* | PASS (gate de proceso) — CA-A-01..09 tendrán tests antes de cerrar tareas, incluyendo el test estadístico obligatorio de CA-A-07 |
| IV. Disciplina de Commits Atómicos | PASS (gate de proceso) |
| V. Corrección de Bugs Dirigida por la Especificación | PASS (gate de proceso) |
| VI. Rendimiento en Tiempo Real (<1s) | PASS — condiciona la Decisión 2 de `research.md`: el agente Complejo usa minimax con poda alfa-beta (espacio de estados de tres en raya es pequeño, <1s incluso sin memoización; la memoización es una mejora, no un requisito de rendimiento) |

Sin violaciones. No se requiere `Complexity Tracking`.

## Project Structure

### Documentation (this feature)

```text
specs/002-agentes-de-juego/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output — esquemas de request/response de agentes
├── quickstart.md         # Phase 1 output
└── contracts/            # Phase 1 output
    └── agents-api.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── game_state.py       # Reutilizado de la spec 001 (sin cambios)
│   ├── engine/                 # Reutilizado de la spec 001 (sin cambios)
│   ├── agents/
│   │   ├── simple.py           # Agente Sencillo: selección aleatoria uniforme
│   │   ├── medium.py           # Agente Medio: ganar > bloquear > azar
│   │   ├── complex.py          # Agente Complejo: minimax + poda alfa-beta + memoización
│   │   └── shared.py           # Utilidades comunes: listar jugadas legales, simular jugada
│   └── api/
│       ├── games.py            # Reutilizado de la spec 001 (sin cambios)
│       └── agents.py           # Router FastAPI: POST /api/agents/{level}/move
└── tests/
    ├── unit/
    │   ├── test_agent_simple.py
    │   ├── test_agent_medium.py
    │   └── test_agent_complex.py
    ├── contract/
    │   └── test_agents_api.py
    └── integration/
        └── test_simple_vs_complex_100_games.py   # CA-A-07 / SC-002

frontend/
└── js/
    └── api.js                  # Se amplía (spec 003) con llamada a /api/agents/{level}/move
```

**Structure Decision**: Se añade `backend/src/agents/` como paquete
independiente de `backend/src/engine/`: los agentes importan y usan las
funciones puras del motor (para listar jugadas legales, simular resultados y
comprobar victoria) pero el motor no importa nada de `agents/` — dependencia
en un solo sentido, preservando que el motor pueda evolucionar (o probarse)
sin conocer la existencia de los agentes.

## Complexity Tracking

*Sin violaciones del Constitution Check; tabla omitida intencionalmente.*
