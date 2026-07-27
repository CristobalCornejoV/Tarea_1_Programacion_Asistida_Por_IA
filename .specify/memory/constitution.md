<!--
Sync Impact Report
==================
Version change: [TEMPLATE] → 1.0.0
Rationale: Initial ratification. All placeholder tokens filled from the project's
founding principles for the first time (MAJOR: establishes the governance baseline).

Modified principles: N/A (initial creation, no prior named principles)

Added sections:
- Core Principles I-VI (Stack Tecnológico Fijo; Motor y Agentes como Funciones
  Puras; Test-First con Cobertura de Criterios de Aceptación; Disciplina de
  Commits Atómicos; Corrección de Bugs Dirigida por la Especificación;
  Rendimiento del Agente en Tiempo Real)
- Flujo de Trabajo y Convenciones (Section 2)
- Revisión de Ediciones Manuales (Section 3)
- Governance

Removed sections: none

Templates requiring updates:
- .specify/templates/plan-template.md ✅ reviewed — generic "Constitution Check"
  gate placeholder remains compatible, no edit required (gate content is
  populated per-feature by /speckit-plan from this file).
- .specify/templates/spec-template.md ✅ reviewed — no constitution-specific
  references to update.
- .specify/templates/tasks-template.md ✅ reviewed — generic task structure is
  compatible with the T-NNN / CA-X-NN convention introduced here; no edit
  required (task IDs are assigned per-feature by /speckit-tasks).
- .claude/skills/speckit-*/SKILL.md ✅ reviewed — no agent-specific or outdated
  naming found.
- README.md ⚠ pending — file does not exist yet in this repository. When
  created, it MUST document the manual-edit review process required by
  Principle V / Section 3.

Follow-up TODOs:
- TODO(README): create README.md and record the manual-edit review log
  location once the first manual edit (if any) occurs.
-->

# Constitución: Tres en Raya con Agentes de Juego

## Core Principles

### I. Stack Tecnológico Fijo

El proyecto MUST usar exclusivamente: backend en FastAPI (Python) para el motor
del juego y los agentes expuestos como endpoints; frontend en Vanilla
JS/HTML/CSS sin frameworks de UI (React, Vue, Angular u otros quedan
prohibidos); Pytest como único framework de pruebas automatizadas. Ninguna
tarea puede introducir una dependencia de UI compleja ni un framework de
testing alternativo sin una enmienda a esta constitución.

**Rationale**: Fijar el stack evita la fragmentación técnica en un proyecto de
curso con integrantes múltiples y tiempo limitado; simplifica la revisión
cruzada y garantiza que cualquier integrante pueda ejecutar y entender todo el
código sin curva de aprendizaje adicional.

### II. Motor y Agentes como Funciones/Endpoints Puros

El motor de juego (reglas, validación de jugadas, detección de fin de partida)
y los agentes (heurísticas, minimax, aleatorio, etc.) MUST implementarse como
funciones puras o endpoints sin estado oculto compartido entre llamadas: dada
la misma entrada (tablero + jugador), siempre producen la misma salida
verificable. La interfaz (frontend) MUST limitarse a consumir la API HTTP
expuesta por FastAPI; MUST NOT contener lógica de juego, validación de reglas
ni decisiones de agente en JavaScript.

**Rationale**: Separar completamente lógica de presentación permite testear el
motor y los agentes con Pytest de forma aislada y determinista, y evita bugs de
sincronización entre una copia de las reglas en el cliente y otra en el
servidor.

### III. Test-First con Cobertura de Criterios de Aceptación (NON-NEGOTIABLE)

Cada criterio de aceptación (CA-*) definido en una especificación MUST tener al
menos un test automatizado en Pytest que lo cubra ANTES de que la tarea que lo
implementa se considere cerrada. Una tarea no MUST cerrarse (ni commitearse
como completa) si existe algún CA-* asociado sin test, o si algún test
asociado está en rojo.

