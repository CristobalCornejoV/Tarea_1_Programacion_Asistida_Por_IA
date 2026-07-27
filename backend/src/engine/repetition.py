"""Regla de empate por repetición de posición (modalidad continua, CA-M-14).

El conteo solo tiene sentido durante la fase de movimiento (ver Assumptions
de spec.md): las posiciones vistas durante la fase de colocación no cuentan.
"""

from backend.src.models.game_state import Casilla


def clave_posicion(board: list[list[Casilla]]) -> str:
    """Representación canónica de un tablero como string de 9 caracteres."""
    return "".join(casilla or "_" for fila in board for casilla in fila)


def registrar_posicion(
    posiciones_vistas: dict[str, int], board: list[list[Casilla]]
) -> tuple[dict[str, int], int]:
    """Incrementa el conteo de la posición dada y devuelve (nuevo_dict, conteo_actual)."""
    clave = clave_posicion(board)
    nuevas = dict(posiciones_vistas)
    nuevas[clave] = nuevas.get(clave, 0) + 1
    return nuevas, nuevas[clave]
