# Data Model: Agentes de Juego

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

> Extiende el modelo de datos base definido en
> [`../001-motor-tres-en-raya/data-model.md`](../001-motor-tres-en-raya/data-model.md).
> No redefine `GameState`; solo añade los esquemas de entrada/salida propios
> del endpoint de agentes.

## Entidad: `SolicitudJugadaAgente` (request)

Subconjunto de `GameState` necesario para decidir o rechazar una solicitud
(sin `game_id`, `winner` ni `winning_line`):

| Campo | Tipo | Descripción |
|---|---|---|
| `board` | `Casilla[3][3]` | Mismo formato que en `GameState` |
| `mode` | `"clasica"` \| `"continua"` | Modalidad de la partida |
| `phase` | `"colocacion"` \| `"movimiento"` \| `null` | Solo relevante si `mode = "continua"` |
| `turn` | `"X"` \| `"O"` | Jugador para el que se solicita la jugada |
| `fichas_disponibles` | `{ "X": int, "O": int }` \| `null` | Igual que en `GameState`; `null` fuera de fase de colocación |
| `status` | `"en_curso"` \| `"victoria"` \| `"empate"` | Permite rechazar una partida finalizada; por compatibilidad su valor por defecto es `"en_curso"` |

El endpoint verifica además la existencia de una línea ganadora directamente
en `board`, por lo que no depende únicamente de que el cliente envíe un
`status` correcto.

## Entidad: `Jugada` (response)

Idéntica en forma a la `Jugada` definida en
`../001-motor-tres-en-raya/data-model.md`, **sin** el campo `player` (el
nivel y el `turn` de la solicitud ya identifican implícitamente para quién
juega el agente; el campo `player` se añade, si se desea, en el cliente antes
de reenviarla al motor):

**Colocar**:

```json
{ "type": "colocar", "to": { "row": 0, "col": 0 } }
```

**Mover** (solo `mode: "continua"`, `phase: "movimiento"`):

```json
{ "type": "mover", "from": { "row": 0, "col": 0 }, "to": { "row": 1, "col": 1 } }
```

## Entidad: `MemoriaPersistente` (interna del agente Complejo)

No forma parte de ningún contrato JSON público; es un detalle de
implementación del agente Complejo:

| Campo | Tipo | Descripción |
|---|---|---|
| clave | `string` | Representación canónica de `(mode, phase, board, turn)` |
| valor | `{ "mejor_jugada": Jugada, "valor_minimax": int }` | Resultado ya evaluado, reutilizado en llamadas futuras (CA-A-09) |

Esta caché vive en memoria del proceso backend y se comparte entre todas las
partidas servidas por ese proceso (no entre reinicios del servidor — ver
`research.md` Decisión 3).

## Relación con la spec 003 (interfaz)

La interfaz nunca construye directamente una `SolicitudJugadaAgente`: la
arma a partir del `GameState` que ya tiene (recibido del motor), extrayendo
únicamente los campos necesarios. La `Jugada` devuelta por el agente se
reenvía al motor añadiendo el campo `player` (igual al `turn` vigente) para
formar el request de `POST /api/games/{game_id}/moves` (spec 001). La
interfaz MUST NOT interpretar ni validar la jugada del agente: la valida el
motor al aplicarla.
