# Quickstart: Motor del Juego Tres en Raya

**Feature**: [spec.md](./spec.md) | **Contrato**: [contracts/games-api.md](./contracts/games-api.md)

## Prerrequisitos

- Python 3.11+
- Dependencias instaladas: `pip install fastapi uvicorn pytest httpx`

## Levantar el servidor

```bash
uvicorn backend.src.main:app --reload --port 8000
```

## Validación end-to-end: partida clásica hasta victoria

```bash
# 1. Crear partida clásica
curl -s -X POST http://localhost:8000/api/games -H "Content-Type: application/json" \
  -d '{"mode":"clasica"}'
# -> anota "game_id" de la respuesta, ej. GID

# 2. X juega (0,0), O juega (1,0), X juega (0,1), O juega (1,1), X juega (0,2) -> X gana fila superior
curl -s -X POST http://localhost:8000/api/games/GID/moves -d '{"player":"X","type":"colocar","to":{"row":0,"col":0}}'
curl -s -X POST http://localhost:8000/api/games/GID/moves -d '{"player":"O","type":"colocar","to":{"row":1,"col":0}}'
curl -s -X POST http://localhost:8000/api/games/GID/moves -d '{"player":"X","type":"colocar","to":{"row":0,"col":1}}'
curl -s -X POST http://localhost:8000/api/games/GID/moves -d '{"player":"O","type":"colocar","to":{"row":1,"col":1}}'
curl -s -X POST http://localhost:8000/api/games/GID/moves -d '{"player":"X","type":"colocar","to":{"row":0,"col":2}}'
# -> última respuesta: "status": "victoria", "winner": "X",
#    "winning_line": [[0,0],[0,1],[0,2]]  (CA-M-05)
```

## Validación end-to-end: jugada inválida

```bash
curl -s -X POST http://localhost:8000/api/games/GID/moves -d '{"player":"X","type":"colocar","to":{"row":0,"col":0}}'
# -> 422 {"error": "casilla_ocupada", ...} (CA-M-03), el estado no cambia
```

## Validación end-to-end: modalidad continua completa

1. `POST /api/games` con `{"mode":"continua"}`.
2. Colocar 3 fichas por jugador (6 jugadas `"type":"colocar"`) → la
   respuesta de la 6ª jugada SHALL mostrar `"phase":"movimiento"` (CA-M-10).
3. Realizar una jugada `"type":"mover"` hacia una casilla no adyacente a la
   de origen → SHALL aceptarse (CA-M-11, movimiento sin restricción de
   adyacencia).
4. Repetir una secuencia de movimientos que regrese 3 veces a la misma
   posición exacta de tablero → la 3ª repetición SHALL devolver
   `"status":"empate"` (CA-M-14).

## Ejecutar la suite de pruebas

```bash
pytest backend/tests/unit backend/tests/contract -v
```

**Resultado esperado**: todos los tests en verde, con cobertura de cada
CA-M-01 a CA-M-15 (ver Principio III de la constitución — gate de cobertura
por criterio de aceptación).
