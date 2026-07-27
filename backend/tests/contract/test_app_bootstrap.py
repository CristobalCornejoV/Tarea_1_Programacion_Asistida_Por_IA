"""Tests fundacionales del esqueleto de la app FastAPI (T006, spec 001) y
del montaje del frontend estático (T002, spec 003).

No cubren un CA-M-*/CA-I-* de comportamiento (son tareas de Setup);
verifican que la app arranca, el router está montado bajo el prefijo
correcto, el almacén en memoria existe y comienza vacío, y que servir
`frontend/` como estáticos en "/" no interfiere con las rutas de `/api/*`.
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


def test_frontend_estatico_sirve_index_html_en_raiz():  # T002
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Tres en Raya</title>" in response.text


def test_montaje_de_frontend_no_interfiere_con_rutas_api():  # T002
    client = TestClient(app)
    # Con el frontend montado en "/", las rutas /api/* SHALL seguir
    # resolviendo contra sus routers (games/agents), no contra StaticFiles.
    response = client.post("/api/games", json={"mode": "clasica"})
    assert response.status_code == 201
