"""Tests de contrato HTTP de la API de agentes: Sencillo (T006, CA-A-01,
CA-A-02), Medio (T011, CA-A-03 a CA-A-06), Complejo (T018, CA-A-08),
rechazo sin jugadas legales (T027, edge case de spec.md) y tiempo de
respuesta (T026, SC-004, Principio VI de la constitución). T029 cubre
CA-A-10 y la regresión de partidas finalizadas con casillas libres.

Ver `contracts/agents-api.md`.
"""

import time

from fastapi.testclient import TestClient

from backend.src.main import app

client = TestClient(app)


def _es_casilla_valida(row: int, col: int) -> bool:
    return 0 <= row <= 2 and 0 <= col <= 2


def _estado_continuo_en_movimiento() -> dict:
    return {
        "board": [
            ["X", "O", "X"],
            ["O", "X", "O"],
            [None, None, None],
        ],
        "mode": "continua",
        "phase": "movimiento",
        "turn": "X",
        "fichas_disponibles": None,
        "status": "en_curso",
    }


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


def test_post_agents_medio_move_juega_victoria_inmediata():  # CA-A-03
    body = {
        "board": [["X", "X", None], ["O", "O", None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/medio/move", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["to"] == {"row": 0, "col": 2}


def test_post_agents_medio_move_bloquea_amenaza_del_rival():  # CA-A-04
    body = {
        "board": [["O", "O", None], ["X", None, None], [None, None, "X"]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/medio/move", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["to"] == {"row": 0, "col": 2}


def test_post_agents_medio_move_azar_si_no_hay_condiciones():  # CA-A-05
    body = {
        "board": [["X", None, None], [None, None, None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "O",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/medio/move", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "colocar"
    assert (data["to"]["row"], data["to"]["col"]) != (0, 0)


def test_post_agents_complejo_move_devuelve_jugada_valida_en_tablero_vacio():
    body = {
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/complejo/move", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "colocar"
    assert _es_casilla_valida(data["to"]["row"], data["to"]["col"])


def test_post_agents_complejo_move_juega_victoria_inmediata():  # CA-A-08
    body = {
        "board": [["X", "X", None], ["O", "O", None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    resp = client.post("/api/agents/complejo/move", json=body)
    assert resp.status_code == 200
    assert resp.json()["to"] == {"row": 0, "col": 2}


def test_post_agents_complejo_continua_devuelve_movimiento_legal_tras_usar_cache_clasica():
    """CA-A-10: la caché clásica no contamina una partida continua."""
    board = _estado_continuo_en_movimiento()["board"]
    clasica = {
        "board": board,
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
        "status": "en_curso",
    }
    assert client.post("/api/agents/complejo/move", json=clasica).status_code == 200

    resp = client.post(
        "/api/agents/complejo/move",
        json=_estado_continuo_en_movimiento(),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "mover"
    assert data["from"] is not None
    origen = data["from"]
    destino = data["to"]
    assert board[origen["row"]][origen["col"]] == "X"
    assert board[destino["row"]][destino["col"]] is None


def test_post_agents_move_rechaza_sin_jugadas_legales_tablero_lleno():  # T027
    body = {
        "board": [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]],
        "mode": "clasica",
        "phase": None,
        "turn": "X",
        "fichas_disponibles": None,
    }
    for nivel in ("sencillo", "medio", "complejo"):
        resp = client.post(f"/api/agents/{nivel}/move", json=body)
        assert resp.status_code == 422


def test_post_agents_move_rechaza_partida_ganada_con_casillas_libres():  # T029
    body = {
        "board": [["X", "X", "X"], ["O", "O", None], [None, None, None]],
        "mode": "clasica",
        "phase": None,
        "turn": "O",
        "fichas_disponibles": None,
        # Se omite status intencionalmente: el backend debe reconocer la
        # línea ganadora y no confiar solo en el cliente.
    }
    for nivel in ("sencillo", "medio", "complejo"):
        resp = client.post(f"/api/agents/{nivel}/move", json=body)
        assert resp.status_code == 422


def test_post_agents_move_responde_en_menos_de_1_segundo_tiempo():  # T026, SC-004
    estados = [
        {
            "board": [[None, None, None], [None, None, None], [None, None, None]],
            "mode": "clasica",
            "phase": None,
            "turn": "X",
            "fichas_disponibles": None,
            "status": "en_curso",
        },
        _estado_continuo_en_movimiento(),
    ]
    for body in estados:
        for nivel in ("sencillo", "medio", "complejo"):
            inicio = time.perf_counter()
            resp = client.post(f"/api/agents/{nivel}/move", json=body)
            duracion = time.perf_counter() - inicio
            assert resp.status_code == 200
            assert duracion < 1.0, (
                f"{nivel}/{body['mode']} tardó {duracion:.3f}s (límite: 1s)"
            )
