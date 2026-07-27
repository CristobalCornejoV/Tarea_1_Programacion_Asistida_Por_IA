# Data Model: Interfaz Gráfica del Juego Tres en Raya

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

> A diferencia de `001-motor-tres-en-raya/data-model.md`, estas entidades
> **no** se serializan hacia ningún backend: viven exclusivamente en memoria
> del navegador como estado de presentación. El único estado que cruza la
> red es el `GameState` y la `Jugada` ya definidos en la spec 001 y 002.

## Entidad: `EstadoUI`

| Campo | Tipo | Descripción |
|---|---|---|
| `pantalla` | `"configuracion"` \| `"en_juego"` \| `"esperando_agente"` \| `"terminada"` | Uno de los 4 estados de UI de `spec.md` |
| `configuracion` | `ConfiguracionPartida` \| `null` | `null` mientras `pantalla = "configuracion"` y no se ha confirmado el inicio |
| `game_state` | `GameState` \| `null` | Última copia del `GameState` recibida del motor (spec 001); `null` antes de crear la partida |
| `foco_actual` | `string` (id de elemento) | Elemento con foco de teclado vigente (CA-I-17) |
| `casilla_seleccionada` | `{ row: int, col: int }` \| `null` | Solo relevante en modalidad continua, fase de movimiento: ficha propia elegida para mover (CA-I-12) |

**Transiciones válidas** (ver también el diagrama de `spec.md` Key Entities):

```text
configuracion --(confirmar inicio válido)--> en_juego
en_juego --(turno de un agente)--> esperando_agente
esperando_agente --(respuesta del agente aplicada)--> en_juego | terminada
en_juego --(status: victoria|empate recibido del motor)--> terminada
terminada --(reiniciar)--> en_juego   # misma configuración, nueva partida, marcador conservado
```

## Entidad: `ConfiguracionPartida`

| Campo | Tipo | Descripción |
|---|---|---|
| `modo` | `"humano_vs_humano"` \| `"humano_vs_agente"` | CA-I-02 |
| `nivel_agente` | `"sencillo"` \| `"medio"` \| `"complejo"` \| `null` | Requerido solo si `modo = "humano_vs_agente"` (CA-I-02) |
| `ficha_jugador_1` | `"X"` \| `"O"` | Ficha del primer jugador humano; la del segundo (humano o agente) es la contraria |
| `modalidad` | `"clasica"` \| `"continua"` | Se envía tal cual como `mode` a `POST /api/games` (spec 001) |

**Validación** (CA-I-04): `ConfiguracionPartida` solo se considera completa
—y habilita el botón de inicio— cuando `modo`, `ficha_jugador_1` y
`modalidad` tienen valor, y `nivel_agente` tiene valor si
`modo = "humano_vs_agente"`.

## Entidad: `MarcadorSesion`

| Campo | Tipo | Descripción |
|---|---|---|
| `victorias_x` | `int` | Partidas ganadas por la ficha X en la sesión (CA-I-13) |
| `victorias_o` | `int` | Partidas ganadas por la ficha O en la sesión (CA-I-13) |
| `empates` | `int` | Partidas empatadas en la sesión (CA-I-13) |

Se incrementa exactamente una vez por cada `GameState` recibido con
`status != "en_curso"` (CA-I-14), y se conserva sin cambios a través de
cualquier número de reinicios de partida (CA-I-15).

## Relación con las specs 001 y 002

- `EstadoUI.game_state` es siempre una copia de solo lectura del último
  `GameState` devuelto por `POST /api/games` / `POST /api/games/{id}/moves`
  (spec 001); la interfaz nunca deriva `status`, `winner` o `winning_line`
  por sí misma.
- `casilla_seleccionada` y el resaltado de fichas movibles (CA-I-11) se
  calculan comparando `game_state.board`, `game_state.turn` y
  `game_state.phase` contra la ficha del jugador humano — sin evaluar
  legalidad de movimiento: la interfaz solo *sugiere* visualmente candidatos
  (cualquier ficha propia; cualquier casilla vacía, según CA-M-11 de la
  spec 001), y es el motor quien valida y puede rechazar con un código de
  `error` (spec 001, `contracts/games-api.md`) si la sugerencia visual fuera
  incorrecta por algún motivo no anticipado.
