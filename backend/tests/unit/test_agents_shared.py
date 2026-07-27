"""Tests unitarios de utilidades compartidas de agentes (T002).

listar_jugadas_legales es una utilidad fundacional, base de CA-A-01,
CA-A-02, CA-A-03, CA-A-05 y CA-A-08 (probados en las fases de US1/US2/US3);
estos tests verifican su corrección estructural de forma independiente.
"""

from backend.src.agents.shared import listar_jugadas_legales
from backend.src.engine.rules import aplicar_jugada, crear_partida
from backend.src.models.game_state import Coordenada, Jugada


def _colocar(player: str, row: int, col: int) -> Jugada:
    return Jugada(player=player, type="colocar", to=Coordenada(row=row, col=col))


def test_lista_9_jugadas_legales_en_tablero_clasico_vacio():
    estado = crear_partida("clasica")
    jugadas = listar_jugadas_legales(estado)
    assert len(jugadas) == 9
    assert all(j.type == "colocar" and j.player == "X" for j in jugadas)


def test_lista_solo_casillas_vacias_en_clasica():
    estado = crear_partida("clasica")
    estado = aplicar_jugada(estado, _colocar("X", 0, 0))
    jugadas = listar_jugadas_legales(estado)
    assert len(jugadas) == 8
    assert all(j.player == "O" for j in jugadas)
    assert not any(j.to.row == 0 and j.to.col == 0 for j in jugadas)


def test_lista_vacia_si_partida_finalizada():
    estado = crear_partida("clasica")
    secuencia = [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1), ("X", 0, 2)]
    for player, row, col in secuencia:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    assert estado.status == "victoria"
    assert listar_jugadas_legales(estado) == []


def test_lista_colocar_en_continua_fase_colocacion():
    estado = crear_partida("continua")
    jugadas = listar_jugadas_legales(estado)
    assert len(jugadas) == 9
    assert all(j.type == "colocar" for j in jugadas)


def test_lista_mover_en_continua_fase_movimiento():
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
    assert estado.phase == "movimiento"

    jugadas = listar_jugadas_legales(estado)
    # 3 fichas propias (turno X) x 3 casillas vacías = 9 combinaciones
    assert len(jugadas) == 9
    assert all(j.type == "mover" and j.player == "X" for j in jugadas)

    origenes = {(j.from_.row, j.from_.col) for j in jugadas}
    destinos = {(j.to.row, j.to.col) for j in jugadas}
    assert origenes == {(0, 0), (0, 1), (1, 0)}
    assert destinos == {(0, 2), (1, 1), (2, 0)}
