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


def _select_human_game(page: Page, variant: str = "Clásica") -> None:
    page.get_by_label("Humano vs Humano").check()
    page.get_by_label("Jugador 1 usa X").check()
    page.get_by_label(variant).check()
    page.get_by_role("button", name="Iniciar partida").click()


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


def test_jugar_partida(page: Page, live_server_url: str) -> None:
    """CA-I-05 a CA-I-08: turno, error, victoria, empate y bloqueo."""

    initial = _game_state()
    move_responses = [
        _game_state(
            board=[["X", None, None], [None, None, None], [None, None, None]],
            turn="O",
        ),
        {
            "error": "casilla_ocupada",
            "message": "La casilla ya está ocupada.",
            "_status": 422,
        },
        _game_state(
            board=[["X", None, None], ["O", None, None], [None, None, None]],
            turn="X",
        ),
        _game_state(
            board=[["X", "X", None], ["O", None, None], [None, None, None]],
            turn="O",
        ),
        _game_state(
            board=[["X", "X", None], ["O", "O", None], [None, None, None]],
            turn="X",
        ),
        _game_state(
            board=[["X", "X", "X"], ["O", "O", None], [None, None, None]],
            turn="X",
            status="victoria",
            winner="X",
            winning_line=[
                {"row": 0, "col": 0},
                {"row": 0, "col": 1},
                {"row": 0, "col": 2},
            ],
        ),
    ]

    page.route(
        "**/api/games",
        lambda route: _fulfill_json(route, initial, status=201),
    )

    def handle_move(route) -> None:
        response = move_responses.pop(0)
        status = response.pop("_status", 200)
        _fulfill_json(route, response, status=status)

    page.route("**/api/games/*/moves", handle_move)
    page.goto(live_server_url)
    _select_human_game(page)

    expect(page.locator("#turn-player")).to_contain_text("Jugador 1")
    expect(page.locator("#turn-detail")).to_contain_text("ficha X")

    page.locator("#cell-0-0").click()
    expect(page.locator("#turn-player")).to_contain_text("Jugador 2")
    expect(page.locator("#turn-detail")).to_contain_text("ficha O")

    board_before_error = page.locator("#board").inner_text()
    page.locator("#cell-0-0").click()
    expect(page.locator("#game-notice")).to_contain_text("ocupada")
    expect(page.locator("#board")).to_have_text(board_before_error)
    expect(page.locator("#turn-detail")).to_contain_text("ficha O")

    for cell_id in ("#cell-1-0", "#cell-0-1", "#cell-1-1", "#cell-0-2"):
        page.locator(cell_id).click()

    expect(page.locator("#app")).to_have_attribute("data-ui-state", "terminada")
    expect(page.locator(".board-cell.is-winning")).to_have_count(3)
    expect(page.locator('.board-cell[aria-disabled="true"]')).to_have_count(9)
    expect(page.locator("#result-title")).to_have_text("Victoria de X")

    draw_states = [
        _game_state(
            game_id="draw-e2e",
            board=[
                ["X", "O", "X"],
                ["X", "O", "O"],
                ["O", "X", "X"],
            ],
            turn="O",
            status="empate",
        )
    ]
    move_responses.extend(draw_states)
    initial["game_id"] = "draw-e2e"
    page.reload()
    _select_human_game(page)
    page.locator("#cell-0-0").click()

    expect(page.locator("#app")).to_have_attribute("data-ui-state", "terminada")
    expect(page.locator("#result-title")).to_have_text("Empate")
    expect(page.locator('.board-cell[aria-disabled="true"]')).to_have_count(9)


def test_espera_agente(page: Page, live_server_url: str) -> None:
    """CA-I-09 y CA-I-10: espera bloqueada y aplicación de jugada del agente."""

    initial = _game_state()
    after_human = _game_state(
        board=[["X", None, None], [None, None, None], [None, None, None]],
        turn="O",
    )
    after_agent = _game_state(
        board=[["X", None, None], [None, "O", None], [None, None, None]],
        turn="X",
    )
    engine_responses = [after_human, after_agent]
    pending_agent_routes = []

    page.route(
        "**/api/games",
        lambda route: _fulfill_json(route, initial, status=201),
    )
    page.route(
        "**/api/games/*/moves",
        lambda route: _fulfill_json(route, engine_responses.pop(0)),
    )
    page.route(
        "**/api/agents/medio/move",
        lambda route: pending_agent_routes.append(route),
    )
    page.goto(live_server_url)

    page.get_by_label("Humano vs Agente").check()
    page.get_by_label("Medio").check()
    page.get_by_label("Jugador 1 usa X").check()
    page.get_by_label("Clásica").check()
    page.get_by_role("button", name="Iniciar partida").click()
    with page.expect_request("**/api/agents/medio/move") as agent_request_info:
        page.locator("#cell-0-0").click()

    expect(page.locator("#app")).to_have_attribute(
        "data-ui-state", "esperando_agente"
    )
    expect(page.locator("#agent-wait")).to_be_visible()
    expect(page.locator('.board-cell[aria-disabled="true"]')).to_have_count(9)
    expect(page.locator("#cell-1-1")).to_be_empty()

    assert len(pending_agent_routes) == 1
    agent_request = agent_request_info.value.post_data_json
    assert set(agent_request) == {
        "board",
        "mode",
        "phase",
        "turn",
        "fichas_disponibles",
    }
    _fulfill_json(
        pending_agent_routes.pop(),
        {"type": "colocar", "to": {"row": 1, "col": 1}},
    )

    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")
    expect(page.locator("#agent-wait")).to_be_hidden()
    expect(page.locator("#cell-1-1")).to_have_text("O")
    expect(page.locator("#turn-detail")).to_contain_text("ficha X")
