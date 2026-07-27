"""Reglas del motor de juego: funciones puras sobre GameState.

Cubre ambas modalidades: clásica (colocar_ficha) y continua (colocar_ficha
en fase de colocación, mover_ficha en fase de movimiento).
"""

import uuid
from typing import Literal

from backend.src.engine.repetition import registrar_posicion
from backend.src.engine.win_detection import comprobar_victoria
from backend.src.models.game_state import Coordenada, GameState, Jugada


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


def _dentro_del_tablero(coord: Coordenada) -> bool:
    return 0 <= coord.row <= 2 and 0 <= coord.col <= 2


def _validar_rango(*coords: Coordenada) -> None:
    """CA-M-*: rechaza coordenadas fuera de las 3x3 casillas del tablero."""
    for coord in coords:
        if not _dentro_del_tablero(coord):
            raise JugadaInvalida(
                "fuera_de_rango",
                f"La casilla ({coord.row}, {coord.col}) está fuera del tablero.",
            )


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
    """Coloca una ficha en una casilla vacía.

    Clásica siempre; continua solo durante la fase de colocación.

    CA-M-02, CA-M-09: coloca y alterna turno (descontando fichas
    disponibles en continua). CA-M-03: rechaza casilla ocupada. CA-M-04:
    rechaza jugada fuera de turno. CA-M-07, CA-M-15: rechaza si la partida
    ya finalizó. CA-M-10: transiciona a fase de movimiento cuando ambos
    jugadores agotan sus fichas. CA-M-15: rechaza colocar fuera de la fase
    de colocación en modalidad continua.
    """
    if estado.status != "en_curso":
        raise JugadaInvalida("partida_finalizada", "La partida ya finalizó.")
    if jugada.player != estado.turn:
        raise JugadaInvalida(
            "fuera_de_turno", f"No es el turno de {jugada.player}."
        )
    if estado.mode == "continua" and estado.phase != "colocacion":
        raise JugadaInvalida(
            "fase_incorrecta",
            "No se puede colocar una ficha fuera de la fase de colocación.",
        )
    _validar_rango(jugada.to)

    fila, col = jugada.to.row, jugada.to.col
    if estado.board[fila][col] is not None:
        raise JugadaInvalida(
            "casilla_ocupada", f"La casilla ({fila}, {col}) ya está ocupada."
        )

    nuevo_board = [fila_actual.copy() for fila_actual in estado.board]
    nuevo_board[fila][col] = jugada.player

    updates: dict = {"board": nuevo_board}

    if estado.mode == "continua":
        nuevas_fichas = dict(estado.fichas_disponibles)
        nuevas_fichas[jugada.player] -= 1
        if nuevas_fichas["X"] == 0 and nuevas_fichas["O"] == 0:
            updates["phase"] = "movimiento"
            updates["fichas_disponibles"] = None
            updates["posiciones_vistas"] = registrar_posicion({}, nuevo_board)[0]
        else:
            updates["fichas_disponibles"] = nuevas_fichas

    linea_ganadora = comprobar_victoria(nuevo_board)
    if linea_ganadora is not None:
        updates.update(
            {
                "status": "victoria",
                "winner": jugada.player,
                "winning_line": linea_ganadora,
            }
        )
        return estado.model_copy(update=updates)

    tablero_lleno = all(
        casilla is not None for fila_b in nuevo_board for casilla in fila_b
    )
    if tablero_lleno:
        updates.update({"status": "empate", "turn": _otro(jugada.player)})
        return estado.model_copy(update=updates)

    updates["turn"] = _otro(jugada.player)
    return estado.model_copy(update=updates)


def mover_ficha(estado: GameState, jugada: Jugada) -> GameState:
    """Mueve una ficha propia a cualquier casilla vacía (solo continua, fase movimiento).

    CA-M-11: mueve sin restricción de adyacencia. CA-M-12: rechaza mover
    ficha ajena o hacia casilla ocupada. CA-M-13: detecta victoria. CA-M-14:
    empate por repetición de posición 3 veces. CA-M-07, CA-M-15: rechaza si
    la partida ya finalizó o si no corresponde la fase/modalidad.
    """
    if estado.status != "en_curso":
        raise JugadaInvalida("partida_finalizada", "La partida ya finalizó.")
    if jugada.player != estado.turn:
        raise JugadaInvalida(
            "fuera_de_turno", f"No es el turno de {jugada.player}."
        )
    if estado.mode != "continua" or estado.phase != "movimiento":
        raise JugadaInvalida(
            "fase_incorrecta",
            "Solo se puede mover una ficha en la fase de movimiento de la modalidad continua.",
        )
    _validar_rango(jugada.from_, jugada.to)

    fila_o, col_o = jugada.from_.row, jugada.from_.col
    fila_d, col_d = jugada.to.row, jugada.to.col

    if estado.board[fila_o][col_o] != jugada.player:
        raise JugadaInvalida(
            "ficha_ajena",
            f"La casilla ({fila_o}, {col_o}) no contiene una ficha de {jugada.player}.",
        )
    if estado.board[fila_d][col_d] is not None:
        raise JugadaInvalida(
            "casilla_ocupada", f"La casilla ({fila_d}, {col_d}) ya está ocupada."
        )

    nuevo_board = [fila_actual.copy() for fila_actual in estado.board]
    nuevo_board[fila_o][col_o] = None
    nuevo_board[fila_d][col_d] = jugada.player

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

    nuevas_posiciones, conteo = registrar_posicion(estado.posiciones_vistas, nuevo_board)
    if conteo >= 3:
        return estado.model_copy(
            update={
                "board": nuevo_board,
                "status": "empate",
                "posiciones_vistas": nuevas_posiciones,
            }
        )

    return estado.model_copy(
        update={
            "board": nuevo_board,
            "turn": _otro(jugada.player),
            "posiciones_vistas": nuevas_posiciones,
        }
    )


def aplicar_jugada(estado: GameState, jugada: Jugada) -> GameState:
    """Punto de entrada único para aplicar una jugada sobre un GameState."""
    if jugada.type == "colocar":
        return colocar_ficha(estado, jugada)
    if jugada.type == "mover":
        return mover_ficha(estado, jugada)
    raise JugadaInvalida("fase_incorrecta", "Tipo de jugada no soportado.")
