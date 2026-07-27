"""Reglas del motor de juego: funciones puras sobre GameState (modalidad clásica).

Las extensiones de modalidad continua (fase de colocación/movimiento,
mover_ficha, repetición de posiciones) se añaden en las tareas de US2.
"""

import uuid
from typing import Literal

from backend.src.engine.win_detection import comprobar_victoria
from backend.src.models.game_state import GameState, Jugada


class JugadaInvalida(Exception):
    """Jugada rechazada por el motor; `codigo` identifica el motivo (ver ErrorJugada)."""

    def __init__(self, codigo: str, mensaje: str):
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(mensaje)


def _tablero_vacio() -> list[list[None]]:
    return [[None, None, None] for _ in range(3)]


def _otro(jugador: Literal["X", "O"]) -> Literal["X", "O"]:
    return "O" if jugador == "X" else "X"


def crear_partida(mode: Literal["clasica", "continua"]) -> GameState:
    """Crea el GameState inicial: tablero vacío, turno de X (CA-M-01, CA-M-08)."""
    board = _tablero_vacio()
    if mode == "continua":
        return GameState(
            game_id=str(uuid.uuid4()),
            mode=mode,
            board=board,
            turn="X",
            phase="colocacion",
            fichas_disponibles={"X": 3, "O": 3},
            status="en_curso",
        )
    return GameState(
        game_id=str(uuid.uuid4()),
        mode=mode,
        board=board,
        turn="X",
        status="en_curso",
    )


def colocar_ficha(estado: GameState, jugada: Jugada) -> GameState:
    """Coloca una ficha en una casilla vacía en modalidad clásica.

    CA-M-02: coloca y alterna turno. CA-M-03: rechaza casilla ocupada.
    CA-M-04: rechaza jugada fuera de turno. CA-M-07: rechaza si la partida
    ya finalizó.
    """
    if estado.status != "en_curso":
        raise JugadaInvalida("partida_finalizada", "La partida ya finalizó.")
    if jugada.player != estado.turn:
        raise JugadaInvalida(
            "fuera_de_turno", f"No es el turno de {jugada.player}."
        )

    fila, col = jugada.to.row, jugada.to.col
    if estado.board[fila][col] is not None:
        raise JugadaInvalida(
            "casilla_ocupada", f"La casilla ({fila}, {col}) ya está ocupada."
        )

    nuevo_board = [fila_actual.copy() for fila_actual in estado.board]
    nuevo_board[fila][col] = jugada.player

    linea_ganadora = comprobar_victoria(nuevo_board)
    if linea_ganadora is not None:
        return estado.model_copy(
            update={
                "board": nuevo_board,
                "status": "victoria",
                "winner": jugada.player,
                "winning_line": linea_ganadora,
            }
        )

    tablero_lleno = all(
        casilla is not None for fila_b in nuevo_board for casilla in fila_b
    )
    if tablero_lleno:
        return estado.model_copy(
            update={
                "board": nuevo_board,
                "status": "empate",
                "turn": _otro(jugada.player),
            }
        )

    return estado.model_copy(
        update={"board": nuevo_board, "turn": _otro(jugada.player)}
    )


def aplicar_jugada(estado: GameState, jugada: Jugada) -> GameState:
    """Punto de entrada único para aplicar una jugada sobre un GameState."""
    if jugada.type == "colocar":
        return colocar_ficha(estado, jugada)
    raise JugadaInvalida(
        "fase_incorrecta",
        "Tipo de jugada 'mover' no soportado en modalidad clásica.",
    )
