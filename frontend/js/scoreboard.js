import {
  actualizarEstadoUI,
  marcadorSesion,
} from "./state.js";

const resultadosRegistrados = new Set();
let botonReiniciar;
let alReiniciarPartida;

export function renderizarMarcador() {
  document.querySelector("#score-x").textContent =
    String(marcadorSesion.victorias_x);
  document.querySelector("#score-o").textContent =
    String(marcadorSesion.victorias_o);
  document.querySelector("#score-draws").textContent =
    String(marcadorSesion.empates);
}

export function registrarResultado(gameState) {
  if (!gameState || gameState.status === "en_curso") {
    return false;
  }

  const claveResultado = `${gameState.game_id}:${gameState.status}:${gameState.winner ?? ""}`;
  if (resultadosRegistrados.has(claveResultado)) {
    return false;
  }
  resultadosRegistrados.add(claveResultado);

  if (gameState.status === "empate") {
    marcadorSesion.empates += 1;
  } else if (gameState.winner === "X") {
    marcadorSesion.victorias_x += 1;
  } else if (gameState.winner === "O") {
    marcadorSesion.victorias_o += 1;
  }

  renderizarMarcador();
  return true;
}

async function manejarReinicio() {
  botonReiniciar.disabled = true;
  botonReiniciar.setAttribute("aria-busy", "true");
  const textoOriginal = botonReiniciar.textContent;
  botonReiniciar.textContent = "Reiniciando…";

  try {
    await alReiniciarPartida();
  } catch (error) {
    actualizarEstadoUI({
      aviso: {
        tipo: "error",
        mensaje: error?.message ?? "No fue posible reiniciar la partida.",
      },
    });
  } finally {
    botonReiniciar.disabled = false;
    botonReiniciar.removeAttribute("aria-busy");
    botonReiniciar.textContent = textoOriginal;
  }
}

export function inicializarMarcador({ alReiniciar }) {
  botonReiniciar = document.querySelector("#restart-game");
  alReiniciarPartida = alReiniciar;
  botonReiniciar.addEventListener("click", manejarReinicio);
  renderizarMarcador();
}
