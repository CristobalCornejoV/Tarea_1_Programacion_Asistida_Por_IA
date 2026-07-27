"""Punto de entrada de la app FastAPI: API y archivos estáticos de la interfaz."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.src.api.agents import router as agents_router
from backend.src.api.games import router as games_router

app = FastAPI(title="Tres en Raya - Motor y Agentes")
app.include_router(games_router)
app.include_router(agents_router)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)
