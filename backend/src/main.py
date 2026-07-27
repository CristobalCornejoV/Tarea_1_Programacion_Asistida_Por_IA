"""Punto de entrada de la app FastAPI: motor, agentes e interfaz del juego
tres en raya."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.src.api.agents import router as agents_router
from backend.src.api.games import router as games_router

app = FastAPI(title="Tres en Raya - Motor y Agentes")
app.include_router(games_router)
app.include_router(agents_router)

# frontend/ se sirve como archivos estáticos (Vanilla JS/HTML/CSS, sin build
# step); montado al final para que las rutas de /api/games y /api/agents ya
# registradas arriba tengan prioridad de coincidencia (spec 003).
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
