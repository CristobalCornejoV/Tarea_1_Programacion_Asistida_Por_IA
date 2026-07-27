"""Router FastAPI del motor de juego (`/api/games`).

Los endpoints se añaden en las tareas de US1 (modalidad clásica) y US2
(modalidad continua); esta tarea solo establece el router y el almacén en
memoria que dichos endpoints usarán.
"""

from fastapi import APIRouter

from backend.src.models.game_state import GameState

router = APIRouter(prefix="/api/games", tags=["games"])

# Almacén en memoria de partidas: game_id -> último GameState de esa partida.
partidas: dict[str, GameState] = {}
