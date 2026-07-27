"""Test de integración estadístico obligatorio (T019, CA-A-07).

Simula 100 partidas completas en modalidad clásica entre el agente
Sencillo y el agente Complejo, alternando quién inicia como X, aplicando
cada jugada a través del motor (spec 001), y verifica que el agente
Complejo termina con 0 derrotas en las 100 partidas.
"""

from backend.src.agents import complex as complex_agent
from backend.src.agents import simple
from backend.src.engine.rules import aplicar_jugada, crear_partida
from backend.src.models.game_state import GameState


def _jugar_partida_completa(agente_x, agente_o) -> GameState:
    estado = crear_partida("clasica")
    while estado.status == "en_curso":
        agente = agente_x if estado.turn == "X" else agente_o
        jugada = agente(estado)
        estado = aplicar_jugada(estado, jugada)
    return estado


def test_complejo_no_pierde_ninguna_de_100_partidas_contra_sencillo():  # CA-A-07
    derrotas_del_complejo = 0

    for i in range(100):
        complejo_es_x = i % 2 == 0
        if complejo_es_x:
            estado_final = _jugar_partida_completa(
                complex_agent.decidir_jugada, simple.decidir_jugada
            )
            complejo_perdio = (
                estado_final.status == "victoria" and estado_final.winner == "O"
            )
        else:
            estado_final = _jugar_partida_completa(
                simple.decidir_jugada, complex_agent.decidir_jugada
            )
            complejo_perdio = (
                estado_final.status == "victoria" and estado_final.winner == "X"
            )

        assert estado_final.status in ("victoria", "empate")
        if complejo_perdio:
            derrotas_del_complejo += 1

    assert derrotas_del_complejo == 0
