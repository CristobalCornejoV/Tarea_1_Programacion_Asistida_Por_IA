# Data Model: Motor del Juego Tres en Raya

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

> Este modelo de datos es la **fuente de verdad compartida** por las tres
> specs del proyecto (`001-motor-tres-en-raya`, `002-agentes-de-juego`,
> `003-interfaz-grafica`). El motor produce y valida `GameState`; los
> agentes (spec 002) lo reciben como entrada de solo lectura; la interfaz
> (spec 003) lo consume tal cual, sin reinterpretar sus reglas.

## Principio de inmutabilidad

Todo `GameState` es **inmutable**: ninguna operación lo modifica en el
lugar. Aplicar una jugada (`aplicar_jugada(estado, jugada)`) SHALL devolver
siempre un `GameState` nuevo; el estado anterior permanece válido e
intacto (útil para depuración, historial y para la regla de repetición en
modalidad continua). Esta es la representación exacta que via API se
serializa a JSON.

## Entidad: `GameState`

| Campo | Tipo | Descripción |
|---|---|---|
| `game_id` | `string` (UUID) | Identificador único de la partida |
| `mode` | `"clasica"` \| `"continua"` | Modalidad elegida al crear la partida |
| `board` | `Casilla[3][3]` | Matriz 3x3 fila-mayor; `Casilla = "X" \| "O" \| null` |
| `turn` | `"X"` \| `"O"` | Ficha a la que corresponde jugar a continuación |
| `phase` | `"colocacion"` \| `"movimiento"` \| `null` | Solo relevante si `mode = "continua"`; `null` si `mode = "clasica"` |
| `fichas_disponibles` | `{ "X": int, "O": int }` \| `null` | Fichas aún no colocadas por jugador; solo si `mode = "continua"` y `phase = "colocacion"` — `null` en el resto de casos |
| `status` | `"en_curso"` \| `"victoria"` \| `"empate"` | Resultado actual de la partida |
| `winner` | `"X"` \| `"O"` \| `null` | Ficha ganadora si `status = "victoria"`; `null` en caso contrario |
| `winning_line` | `[[int,int],[int,int],[int,int]]` \| `null` | Las 3 coordenadas `[row, col]` de la línea ganadora si `status = "victoria"`; `null` en caso contrario |

**Invariantes**:

- `board` SHALL tener exactamente 3 filas de 3 elementos.
- `turn` SHALL alternar entre `"X"` y `"O"` en cada jugada válida aplicada;
  X SHALL ser el turno inicial de toda partida nueva (CA-M-01).
- `fichas_disponibles` únicamente tiene sentido durante `phase =
  "colocacion"` en modalidad continua; en modalidad clásica y en fase de
  movimiento su valor SHALL ser `null`.
- `status != "en_curso"` implica que ninguna jugada adicional SHALL ser
  aceptada (CA-M-07, CA-M-15).

**Campo interno no serializado**: el motor mantiene, únicamente en memoria de
proceso y solo durante `mode = "continua"`, un contador de posiciones vistas
(`posiciones_vistas: dict[str, int]`) usado para la regla de empate por
repetición (CA-M-14, ver `research.md` Decisión 4). No forma parte del JSON
público de `GameState` y ningún consumidor (agentes, interfaz) depende de él.

## Entidad: `Jugada` (Move) — request de entrada

Dos formas según el tipo de jugada:

**Colocar** (modalidad clásica siempre; modalidad continua en fase de
colocación):

| Campo | Tipo | Descripción |
|---|---|---|
| `player` | `"X"` \| `"O"` | Jugador que realiza la jugada |
| `type` | `"colocar"` | Tipo de jugada |
| `to` | `{ "row": int, "col": int }` | Casilla destino (debe estar vacía) |

**Mover** (solo modalidad continua, fase de movimiento):

| Campo | Tipo | Descripción |
|---|---|---|
| `player` | `"X"` \| `"O"` | Jugador que realiza la jugada |
| `type` | `"mover"` | Tipo de jugada |
| `from` | `{ "row": int, "col": int }` | Casilla de origen (debe contener una ficha propia) |
| `to` | `{ "row": int, "col": int }` | Casilla destino (debe estar vacía) |

## Entidad: `ErrorJugada` — respuesta de error

| Campo | Tipo | Descripción |
|---|---|---|
| `error` | `string` (enum) | Uno de: `casilla_ocupada`, `fuera_de_turno`, `ficha_ajena`, `fase_incorrecta`, `fuera_de_rango`, `partida_finalizada` |
| `message` | `string` | Descripción legible del motivo de rechazo |

## Diagrama de transición de estados (por partida)

```text
[creación] --> en_curso (colocacion)*  --> en_curso (movimiento)*  --> victoria | empate
                    |                              |
                    +-------- (solo continua) ------+
              * "colocacion"/"movimiento" solo existen si mode = "continua";
                en "clasica" no hay fases, solo en_curso -> victoria | empate.
```

Una vez alcanzado `victoria` o `empate`, el estado es terminal: no existen
transiciones salientes (CA-M-07, CA-M-15).

## Relación con las specs 002 y 003

- **002-agentes-de-juego**: los endpoints de agente reciben un subconjunto de
  `GameState` (board, mode, phase, turn, fichas_disponibles) como entrada de
  solo lectura y devuelven una `Jugada` con la misma forma definida aquí (ver
  `../002-agentes-de-juego/data-model.md`).
- **003-interfaz-grafica**: consume `GameState` tal cual para pintar tablero,
  turno, resultado y línea ganadora, y construye objetos `Jugada` a partir de
  la interacción del usuario (ver `../003-interfaz-grafica/data-model.md`).
  La interfaz MUST NOT reimplementar `comprobar_victoria` ni ninguna otra
  regla; solo lee los campos `status`, `winner` y `winning_line`.
