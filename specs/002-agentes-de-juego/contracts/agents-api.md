# Contrato HTTP: API de Agentes (`/api/agents`)

**Feature**: [../spec.md](../spec.md) | **Modelo de datos**: [../data-model.md](../data-model.md)

## `POST /api/agents/{level}/move`

`{level}` es uno de: `sencillo`, `medio`, `complejo`.

**Request body** (`SolicitudJugadaAgente`, modalidad clásica):

```json
{
  "board": [["X","O",null],[null,"X",null],[null,null,"O"]],
  "mode": "clasica",
  "phase": null,
  "turn": "X",
  "fichas_disponibles": null
}
```

**Response `200 OK`** (`Jugada`):

```json
{ "type": "colocar", "to": { "row": 1, "col": 0 } }
```

En modalidad continua, fase de movimiento:

```json
{ "type": "mover", "from": { "row": 0, "col": 0 }, "to": { "row": 2, "col": 2 } }
```

**Errores**:

- `404` si `{level}` no es uno de los tres niveles soportados.
- `422` si el `board` no tiene jugadas legales disponibles (tablero lleno) o
  la combinación `mode`/`phase`/`fichas_disponibles` es inconsistente.

## Semántica por nivel

| `{level}` | Comportamiento garantizado |
|---|---|
| `sencillo` | Selección aleatoria uniforme entre jugadas legales (CA-A-01, CA-A-02) |
| `medio` | Ganar si puede (CA-A-03) → bloquear si el rival puede ganar (CA-A-04) → azar (CA-A-05) |
| `complejo` | Jugada óptima vía minimax con poda alfa-beta en modalidad clásica; nunca permite una derrota evitable (CA-A-07, CA-A-08); reutiliza memoria persistente entre partidas (CA-A-09) |

## Trazabilidad con criterios de aceptación

| Elemento del contrato | CA-A-* cubiertos |
|---|---|
| `POST /api/agents/sencillo/move` | CA-A-01, CA-A-02 |
| `POST /api/agents/medio/move` | CA-A-03, CA-A-04, CA-A-05, CA-A-06 |
| `POST /api/agents/complejo/move` | CA-A-07, CA-A-08, CA-A-09 |
| Todo el endpoint (tiempo de respuesta) | SC-004 |
