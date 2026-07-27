"""Utilidades compartidas por los tres niveles de agente.

Reutilizan exclusivamente el motor de la spec 001
(`backend.src.models.game_state`, `backend.src.engine.rules`) como entrada
de solo lectura; ningún agente reimplementa reglas de juego.
"""

from typing import Optional

from backend.src.engine.rules import aplicar_jugada
from backend.src.engine.win_detection import comprobar_victoria
from backend.src.models.game_state import Coordenada, Ficha, GameState, Jugada


def otro_jugador(jugador: Ficha) -> Ficha:
    return "O" if jugador == "X" else "X"


def listar_jugadas_legales(estado: GameState) -> list[Jugada]:
    """Lista las jugadas legales para `estado.turn` en el estado dado.

    Modalidad clásica, o continua en fase de colocación: coloca en
    cualquier casilla vacía. Continua en fase de movimiento: mueve
    cualquier ficha propia hacia cualquier casilla vacía (sin restricción
    de adyacencia, CA-M-11). Devuelve una lista vacía si la partida ya
    finalizó.
    """
    if estado.status != "en_curso":
        return []

    jugador = estado.turn
    vacias = [
        (fila, col)
        for fila in range(3)
        for col in range(3)
        if estado.board[fila][col] is None
    ]

    if estado.mode == "clasica" or estado.phase == "colocacion":
        if estado.mode == "continua" and estado.fichas_disponibles.get(jugador, 0) <= 0:
            # `jugador` ya agotó sus fichas de colocación (solo puede darse
            # al evaluar hipotéticamente el turno del rival, ver
            # detectar_jugada_ganadora); no tiene jugada de colocar posible.
            return []
        return [
            Jugada(player=jugador, type="colocar", to=Coordenada(row=fila, col=col))
            for fila, col in vacias
        ]

    # Modalidad continua, fase de movimiento.
    propias = [
        (fila, col)
        for fila in range(3)
        for col in range(3)
        if estado.board[fila][col] == jugador
    ]
    return [
        Jugada(
            player=jugador,
            type="mover",
            to=Coordenada(row=fila_d, col=col_d),
            **{"from": Coordenada(row=fila_o, col=col_o)},
        )
        for fila_o, col_o in propias
        for fila_d, col_d in vacias
    ]


def simular_jugada(estado: GameState, jugada: Jugada) -> GameState:
    """Envoltorio de solo lectura sobre `aplicar_jugada` del motor (spec 001).

    Los agentes lo usan para explorar hipotéticamente el resultado de una
    jugada (p. ej. para detectar victorias o amenazas) sin duplicar
    ninguna regla de juego: `estado` no se modifica, se recibe un
    `GameState` nuevo. Se asume que `jugada` proviene de
    `listar_jugadas_legales(estado)` y por tanto es legal; no se captura
    `JugadaInvalida` aquí.
    """
    return aplicar_jugada(estado, jugada)


def detectar_jugada_ganadora(estado: GameState, jugador: Ficha) -> Optional[Jugada]:
    """Devuelve una jugada de `jugador` que le da la victoria inmediata, si existe.

    `jugador` puede ser distinto de `estado.turn` (p. ej. el agente Medio
    evaluando si el rival podría ganar en su próximo turno, CA-A-04): en
    ese caso se evalúa hipotéticamente un estado con el turno de
    `jugador`, reutilizando `listar_jugadas_legales` y `simular_jugada` sin
    modificar `estado`. Usada también por el agente Complejo (CA-A-08).
    """
    estado_hipotetico = (
        estado if jugador == estado.turn else estado.model_copy(update={"turn": jugador})
    )
    for jugada in listar_jugadas_legales(estado_hipotetico):
        resultado = simular_jugada(estado_hipotetico, jugada)
        if comprobar_victoria(resultado.board) is not None:
            return jugada
    return None
