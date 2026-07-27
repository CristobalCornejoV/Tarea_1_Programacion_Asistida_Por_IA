"""Router FastAPI del motor de juego (`/api/games`).

Ver `contracts/games-api.md` (spec 001) para el contrato HTTP exacto.
"""

from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.src.engine.rules import JugadaInvalida, aplicar_jugada, crear_partida
from backend.src.models.game_state import ErrorJugada, GameState, Jugada

router = APIRouter(prefix="/api/games", tags=["games"])

# Almacén en memoria de partidas: game_id -> último GameState de esa partida.
partidas: dict[str, GameState] = {}


class CrearPartidaRequest(BaseModel):
    mode: Literal["clasica", "continua"]


@router.post("", status_code=201, response_model=GameState)
def crear_partida_endpoint(body: CrearPartidaRequest) -> GameState:
    """Crea una partida nueva (CA-M-01, CA-M-08)."""
    estado = crear_partida(body.mode)
    partidas[estado.game_id] = estado
    return estado


@router.get("/{game_id}", response_model=GameState)
def obtener_partida_endpoint(game_id: str) -> GameState:
    """Consulta el GameState actual de una partida existente."""
    estado = partidas.get(game_id)
    if estado is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada.")
    return estado


@router.post("/{game_id}/moves")
def aplicar_jugada_endpoint(game_id: str, jugada: Jugada):
    """Aplica una jugada; 422 con ErrorJugada si es inválida (CA-M-02 a CA-M-07)."""
    estado = partidas.get(game_id)
    if estado is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada.")
    try:
        nuevo_estado = aplicar_jugada(estado, jugada)
    except JugadaInvalida as exc:
        error = ErrorJugada(error=exc.codigo, message=exc.mensaje)
        return JSONResponse(status_code=422, content=error.model_dump())
    partidas[game_id] = nuevo_estado
    return nuevo_estado
