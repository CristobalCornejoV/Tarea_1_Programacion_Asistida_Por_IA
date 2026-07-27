"""Tests e2e de la interfaz gráfica (Pytest + Playwright, ver research.md
Decisión 4). Cada función cubre uno o más CA-I-* de spec.md.
"""


def _esperar_pantalla(page, pantalla: str) -> None:
    """Espera a que EstadoUI.pantalla transicione (llamadas fetch async)."""
    page.wait_for_function(
        "(p) => document.getElementById('pantalla-' + p).hidden === false",
        arg=pantalla,
    )


def test_arnes_e2e_sirve_la_pagina(page, base_url):
    """T003: el servidor real arranca y sirve frontend/index.html."""
    page.goto(base_url + "/")
    assert page.title() == "Tres en Raya"


def test_esqueleto_carga_sin_errores_y_solo_configuracion_visible(page, base_url):
    """T006: las 4 secciones de pantalla existen; solo Configuración parte
    visible (EstadoUI.pantalla inicial), sin errores de consola/JS."""
    errores = []
    page.on("console", lambda msg: errores.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errores.append(str(exc)))

    page.goto(base_url + "/")

    assert page.locator("#pantalla-configuracion").count() == 1
    assert page.locator("#pantalla-configuracion").get_attribute("hidden") is None
    for pantalla in ("en_juego", "esperando_agente", "terminada"):
        assert page.locator(f"#pantalla-{pantalla}").get_attribute("hidden") is not None

    assert errores == []


def test_configuracion_inicial(page, base_url):
    """T007: cubre CA-I-01 a CA-I-04."""
    page.goto(base_url + "/")

    # CA-I-01: Configuración es la pantalla inicial.
    assert page.locator("#pantalla-configuracion").get_attribute("hidden") is None

    # CA-I-04: confirmar sin ninguna selección se rechaza, sin salir de
    # Configuración, e indica qué falta.
    page.click("#btn-iniciar")
    assert page.locator("#pantalla-configuracion").get_attribute("hidden") is None
    assert page.locator("#pantalla-en_juego").get_attribute("hidden") is not None
    assert page.locator("#config-error").inner_text().strip() != ""

    # CA-I-02: elegir modo Humano vs Agente muestra el selector de nivel.
    assert page.locator("#grupo-nivel-agente").get_attribute("hidden") is not None
    page.check('input[name="modo"][value="humano_vs_agente"]')
    assert page.locator("#grupo-nivel-agente").get_attribute("hidden") is None

    # CA-I-04 (parcial): sin nivel de agente todavía, sigue rechazando.
    page.check('input[name="ficha_jugador_1"][value="X"]')
    page.check('input[name="modalidad"][value="clasica"]')
    page.click("#btn-iniciar")
    assert page.locator("#pantalla-configuracion").get_attribute("hidden") is None
    assert "nivel del agente" in page.locator("#config-error").inner_text()

    # CA-I-02 + CA-I-03: selección completa confirma y transiciona a En Juego.
    page.select_option("#nivel_agente", "medio")
    page.click("#btn-iniciar")
    _esperar_pantalla(page, "en_juego")
    assert page.locator("#pantalla-configuracion").get_attribute("hidden") is not None


def test_configuracion_humano_vs_humano_no_requiere_nivel_agente(page, base_url):
    """CA-I-02, CA-I-03: en modo Humano vs Humano no se exige nivel_agente."""
    page.goto(base_url + "/")

    page.check('input[name="modo"][value="humano_vs_humano"]')
    assert page.locator("#grupo-nivel-agente").get_attribute("hidden") is not None

    page.check('input[name="ficha_jugador_1"][value="O"]')
    page.check('input[name="modalidad"][value="continua"]')
    page.click("#btn-iniciar")

    _esperar_pantalla(page, "en_juego")
    assert page.locator("#pantalla-configuracion").get_attribute("hidden") is not None
