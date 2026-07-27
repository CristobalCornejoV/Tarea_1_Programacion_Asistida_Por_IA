"""Integración E2E de la interfaz con el motor y los agentes reales.

``test_ui_flows.py`` mantiene respuestas HTTP controladas para verificar con
precisión los contratos visuales. Este módulo añade la segunda capa: recorre
los mismos flujos contra FastAPI sin interceptar sus respuestas.
"""

from __future__ import annotations

import re

import pytest

playwright = pytest.importorskip(
    "playwright.sync_api",
    reason="pytest-playwright es una dependencia opcional de pruebas E2E",
)
Page = playwright.Page
Request = playwright.Request
expect = playwright.expect


def _iniciar_partida_real(
    page: Page,
    live_server_url: str,
    *,
    modo: str = "Humano vs Humano",
    ficha: str = "X",
    modalidad: str = "Clásica",
    nivel: str | None = None,
) -> None:
    page.goto(live_server_url)
    page.get_by_label(modo).check()
    if nivel is not None:
        page.get_by_label(nivel).check()
    page.get_by_label(f"Jugador 1 usa {ficha}").check()
    page.get_by_label(modalidad).check()
    page.get_by_role("button", name="Iniciar partida").click()
    expect(page.locator("#config-screen")).to_be_hidden()
    expect(page.locator("#game-screen")).to_be_visible()


def _jugar_casilla(page: Page, row: int, col: int, ficha: str) -> None:
    casilla = page.locator(f"#cell-{row}-{col}")
    casilla.click()
    expect(casilla).to_have_text(ficha)


def _capturar_errores_navegador(
    page: Page,
    *,
    ignorar_errores_de_red: bool = False,
) -> list[str]:
    errores: list[str] = []

    def capturar_consola(mensaje) -> None:
        if mensaje.type != "error":
            return
        if ignorar_errores_de_red and mensaje.text.startswith(
            "Failed to load resource"
        ):
            return
        errores.append(mensaje.text)

    page.on(
        "console",
        capturar_consola,
    )
    page.on("pageerror", lambda error: errores.append(str(error)))
    return errores


def test_backend_real_carga_sin_errores_navegador(
    page: Page,
    live_server_url: str,
) -> None:
    errores = _capturar_errores_navegador(page)

    page.goto(live_server_url)

    expect(page.locator("#config-screen")).to_be_visible()
    assert errores == []


def test_backend_real_partida_clasica_error_victoria_y_reinicio(
    page: Page,
    live_server_url: str,
) -> None:
    """CA-I-05 a CA-I-08 y CA-I-13 a CA-I-15 con el motor real."""

    errores = _capturar_errores_navegador(page, ignorar_errores_de_red=True)
    _iniciar_partida_real(page, live_server_url)

    _jugar_casilla(page, 0, 0, "X")
    tablero_antes_error = page.locator(".board-cell").all_text_contents()
    page.locator("#cell-0-0").click()
    expect(page.locator("#game-notice")).to_contain_text("ocupada")
    expect(page.locator(".board-cell")).to_have_text(tablero_antes_error)

    for row, col, ficha in (
        (1, 0, "O"),
        (0, 1, "X"),
        (1, 1, "O"),
        (0, 2, "X"),
    ):
        _jugar_casilla(page, row, col, ficha)

    expect(page.locator("#app")).to_have_attribute("data-ui-state", "terminada")
    expect(page.locator(".board-cell.is-winning")).to_have_count(3)
    expect(page.locator('.board-cell[aria-disabled="true"]')).to_have_count(9)
    expect(page.locator("#score-x")).to_have_text("1")

    page.get_by_role("button", name="Reiniciar partida").click()
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")
    expect(page.locator(".board-cell")).to_have_text([""] * 9)
    expect(page.locator("#score-x")).to_have_text("1")
    assert errores == []


def test_backend_real_partida_clasica_termina_en_empate(
    page: Page,
    live_server_url: str,
) -> None:
    """CA-I-07 y CA-I-14 consumiendo estados reales del motor."""

    _iniciar_partida_real(page, live_server_url)

    for row, col, ficha in (
        (0, 0, "X"),
        (0, 1, "O"),
        (0, 2, "X"),
        (1, 2, "O"),
        (1, 0, "X"),
        (2, 0, "O"),
        (1, 1, "X"),
        (2, 2, "O"),
        (2, 1, "X"),
    ):
        _jugar_casilla(page, row, col, ficha)

    expect(page.locator("#app")).to_have_attribute("data-ui-state", "terminada")
    expect(page.locator("#result-title")).to_have_text("Empate")
    expect(page.locator("#score-draws")).to_have_text("1")


