"""Infraestructura compartida para las pruebas de interfaz en navegador."""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


@pytest.fixture(scope="session")
def live_server_url() -> Iterator[str]:
    """Levanta la aplicación real en un puerto libre durante la suite E2E."""

    port = _available_port()
    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.src.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=REPOSITORY_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("El servidor de pruebas terminó antes de iniciar.")
        try:
            with urllib.request.urlopen(url, timeout=0.25) as response:
                if response.status == 200:
                    break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)
    else:
        process.terminate()
        raise RuntimeError("El servidor de pruebas no respondió a tiempo.")

    yield url

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
