# Matriz de trazabilidad

Recorrido navegable desde criterios de aceptación hacia tareas, commits y
pruebas. Los commits agrupados se mantienen como evidencia histórica; las
tareas individuales están detalladas en cada `tasks.md`.

| Criterios | Tareas | Commit(s) principal(es) | Prueba automatizada |
|---|---|---|---|
| CA-M-01 a CA-M-07 | [`001/tasks.md`](specs/001-motor-tres-en-raya/tasks.md) T004-T016 | `7e585ff`, `e02b441`, `e0f6dca` | [`test_engine_rules.py`](backend/tests/unit/test_engine_rules.py), [`test_games_api.py`](backend/tests/contract/test_games_api.py) |
| CA-M-08 a CA-M-15 | [`001/tasks.md`](specs/001-motor-tres-en-raya/tasks.md) T017-T030 | `54ca823`, `b32e20b`, `02a74ca`, `9a195b6` | [`test_engine_rules.py`](backend/tests/unit/test_engine_rules.py), [`test_games_api.py`](backend/tests/contract/test_games_api.py) |
| CA-A-01 y CA-A-02 | [`002/tasks.md`](specs/002-agentes-de-juego/tasks.md) T002-T008 | `cdb7c9b`, `f7a3a70` | [`test_agent_simple.py`](backend/tests/unit/test_agent_simple.py), [`test_agents_api.py`](backend/tests/contract/test_agents_api.py) |
| CA-A-03 a CA-A-06 | [`002/tasks.md`](specs/002-agentes-de-juego/tasks.md) T009-T016 | `8142579` | [`test_agent_medium.py`](backend/tests/unit/test_agent_medium.py), [`test_agents_api.py`](backend/tests/contract/test_agents_api.py) |
| CA-A-07 | [`002/tasks.md`](specs/002-agentes-de-juego/tasks.md) T019 | `8142579`, `04db538` | [`test_simple_vs_complex_100_games.py`](backend/tests/integration/test_simple_vs_complex_100_games.py) |
| CA-A-08 y CA-A-09 | [`002/tasks.md`](specs/002-agentes-de-juego/tasks.md) T017-T024 | `8142579`, `04db538` | [`test_agent_complex.py`](backend/tests/unit/test_agent_complex.py), [`test_agents_api.py`](backend/tests/contract/test_agents_api.py) |
| CA-A-10 | [`002/tasks.md`](specs/002-agentes-de-juego/tasks.md) T029-T030 | `6952a4f` | [`test_agents_api.py`](backend/tests/contract/test_agents_api.py) |
| CA-I-01 a CA-I-04 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T007-T011 | `a8e7aa8`, `7c2bbe2` | [`test_ui_flows.py::test_configuracion_inicial`](tests/e2e/test_ui_flows.py) |
| CA-I-05 a CA-I-08 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T012-T016 | `821a52b`, `67fe4ff`, `5c28abf` | [`test_ui_flows.py::test_jugar_partida`](tests/e2e/test_ui_flows.py), [`test_ui_integration.py`](tests/e2e/test_ui_integration.py) |
| CA-I-09 y CA-I-10 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T017-T020 | `821a52b`, `fd83771`, `5c28abf` | [`test_ui_flows.py::test_espera_agente`](tests/e2e/test_ui_flows.py), [`test_ui_integration.py`](tests/e2e/test_ui_integration.py) |
| CA-I-11 y CA-I-12 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T021-T024 | `2737fda`, `11ba7b3`, `5c28abf` | [`test_ui_flows.py::test_modalidad_continua_movimiento`](tests/e2e/test_ui_flows.py), [`test_ui_integration.py`](tests/e2e/test_ui_integration.py) |
| CA-I-13 a CA-I-15 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T025-T028 | `cf748e7`, `68d2b89`, `5c28abf` | [`test_ui_flows.py::test_marcador_y_reinicio`](tests/e2e/test_ui_flows.py), [`test_ui_integration.py`](tests/e2e/test_ui_integration.py) |
| CA-I-16 a CA-I-18 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T029-T034 | `ff7aac9`, `670f3bd`, `5c28abf` | [`test_ui_flows.py::test_operacion_por_teclado`](tests/e2e/test_ui_flows.py), [`test_ui_integration.py`](tests/e2e/test_ui_integration.py) |
| CA-I-19 a CA-I-22 | [`003/tasks.md`](specs/003-interfaz-grafica/tasks.md) T035-T042 | `95ba571`, `dff9ea2` | Pruebas `test_responsive_*` de [`test_ui_flows.py`](tests/e2e/test_ui_flows.py) |

## Caso spec-first demostrable

1. Se detectó que Complejo podía bloquearse o devolver `colocar` durante el
   movimiento continuo.
2. Se actualizó primero CA-A-10, FR-009, `research.md`, el contrato y T029-T031.
3. Se añadieron pruebas de regresión para caché, legalidad y tiempo.
4. Se implementó la estrategia continua acotada y el aislamiento de caché.
5. La suite completa se ejecutó en verde.
