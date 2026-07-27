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

# Caché de memoización (tabla de transposición): clave canónica ->
# (valor, tipo_cota, mejor_jugada). `tipo_cota` es necesario porque, con
# poda alfa-beta, un valor calculado bajo una ventana [alpha, beta]
# estrecha puede ser solo una cota (no el valor exacto); reutilizarlo sin
# distinguir el tipo de cota daría resultados incorrectos bajo una ventana
# distinta. Persiste en memoria de proceso entre partidas (CA-A-09); nunca
# se limpia entre llamadas.
_memo: dict[str, tuple[int, str, Optional[Jugada]]] = {}

_EXACTO = "exacto"
_COTA_INFERIOR = "cota_inferior"
_COTA_SUPERIOR = "cota_superior"


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

    Nota importante: el motor (spec 001) deja `turn` sin alternar tras una
    jugada ganadora (`turn` queda igual al ganador), a diferencia de una
    jugada que continúa la partida o que empata (donde `turn` sí alterna).
    Por eso las transiciones terminales se evalúan aquí mismo, en el bucle,
    relativas a `jugada.player` (quien acaba de mover) — NO negando
    genéricamente el valor de una llamada recursiva sobre el hijo — ya que
    asumir que el turno siempre alterna daría un signo incorrecto
    precisamente en el caso de una victoria.

    La caché (tabla de transposición) solo corta la búsqueda cuando el tipo
    de cota almacenado es concluyente para la ventana [alpha, beta]
    vigente; en caso contrario, se usa únicamente para acotar alpha/beta
    antes de continuar la búsqueda, evitando el error clásico de reutilizar
    una cota como si fuera un valor exacto.
    """
    terminal_raiz = _valor_terminal_para_estado_raiz(estado)
    if terminal_raiz is not None:
        return None, terminal_raiz

    alpha_original = alpha
    clave = _clave_canonica(estado)
    entrada = _memo.get(clave)
    if entrada is not None:
        valor_cacheado, tipo_cota, jugada_cacheada = entrada
        if tipo_cota == _EXACTO:
            return jugada_cacheada, valor_cacheado
        if tipo_cota == _COTA_INFERIOR:
            alpha = max(alpha, valor_cacheado)
        elif tipo_cota == _COTA_SUPERIOR:
            beta = min(beta, valor_cacheado)
        if alpha >= beta:
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

    if mejor_valor <= alpha_original:
        tipo_cota = _COTA_SUPERIOR
    elif mejor_valor >= beta:
        tipo_cota = _COTA_INFERIOR
    else:
        tipo_cota = _EXACTO
    _memo[clave] = (mejor_valor, tipo_cota, mejor_jugada)
    return mejor_jugada, mejor_valor


def decidir_jugada(estado: GameState) -> Jugada:
    """Jugada óptima para `estado.turn`: victoria forzada si existe, empate en
    caso contrario (CA-A-08), nunca una derrota evitable (CA-A-07)."""
    jugada, _ = _negamax(estado, -2, 2)
    return jugada
