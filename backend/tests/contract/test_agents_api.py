"""Tests de contrato HTTP de la API de agentes (T006). Cubre CA-A-01, CA-A-02.

Ver `contracts/agents-api.md`.
"""

from fastapi.testclient import TestClient

from backend.src.main import app

client = TestClient(app)


def _es_casilla_valida(row: int, col: int) -> bool:
    return 0 <= row <= 2 and 0 <= col <= 2


def test_post_agents_sencillo_move_devuelve_jugada_legal_en_tablero_vacio():
    body = {
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/sencillo/move", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "colocar"
    assert _es_casilla_valida(data["to"]["row"], data["to"]["col"])
    assert "player" not in data


def test_post_agents_sencillo_move_devuelve_jugada_legal_en_tablero_parcial():
    body = {
        "board": [["X", None, None], [None, "O", None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "O",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/sencillo/move", json=body)
    assert resp.status_code == 200
    data = resp.json()
    to = data["to"]
    assert _es_casilla_valida(to["row"], to["col"])
    assert (to["row"], to["col"]) not in [(0, 0), (1, 1)]


def test_post_agents_nivel_desconocido_devuelve_404():
    body = {
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/inexistente/move", json=body)
    assert resp.status_code == 404
