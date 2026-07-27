"""Tests unitarios del motor en modalidad clásica (T007).

Cubre CA-M-01 a CA-M-07. Las extensiones de modalidad continua (CA-M-08 en
adelante) se testean por separado en la fase de US2.
"""

import pytest

from backend.src.engine.rules import JugadaInvalida, aplicar_jugada, crear_partida
from backend.src.models.game_state import Coordenada, Jugada


def _colocar(player: str, row: int, col: int) -> Jugada:
    return Jugada(player=player, type="colocar", to=Coordenada(row=row, col=col))


def test_estado_inicial_tablero_vacio_y_turno_de_x():  # CA-M-01
    estado = crear_partida("clasica")
    assert estado.mode == "clasica"
    assert estado.turn == "X"
    assert estado.status == "en_curso"
    assert all(casilla is None for fila in estado.board for casilla in fila)


def test_colocar_en_turno_valido_coloca_y_alterna_turno():  # CA-M-02
    estado = crear_partida("clasica")
    nuevo = aplicar_jugada(estado, _colocar("X", 0, 0))
    assert nuevo.board[0][0] == "X"
    assert nuevo.turn == "O"
    # Inmutabilidad: el estado anterior permanece intacto
    assert estado.board[0][0] is None
    assert estado.turn == "X"


def test_rechaza_casilla_ocupada():  # CA-M-03
    estado = crear_partida("clasica")
    estado = aplicar_jugada(estado, _colocar("X", 0, 0))
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _colocar("O", 0, 0))
    assert exc.value.codigo == "casilla_ocupada"
    # El estado no se modifica ante una jugada rechazada
    assert estado.board[0][0] == "X"


def test_rechaza_jugada_fuera_de_turno():  # CA-M-04
    estado = crear_partida("clasica")
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _colocar("O", 0, 0))  # X debe jugar primero
    assert exc.value.codigo == "fuera_de_turno"
    assert all(casilla is None for fila in estado.board for casilla in fila)


def test_detecta_victoria_en_alineacion():  # CA-M-05
    estado = crear_partida("clasica")
    secuencia = [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1), ("X", 0, 2)]
    for player, row, col in secuencia:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    assert estado.status == "victoria"
    assert estado.winner == "X"
    assert [(c.row, c.col) for c in estado.winning_line] == [(0, 0), (0, 1), (0, 2)]


def test_empate_por_tablero_lleno_sin_ganador():  # CA-M-06
    estado = crear_partida("clasica")
    # Tablero final: X O X / X X O / O X O (sin alineación completa)
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
    for player, row, col in secuencia:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    assert estado.status == "empate"
    assert estado.winner is None
    assert all(casilla is not None for fila in estado.board for casilla in fila)


def test_rechaza_jugada_tras_finalizar():  # CA-M-07
    estado = crear_partida("clasica")
    secuencia = [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1), ("X", 0, 2)]
    for player, row, col in secuencia:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    assert estado.status == "victoria"
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _colocar("O", 2, 2))
    assert exc.value.codigo == "partida_finalizada"
