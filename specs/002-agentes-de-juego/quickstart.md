# Quickstart: Agentes de Juego

**Feature**: [spec.md](./spec.md) | **Contrato**: [contracts/agents-api.md](./contracts/agents-api.md)

## Prerrequisitos

- Backend de la spec 001 corriendo (`uvicorn backend.src.main:app --reload`),
  ya que los agentes se registran en la misma app FastAPI.

## Validación: agente Medio bloquea una amenaza

```bash
curl -s -X POST http://localhost:8000/api/agents/medio/move \
  -H "Content-Type: application/json" \
  -d '{
    "board": [["X","X",null],[null,"O",null],[null,null,null]],
    "mode": "clasica", "phase": null, "turn": "O", "fichas_disponibles": null
  }'
# -> {"type":"colocar","to":{"row":0,"col":2}}  (bloquea la fila superior, CA-A-04)
```

## Validación: agente Complejo nunca pierde (CA-A-07)

```bash
pytest backend/tests/integration/test_simple_vs_complex_100_games.py -v
```

**Resultado esperado**: el test simula 100 partidas completas en modalidad
clásica entre el agente Sencillo y el agente Complejo (alternando quién
inicia como X), aplicando cada jugada a través del motor de la spec 001, y
verifica que el agente Complejo termina con 0 derrotas en las 100 partidas
(CA-A-07 / SC-002).

## Validación: tiempo de respuesta (<1s)

```bash
pytest backend/tests/contract/test_agents_api.py -k "tiempo" -v
```

**Resultado esperado**: cada nivel de agente responde en menos de 1 segundo
sobre cualquier estado de tablero válido (SC-004).

## Ejecutar toda la suite de la feature

```bash
pytest backend/tests/unit/test_agent_simple.py \
       backend/tests/unit/test_agent_medium.py \
       backend/tests/unit/test_agent_complex.py \
       backend/tests/contract/test_agents_api.py \
       backend/tests/integration/test_simple_vs_complex_100_games.py -v
```
