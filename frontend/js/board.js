import { PANTALLAS } from "./state.js";

let casillas = [];

function mismaCoordenada(a, b) {
  return a?.row === b?.row && a?.col === b?.col;
}

function perteneceLineaGanadora(gameState, coordenada) {
  return Boolean(
    gameState.winning_line?.some((posicion) =>
      mismaCoordenada(posicion, coordenada),
    ),
  );
}

function esFichaHumana(configuracion, ficha) {
  if (configuracion.modo === "humano_vs_humano") {
    return true;
  }
  return ficha === configuracion.ficha_jugador_1;
}

function etiquetaCasilla(row, col, ficha, clases) {
  const contenido = ficha ? `ficha ${ficha}` : "vacía";
  const estados = [];
  if (clases.ganadora) {
    estados.push("parte de la línea ganadora");
  }
  if (clases.movible) {
    estados.push("ficha movible");
  }
  if (clases.destino) {
    estados.push("destino disponible");
  }
  if (clases.seleccionada) {
    estados.push("seleccionada");
  }
  const sufijo = estados.length ? `, ${estados.join(", ")}` : "";
  return `Fila ${row + 1}, columna ${col + 1}, ${contenido}${sufijo}`;
}

export function inicializarTablero(alSeleccionar) {
  casillas = [...document.querySelectorAll(".board-cell")];
  for (const casilla of casillas) {
    casilla.addEventListener("click", () => {
      alSeleccionar({
        row: Number(casilla.dataset.row),
        col: Number(casilla.dataset.col),
      });
    });
  }
}

export function renderizarTablero({
  gameState,
  pantalla,
  configuracion,
  casillaSeleccionada,
  solicitudEnCurso,
}) {
  if (!gameState || !configuracion) {
    return;
  }

  const bloqueado =
    pantalla !== PANTALLAS.EN_JUEGO ||
    gameState.status !== "en_curso" ||
    solicitudEnCurso;
  const faseMovimiento =
    gameState.mode === "continua" &&
    gameState.phase === "movimiento" &&
    pantalla === PANTALLAS.EN_JUEGO &&
    esFichaHumana(configuracion, gameState.turn);

  for (const casilla of casillas) {
    const row = Number(casilla.dataset.row);
    const col = Number(casilla.dataset.col);
    const ficha = gameState.board[row][col];
    const coordenada = { row, col };
    const seleccionada =
      faseMovimiento && mismaCoordenada(casillaSeleccionada, coordenada);
    const movible = faseMovimiento && ficha === gameState.turn;
    const destino =
      faseMovimiento && Boolean(casillaSeleccionada) && ficha === null;
    const ganadora = perteneceLineaGanadora(gameState, coordenada);

    casilla.textContent = ficha ?? "";
    casilla.classList.toggle("token-x", ficha === "X");
    casilla.classList.toggle("token-o", ficha === "O");
    casilla.classList.toggle("is-winning", ganadora);
    casilla.classList.toggle("is-movable", movible);
    casilla.classList.toggle("is-selected", seleccionada);
    casilla.classList.toggle("is-destination", destino);
    casilla.setAttribute("aria-disabled", String(bloqueado));
    casilla.setAttribute(
      "aria-label",
      etiquetaCasilla(row, col, ficha, {
        ganadora,
        movible,
        destino,
        seleccionada,
      }),
    );
  }
}
