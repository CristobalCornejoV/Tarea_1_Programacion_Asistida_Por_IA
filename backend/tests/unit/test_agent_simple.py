"""Tests unitarios del agente Sencillo (T005). Cubre CA-A-01, CA-A-02."""

from backend.src.agents.shared import listar_jugadas_legales
from backend.src.agents.simple import decidir_jugada
from backend.src.engine.rules import aplicar_jugada, crear_partida
from backend.src.models.game_state import Coordenada, Jugada


def _colocar(player: str, row: int, col: int) -> Jugada:
    return Jugada(player=player, type="colocar", to=Coordenada(row=row, col=col))


def test_toda_jugada_devuelta_es_legal_en_tablero_vacio():  # CA-A-01
    estado = crear_partida("clasica")
    legales = listar_jugadas_legales(estado)
    for _ in range(50):
        jugada = decidir_jugada(estado)
        assert jugada in legales


def test_toda_jugada_devuelta_es_legal_en_tablero_parcial():  # CA-A-01
    estado = crear_partida("clasica")
    estado = aplicar_jugada(estado, _colocar("X", 0, 0))
    estado = aplicar_jugada(estado, _colocar("O", 1, 1))
    legales = listar_jugadas_legales(estado)
    for _ in range(50):
        jugada = decidir_jugada(estado)
        assert jugada in legales
        assert jugada.player == "X"  # turno alterna X->O->X tras las 2 jugadas previas


def test_distribucion_cubre_todas_las_opciones_legales_sin_depender_de_llamadas_previas():  # CA-A-02
    estado = crear_partida("clasica")
    legales = listar_jugadas_legales(estado)
    destinos_legales = {(j.to.row, j.to.col) for j in legales}

    destinos_obtenidos = set()
    for _ in range(500):
        jugada = decidir_jugada(estado)
        destinos_obtenidos.add((jugada.to.row, jugada.to.col))

    # Sobre 500 llamadas independientes al MISMO estado (sin pasar historial
    # alguno), la distribución cubre las 9 casillas legales.
    assert destinos_obtenidos == destinos_legales
