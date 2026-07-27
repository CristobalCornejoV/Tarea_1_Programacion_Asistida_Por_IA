"""Tests unitarios del motor: modalidad clásica (T007, CA-M-01 a CA-M-07) y
modalidad continua (T017, CA-M-08 a CA-M-15).
"""

import pytest

from backend.src.engine.rules import JugadaInvalida, aplicar_jugada, crear_partida
from backend.src.models.game_state import Coordenada, Jugada


def _colocar(player: str, row: int, col: int) -> Jugada:
    return Jugada(player=player, type="colocar", to=Coordenada(row=row, col=col))


def _mover(player: str, fila_o: int, col_o: int, fila_d: int, col_d: int) -> Jugada:
    return Jugada(
        player=player,
        type="mover",
        to=Coordenada(row=fila_d, col=col_d),
        **{"from": Coordenada(row=fila_o, col=col_o)},
    )


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


# --- Modalidad continua (CA-M-08 a CA-M-15) ---------------------------------


def _estado_en_movimiento():
    """Estado en fase de movimiento: X en (0,0),(0,1),(1,0); O en (1,2),(2,1),(2,2)."""
    estado = crear_partida("continua")
    colocaciones = [
        ("X", 0, 0),
        ("O", 2, 2),
        ("X", 0, 1),
        ("O", 2, 1),
        ("X", 1, 0),
        ("O", 1, 2),
    ]
    for player, row, col in colocaciones:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    return estado


def _estado_en_movimiento_para_repeticion():
    """Estado en fase de movimiento: X en (0,0),(0,1),(1,1); O en (1,2),(2,1),(2,2)."""
    estado = crear_partida("continua")
    colocaciones = [
        ("X", 0, 0),
        ("O", 1, 2),
        ("X", 0, 1),
        ("O", 2, 1),
        ("X", 1, 1),
        ("O", 2, 2),
    ]
    for player, row, col in colocaciones:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    return estado


def test_estado_inicial_continua_tiene_3_fichas_por_jugador():  # CA-M-08
    estado = crear_partida("continua")
    assert estado.mode == "continua"
    assert estado.phase == "colocacion"
    assert estado.fichas_disponibles == {"X": 3, "O": 3}
    assert estado.turn == "X"
    assert all(casilla is None for fila in estado.board for casilla in fila)


def test_colocar_en_fase_colocacion_descuenta_fichas_y_alterna_turno():  # CA-M-09
    estado = crear_partida("continua")
    nuevo = aplicar_jugada(estado, _colocar("X", 0, 0))
    assert nuevo.fichas_disponibles == {"X": 2, "O": 3}
    assert nuevo.turn == "O"
    assert nuevo.phase == "colocacion"


def test_transicion_a_fase_movimiento_tras_agotar_fichas():  # CA-M-10
    estado = _estado_en_movimiento()
    assert estado.phase == "movimiento"
    assert estado.fichas_disponibles is None
    assert estado.status == "en_curso"
    assert estado.turn == "X"


def test_mover_a_casilla_no_adyacente_se_acepta():  # CA-M-11
    estado = _estado_en_movimiento()
    nuevo = aplicar_jugada(estado, _mover("X", 0, 0, 2, 0))
    assert nuevo.board[0][0] is None
    assert nuevo.board[2][0] == "X"
    assert nuevo.turn == "O"
    # Inmutabilidad: el estado anterior permanece intacto
    assert estado.board[0][0] == "X"


def test_rechaza_mover_ficha_ajena():  # CA-M-12 (ficha ajena)
    estado = _estado_en_movimiento()
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _mover("X", 1, 2, 1, 1))  # (1,2) es de O
    assert exc.value.codigo == "ficha_ajena"


def test_rechaza_mover_a_casilla_ocupada():  # CA-M-12 (casilla ocupada)
    estado = _estado_en_movimiento()
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _mover("X", 0, 0, 0, 1))  # (0,1) ya tiene X
    assert exc.value.codigo == "casilla_ocupada"


def test_detecta_victoria_tras_mover_en_fase_movimiento():  # CA-M-13
    estado = _estado_en_movimiento()
    nuevo = aplicar_jugada(estado, _mover("X", 1, 0, 0, 2))  # completa fila 0
    assert nuevo.status == "victoria"
    assert nuevo.winner == "X"
    assert [(c.row, c.col) for c in nuevo.winning_line] == [(0, 0), (0, 1), (0, 2)]


def test_empate_por_repeticion_de_posicion_3_veces():  # CA-M-14
    estado = _estado_en_movimiento_para_repeticion()
    assert estado.phase == "movimiento"

    ciclo = [
        ("X", 1, 1, 1, 0),
        ("O", 1, 2, 0, 2),
        ("X", 1, 0, 1, 1),
        ("O", 0, 2, 1, 2),  # 2da vez en la posición inicial del ciclo
        ("X", 1, 1, 1, 0),
        ("O", 1, 2, 0, 2),
        ("X", 1, 0, 1, 1),
    ]
    for player, fila_o, col_o, fila_d, col_d in ciclo:
        estado = aplicar_jugada(estado, _mover(player, fila_o, col_o, fila_d, col_d))
        assert estado.status == "en_curso"

    # 3ra vez en la posición inicial del ciclo -> empate
    estado = aplicar_jugada(estado, _mover("O", 0, 2, 1, 2))
    assert estado.status == "empate"
    assert estado.winner is None


def test_rechaza_mover_antes_de_completar_fase_colocacion():  # CA-M-15 (fase incorrecta)
    estado = crear_partida("continua")
    estado = aplicar_jugada(estado, _colocar("X", 0, 0))  # aún en colocación
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _mover("O", 0, 0, 1, 1))
    assert exc.value.codigo == "fase_incorrecta"


def test_rechaza_colocar_durante_fase_movimiento():  # CA-M-15 (fase incorrecta)
    estado = _estado_en_movimiento()
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _colocar("X", 2, 0))
    assert exc.value.codigo == "fase_incorrecta"


def test_rechaza_jugada_tras_finalizar_en_continua():  # CA-M-15 (partida finalizada)
    estado = _estado_en_movimiento()
    estado = aplicar_jugada(estado, _mover("X", 1, 0, 0, 2))  # gana X
    assert estado.status == "victoria"
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _mover("O", 1, 2, 1, 1))
    assert exc.value.codigo == "partida_finalizada"


# --- Coordenadas fuera de rango (T029, edge case de spec.md) ----------------


def test_rechaza_colocar_fuera_de_rango():
    estado = crear_partida("clasica")
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _colocar("X", 3, 0))
    assert exc.value.codigo == "fuera_de_rango"
    assert all(casilla is None for fila in estado.board for casilla in fila)


def test_rechaza_colocar_con_columna_negativa():
    estado = crear_partida("clasica")
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _colocar("X", 0, -1))
    assert exc.value.codigo == "fuera_de_rango"


def test_rechaza_mover_con_origen_fuera_de_rango():
    estado = _estado_en_movimiento()
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _mover("X", 5, 0, 1, 1))
    assert exc.value.codigo == "fuera_de_rango"


def test_rechaza_mover_con_destino_fuera_de_rango():
    estado = _estado_en_movimiento()
    with pytest.raises(JugadaInvalida) as exc:
        aplicar_jugada(estado, _mover("X", 0, 0, 0, 7))
    assert exc.value.codigo == "fuera_de_rango"
