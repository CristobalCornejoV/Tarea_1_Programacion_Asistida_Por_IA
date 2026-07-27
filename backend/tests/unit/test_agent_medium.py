"""Tests unitarios del agente Medio (T010). Cubre CA-A-03 a CA-A-06."""

from backend.src.agents.medium import decidir_jugada
from backend.src.agents.shared import listar_jugadas_legales
from backend.src.engine.rules import aplicar_jugada, crear_partida
from backend.src.models.game_state import Coordenada, Jugada


def _colocar(player: str, row: int, col: int) -> Jugada:
    return Jugada(player=player, type="colocar", to=Coordenada(row=row, col=col))


def test_juega_victoria_inmediata_si_existe():  # CA-A-03
    estado = crear_partida("clasica")
    for player, row, col in [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1)]:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    jugada = decidir_jugada(estado)  # turno de X, victoria disponible en (0,2)
    assert jugada.player == "X"
    assert jugada.type == "colocar"
    assert (jugada.to.row, jugada.to.col) == (0, 2)


def test_bloquea_amenaza_del_rival_si_no_tiene_victoria_propia():  # CA-A-04
    estado = crear_partida("clasica")
    for player, row, col in [("X", 2, 2), ("O", 0, 0), ("X", 1, 0), ("O", 0, 1)]:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    # turno de X: (2,2) y (1,0) no comparten ninguna línea -> sin victoria
    # propia; O amenaza completar la fila superior en (0,2)
    jugada = decidir_jugada(estado)
    assert jugada.player == "X"
    assert (jugada.to.row, jugada.to.col) == (0, 2)


def test_prioriza_ganar_sobre_bloquear_si_ambas_condiciones_aplican():
    estado = crear_partida("clasica")
    for player, row, col in [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1)]:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    # turno de X: X gana en (0,2); O amenaza por separado en (1,2)
    jugada = decidir_jugada(estado)
    assert (jugada.to.row, jugada.to.col) == (0, 2)


def test_juega_al_azar_si_no_hay_victoria_ni_amenaza():  # CA-A-05
    estado = crear_partida("clasica")
    estado = aplicar_jugada(estado, _colocar("X", 0, 0))
    jugada = decidir_jugada(estado)  # turno de O, sin amenazas de ninguno
    legales = listar_jugadas_legales(estado)
    assert jugada in legales


def test_decision_no_depende_de_como_se_llego_al_tablero():  # CA-A-06
    estado_a = crear_partida("clasica")
    for player, row, col in [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1)]:
        estado_a = aplicar_jugada(estado_a, _colocar(player, row, col))

    # Mismo tablero final, orden de colocación distinto.
    estado_b = crear_partida("clasica")
    for player, row, col in [("X", 0, 1), ("O", 1, 1), ("X", 0, 0), ("O", 1, 0)]:
        estado_b = aplicar_jugada(estado_b, _colocar(player, row, col))

    assert estado_a.board == estado_b.board
    assert estado_a.turn == estado_b.turn

    jugada_a = decidir_jugada(estado_a)
    jugada_b = decidir_jugada(estado_b)
    assert (jugada_a.to.row, jugada_a.to.col) == (0, 2)
    assert (jugada_b.to.row, jugada_b.to.col) == (0, 2)
