"""Router FastAPI de agentes (`/api/agents`).

Ver `contracts/agents-api.md` (spec 002) para el contrato HTTP exacto. El
registro `AGENTES` mapea cada nivel a su función `decidir_jugada`; un nivel
ausente del registro (incluyendo niveles aún no implementados) responde 404.
"""

from typing import Callable, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from backend.src.agents import simple
from backend.src.models.game_state import Casilla, Coordenada, Ficha, GameState, Jugada

router = APIRouter(prefix="/api/agents", tags=["agents"])


class SolicitudJugadaAgente(BaseModel):
    """Subconjunto de GameState necesario para decidir una jugada (data-model.md)."""

    board: list[list[Casilla]]
    mode: Literal["clasica", "continua"]
    phase: Optional[Literal["colocacion", "movimiento"]] = None
    turn: Ficha
    fichas_disponibles: Optional[dict[Ficha, int]] = None


class JugadaAgenteResponse(BaseModel):
    """Respuesta del agente: misma forma que Jugada, sin el campo `player`."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["colocar", "mover"]
    to: Coordenada
    from_: Optional[Coordenada] = Field(default=None, alias="from")

    @classmethod
    def desde_jugada(cls, jugada: Jugada) -> "JugadaAgenteResponse":
        return cls(type=jugada.type, to=jugada.to, **{"from": jugada.from_})


def _estado_desde_solicitud(solicitud: SolicitudJugadaAgente) -> GameState:
    return GameState(
        game_id="",
        mode=solicitud.mode,
        board=solicitud.board,
        turn=solicitud.turn,
        phase=solicitud.phase,
        fichas_disponibles=solicitud.fichas_disponibles,
        status="en_curso",
    )


# Registro de niveles soportados: se completa a medida que cada uno se
# implementa (US1: sencillo, US2: medio, US3: complejo).
AGENTES: dict[str, Callable[[GameState], Jugada]] = {
    "sencillo": simple.decidir_jugada,
}


@router.post("/{level}/move", response_model=JugadaAgenteResponse)
def decidir_jugada_endpoint(level: str, solicitud: SolicitudJugadaAgente):
    """Devuelve la jugada elegida por el agente del nivel indicado."""
    decidir_jugada = AGENTES.get(level)
    if decidir_jugada is None:
        raise HTTPException(status_code=404, detail=f"Nivel de agente desconocido: {level}")
    estado = _estado_desde_solicitud(solicitud)
    jugada = decidir_jugada(estado)
    return JugadaAgenteResponse.desde_jugada(jugada)
