import {
  actualizarEstadoUI,
  estadoUI,
} from "./state.js";

const TECLAS_DIRECCION = Object.freeze({
  ArrowUp: { row: -1, col: 0 },
  ArrowDown: { row: 1, col: 0 },
  ArrowLeft: { row: 0, col: -1 },
  ArrowRight: { row: 0, col: 1 },
});

let casillas = [];

function limitar(valor) {
  return Math.max(0, Math.min(2, valor));
}

function idCasilla(row, col) {
  return `cell-${row}-${col}`;
}

function establecerCasillaTabulable(casillaActiva) {
  for (const casilla of casillas) {
    casilla.tabIndex = casilla === casillaActiva ? 0 : -1;
  }
  actualizarEstadoUI(
    { foco_actual: casillaActiva.id },
    { notificar: false },
  );
}

function moverFoco(casilla, desplazamiento) {
  const row = Number(casilla.dataset.row);
  const col = Number(casilla.dataset.col);
  const destino = document.querySelector(
    `#${idCasilla(
      limitar(row + desplazamiento.row),
      limitar(col + desplazamiento.col),
    )}`,
  );
  establecerCasillaTabulable(destino);
  destino.focus();
}

function manejarTecla(event) {
  const casilla = event.target.closest(".board-cell");
  if (!casilla) {
    return;
  }

  const desplazamiento = TECLAS_DIRECCION[event.key];
  if (desplazamiento) {
    event.preventDefault();
    moverFoco(casilla, desplazamiento);
    return;
  }

  if (
    (event.key === "Enter" || event.key === " ") &&
    casilla.getAttribute("aria-disabled") === "true"
  ) {
    event.preventDefault();
    event.stopPropagation();
  }
}

function manejarFoco(event) {
  const casilla = event.target.closest(".board-cell");
  if (casilla) {
    establecerCasillaTabulable(casilla);
  }
}

export function inicializarTeclado() {
  const tablero = document.querySelector("#board");
  casillas = [...tablero.querySelectorAll(".board-cell")];
  tablero.addEventListener("keydown", manejarTecla);
  tablero.addEventListener("focusin", manejarFoco);

  const focoGuardado = document.querySelector(`#${estadoUI.foco_actual}`);
  establecerCasillaTabulable(focoGuardado ?? casillas[0]);
}
