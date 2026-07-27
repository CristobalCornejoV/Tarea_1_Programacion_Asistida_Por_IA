// Render del tablero a partir de GameState; resaltado de línea ganadora,
// fichas movibles y casillas destino (CA-I-05 a CA-I-07, CA-I-11, CA-I-12).
import { EstadoUI } from "./state.js";

function esCeldaGanadora(estado, fila, col) {
  return (estado.winning_line ?? []).some((c) => c.row === fila && c.col === col);
}

function esCeldaMovible(estado, fila, col) {
  if (estado.mode !== "continua" || estado.phase !== "movimiento") return false;
  return estado.board[fila][col] === estado.turn;
}

function esCeldaDestinoValido(estado, seleccion, fila, col) {
  if (!seleccion) return false;
  return estado.board[fila][col] === null;
}

/**
 * Pinta el tablero, indicador de turno, indicación de espera/resultado, y
 * un contenedor de aviso de error, dentro de `contenedor`.
 *
 * `opciones.deshabilitado`: bloquea toda interacción (CA-I-06, CA-I-07,
 * CA-I-09). `opciones.onClickCasilla(fila, col)`: callback de clic, lo
 * provee game-screen.js (inyección de dependencia, sin import circular).
 */
export function pintarTablero(contenedor, opciones = {}) {
  const { deshabilitado = false, onClickCasilla = null } = opciones;
  const estado = EstadoUI.game_state;
  if (!estado || !contenedor) return;

  const seleccion = EstadoUI.casilla_seleccionada;

  const habiaFocoEnTablero = document.activeElement?.classList?.contains("casilla") ?? false;
  const filaFocoPrevio = habiaFocoEnTablero ? Number(document.activeElement.dataset.row) : 0;
  const colFocoPrevio = habiaFocoEnTablero ? Number(document.activeElement.dataset.col) : 0;

  const filasHtml = [];
  for (let fila = 0; fila < 3; fila++) {
    const celdas = [];
    for (let col = 0; col < 3; col++) {
      const valor = estado.board[fila][col];
      const clases = ["casilla"];
      if (esCeldaGanadora(estado, fila, col)) clases.push("casilla-ganadora");
      if (!deshabilitado && esCeldaMovible(estado, fila, col)) clases.push("casilla-movible");
      if (!deshabilitado && esCeldaDestinoValido(estado, seleccion, fila, col)) {
        clases.push("casilla-destino");
      }
      if (seleccion && seleccion.row === fila && seleccion.col === col) {
        clases.push("casilla-seleccionada");
      }
      const esFoco = fila === filaFocoPrevio && col === colFocoPrevio;
      const etiqueta = `Casilla fila ${fila + 1}, columna ${col + 1}${
        valor ? ", ficha " + valor : ", vacía"
      }`;
      celdas.push(
        `<button type="button" class="${clases.join(" ")}" data-row="${fila}" data-col="${col}" ` +
          `tabindex="${esFoco ? "0" : "-1"}" aria-label="${etiqueta}" ` +
          `${deshabilitado ? "disabled" : ""}>${valor ?? ""}</button>`
      );
    }
    filasHtml.push(`<div class="fila-tablero">${celdas.join("")}</div>`);
  }

  let resultadoHtml = "";
  if (estado.status === "victoria") {
    resultadoHtml = `<p id="resultado-partida" role="status">Ganó ${estado.winner}</p>`;
  } else if (estado.status === "empate") {
    resultadoHtml = `<p id="resultado-partida" role="status">Empate</p>`;
  }

  const esperaHtml =
    deshabilitado && estado.status === "en_curso"
      ? `<p id="indicador-espera-agente" role="status">El agente está pensando…</p>`
      : "";

  contenedor.innerHTML = `
    <p id="indicador-turno">Turno: <strong>${estado.turn}</strong></p>
    ${esperaHtml}
    ${resultadoHtml}
    <div id="tablero" role="grid" aria-label="Tablero de tres en raya">
      ${filasHtml.join("")}
    </div>
    <p id="tablero-error" role="alert"></p>
  `;

  if (onClickCasilla) {
    contenedor.querySelectorAll(".casilla").forEach((boton) => {
      boton.addEventListener("click", () => {
        onClickCasilla(Number(boton.dataset.row), Number(boton.dataset.col));
      });
    });
  }

  if (habiaFocoEnTablero && !deshabilitado) {
    contenedor
      .querySelector(`.casilla[data-row="${filaFocoPrevio}"][data-col="${colFocoPrevio}"]`)
      ?.focus();
  }
}
