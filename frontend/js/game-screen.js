import {
  ErrorAPI,
  aplicarJugada,
  crearPartida,
} from "./api.js";
import {
  inicializarTablero,
  renderizarTablero,
} from "./board.js";
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

function nombreControlador(ficha) {
  const configuracion = estadoUI.configuracion;
  if (ficha === configuracion.ficha_jugador_1) {
    return "Jugador 1";
  }
  return configuracion.modo === "humano_vs_agente" ? "Agente" : "Jugador 2";
}

function renderizarTurno() {
  const gameState = estadoUI.game_state;
  if (!gameState) {
    return;
  }

  const ficha = gameState.turn;
  const token = document.querySelector("#turn-token");
  token.textContent = ficha;
  token.classList.toggle("token-x", ficha === "X");
  token.classList.toggle("token-o", ficha === "O");
  document.querySelector("#turn-player").textContent =
    `Turno de ${nombreControlador(ficha)}`;
  document.querySelector("#turn-detail").textContent =
    `Juega con la ficha ${ficha}`;

  const mostrarTurno = estadoUI.pantalla === PANTALLAS.EN_JUEGO;
  document.querySelector("#turn-card").hidden = !mostrarTurno;
}

function renderizarAviso() {
  const contenedor = document.querySelector("#game-notice");
  contenedor.hidden = !estadoUI.aviso;
  contenedor.textContent = estadoUI.aviso?.mensaje ?? "";
  contenedor.classList.toggle(
    "notice-error",
    estadoUI.aviso?.tipo === "error",
  );
}

function renderizarResultado() {
  const gameState = estadoUI.game_state;
  const panel = document.querySelector("#result-panel");
  const terminada = estadoUI.pantalla === PANTALLAS.TERMINADA;
  panel.hidden = !terminada;
  if (!terminada || !gameState) {
    return;
  }

  const titulo = document.querySelector("#result-title");
  const mensaje = document.querySelector("#result-message");
  const simbolo = document.querySelector("#result-symbol");

  if (gameState.status === "victoria") {
    simbolo.textContent = gameState.winner;
    simbolo.hidden = false;
    titulo.textContent = `Victoria de ${gameState.winner}`;
    mensaje.textContent = "La línea ganadora está resaltada en el tablero.";
  } else {
    simbolo.textContent = "—";
    simbolo.hidden = false;
    titulo.textContent = "Empate";
    mensaje.textContent = "La partida terminó sin una línea ganadora.";
  }
}

function renderizarPantalla() {
  const esConfiguracion = estadoUI.pantalla === PANTALLAS.CONFIGURACION;
  const app = document.querySelector("#app");
  const pantallaConfiguracion = document.querySelector("#config-screen");
  const pantallaJuego = document.querySelector("#game-screen");

  app.dataset.uiState = estadoUI.pantalla;
  pantallaConfiguracion.hidden = !esConfiguracion;
  pantallaJuego.hidden = esConfiguracion;

  const etiquetasEstado = {
    [PANTALLAS.EN_JUEGO]: "En juego",
    [PANTALLAS.ESPERANDO_AGENTE]: "Esperando agente",
    [PANTALLAS.TERMINADA]: "Terminada",
  };
  document.querySelector("#game-state-label").textContent =
    etiquetasEstado[estadoUI.pantalla] ?? "";
  document.querySelector("#agent-wait").hidden =
    estadoUI.pantalla !== PANTALLAS.ESPERANDO_AGENTE;

  renderizarDatosPartida();
  renderizarTurno();
  renderizarAviso();
  renderizarResultado();
  renderizarTablero({
    gameState: estadoUI.game_state,
    pantalla: estadoUI.pantalla,
    configuracion: estadoUI.configuracion,
    casillaSeleccionada: estadoUI.casilla_seleccionada,
    solicitudEnCurso: estadoUI.solicitud_en_curso,
  });
}

function pantallaParaGameState(gameState) {
  return gameState.status === "en_curso"
    ? PANTALLAS.EN_JUEGO
    : PANTALLAS.TERMINADA;
}

function jugadaColocacion(coordenada) {
  return {
    player: estadoUI.game_state.turn,
    type: "colocar",
    to: coordenada,
  };
}

async function manejarSeleccionCasilla(coordenada) {
  if (
    estadoUI.pantalla !== PANTALLAS.EN_JUEGO ||
    estadoUI.solicitud_en_curso ||
    estadoUI.game_state?.status !== "en_curso"
  ) {
    return;
  }

  if (
    estadoUI.game_state.mode === "continua" &&
    estadoUI.game_state.phase === "movimiento"
  ) {
    return;
  }

  actualizarEstadoUI({
    solicitud_en_curso: true,
    aviso: null,
  });

  try {
    const gameState = await aplicarJugada(
      estadoUI.game_state.game_id,
      jugadaColocacion(coordenada),
    );
    actualizarEstadoUI({
      game_state: gameState,
      pantalla: pantallaParaGameState(gameState),
      solicitud_en_curso: false,
      casilla_seleccionada: null,
      aviso: null,
    });
  } catch (error) {
    const mensaje =
      error instanceof ErrorAPI
        ? error.message
        : "No fue posible enviar la jugada. Inténtalo nuevamente.";
    actualizarEstadoUI({
      solicitud_en_curso: false,
      aviso: { tipo: "error", mensaje },
    });
  }
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
  inicializarTablero(manejarSeleccionCasilla);
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
