"""Tests de contrato HTTP del motor en modalidad clásica (T008).

Cubre CA-M-01 a CA-M-07 a nivel HTTP, incluyendo el cuerpo `ErrorJugada` de
las respuestas 422. Ver `contracts/games-api.md`.
"""

from fastapi.testclient import TestClient

from backend.src.main import app

client = TestClient(app)


def _crear_partida_clasica() -> dict:
    resp = client.post("/api/games", json={"mode": "clasica"})
    assert resp.status_code == 201
    return resp.json()


def _jugar(game_id: str, player: str, row: int, col: int):
    return client.post(
        f"/api/games/{game_id}/moves",
        json={"player": player, "type": "colocar", "to": {"row": row, "col": col}},
    )


def test_post_games_crea_partida_clasica_inicial():  # CA-M-01
    data = _crear_partida_clasica()
    assert data["mode"] == "clasica"
    assert data["turn"] == "X"
    assert data["status"] == "en_curso"
    assert data["board"] == [[None, None, None]] * 3
    assert data["game_id"]


def test_post_games_rechaza_mode_invalido():
    resp = client.post("/api/games", json={"mode": "invalido"})
    assert resp.status_code == 422


def test_get_games_devuelve_estado_actual():
    data = _crear_partida_clasica()
    resp = client.get(f"/api/games/{data['game_id']}")
    assert resp.status_code == 200
    assert resp.json()["game_id"] == data["game_id"]


def test_get_games_404_si_no_existe():
    resp = client.get("/api/games/no-existe")
    assert resp.status_code == 404


def test_post_moves_coloca_ficha_y_alterna_turno():  # CA-M-02
    data = _crear_partida_clasica()
    resp = _jugar(data["game_id"], "X", 0, 0)
    assert resp.status_code == 200
    body = resp.json()
    assert body["board"][0][0] == "X"
    assert body["turn"] == "O"


def test_post_moves_rechaza_casilla_ocupada():  # CA-M-03
    data = _crear_partida_clasica()
    gid = data["game_id"]
    _jugar(gid, "X", 0, 0)
    resp = _jugar(gid, "O", 0, 0)
    assert resp.status_code == 422
    assert resp.json() == {
        "error": "casilla_ocupada",
        "message": "La casilla (0, 0) ya está ocupada.",
    }


def test_post_moves_rechaza_fuera_de_turno():  # CA-M-04
    data = _crear_partida_clasica()
    resp = _jugar(data["game_id"], "O", 0, 0)  # X debe jugar primero
    assert resp.status_code == 422
    assert resp.json()["error"] == "fuera_de_turno"


def test_post_moves_detecta_victoria():  # CA-M-05
    data = _crear_partida_clasica()
    gid = data["game_id"]
    secuencia = [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1), ("X", 0, 2)]
    resp = None
    for player, row, col in secuencia:
        resp = _jugar(gid, player, row, col)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "victoria"
    assert body["winner"] == "X"
    assert body["winning_line"] == [
        {"row": 0, "col": 0},
        {"row": 0, "col": 1},
        {"row": 0, "col": 2},
    ]


def test_post_moves_detecta_empate():  # CA-M-06
    data = _crear_partida_clasica()
    gid = data["game_id"]
    secuencia = [
        ("X", 0, 0),
        ("O", 0, 1),
        ("X", 0, 2),
        ("O", 1, 2),
        ("X", 1, 0),
        ("O", 2, 0),
        ("X", 1, 1),
        ("O", 2, 2),
        ("X", 2, 1),
    ]
    resp = None
    for player, row, col in secuencia:
        resp = _jugar(gid, player, row, col)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "empate"
    assert body["winner"] is None


def test_post_moves_rechaza_tras_finalizar():  # CA-M-07
    data = _crear_partida_clasica()
    gid = data["game_id"]
    secuencia = [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1), ("X", 0, 2)]
    for player, row, col in secuencia:
        _jugar(gid, player, row, col)
    resp = _jugar(gid, "O", 2, 2)
    assert resp.status_code == 422
    assert resp.json()["error"] == "partida_finalizada"
