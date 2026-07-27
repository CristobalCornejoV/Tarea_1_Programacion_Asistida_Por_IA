# Research: Motor del Juego Tres en Raya

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

No quedaron marcadores `NEEDS CLARIFICATION` en el Technical Context del plan
(el stack está fijado por la constitución). Este documento registra las
decisiones de diseño técnico necesarias para pasar de la especificación a un
modelo de datos y contratos concretos.

## Decisión 1: Representación del tablero

- **Decision**: El tablero se representa como una matriz 3x3 (lista de 3
  listas de 3 elementos), fila-mayor, con valores `"X"`, `"O"` o `null` por
  casilla. Las coordenadas se expresan como `{"row": 0-2, "col": 0-2}`.
- **Rationale**: Es la representación más directa de mapear a JSON y a la
  cuadrícula visual de la interfaz (spec 003); evita traducir entre índices
  planos (0-8) y posiciones de fila/columna en cada capa.
- **Alternatives considered**: Lista plana de 9 elementos (más compacta, pero
  obliga a recalcular fila/columna en el frontend para resaltar filas,
  columnas y diagonales); notación algebraica tipo ajedrez (innecesaria para
  un tablero 3x3 sin ambigüedad).

## Decisión 2: Inmutabilidad del estado

- **Decision**: `GameState` se modela como un modelo Pydantic `frozen=True`.
  Cada función del motor (`aplicar_jugada`, `colocar_ficha`, `mover_ficha`)
  recibe un `GameState` y devuelve uno **nuevo**; nunca muta el recibido. El
  backend conserva únicamente el último `GameState` por partida en un
  diccionario en memoria (`game_id -> GameState`).
- **Rationale**: Cumple directamente el Principio II (funciones puras) y hace
  trivialmente testeable el motor con Pytest: mismas entradas, mismas
  salidas, sin efectos colaterales ocultos.
- **Alternatives considered**: Clase mutable con métodos que modifican el
  tablero in-place (más simple de escribir pero viola la pureza exigida y
  complica la detección de repetición de posiciones, que necesita comparar
  estados pasados).

## Decisión 3: Detección de victoria

- **Decision**: `comprobar_victoria(board)` evalúa las 8 líneas posibles (3
  filas, 3 columnas, 2 diagonales) como una lista fija de tuplas de 3
  coordenadas, y devuelve la primera línea completa con fichas iguales no
  vacías, o `None`.
- **Rationale**: Con un tablero de 3x3 fijo, una lista estática de las 8
  líneas es más simple, legible y rápida que un algoritmo genérico de
  detección de alineación (irrelevante en rendimiento a esta escala, pero
  relevante en claridad para el curso).
- **Alternatives considered**: Algoritmo genérico N-en-raya parametrizable
  (sobre-ingeniería fuera de alcance; el tablero es siempre 3x3 según la
  especificación).

## Decisión 4: Regla de repetición (modalidad continua)

- **Decision**: El backend mantiene, solo durante la fase de movimiento, un
  contador interno `posiciones_vistas: dict[str, int]` (no expuesto en el
  JSON público de `GameState`) donde la clave es una representación canónica
  del tablero (string de 9 caracteres). Tras cada jugada de movimiento, se
  incrementa el contador de la posición resultante; si algún valor alcanza 3,
  la partida se declara empatada (CA-M-14).
- **Rationale**: Evita recalcular el historial completo de jugadas en cada
  consulta; el contador es un detalle interno de implementación del motor
  (aún compatible con el Principio II, ya que sigue siendo determinista y
  reproducible a partir de la secuencia de jugadas aplicadas).
- **Alternatives considered**: Exponer el historial completo de posiciones en
  el JSON de `GameState` (innecesario para el frontend, incrementa el tamaño
  del contrato sin aportar valor de UI).

## Decisión 5: Superficie de la API HTTP

- **Decision**: Tres endpoints en `backend/src/api/games.py`:
  `POST /api/games` (crear partida), `GET /api/games/{game_id}` (consultar
  estado), `POST /api/games/{game_id}/moves` (aplicar una jugada). No existe
  endpoint de "reiniciar": el frontend simplemente crea una partida nueva
  (`POST /api/games`) conservando su marcador de sesión en el propio cliente
  (ver spec 003), ya que el marcador es un concepto de interfaz, no del
  motor.
- **Rationale**: Mantiene el motor mínimo y con una única responsabilidad;
  el "reinicio conservando marcador" (CA-I-15) es un requisito de interfaz
  que no requiere lógica adicional en el motor.
- **Alternatives considered**: Endpoint `PATCH /api/games/{game_id}/reset`
  (redundante con crear una partida nueva; añadiría estado mutable al motor
  sin necesidad).

## Decisión 6: Errores de jugada inválida

- **Decision**: Las jugadas inválidas devuelven HTTP 422 con un cuerpo
  `{"error": "<codigo>", "message": "<detalle>"}`, donde `<codigo>` es uno de:
  `casilla_ocupada`, `fuera_de_turno`, `ficha_ajena`, `fase_incorrecta`,
  `fuera_de_rango`, `partida_finalizada`. El `GameState` de la partida no se
  modifica (se conserva el mismo `game_id` con el mismo estado anterior).
- **Rationale**: Un código de error estable y enumerado permite que la
  interfaz (spec 003) muestre el aviso visual correcto (CA-I-08) sin tener
  que interpretar mensajes de texto libre, y permite testear cada código con
  Pytest de forma independiente.
- **Alternatives considered**: Devolver siempre 200 con un campo `valida:
  false` (mezcla semántica de éxito/fracaso en el código de estado HTTP,
  dificulta el manejo de errores estándar en `fetch`).