**Rationale**: Es el mecanismo central de control de calidad del curso (SDD):
la trazabilidad CA → test es lo que permite verificar objetivamente que una
tarea cumple la especificación, no solo que "parece funcionar".

### IV. Disciplina de Commits Atómicos

Cada tarea MUST corresponder a exactamente un commit, con mensaje en el
formato exacto `T-NNN: descripción (CA-X-NN)`, donde `T-NNN` es el identificador
de tarea y `CA-X-NN` referencia el/los criterios de aceptación cubiertos. Los
tests relacionados con esa tarea MUST estar en verde antes de crear el commit.
MUST NOT mezclarse cambios de múltiples tareas en un mismo commit, ni
commitear con tests fallando.

**Rationale**: Un historial de commits atómico y trazable a tareas y criterios
de aceptación permite auditar el progreso del curso y facilita el rollback
selectivo si una tarea introduce una regresión.

### V. Corrección de Bugs Dirigida por la Especificación

Cuando se detecta un bug, la corrección MUST aplicarse primero en la
especificación (spec) correspondiente, y el código MUST regenerarse a partir de
la especificación corregida. Se permiten ediciones manuales directas al código
únicamente como excepción, y en ese caso MUST documentarse en README.md
(motivo, alcance del cambio, y quién lo aplicó) y MUST recibir revisión humana
de un integrante distinto de quien la realizó antes de integrarse.

**Rationale**: Mantiene la especificación como fuente de verdad (spec-driven
development); sin este gate, el código y la spec divergen silenciosamente y el
curso deja de poder evaluar el proceso SDD, no solo el resultado.

### VI. Rendimiento del Agente en Tiempo Real

Todo agente de juego (aleatorio, heurístico, minimax u otro) MUST responder con
su jugada en menos de 1 segundo, en cualquier nivel de dificultad y en
cualquier estado válido del tablero. Este límite MUST verificarse mediante al
menos un test automatizado de rendimiento por agente.

**Rationale**: El tres en raya es un juego interactivo; una respuesta lenta del
agente rompe la experiencia de usuario y sugiere una implementación
ineficiente (p. ej. minimax sin poda) que además complicaría escalar el juego a
tableros o reglas más complejos.

## Flujo de Trabajo y Convenciones

Toda tarea del proyecto sigue el ciclo: (1) especificación con CA-* numerados
(`CA-X-NN`), (2) escritura de tests Pytest que cubran cada CA-* (deben fallar
inicialmente), (3) implementación mínima para poner los tests en verde, (4)
commit único en formato `T-NNN: descripción (CA-X-NN)`. Los identificadores de
tarea (`T-NNN`) MUST ser secuenciales y únicos dentro del proyecto. Ningún
endpoint de la API ni función del motor/agentes se considera "hecho" sin su
test correspondiente en verde.

## Revisión de Ediciones Manuales

Toda edición manual de código que no provenga de la regeneración desde una
especificación corregida (ver Principio V) MUST registrarse en README.md con:
fecha, tarea/bug relacionado, descripción del cambio, y nombre de la persona
que dio la revisión humana (que MUST ser un integrante distinto del autor del
cambio). No se permite mergear una edición manual sin este registro completo.

## Governance

Esta constitución prevalece sobre cualquier otra convención o preferencia
individual dentro del proyecto. Toda enmienda MUST documentarse en este
archivo con: descripción del cambio, nueva versión (siguiendo semver:
MAJOR para eliminación o redefinición incompatible de principios/gates, MINOR
para añadir un principio o expandir una guía de forma material, PATCH para
aclaraciones o correcciones de redacción) y fecha de enmienda. Cualquier
Pull Request o revisión de tarea MUST verificar cumplimiento de los seis
principios y de los tres GATEs (cobertura de tests por CA-*, un commit por
tarea con tests en verde, y corrección de bugs vía spec); una tarea que viole
un GATE no puede cerrarse hasta corregir la violación o documentar la excepción
conforme al Principio V.

**Version**: 1.0.0 | **Ratified**: 2026-07-26 | **Last Amended**: 2026-07-26
