"""Tests fundacionales de comprobar_victoria (T005).

Base usada por CA-M-05 (detección de victoria en modalidad clásica),
CA-M-06 (empate por tablero lleno sin victoria) y CA-M-13 (victoria en
modalidad continua, cualquier fase).
"""

from backend.src.engine.win_detection import comprobar_victoria


def _vacio():
    return [[None, None, None], [None, None, None], [None, None, None]]


def test_tablero_vacio_no_tiene_ganador():
    assert comprobar_victoria(_vacio()) is None


def test_detecta_victoria_en_cada_fila():
    for fila in range(3):
        board = _vacio()
        board[fila] = ["X", "X", "X"]
        linea = comprobar_victoria(board)
        assert linea is not None
        assert [(c.row, c.col) for c in linea] == [(fila, 0), (fila, 1), (fila, 2)]


def test_detecta_victoria_en_cada_columna():
    for col in range(3):
        board = _vacio()
        board[0][col] = board[1][col] = board[2][col] = "O"
        linea = comprobar_victoria(board)
        assert linea is not None
        assert [(c.row, c.col) for c in linea] == [(0, col), (1, col), (2, col)]


def test_detecta_victoria_diagonal_principal():
    board = _vacio()
    board[0][0] = board[1][1] = board[2][2] = "X"
    linea = comprobar_victoria(board)
    assert [(c.row, c.col) for c in linea] == [(0, 0), (1, 1), (2, 2)]


def test_detecta_victoria_diagonal_secundaria():
    board = _vacio()
    board[0][2] = board[1][1] = board[2][0] = "O"
    linea = comprobar_victoria(board)
    assert [(c.row, c.col) for c in linea] == [(0, 2), (1, 1), (2, 0)]


def test_tablero_lleno_sin_alineacion_no_tiene_ganador():
    # Tablero completo (empate clásico) sin ninguna de las 8 líneas alineada
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]
    assert comprobar_victoria(board) is None


def test_no_detecta_victoria_con_fichas_distintas_en_linea():
    board = _vacio()
    board[0] = ["X", "O", "X"]
    assert comprobar_victoria(board) is None


def test_ignora_lineas_parcialmente_vacias():
    board = _vacio()
    board[0][0] = "X"
    board[0][1] = "X"
    # falta board[0][2]: no debe considerarse victoria
    assert comprobar_victoria(board) is None
