# Tres en Raya con Agentes de Juego

Aplicación web desarrollada mediante especificaciones para jugar tres en raya
en modalidad clásica o continua, como Humano vs. Humano o Humano vs. Agente.
Incluye tres niveles de agente, marcador de sesión, operación completa por
teclado y diseño responsive.

## Ejecutar localmente (3 pasos)

1. Instalar dependencias:
   `python -m pip install fastapi uvicorn pydantic pytest httpx pytest-playwright`
   y `python -m playwright install chromium`.
2. Levantar la aplicación desde la raíz del repositorio:
   `uvicorn backend.src.main:app --port 8000`.
3. Abrir `http://localhost:8000` y validar con
   `pytest -q --browser chromium`.

Requiere Python 3.11 o superior. El frontend no tiene build step ni
dependencias JavaScript.

## Funcionalidad

- Tablero 3x3 con victoria por fila, columna o diagonal.
- Modalidad clásica: colocación hasta victoria o empate.
- Modalidad continua: tres fichas por jugador y fase posterior de movimiento.
- Humano vs. Humano y Humano vs. Agente.
- Agentes Sencillo, Medio y Complejo.
- Marcador de victorias y empates durante la sesión.
- Interfaz operable con mouse, tacto y teclado.
- Layout responsive entre 320px y 1920px.

## Arquitectura

```text
frontend/                 Vanilla HTML, CSS y JavaScript
backend/src/engine/       Reglas puras del juego
backend/src/agents/       Estrategias Sencillo, Medio y Complejo
backend/src/api/          Contratos FastAPI
backend/tests/            Pruebas unitarias, contrato e integración
tests/e2e/                Pruebas de interfaz con Pytest + Playwright
specs/                    Spec, plan, tareas, contratos y decisiones SDD
```

La interfaz consume exclusivamente los endpoints del backend. No contiene
reglas de victoria, validación de movimientos ni heurísticas de agentes.

## Proceso SDD y trazabilidad

El flujo seguido es `constitution → specify → plan → tasks → implement`.

- Constitución: [`.specify/memory/constitution.md`](.specify/memory/constitution.md)
- Motor: [`specs/001-motor-tres-en-raya/`](specs/001-motor-tres-en-raya/)
- Agentes: [`specs/002-agentes-de-juego/`](specs/002-agentes-de-juego/)
- Interfaz: [`specs/003-interfaz-grafica/`](specs/003-interfaz-grafica/)
- Matriz CA → tarea → commit → test: [`TRAZABILIDAD.md`](TRAZABILIDAD.md)
- Guion de demostración: [`PRESENTACION.md`](PRESENTACION.md)

## Pruebas

La suite cubre motor, contratos HTTP, agentes, simulaciones estadísticas y
flujos E2E contra FastAPI real. Cada criterio de aceptación está relacionado
con al menos una tarea y una prueba en [`TRAZABILIDAD.md`](TRAZABILIDAD.md).

Última validación de entrega: **124 pruebas aprobadas** con
`pytest -q --browser chromium`.

## Declaración de uso de IA

Todas las especificaciones y artefactos del proceso SDD —constitución,
`spec.md`, `plan.md`, `tasks.md`, modelos de datos, contratos y decisiones de
investigación— fueron elaborados y versionados con **Spec Kit mediante Claude
Code**, siguiendo el flujo solicitado en la tarea.

La implementación original del backend —motor, agentes y API— fue realizada
con **Claude Code** a partir de esos artefactos. **OpenAI Codex** se utilizó
para la codificación de la interfaz gráfica, guiándose exclusivamente por la
spec 003 previamente creada y versionada.

Durante la revisión final, Codex también realizó las correcciones acotadas
T-029 a T-031 sobre los agentes: comportamiento de Complejo en modalidad
continua, aislamiento de caché y rechazo de partidas finalizadas. Estas
correcciones conservaron el enfoque spec-first: primero se actualizaron la
spec, el contrato y las tareas; después se modificaron las pruebas y el
código.

El uso de Codex queda declarado explícitamente como uso de IA fuera de la
herramienta original del flujo Spec Kit/Claude Code.

No se incorporó código desde fuentes externas sin declararlo. La
responsabilidad de revisar, comprender y explicar las especificaciones y el
código corresponde a los integrantes del grupo.

## Registro de herramientas y alcance

| Alcance | Herramienta declarada |
|---|---|
| Especificaciones y artefactos SDD | Spec Kit mediante Claude Code |
| Implementación original del backend | Claude Code |
| T-035 a T-050: interfaz gráfica, accesibilidad e integración E2E | OpenAI Codex, utilizando la spec 003 como fuente de verdad |
| T-029 a T-031: correcciones finales de agentes | OpenAI Codex, después de actualizar spec, contrato y tareas |