def test_backend_real_modalidad_continua_llega_a_movimiento(
    page: Page,
    live_server_url: str,
) -> None:
    """CA-I-11 y CA-I-12 con colocación y movimiento reales."""

    _iniciar_partida_real(page, live_server_url, modalidad="Continua")

    for row, col, ficha in (
        (0, 0, "X"),
        (2, 2, "O"),
        (0, 1, "X"),
        (2, 1, "O"),
        (1, 0, "X"),
        (1, 2, "O"),
    ):
        _jugar_casilla(page, row, col, ficha)

    expect(page.locator("#fact-phase")).to_have_text("Movimiento")
    expect(page.locator(".board-cell.is-movable")).to_have_count(3)

    page.locator("#cell-0-0").click()
    expect(page.locator("#cell-0-0")).to_have_class(
        re.compile(r"\bis-selected\b")
    )
    expect(page.locator(".board-cell.is-destination")).to_have_count(3)

    page.locator("#cell-2-0").click()
    expect(page.locator("#cell-2-0")).to_have_text("X")
    expect(page.locator("#cell-0-0")).to_be_empty()


@pytest.mark.parametrize("nivel", ["Sencillo", "Medio", "Complejo"])
def test_backend_real_agente_puede_abrir_la_partida(
    page: Page,
    live_server_url: str,
    nivel: str,
) -> None:
    """CA-I-09 y CA-I-10 para cada nivel de agente real."""

    _iniciar_partida_real(
        page,
        live_server_url,
        modo="Humano vs Agente",
        ficha="O",
        nivel=nivel,
    )

    expect(page.locator(".board-cell:not(:empty)")).to_have_count(1, timeout=5000)
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")
    expect(page.locator("#turn-detail")).to_contain_text("ficha O")


def test_backend_real_flujo_completo_por_teclado_conserva_foco(
    page: Page,
    live_server_url: str,
) -> None:
    """CA-I-16 a CA-I-18 usando el motor real de principio a fin."""

    page.goto(live_server_url)
    page.get_by_label("Humano vs Humano").focus()
    page.keyboard.press("Space")
    page.get_by_label("Jugador 1 usa X").focus()
    page.keyboard.press("Space")
    page.get_by_label("Clásica").focus()
    page.keyboard.press("Space")
    page.get_by_role("button", name="Iniciar partida").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")

    page.locator("#cell-0-0").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#cell-0-0")).to_have_text("X")

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Space")
    expect(page.locator("#cell-1-0")).to_have_text("O")

    page.keyboard.press("ArrowUp")
    page.keyboard.press("ArrowRight")
    page.keyboard.press("Enter")
    expect(page.locator("#cell-0-1")).to_have_text("X")

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Space")
    expect(page.locator("#cell-1-1")).to_have_text("O")

    page.keyboard.press("ArrowUp")
    page.keyboard.press("ArrowRight")
    page.keyboard.press("Enter")
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "terminada")
    expect(page.locator("#cell-0-2")).to_be_focused()

    tablero_terminado = page.locator(".board-cell").all_text_contents()
    page.keyboard.press("Space")
    expect(page.locator(".board-cell")).to_have_text(tablero_terminado)
    expect(page.locator("#cell-0-2")).to_be_focused()

    page.keyboard.press("Tab")
    expect(page.locator("#restart-game")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")
    expect(page.locator("#score-x")).to_have_text("1")


def test_resiliencia_bloquea_dobles_envios(
    page: Page,
    live_server_url: str,
) -> None:
    """Una acción física rápida produce una sola solicitud por intención."""

    solicitudes_post: list[str] = []

    def capturar_solicitud(solicitud: Request) -> None:
        if solicitud.method == "POST":
            solicitudes_post.append(solicitud.url)

    page.on("request", capturar_solicitud)
    page.goto(live_server_url)
    page.get_by_label("Humano vs Humano").check()
    page.get_by_label("Jugador 1 usa X").check()
    page.get_by_label("Clásica").check()

    page.get_by_role("button", name="Iniciar partida").dblclick()
    expect(page.locator("#app")).to_have_attribute("data-ui-state", "en_juego")
    page.wait_for_timeout(150)
    assert sum(url.endswith("/api/games") for url in solicitudes_post) == 1

    page.locator("#cell-0-0").dblclick()
    expect(page.locator("#cell-0-0")).to_have_text("X")
    page.wait_for_timeout(150)
    assert sum("/moves" in url for url in solicitudes_post) == 1
    expect(page.locator("#game-notice")).to_be_hidden()


def test_resiliencia_fallo_de_red_es_visible_y_recuperable(
    page: Page,
    live_server_url: str,
) -> None:
    """Un fallo de transporte no genera errores JS ni deja el botón bloqueado."""

    errores = _capturar_errores_navegador(page, ignorar_errores_de_red=True)
    page.route("**/api/games", lambda route: route.abort())
    page.goto(live_server_url)

    expect(page.locator("#restart-game")).to_be_hidden()
    page.get_by_label("Humano vs Humano").check()
    page.get_by_label("Jugador 1 usa X").check()
    page.get_by_label("Clásica").check()
    page.get_by_role("button", name="Iniciar partida").click()

    resumen = page.locator("#config-error-summary")
    expect(resumen).to_be_visible()
    assert resumen.inner_text().strip()
    expect(page.locator("#start-game")).to_be_enabled()
    expect(page.locator("#start-game")).not_to_have_attribute("aria-busy", "true")
    expect(page.locator("#config-screen")).to_be_visible()
    assert errores == []
