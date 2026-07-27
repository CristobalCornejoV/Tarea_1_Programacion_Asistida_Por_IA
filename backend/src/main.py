"""Punto de entrada de la app FastAPI: motor y agentes del juego tres en raya."""

from fastapi import FastAPI

from backend.src.api.games import router as games_router

app = FastAPI(title="Tres en Raya - Motor y Agentes")
app.include_router(games_router)
