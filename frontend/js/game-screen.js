// Pantalla En Juego / Esperando Agente / Terminada (CA-I-05 a CA-I-12).
import { aplicarJugada, crearPartida, obtenerJugadaAgente } from "./api.js";
import { pintarTablero } from "./board.js";
import { registrarResultado, inicializarMarcador } from "./scoreboard.js";
import { EstadoUI, mostrarPantalla } from "./state.js";

function fichaDelAgente() {
  if (EstadoUI.configuracion?.modo !== "humano_vs_agente") return null;
  return EstadoUI.configuracion.ficha_jugador_1 === "X" ? "O" : "X";
}

function esTurnoDeAgente(estado) {
  const ficha = fichaDelAgente();
  return ficha !== null && estado.turn === ficha;
}

function contenedorDePantalla(pantalla) {
  return document.getElementById(`pantalla-${pantalla}`);
}

function renderizarPantallaActual(deshabilitado) {
  const contenedor = contenedorDePantalla(EstadoUI.pantalla);
  pintarTablero(contenedor, { deshabilitado, onClickCasilla: alClickCasilla });
}

/**
 * Punto de entrada único cuando llega un GameState nuevo (desde crear
 * partida, aplicar una jugada humana, o la jugada de un agente): decide la
 * pantalla correcta y dispara el turno del agente si corresponde.
 */
export function manejarNuevoEstado(gameState) {
  EstadoUI.game_state = gameState;
  EstadoUI.casilla_seleccionada = null;

  if (gameState.status !== "en_curso") {
    registrarResultado(gameState); // CA-I-13, CA-I-14
    mostrarPantalla("terminada"); // CA-I-06, CA-I-07
    renderizarPantallaActual(true);
    return;
  }

  if (esTurnoDeAgente(gameState)) {
    mostrarPantalla("esperando_agente"); // CA-I-09
    renderizarPantallaActual(true);
    jugarTurnoDeAgente();
    return;
  }

  mostrarPantalla("en_juego");
  renderizarPantallaActual(false);
}

async function jugarTurnoDeAgente() {
  const estado = EstadoUI.game_state;
  const solicitud = {
    board: estado.board,
    mode: estado.mode,
    phase: estado.phase,
    turn: estado.turn,
    fichas_disponibles: estado.fichas_disponibles,
  };
  const respuestaAgente = await obtenerJugadaAgente(
    EstadoUI.configuracion.nivel_agente,
    solicitud
  );
  if (!respuestaAgente.ok) {
    mostrarAvisoError({ message: "El agente no pudo responder." });
    return;
  }
  const jugada = { player: estado.turn, ...respuestaAgente.body };
  const resultado = await aplicarJugada(estado.game_id, jugada);
  if (!resultado.ok) {
    mostrarAvisoError(resultado.body);
    return;
  }
  manejarNuevoEstado(resultado.body); // CA-I-10
}

function mostrarAvisoError(errorJugada) {
  const contenedor = contenedorDePantalla(EstadoUI.pantalla);
  const elementoError = contenedor?.querySelector("#tablero-error");
  if (elementoError) {
    elementoError.textContent = errorJugada.message || "Jugada inválida.";
  }
}

async function enviarJugada(jugada) {
  const resultado = await aplicarJugada(EstadoUI.game_state.game_id, jugada);
  if (!resultado.ok) {
    mostrarAvisoError(resultado.body); // CA-I-08: no se altera game_state
    return;
  }
  manejarNuevoEstado(resultado.body);
}

function alClickCasilla(fila, col) {
  const estado = EstadoUI.game_state;
  if (!estado || estado.status !== "en_curso" || esTurnoDeAgente(estado)) return;

  const jugador = estado.turn;

  if (estado.mode === "continua" && estado.phase === "movimiento") {
    manejarClickEnMovimiento(fila, col, jugador);
    return;
  }

  enviarJugada({ player: jugador, type: "colocar", to: { row: fila, col: col } });
}

function manejarClickEnMovimiento(fila, col, jugador) {
  const estado = EstadoUI.game_state;
  const contenidoCelda = estado.board[fila][col];
  const seleccion = EstadoUI.casilla_seleccionada;

  if (contenidoCelda === jugador) {
    // Seleccionar (o cambiar la selección a) una ficha propia (CA-I-11).
    EstadoUI.casilla_seleccionada = { row: fila, col: col };
    renderizarPantallaActual(false);
    return;
  }

  if (seleccion && contenidoCelda === null) {
    // CA-I-12: destino elegido para la ficha ya seleccionada.
    enviarJugada({
      player: jugador,
      type: "mover",
      from: { row: seleccion.row, col: seleccion.col },
      to: { row: fila, col: col },
    });
  }
}

async function reiniciarPartida() {
  const resultado = await crearPartida(EstadoUI.configuracion.modalidad);
  if (resultado.ok) {
    manejarNuevoEstado(resultado.body); // CA-I-15: MarcadorSesion no se toca aquí
  }
}

// Delegación de eventos: el botón "Reiniciar" es renderizado por
// scoreboard.js, pero su comportamiento (crear partida + orquestar el
// siguiente turno) vive aquí, evitando un import circular entre módulos.
document.getElementById("marcador-sesion")?.addEventListener("click", (evento) => {
  if (evento.target && evento.target.id === "btn-reiniciar") {
    reiniciarPartida();
  }
});

inicializarMarcador();
