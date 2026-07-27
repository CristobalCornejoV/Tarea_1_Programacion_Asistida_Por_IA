"""Tests unitarios del agente Complejo (T017). Cubre CA-A-07, CA-A-08, CA-A-09.

Optimalidad acotada a modalidad clásica (ver Assumptions de `spec.md` y
`research.md` Decisión 4).
"""

from backend.src.agents import complex as complex_agent
from backend.src.agents import simple
from backend.src.engine.rules import aplicar_jugada, crear_partida
from backend.src.models.game_state import Coordenada, Jugada


def _colocar(player: str, row: int, col: int) -> Jugada:
    return Jugada(player=player, type="colocar", to=Coordenada(row=row, col=col))


def test_valor_optimo_de_tablero_vacio_es_empate():  # CA-A-08
    # Resultado conocido de tres en raya clásico: con juego óptimo de ambos
    # lados, la partida siempre termina en empate.
    complex_agent._memo.clear()
    estado = crear_partida("clasica")
    _, valor = complex_agent._negamax(estado, -2, 2)
    assert valor == 0


def test_juega_la_victoria_inmediata_si_existe():  # CA-A-08
    estado = crear_partida("clasica")
    for player, row, col in [("X", 0, 0), ("O", 1, 0), ("X", 0, 1), ("O", 1, 1)]:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    jugada = complex_agent.decidir_jugada(estado)
    assert (jugada.to.row, jugada.to.col) == (0, 2)


def test_bloquea_si_es_necesario_para_evitar_una_derrota():  # CA-A-07, CA-A-08
    estado = crear_partida("clasica")
    for player, row, col in [("X", 2, 2), ("O", 0, 0), ("X", 1, 0), ("O", 0, 1)]:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    # turno de X: sin victoria propia; si X no ocupa (0,2), O gana en su
    # siguiente turno. Bloquear es la única jugada que evita una derrota.
    _, valor = complex_agent._negamax(estado, -2, 2)
    assert valor >= 0  # nunca una derrota evitable
    jugada = complex_agent.decidir_jugada(estado)
    assert (jugada.to.row, jugada.to.col) == (0, 2)


def test_reconoce_posicion_donde_solo_el_empate_es_alcanzable():  # CA-A-08
    estado = crear_partida("clasica")
    secuencia = [
        ("X", 0, 0),
        ("O", 0, 1),
        ("X", 0, 2),
        ("O", 1, 2),
        ("X", 1, 0),
        ("O", 2, 0),
        ("X", 1, 1),
        ("O", 2, 2),
    ]
    for player, row, col in secuencia:
        estado = aplicar_jugada(estado, _colocar(player, row, col))
    _, valor = complex_agent._negamax(estado, -2, 2)
    assert valor == 0
    jugada = complex_agent.decidir_jugada(estado)
    assert (jugada.to.row, jugada.to.col) == (2, 1)  # única casilla vacía


def test_memoizacion_reutiliza_resultado_ya_evaluado():  # CA-A-09
    complex_agent._memo.clear()
    estado = crear_partida("clasica")

    resultado_1 = complex_agent._negamax(estado, -2, 2)
    tam_tras_primera_llamada = len(complex_agent._memo)
    assert tam_tras_primera_llamada > 0

    resultado_2 = complex_agent._negamax(estado, -2, 2)
    # La segunda llamada reutiliza la entrada memoizada: mismo resultado y
    # ningún crecimiento adicional de la caché.
    assert resultado_2 == resultado_1
    assert len(complex_agent._memo) == tam_tras_primera_llamada


def test_no_pierde_una_partida_previamente_reproducida_con_cache_persistente():
    """Regresión: con random.seed(758), jugando Complejo=X vs Sencillo=O con
    la caché de _negamax ya usada en turnos anteriores de la MISMA partida,
    Complejo llegaba a una posición con victoria inmediata en (2,2)
    (diagonal (0,0),(1,1),(2,2)) y en su lugar jugaba (1,0), perdiendo la
    partida.

    Causa raíz: la caché guardaba también cotas (no solo valores exactos)
    de búsquedas podadas por alfa-beta, y una cota obsoleta (aunque
    técnicamente correcta para la ventana con la que se calculó) se usaba
    para acotar alpha/beta de una llamada posterior con una ventana
    distinta, provocando un corte prematuro que nunca llegó a evaluar la
    respuesta ganadora real del rival. Corregido memoizando únicamente
    valores exactos (búsquedas no podadas).
    """
    import random

    random.seed(758)
    complex_agent._memo.clear()

    estado = crear_partida("clasica")
    while estado.status == "en_curso":
        if estado.turn == "X":
            jugada = complex_agent.decidir_jugada(estado)
        else:
            jugada = simple.decidir_jugada(estado)
        estado = aplicar_jugada(estado, jugada)

    assert not (estado.status == "victoria" and estado.winner == "O")
