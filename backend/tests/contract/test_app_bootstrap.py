"""Tests fundacionales del esqueleto de la app FastAPI (T006).

No cubren un CA-M-* de comportamiento de juego (el router de /api/games aún
no tiene endpoints; esos llegan en las tareas de US1/US2); verifican que la
app arranca, el router está montado bajo el prefijo correcto, y el almacén
en memoria existe y comienza vacío.
"""

from fastapi.testclient import TestClient

from backend.src.api.games import partidas, router as games_router
from backend.src.main import app


def test_app_arranca_sin_error_de_servidor():
    client = TestClient(app)
    # El router aún no define endpoints (llegan en US1/US2); cualquier ruta
    # bajo el prefijo montado debe responder 404 "no encontrado", nunca un
    # error 500 de arranque o de resolución de dependencias.
    response = client.get("/api/games/inexistente")
    assert response.status_code == 404


def test_router_games_tiene_el_prefijo_correcto():
    # El router aún no tiene endpoints propios (llegan en US1/US2); esta
    # tarea solo garantiza que `app.include_router(games_router)` (main.py)
    # no lanzó excepciones al importar, y que el prefijo quedó bien definido
    # para que los endpoints de US1/US2 se registren bajo /api/games.
    assert games_router.prefix == "/api/games"
    assert app is not None


def test_almacen_en_memoria_de_partidas_inicia_vacio():
    assert partidas == {}
