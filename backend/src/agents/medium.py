"""Agente Medio: ganar > bloquear > azar (CA-A-03, CA-A-04, CA-A-05, CA-A-06)."""

import random

from backend.src.agents.shared import (
    detectar_jugada_ganadora,
    listar_jugadas_legales,
    otro_jugador,
)
from backend.src.models.game_state import GameState, Jugada


def decidir_jugada(estado: GameState) -> Jugada:
    """Aplica, en orden: victoria propia -> bloqueo del rival -> azar.

    Es una función pura de `estado`: no lee ni escribe ningún estado
    propio entre llamadas. La "memoria de la partida en curso" exigida por
    CA-A-06 queda satisfecha porque `estado` (el `GameState` completo
    recibido en cada solicitud) ya contiene toda la información necesaria
    para evaluar ambas condiciones; no hace falta recordar nada de
    solicitudes anteriores (ver `research.md` Decisión 1).
    """
    victoria_propia = detectar_jugada_ganadora(estado, estado.turn)
    if victoria_propia is not None:
        return victoria_propia

    rival = otro_jugador(estado.turn)
    amenaza_rival = detectar_jugada_ganadora(estado, rival)
    if amenaza_rival is not None:
        # Bloquear: ocupar la misma casilla destino, pero como estado.turn
        # (la jugada de `amenaza_rival` pertenece al rival, no a nosotros).
        bloqueos = [
            jugada
            for jugada in listar_jugadas_legales(estado)
            if jugada.to == amenaza_rival.to
        ]
        if bloqueos:
            return random.choice(bloqueos)

    return random.choice(listar_jugadas_legales(estado))
