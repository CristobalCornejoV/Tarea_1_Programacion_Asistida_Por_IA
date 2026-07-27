"""Detección de victoria: evalúa las 8 líneas fijas de un tablero 3x3."""

from typing import Optional

from backend.src.models.game_state import Casilla, Coordenada

LINEAS: list[list[tuple[int, int]]] = [
    # Filas
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    # Columnas
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    # Diagonales
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
]


def comprobar_victoria(board: list[list[Casilla]]) -> Optional[list[Coordenada]]:
    """Devuelve las 3 coordenadas de la línea ganadora, o None si no hay victoria."""
    for linea in LINEAS:
        valores = [board[fila][col] for fila, col in linea]
        if valores[0] is not None and valores[0] == valores[1] == valores[2]:
            return [Coordenada(row=fila, col=col) for fila, col in linea]
    return None
