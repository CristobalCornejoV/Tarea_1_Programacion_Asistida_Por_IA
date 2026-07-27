# Contrato HTTP: API del Motor (`/api/games`)

**Feature**: [../spec.md](../spec.md) | **Modelo de datos**: [../data-model.md](../data-model.md)

Todas las respuestas usan `Content-Type: application/json`. El cuerpo de
éxito es siempre un `GameState` completo (ver `data-model.md`), de forma que
el cliente nunca necesita fusionar estado parcial.

## `POST /api/games`

Crea una partida nueva.

**Request body**:

```json
{ "mode": "clasica" }
```

o

```json
{ "mode": "continua" }
```

**Response `201 Created`** — `GameState` inicial (CA-M-01, CA-M-08):

```json
{
  "game_id": "3f2b6c1a-...-...",
  "mode": "clasica",
  "board": [[null,null,null],[null,null,null],[null,null,null]],
  "turn": "X",
  "phase": null,
  "fichas_disponibles": null,
  "status": "en_curso",
  "winner": null,
  "winning_line": null
}
```

Para `mode: "continua"`, el estado inicial incluye `phase: "colocacion"` y
`fichas_disponibles: { "X": 3, "O": 3 }`.

**Errores**: `422` si `mode` no es `"clasica"` ni `"continua"`.

---

## `GET /api/games/{game_id}`

Consulta el `GameState` actual de una partida existente.

**Response `200 OK`**: `GameState` (mismo esquema que arriba).

**Errores**: `404` si `game_id` no existe.

---

## `POST /api/games/{game_id}/moves`

Aplica una jugada (colocar o mover) a una partida existente.

**Request body** (colocar — CA-M-02, CA-M-09):

```json
{ "player": "X", "type": "colocar", "to": { "row": 0, "col": 0 } }
```

**Request body** (mover — solo modalidad continua en fase de movimiento,
CA-M-11):

```json
{
  "player": "X",
  "type": "mover",
  "from": { "row": 0, "col": 0 },
  "to": { "row": 1, "col": 1 }
}
```

**Response `200 OK`**: `GameState` resultante tras aplicar la jugada,
incluyendo, si corresponde:

- `status: "victoria"`, `winner`, `winning_line` (CA-M-05, CA-M-13)
- `status: "empate"` por tablero lleno (CA-M-06) o por repetición de
  posición en modalidad continua (CA-M-14)
- Transición de `phase: "colocacion"` a `phase: "movimiento"` cuando ambos
  jugadores agotan sus fichas disponibles (CA-M-10)

**Response `422 Unprocessable Entity`** — jugada inválida, `GameState` de la
partida sin modificar (CA-M-03, CA-M-04, CA-M-07, CA-M-12, CA-M-15):

```json
{ "error": "casilla_ocupada", "message": "La casilla (0, 0) ya está ocupada." }
```

Códigos de `error` posibles: `casilla_ocupada`, `fuera_de_turno`,
`ficha_ajena`, `fase_incorrecta`, `fuera_de_rango`, `partida_finalizada`.

**Errores**: `404` si `game_id` no existe.

---

## Trazabilidad con criterios de aceptación

| Endpoint | CA-M-* cubiertos |
|---|---|
| `POST /api/games` | CA-M-01, CA-M-08 |
| `GET /api/games/{game_id}` | (soporte transversal a todos los CA-M-*) |
| `POST /api/games/{game_id}/moves` | CA-M-02 a CA-M-07, CA-M-09 a CA-M-15 |
