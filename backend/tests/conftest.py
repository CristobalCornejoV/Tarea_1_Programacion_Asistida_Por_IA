"""Fixtures compartidas: aísla el almacén en memoria de partidas entre tests."""

import pytest

from backend.src.api.games import partidas


@pytest.fixture(autouse=True)
def _reset_partidas_store():
    partidas.clear()
    yield
    partidas.clear()
