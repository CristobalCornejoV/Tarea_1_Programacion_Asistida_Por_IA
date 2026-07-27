// Navegación y foco por teclado (CA-I-16 a CA-I-18).
// Delegación sobre `document`: board.js recrea las 9 casillas en cada
// render, así que un listener atado a los elementos viejos se perdería;
// delegar sobre `document` sobrevive a cualquier repintado.

function moverFoco(tableroEl, actual, deltaFila, deltaCol) {
  const fila = Math.max(0, Math.min(2, Number(actual.dataset.row) + deltaFila));
  const col = Math.max(0, Math.min(2, Number(actual.dataset.col) + deltaCol));
  const destino = tableroEl.querySelector(`.casilla[data-row="${fila}"][data-col="${col}"]`);
  if (!destino) return;
  actual.setAttribute("tabindex", "-1");
  destino.setAttribute("tabindex", "0");
  destino.focus();
}

document.addEventListener("keydown", (evento) => {
  const objetivo = evento.target;
  if (!objetivo.classList || !objetivo.classList.contains("casilla")) return;

  // CA-I-18: una casilla deshabilitada no debe reaccionar a ninguna
  // entrada de teclado (tablero en "esperando_agente" o "terminada").
  if (objetivo.disabled) return;

  const tableroEl = objetivo.closest("#tablero");
  if (!tableroEl) return;

  switch (evento.key) {
    case "ArrowUp":
      evento.preventDefault();
      moverFoco(tableroEl, objetivo, -1, 0);
      break;
    case "ArrowDown":
      evento.preventDefault();
      moverFoco(tableroEl, objetivo, 1, 0);
      break;
    case "ArrowLeft":
      evento.preventDefault();
      moverFoco(tableroEl, objetivo, 0, -1);
      break;
    case "ArrowRight":
      evento.preventDefault();
      moverFoco(tableroEl, objetivo, 0, 1);
      break;
    case "Enter":
    case " ":
      evento.preventDefault();
      objetivo.click();
      break;
    default:
      break;
  }
});
