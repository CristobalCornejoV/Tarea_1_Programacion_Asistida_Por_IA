# Implementation Plan: Interfaz Gráfica del Juego Tres en Raya

**Branch**: `003-interfaz-grafica` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-interfaz-grafica/spec.md`

**Note**: Este plan consume, sin redefinirlos, los contratos ya establecidos
en [`../001-motor-tres-en-raya/contracts/games-api.md`](../001-motor-tres-en-raya/contracts/games-api.md)
y [`../002-agentes-de-juego/contracts/agents-api.md`](../002-agentes-de-juego/contracts/agents-api.md).
La interfaz no define ningún endpoint propio ni ninguna regla de juego.

## Summary

Implementar la interfaz gráfica (Vanilla JS/HTML/CSS, sin frameworks) como
una capa de presentación y orquestación que consume exclusivamente la API
del motor (spec 001) y de los agentes (spec 002) vía `fetch`. La interfaz
mantiene únicamente estado de presentación (estado de UI, configuración
elegida, marcador de sesión); todo el estado de juego (`GameState`) proviene
siempre del backend y se pinta tal cual, sin reinterpretar sus reglas.

## Technical Context

**Language/Version**: JavaScript ES2020+ ejecutado directamente en el
navegador (sin transpilación ni bundler), HTML5, CSS3

**Primary Dependencies**: Ninguna librería de UI (Principio I de la
constitución); `fetch` nativo del navegador para consumir `backend/src/api/*`

**Storage**: Estado de UI y marcador de sesión en memoria del navegador
(variables JS de módulo); sin `localStorage` ni cookies, dado que el
marcador es explícitamente volátil por sesión (ver Assumptions de `spec.md`)

**Testing**: Pytest — dado que la constitución fija Pytest como único
framework de pruebas del proyecto y no permite frameworks de testing JS, la
verificación automatizada de la interfaz se limita a lo que Pytest puede
cubrir vía un navegador controlado (Playwright para Python) sobre los flujos
críticos (CA-I-01 a CA-I-18); la validación exploratoria de UX/estética se
hace manualmente contra `quickstart.md` (ver `research.md` Decisión 4)

**Target Platform**: Navegador web de escritorio moderno, servido como
archivos estáticos por el propio backend FastAPI (`StaticFiles`) o un
servidor de archivos simple en desarrollo

**Project Type**: Web application (frontend de un backend+frontend
compartido con las specs 001 y 002)

**Performance Goals**: El tablero SHALL habilitarse de nuevo en menos de 1
segundo tras recibir la jugada del agente (SC-004), heredado directamente
del límite de respuesta de los agentes (Principio VI de la constitución)

**Constraints**: La interfaz MUST NOT implementar ninguna regla de juego
(detección de victoria/empate, validación de jugada legal, heurísticas de
agente): toda decisión de negocio proviene de la respuesta HTTP del motor o
de los agentes; la interfaz solo interpreta campos ya resueltos (`status`,
`winner`, `winning_line`, códigos de `error`)

**Scale/Scope**: Una sola página (SPA minimalista sin router), cuatro
estados de UI (Configuración, En Juego, Esperando Agente, Terminada), un
tablero de 9 casillas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| I. Stack Tecnológico Fijo | PASS — Vanilla JS/HTML/CSS, sin frameworks de UI |
| II. Motor y Agentes como Funciones/Endpoints Puros | PASS — la interfaz consume la API sin reimplementar reglas; ver Constraints arriba |
| III. Test-First con Cobertura de CA-* | PASS (gate de proceso) — CA-I-01..18 tendrán al menos un test (Pytest + navegador controlado) antes de cerrar sus tareas |
| IV. Disciplina de Commits Atómicos | PASS (gate de proceso) |
| V. Corrección de Bugs Dirigida por la Especificación | PASS (gate de proceso) |
| VI. Rendimiento en Tiempo Real (<1s) | PASS — la interfaz no añade cómputo relevante; el límite de tiempo lo determina la respuesta del agente (spec 002), la interfaz solo debe reaccionar a ella sin demora perceptible |

Sin violaciones. No se requiere `Complexity Tracking`.

## Project Structure

### Documentation (this feature)

```text
specs/003-interfaz-grafica/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output — estado de UI (no persistido en backend)
├── quickstart.md         # Phase 1 output
└── contracts/            # Phase 1 output — contrato de consumo de la API (no HTTP propio)
    └── ui-consumption-contract.md
```

### Source Code (repository root)

```text
backend/
└── src/
    └── main.py                    # Se amplía (spec 001) para servir frontend/ como estáticos

frontend/
├── index.html                     # Estructura de las 4 pantallas/estados de UI
├── css/
│   └── styles.css                 # Estilos + estados de foco visibles (CA-I-17)
└── js/
    ├── api.js                     # Cliente fetch: /api/games, /api/agents (spec 001/002)
    ├── state.js                   # Estado de UI: estado actual, configuración, marcador de sesión
    ├── board.js                   # Render del tablero a partir de GameState; resaltado de línea ganadora
    ├── config-screen.js           # Pantalla de Configuración (CA-I-01 a CA-I-04)
    ├── game-screen.js             # Pantalla En Juego / Esperando Agente / Terminada (CA-I-05 a CA-I-12)
    ├── scoreboard.js               # Marcador de sesión y reinicio (CA-I-13 a CA-I-15)
    └── keyboard.js                 # Navegación y foco por teclado (CA-I-16 a CA-I-18)

tests/
└── e2e/
    └── test_ui_flows.py           # Pytest + navegador controlado sobre frontend/ servido localmente
```

**Structure Decision**: El frontend es puramente estático (`frontend/`) y no
requiere build step; `backend/src/main.py` (spec 001) monta
`frontend/` como archivos estáticos para servir la SPA desde el mismo
proceso que la API, evitando problemas de CORS en desarrollo. Los módulos JS
se organizan por responsabilidad (estado, tablero, pantallas, teclado) pero
ninguno contiene lógica de reglas de juego — todos delegan en `api.js`, que
es el único punto de contacto con el backend.

## Complexity Tracking

*Sin violaciones del Constitution Check; tabla omitida intencionalmente.*
