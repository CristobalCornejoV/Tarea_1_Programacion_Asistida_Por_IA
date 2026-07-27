// Estado de UI (EstadoUI) y MarcadorSesion, según data-model.md.
// Objetos mutables en memoria del navegador; ningún dato aquí proviene de
// reglas de juego propias — game_state siempre es una copia de solo
// lectura del último GameState devuelto por el backend.

export const EstadoUI = {
  pantalla: "configuracion", // "configuracion" | "en_juego" | "esperando_agente" | "terminada"
  configuracion: null, // ConfiguracionPartida | null
  game_state: null, // GameState | null (última respuesta del motor)
  foco_actual: null, // string (id del elemento con foco de teclado, CA-I-17)
  casilla_seleccionada: null, // {row, col} | null (modalidad continua, CA-I-12)
};

export const MarcadorSesion = {
  victorias_x: 0,
  victorias_o: 0,
  empates: 0,
};

/** ConfiguracionPartida vacía, punto de partida de la pantalla de Configuración. */
export function crearConfiguracionVacia() {
  return {
    modo: null, // "humano_vs_humano" | "humano_vs_agente"
    nivel_agente: null, // "sencillo" | "medio" | "complejo" | null
    ficha_jugador_1: null, // "X" | "O"
    modalidad: null, // "clasica" | "continua"
  };
}

/**
 * CA-I-04: una ConfiguracionPartida solo habilita el inicio cuando modo,
 * ficha_jugador_1 y modalidad tienen valor, y nivel_agente tiene valor si
 * modo = "humano_vs_agente".
 */
export function configuracionEstaCompleta(configuracion) {
  if (configuracion == null) return false;
  const { modo, nivel_agente, ficha_jugador_1, modalidad } = configuracion;
  if (!modo || !ficha_jugador_1 || !modalidad) return false;
  if (modo === "humano_vs_agente" && !nivel_agente) return false;
  return true;
}

const PANTALLAS = ["configuracion", "en_juego", "esperando_agente", "terminada"];

/**
 * Transiciona EstadoUI.pantalla y muestra/oculta los 4 contenedores de
 * index.html (uno por valor de `pantalla`) de forma centralizada, para que
 * config-screen.js y game-screen.js no dupliquen esta lógica.
 */
export function mostrarPantalla(pantalla) {
  EstadoUI.pantalla = pantalla;
  for (const nombre of PANTALLAS) {
    const elemento = document.getElementById(`pantalla-${nombre}`);
    if (elemento) elemento.hidden = nombre !== pantalla;
  }
}
