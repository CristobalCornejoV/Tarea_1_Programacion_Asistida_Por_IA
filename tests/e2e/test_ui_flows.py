"""Tests e2e de la interfaz gráfica (Pytest + Playwright, ver research.md
Decisión 4). Cada función cubre uno o más CA-I-* de spec.md.
"""

from playwright.sync_api import expect


def _esperar_pantalla(page, pantalla: str) -> None:
    """Espera a que EstadoUI.pantalla transicione (llamadas fetch async)."""
    page.wait_for_function(
        "(p) => document.getElementById('pantalla-' + p).hidden === false",
        arg=pantalla,
    )


def _iniciar_partida(
    page,
    base_url,
    modo="humano_vs_humano",
    ficha_jugador_1="X",
    modalidad="clasica",
    nivel_agente=None,
):
    """Navega, completa Configuración, confirma, y espera a salir de ella."""
    page.goto(base_url + "/")
    page.check(f'input[name="modo"][value="{modo}"]')
    if modo == "humano_vs_agente":
        page.select_option("#nivel_agente", nivel_agente)
    page.check(f'input[name="ficha_jugador_1"][value="{ficha_jugador_1}"]')
    page.check(f'input[name="modalidad"][value="{modalidad}"]')
    page.click("#btn-iniciar")
    page.wait_for_function(
        "() => document.getElementById('pantalla-configuracion').hidden === true"
    )


def _celda(page, fila: int, col: int):
    """Localiza la casilla (fila, col) en la pantalla actualmente visible.

    Cada pantalla (en_juego/esperando_agente/terminada) tiene su propia
    copia del tablero, repintada solo mientras está activa; usar `:visible`
    en vez de fijar un `#pantalla-*` evita apuntar a una copia obsoleta
    justo cuando una jugada transiciona de pantalla (p. ej. la jugada que
    termina la partida).
    """
    return page.locator(f".casilla[data-row='{fila}'][data-col='{col}']:visible")


def _jugar_casilla(page, fila: int, col: int, valor_esperado: str):
    """Clica una casilla y espera (auto-retry) a que refleje la ficha
    colocada, evitando la condición de carrera del fetch asíncrono."""
    _celda(page, fila, col).click()
    expect(_celda(page, fila, col)).to_have_text(valor_esperado)


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


def test_jugar_partida(page, base_url):
    """T012: cubre CA-I-05 a CA-I-08 (modo Humano vs Humano, clásica)."""
    _iniciar_partida(page, base_url, modo="humano_vs_humano", ficha_jugador_1="X")

    # CA-I-05: turno y ficha visibles.
    expect(page.locator("#pantalla-en_juego #indicador-turno")).to_contain_text("X")

    # X gana la fila superior: X,O,X,O,X.
    secuencia = [(0, 0, "X"), (1, 0, "O"), (0, 1, "X"), (1, 1, "O"), (0, 2, "X")]
    for fila, col, ficha in secuencia:
        _jugar_casilla(page, fila, col, ficha)

    # CA-I-06: línea ganadora resaltada y tablero bloqueado; transiciona a
    # Terminada (renderizada dentro de #pantalla-terminada).
    _esperar_pantalla(page, "terminada")
    expect(page.locator("#pantalla-terminada #resultado-partida")).to_contain_text("X")
    for fila, col in [(0, 0), (0, 1), (0, 2)]:
        expect(_celda(page, fila, col)).to_have_class("casilla casilla-ganadora")
        expect(_celda(page, fila, col)).to_be_disabled()


def test_jugar_partida_hasta_empate(page, base_url):
    """T012: CA-I-07 (empate resalta resultado y bloquea el tablero)."""
    _iniciar_partida(page, base_url, modo="humano_vs_humano", ficha_jugador_1="X")

    # Tablero final sin alineación: X O X / X X O / O X O.
    secuencia = [
        (0, 0, "X"), (0, 1, "O"), (0, 2, "X"),
        (1, 2, "O"), (1, 0, "X"), (2, 0, "O"),
        (1, 1, "X"), (2, 2, "O"), (2, 1, "X"),
    ]
    for fila, col, ficha in secuencia:
        _jugar_casilla(page, fila, col, ficha)

    _esperar_pantalla(page, "terminada")
    expect(page.locator("#pantalla-terminada #resultado-partida")).to_contain_text("Empate")
    expect(_celda(page, 0, 0)).to_be_disabled()


def test_jugar_partida_rechaza_jugada_ilegal(page, base_url):
    """T012: CA-I-08 (casilla ocupada no altera el tablero)."""
    _iniciar_partida(page, base_url, modo="humano_vs_humano", ficha_jugador_1="X")

    _jugar_casilla(page, 0, 0, "X")
    # O intenta jugar sobre la misma casilla ya ocupada por X.
    _celda(page, 0, 0).click()

    expect(page.locator("#pantalla-en_juego #tablero-error")).not_to_have_text("")
    # El estado no cambió: sigue mostrando X y el turno sigue siendo O.
    expect(_celda(page, 0, 0)).to_have_text("X")
    expect(page.locator("#pantalla-en_juego #indicador-turno")).to_contain_text("O")


def test_espera_agente(page, base_url):
    """T017: cubre CA-I-09, CA-I-10.

    Se retrasa artificialmente la respuesta del agente porque en
    condiciones normales responde en unos pocos milisegundos: sin el
    retraso, el estado "esperando_agente" podría resolverse antes de que
    Playwright llegue a comprobarlo.

    El retraso se implementa envolviendo `window.fetch` en el propio
    navegador (`add_init_script`), no interceptando la petición de red
    desde Python (`page.route`): un `time.sleep()` dentro de un handler de
    `page.route()` bloquea el hilo de despacho síncrono de Playwright y
    termina dejando pasar la petición sin ningún retraso real (bug
    detectado al escribir este test — ver commit).
    """
    page.add_init_script(
        """
        const _fetchOriginal = window.fetch;
        window.fetch = function(...args) {
          const url = args[0];
          if (typeof url === "string" && url.includes("/api/agents/")) {
            return new Promise((resolve) => setTimeout(resolve, 300))
              .then(() => _fetchOriginal.apply(window, args));
          }
          return _fetchOriginal.apply(window, args);
        };
        """
    )

    _iniciar_partida(
        page, base_url, modo="humano_vs_agente", ficha_jugador_1="X", nivel_agente="sencillo"
    )
    _jugar_casilla(page, 0, 0, "X")  # turno de X; le sigue el agente (O)

    # CA-I-09: indicación de espera visible y tablero deshabilitado.
    _esperar_pantalla(page, "esperando_agente")
    expect(page.locator("#pantalla-esperando_agente #indicador-espera-agente")).to_be_visible()
    expect(_celda(page, 1, 1)).to_be_disabled()

    # CA-I-10: al recibir la jugada del agente, se oculta la espera y se
    # retorna a En Juego o Terminada con la jugada ya aplicada.
    page.wait_for_function(
        "() => document.getElementById('pantalla-esperando_agente').hidden === true"
    )
    en_terminada = page.locator("#pantalla-terminada").get_attribute("hidden") is None
    en_juego = page.locator("#pantalla-en_juego").get_attribute("hidden") is None
    assert en_terminada or en_juego
