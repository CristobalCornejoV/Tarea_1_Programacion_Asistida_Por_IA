"""Tests de contrato HTTP del motor: modalidad clásica (T008, CA-M-01 a
CA-M-07) y modalidad continua (T018, CA-M-08 a CA-M-15).

Ver `contracts/games-api.md`.
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


# --- Modalidad continua (CA-M-08 a CA-M-15) ---------------------------------


def _crear_partida_continua() -> dict:
    resp = client.post("/api/games", json={"mode": "continua"})
    assert resp.status_code == 201
    return resp.json()


def _colocar(gid: str, player: str, row: int, col: int):
    return client.post(
        f"/api/games/{gid}/moves",
        json={"player": player, "type": "colocar", "to": {"row": row, "col": col}},
    )


def _mover(gid: str, player: str, fila_o: int, col_o: int, fila_d: int, col_d: int):
    return client.post(
        f"/api/games/{gid}/moves",
        json={
            "player": player,
            "type": "mover",
            "from": {"row": fila_o, "col": col_o},
            "to": {"row": fila_d, "col": col_d},
        },
    )


def _colocar_hasta_movimiento(gid: str) -> dict:
    """Coloca 6 fichas (3 por jugador) hasta transicionar a fase de movimiento.

    Resulta en: X en (0,0),(0,1),(1,0); O en (1,2),(2,1),(2,2); turno de X.
    """
    secuencia = [
        ("X", 0, 0),
        ("O", 2, 2),
        ("X", 0, 1),
        ("O", 2, 1),
        ("X", 1, 0),
        ("O", 1, 2),
    ]
    resp = None
    for player, row, col in secuencia:
        resp = _colocar(gid, player, row, col)
    return resp.json()


def test_post_games_crea_partida_continua_inicial():  # CA-M-08
    data = _crear_partida_continua()
    assert data["mode"] == "continua"
    assert data["phase"] == "colocacion"
    assert data["fichas_disponibles"] == {"X": 3, "O": 3}
    assert data["turn"] == "X"


def test_post_moves_colocar_en_continua_descuenta_fichas():  # CA-M-09
    data = _crear_partida_continua()
    resp = _colocar(data["game_id"], "X", 0, 0)
    assert resp.status_code == 200
    body = resp.json()
    assert body["fichas_disponibles"] == {"X": 2, "O": 3}
    assert body["turn"] == "O"


def test_post_moves_transiciona_a_movimiento_tras_agotar_fichas():  # CA-M-10
    data = _crear_partida_continua()
    body = _colocar_hasta_movimiento(data["game_id"])
    assert body["phase"] == "movimiento"
    assert body["fichas_disponibles"] is None


def test_post_moves_mover_a_casilla_no_adyacente():  # CA-M-11
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    resp = _mover(gid, "X", 0, 0, 2, 0)
    assert resp.status_code == 200
    body = resp.json()
    assert body["board"][0][0] is None
    assert body["board"][2][0] == "X"


def test_post_moves_rechaza_mover_ficha_ajena():  # CA-M-12
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    resp = _mover(gid, "X", 1, 2, 1, 1)  # (1,2) es de O
    assert resp.status_code == 422
    assert resp.json()["error"] == "ficha_ajena"


def test_post_moves_rechaza_mover_a_casilla_ocupada():  # CA-M-12
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    resp = _mover(gid, "X", 0, 0, 0, 1)
    assert resp.status_code == 422
    assert resp.json()["error"] == "casilla_ocupada"


def test_post_moves_detecta_victoria_en_movimiento():  # CA-M-13
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    resp = _mover(gid, "X", 1, 0, 0, 2)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "victoria"
    assert body["winner"] == "X"


def test_post_moves_empate_por_repeticion():  # CA-M-14
    data = _crear_partida_continua()
    gid = data["game_id"]
    secuencia = [
        ("X", 0, 0),
        ("O", 1, 2),
        ("X", 0, 1),
        ("O", 2, 1),
        ("X", 1, 1),
        ("O", 2, 2),
    ]
    for player, row, col in secuencia:
        _colocar(gid, player, row, col)

    ciclo = [
        ("X", 1, 1, 1, 0),
        ("O", 1, 2, 0, 2),
        ("X", 1, 0, 1, 1),
        ("O", 0, 2, 1, 2),
        ("X", 1, 1, 1, 0),
        ("O", 1, 2, 0, 2),
        ("X", 1, 0, 1, 1),
    ]
    resp = None
    for player, fila_o, col_o, fila_d, col_d in ciclo:
        resp = _mover(gid, player, fila_o, col_o, fila_d, col_d)
        assert resp.status_code == 200
        assert resp.json()["status"] == "en_curso"

    resp = _mover(gid, "O", 0, 2, 1, 2)
    assert resp.status_code == 200
    assert resp.json()["status"] == "empate"


def test_post_moves_rechaza_mover_antes_de_completar_colocacion():  # CA-M-15
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar(gid, "X", 0, 0)
    resp = _mover(gid, "O", 0, 0, 1, 1)
    assert resp.status_code == 422
    assert resp.json()["error"] == "fase_incorrecta"


def test_post_moves_rechaza_colocar_durante_movimiento():  # CA-M-15
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    resp = _colocar(gid, "X", 2, 0)
    assert resp.status_code == 422
    assert resp.json()["error"] == "fase_incorrecta"


def test_post_moves_rechaza_jugada_tras_finalizar_continua():  # CA-M-15
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    _mover(gid, "X", 1, 0, 0, 2)  # gana X
    resp = _mover(gid, "O", 1, 2, 1, 1)
    assert resp.status_code == 422
    assert resp.json()["error"] == "partida_finalizada"


# --- Coordenadas fuera de rango (T029, edge case de spec.md) ----------------


def test_post_moves_rechaza_colocar_fuera_de_rango():
    data = _crear_partida_clasica()
    resp = _jugar(data["game_id"], "X", 3, 0)
    assert resp.status_code == 422
    assert resp.json()["error"] == "fuera_de_rango"


def test_post_moves_rechaza_mover_fuera_de_rango():
    data = _crear_partida_continua()
    gid = data["game_id"]
    _colocar_hasta_movimiento(gid)
    resp = _mover(gid, "X", 0, 0, 9, 9)
    assert resp.status_code == 422
    assert resp.json()["error"] == "fuera_de_rango"
