"""Tests e2e de la interfaz gráfica (Pytest + Playwright, ver research.md
Decisión 4). Cada función cubre uno o más CA-I-* de spec.md.
"""


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
