# Guion de presentación - 10 minutos

## 0:00-1:00 - Objetivo y flujo SDD

- Mostrar el objetivo del producto.
- Abrir constitución y las tres specs.
- Explicar `constitution → specify → plan → tasks → implement`.

## 1:00-3:00 - Partida clásica

- Configurar Humano vs. Humano, modalidad Clásica.
- Mostrar turno y ficha.
- Intentar una casilla ocupada y comprobar que el tablero no cambia.
- Completar una victoria y mostrar línea ganadora, bloqueo y marcador.

## 3:00-5:30 - Modalidad continua

- Configurar Humano vs. Agente, modalidad Continua, nivel Complejo.
- Colocar las seis fichas.
- Mostrar transición a movimiento, fichas movibles y destinos.
- Ejecutar al menos un movimiento del humano y uno del agente.

## 5:30-6:30 - Tres niveles

- Sencillo: elección legal aleatoria.
- Medio: demostrar un bloqueo inmediato.
- Complejo: explicar minimax óptimo en clásica y táctica acotada en continua.

## 6:30-7:30 - Interfaz

- Mostrar marcador persistente al reiniciar.
- Navegar con Tab y flechas; jugar con Enter/Espacio.
- Redimensionar a móvil para demostrar ausencia de scroll horizontal.

## 7:30-8:30 - Trazabilidad

Usar CA-A-10 como recorrido:

`spec.md → tasks.md T029/T030 → commit de cierre → test_agents_api.py`.

Abrir [`TRAZABILIDAD.md`](TRAZABILIDAD.md) para el resto de los criterios.

## 8:30-9:30 - Caso real spec-first

- Bug: Complejo + Continua superaba un segundo o reutilizaba una jugada
  clásica de tipo `colocar` durante movimiento.
- Corrección primero en CA-A-10, FR-009, research y contrato.
- Después prueba roja y estrategia acotada.
- Resultado: jugada legal en menos de un segundo y caché aislada.

## 9:30-10:00 - Evidencia y cierre

- Ejecutar o mostrar `pytest -q --browser chromium`.
- Indicar cantidad de pruebas aprobadas.
- Recordar que cualquier integrante debe poder explicar cualquier parte.

## Lista previa a presentar

- [ ] Sustituir la revisión pendiente del README por nombre del integrante.
- [ ] Tener servidor levantado en `http://localhost:8000`.
- [ ] Haber ejecutado la suite inmediatamente antes de la demo.
- [ ] Ensayar el recorrido en menos de diez minutos.

