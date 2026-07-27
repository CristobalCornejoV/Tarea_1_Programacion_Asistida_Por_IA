"""Flujos críticos de la interfaz definidos por CA-I-01 a CA-I-18."""

from __future__ import annotations

import json

import pytest

playwright = pytest.importorskip(
    "playwright.sync_api",
    reason="pytest-playwright es una dependencia opcional de pruebas E2E",
)
Page = playwright.Page
expect = playwright.expect


def _game_state(
    *,
    game_id: str = "game-e2e",
    mode: str = "clasica",
    board: list[list[str | None]] | None = None,
    turn: str = "X",
    phase: str | None = None,
    fichas_disponibles: dict[str, int] | None = None,
    status: str = "en_curso",
    winner: str | None = None,
    winning_line: list[dict[str, int]] | None = None,
) -> dict:
    return {
        "game_id": game_id,
        "mode": mode,
        "board": board or [[None, None, None] for _ in range(3)],
        "turn": turn,
        "phase": phase,
        "fichas_disponibles": fichas_disponibles,
        "status": status,
        "winner": winner,
        "winning_line": winning_line,
    }


def _fulfill_json(route, payload: dict, status: int = 200) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=json.dumps(payload),
    )


def test_configuracion_inicial(page: Page, live_server_url: str) -> None:
    """CA-I-01 a CA-I-04: configuración inicial, completa e incompleta."""

    page.route(
        "**/api/games",
        lambda route: _fulfill_json(route, _game_state(), status=201),
    )
    page.goto(live_server_url)

    expect(page.locator("#config-screen")).to_be_visible()
    expect(page.locator("#game-screen")).to_be_hidden()
    expect(page.locator('input[name="modo"]')).to_have_count(2)
    expect(page.locator('input[name="ficha_jugador_1"]')).to_have_count(2)
    expect(page.locator('input[name="modalidad"]')).to_have_count(2)

    page.get_by_role("button", name="Iniciar partida").click()
    expect(page.locator("#config-error-summary")).to_be_visible()
    expect(page.locator("#config-screen")).to_be_visible()
    expect(page.locator("[data-config-field].has-error")).to_have_count(3)

    page.get_by_label("Humano vs Agente").check()
    expect(page.locator("#agent-level-group")).to_be_visible()
    expect(page.locator('input[name="nivel_agente"]')).to_have_count(3)
    page.get_by_label("Medio").check()
    page.get_by_label("Jugador 1 usa O").check()
    page.get_by_label("Clásica").check()
    page.get_by_role("button", name="Iniciar partida").click()

    expect(page.locator("#config-screen")).to_be_hidden()
    expect(page.locator("#game-screen")).to_be_visible()
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")
    expect(page.locator("#fact-mode")).to_have_text("Humano vs Agente")
    expect(page.locator("#fact-level")).to_have_text("Medio")
