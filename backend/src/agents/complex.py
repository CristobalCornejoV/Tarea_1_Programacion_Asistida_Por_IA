"""Agente Complejo: juego óptimo vía negamax con poda alfa-beta (CA-A-07,
CA-A-08), con memoria persistente entre partidas (CA-A-09).

Garantía de optimalidad acotada a modalidad clásica (ver
`research.md` Decisión 4): el árbol de búsqueda de tres en raya clásico es
finito y pequeño (máximo 9 jugadas), por lo que un cálculo completo desde
cero resuelve muy por debajo de 1 segundo incluso sin memoización.
"""

from typing import Optional

from backend.src.agents.shared import listar_jugadas_legales, simular_jugada
from backend.src.models.game_state import GameState, Jugada

# Caché de memoización: clave canónica -> (valor, mejor_jugada). Solo se
# almacena (y solo se reutiliza) cuando el valor es EXACTO — es decir, la
# búsqueda que lo produjo no fue interrumpida por poda alfa-beta. Un valor
# obtenido bajo poda es apenas una cota (válida solo para la ventana
# [alpha, beta] con la que se pidió), no el valor real de la posición;
# usar esa cota para acotar alpha/beta de una llamada futura con una
# ventana distinta puede corromper esa búsqueda (ver nota larga en
# `_negamax`). Persiste en memoria de proceso entre partidas (CA-A-09).
_memo: dict[str, tuple[int, Optional[Jugada]]] = {}


def _clave_canonica(estado: GameState) -> str:
    """Representación canónica de (board, turn) usada como clave de caché (CA-A-09)."""
    tablero = "".join(casilla or "_" for fila in estado.board for casilla in fila)
    return f"{tablero}:{estado.turn}"


def _valor_terminal_para_estado_raiz(estado: GameState) -> Optional[int]:
    """Valor terminal relativo a `estado.turn`, solo para una llamada externa
    directa sobre un estado ya finalizado (no se usa en la recursión interna:
    ver la nota en `_negamax` sobre por qué el turno no sirve como
    perspectiva genérica al atravesar una transición ganadora)."""
    if estado.status == "victoria":
        return 1 if estado.winner == estado.turn else -1
    if estado.status == "empate":
        return 0
    return None


def _negamax(estado: GameState, alpha: int, beta: int) -> tuple[Optional[Jugada], int]:
    """Devuelve (mejor_jugada, valor) para `estado.turn`, vía negamax con poda alfa-beta.

    Nota importante (1): el motor (spec 001) deja `turn` sin alternar tras
    una jugada ganadora (`turn` queda igual al ganador), a diferencia de
    una jugada que continúa la partida o que empata (donde `turn` sí
    alterna). Por eso las transiciones terminales se evalúan aquí mismo, en
    el bucle, relativas a `jugada.player` (quien acaba de mover) — NO
    negando genéricamente el valor de una llamada recursiva sobre el hijo —
    ya que asumir que el turno siempre alterna daría un signo incorrecto
    precisamente en el caso de una victoria.

    Nota importante (2): la caché solo guarda y reutiliza valores EXACTOS
    (búsquedas que no fueron cortadas por la poda alfa-beta, es decir,
    `alpha_original < mejor_valor < beta`). Una primera versión también
    guardaba cotas (superior/inferior) para usarlas al acotar alpha/beta de
    llamadas futuras; eso introdujo un bug real: una cota, aunque
    correcta para la ventana con la que se calculó, puede ser irrelevante
    o incluso vacía de información bajo otra ventana (p. ej. una cota
    inferior igual al valor máximo posible del juego no acota nada), y
    usarla igualmente para estrechar alpha/beta de una búsqueda posterior
    podía provocar que esa búsqueda se cortara antes de examinar la
    respuesta ganadora real del rival, produciendo una decisión
    incorrecta. Guardar solo valores exactos evita el problema por
    completo: un valor exacto es correcto para cualquier ventana.
    """
    terminal_raiz = _valor_terminal_para_estado_raiz(estado)
    if terminal_raiz is not None:
        return None, terminal_raiz

    alpha_original = alpha
    clave = _clave_canonica(estado)
    entrada = _memo.get(clave)
    if entrada is not None:
        valor_cacheado, jugada_cacheada = entrada
        return jugada_cacheada, valor_cacheado

    mejor_valor = -2
    mejor_jugada: Optional[Jugada] = None
    for jugada in listar_jugadas_legales(estado):
        resultado = simular_jugada(estado, jugada)
        if resultado.status == "victoria":
            valor = 1 if resultado.winner == jugada.player else -1
        elif resultado.status == "empate":
            valor = 0
        else:
            _, valor_hijo = _negamax(resultado, -beta, -alpha)
            valor = -valor_hijo

        if valor > mejor_valor:
            mejor_valor = valor
            mejor_jugada = jugada
        alpha = max(alpha, mejor_valor)
        if alpha >= beta:
            break

    if alpha_original < mejor_valor < beta:
        _memo[clave] = (mejor_valor, mejor_jugada)
    return mejor_jugada, mejor_valor


def decidir_jugada(estado: GameState) -> Jugada:
    """Jugada óptima para `estado.turn`: victoria forzada si existe, empate en
    caso contrario (CA-A-08), nunca una derrota evitable (CA-A-07)."""
    jugada, _ = _negamax(estado, -2, 2)
    return jugada
