"""Agente Sencillo: jugada legal elegida al azar, sin memoria (CA-A-01, CA-A-02)."""

import random

from backend.src.agents.shared import listar_jugadas_legales
from backend.src.models.game_state import GameState, Jugada


def decidir_jugada(estado: GameState) -> Jugada:
    """Elige una jugada legal al azar, sin usar información de turnos anteriores.

    No lee ni escribe ningún estado propio entre llamadas: toda la
    información necesaria proviene únicamente del `estado` recibido
    (CA-A-02).
    """
    return random.choice(listar_jugadas_legales(estado))
