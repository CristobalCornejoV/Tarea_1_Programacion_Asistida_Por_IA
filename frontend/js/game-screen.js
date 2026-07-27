import { crearPartida } from "./api.js";
import {
  inicializarPantallaConfiguracion,
  prepararPantallaConfiguracion,
} from "./config-screen.js";
import {
  PANTALLAS,
  actualizarEstadoUI,
  estadoUI,
  suscribirEstado,
  volverAConfiguracion,
} from "./state.js";

const TEXTOS = Object.freeze({
  modos: {
    humano_vs_humano: "Humano vs Humano",
    humano_vs_agente: "Humano vs Agente",
  },
  modalidades: {
    clasica: "Clásica",
    continua: "Continua",
  },
  niveles: {
    sencillo: "Sencillo",
    medio: "Medio",
    complejo: "Complejo",
  },
  fases: {
    colocacion: "Colocación",
    movimiento: "Movimiento",
  },
});

function renderizarDatosPartida() {
  const configuracion = estadoUI.configuracion;
  const gameState = estadoUI.game_state;
  if (!configuracion || !gameState) {
    return;
  }

  document.querySelector("#fact-mode").textContent =
    TEXTOS.modos[configuracion.modo];
  document.querySelector("#fact-variant").textContent =
    TEXTOS.modalidades[configuracion.modalidad];

  const filaNivel = document.querySelector("#fact-level-row");
  filaNivel.hidden = configuracion.modo !== "humano_vs_agente";
  document.querySelector("#fact-level").textContent =
    TEXTOS.niveles[configuracion.nivel_agente] ?? "";

  const filaFase = document.querySelector("#fact-phase-row");
  filaFase.hidden = gameState.mode !== "continua";
  document.querySelector("#fact-phase").textContent =
    TEXTOS.fases[gameState.phase] ?? "";
}

function renderizarPantalla() {
  const esConfiguracion = estadoUI.pantalla === PANTALLAS.CONFIGURACION;
  const app = document.querySelector("#app");
  const pantallaConfiguracion = document.querySelector("#config-screen");
  const pantallaJuego = document.querySelector("#game-screen");

  app.dataset.uiState = estadoUI.pantalla;
  pantallaConfiguracion.hidden = !esConfiguracion;
  pantallaJuego.hidden = esConfiguracion;

  renderizarDatosPartida();
}

export async function iniciarPartida(configuracion) {
  const gameState = await crearPartida(configuracion.modalidad);
  actualizarEstadoUI({
    configuracion: { ...configuracion },
    configuracion_borrador: { ...configuracion },
    game_state: gameState,
    pantalla: PANTALLAS.EN_JUEGO,
    casilla_seleccionada: null,
    solicitud_en_curso: false,
    aviso: null,
  });
}

function manejarCambioConfiguracion() {
  volverAConfiguracion();
  prepararPantallaConfiguracion();
}

function inicializar() {
  inicializarPantallaConfiguracion({ alIniciar: iniciarPartida });
  document
    .querySelector("#change-config")
    .addEventListener("click", manejarCambioConfiguracion);
  suscribirEstado(renderizarPantalla);
  renderizarPantalla();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", inicializar, { once: true });
} else {
  inicializar();
}
