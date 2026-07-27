"""Tests fundacionales de los modelos inmutables de data-model.md (T004).

No cubren un CA-M-* de comportamiento de juego (esos se testean en las
fases US1/US2); verifican que la estructura de datos compartida por las
tres specs es correcta e inmutable.
"""

import pytest
from pydantic import ValidationError

from backend.src.models.game_state import Coordenada, ErrorJugada, GameState, Jugada


def _tablero_vacio():
    return [[None, None, None], [None, None, None], [None, None, None]]


def test_game_state_valido_se_construye():
    estado = GameState(
        game_id="abc",
        mode="clasica",
        board=_tablero_vacio(),
        turn="X",
        status="en_curso",
    )
    assert estado.turn == "X"
    assert estado.status == "en_curso"
    assert estado.phase is None
    assert estado.fichas_disponibles is None


def test_game_state_es_inmutable():
    estado = GameState(
        game_id="abc", mode="clasica", board=_tablero_vacio(), turn="X"
    )
    with pytest.raises(ValidationError):
        estado.turn = "O"


def test_game_state_rechaza_tablero_no_3x3():
    with pytest.raises(ValidationError):
        GameState(
            game_id="abc",
            mode="clasica",
            board=[[None, None], [None, None]],
            turn="X",
        )


def test_game_state_rechaza_winning_line_de_longitud_distinta_de_3():
    with pytest.raises(ValidationError):
        GameState(
            game_id="abc",
            mode="clasica",
            board=_tablero_vacio(),
            turn="X",
            status="victoria",
            winner="X",
            winning_line=[Coordenada(row=0, col=0), Coordenada(row=0, col=1)],
        )


def test_game_state_acepta_winning_line_de_3():
    estado = GameState(
        game_id="abc",
        mode="clasica",
        board=_tablero_vacio(),
        turn="X",
        status="victoria",
        winner="X",
        winning_line=[
            Coordenada(row=0, col=0),
            Coordenada(row=0, col=1),
            Coordenada(row=0, col=2),
        ],
    )
    assert len(estado.winning_line) == 3


def test_jugada_colocar_no_requiere_from():
    jugada = Jugada(player="X", type="colocar", to=Coordenada(row=0, col=0))
    assert jugada.from_ is None


def test_jugada_mover_requiere_from():
    with pytest.raises(ValidationError):
        Jugada(player="X", type="mover", to=Coordenada(row=1, col=1))


def test_jugada_mover_con_from_es_valida():
    jugada = Jugada(
        player="X",
        type="mover",
        to=Coordenada(row=1, col=1),
        **{"from": Coordenada(row=0, col=0)},
    )
    assert jugada.from_.row == 0 and jugada.from_.col == 0


def test_jugada_acepta_alias_from_en_serializacion_json():
    jugada = Jugada.model_validate(
        {
            "player": "X",
            "type": "mover",
            "from": {"row": 0, "col": 0},
            "to": {"row": 1, "col": 1},
        }
    )
    assert jugada.from_.row == 0


def test_error_jugada_valido():
    error = ErrorJugada(error="casilla_ocupada", message="La casilla ya está ocupada.")
    assert error.error == "casilla_ocupada"


def test_error_jugada_rechaza_codigo_no_enumerado():
    with pytest.raises(ValidationError):
        ErrorJugada(error="codigo_inventado", message="x")
