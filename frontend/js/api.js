// Cliente fetch hacia /api/games y /api/agents (specs 001/002).
// Único módulo que conoce URLs y forma de las peticiones HTTP; el resto de
// la interfaz solo lee los objetos devueltos (GameState, Jugada, error).

async function _enviar(url, opciones) {
  const respuesta = await fetch(url, opciones);
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, status: respuesta.status, body: cuerpo };
}

function _post(url, datos) {
  return _enviar(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

/** Crea una partida nueva. `modalidad`: "clasica" | "continua". */
export function crearPartida(modalidad) {
  return _post("/api/games", { mode: modalidad });
}

/** Consulta el GameState actual de una partida existente. */
export function obtenerPartida(gameId) {
  return _enviar(`/api/games/${gameId}`, { method: "GET" });
}

/**
 * Aplica una jugada. `jugada` es {player, type, to, from?}. En 200 el body
 * es el nuevo GameState; en 422 el body es {error, message} y el estado de
 * la partida no cambió (ver contracts/games-api.md).
 */
export function aplicarJugada(gameId, jugada) {
  return _post(`/api/games/${gameId}/moves`, jugada);
}

/**
 * Pide la jugada de un agente. `nivel`: "sencillo" | "medio" | "complejo".
 * `solicitud` es el subconjunto de GameState que exige agents-api.md
 * (board, mode, phase, turn, fichas_disponibles). El body de respuesta es
 * {type, to, from?} (sin `player`, ver data-model.md de la spec 002).
 */
export function obtenerJugadaAgente(nivel, solicitud) {
  return _post(`/api/agents/${nivel}/move`, solicitud);
}
