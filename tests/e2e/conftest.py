"""Arnés de pruebas e2e: levanta la app FastAPI real (motor + agentes +
frontend estático) en un hilo, para que Playwright navegue contra ella
como un navegador real (T003).
"""

import threading
import time

import httpx
import pytest
import uvicorn

from backend.src.main import app

_PUERTO = 8199


class _ServidorEnHilo:
    def __init__(self, app, host: str, port: int):
        self._config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        self._server = uvicorn.Server(self._config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self.base_url = f"http://{host}:{port}"

    def start(self) -> None:
        self._thread.start()
        for _ in range(100):
            if getattr(self._server, "started", False):
                return
            time.sleep(0.05)
        raise RuntimeError("El servidor de pruebas e2e no arrancó a tiempo.")

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Sobrescribe el `base_url` de pytest-playwright con el servidor real."""
    servidor = _ServidorEnHilo(app, host="127.0.0.1", port=_PUERTO)
    servidor.start()
    yield servidor.base_url
    servidor.stop()


@pytest.fixture(autouse=True)
def _reiniciar_almacen_de_partidas():
    """Aísla cada test e2e limpiando el almacén en memoria del motor."""
    from backend.src.api.games import partidas

    partidas.clear()
    yield
    partidas.clear()
