/**
 * Único punto de contacto de la interfaz con el backend.
 *
 * Este módulo no interpreta reglas: envía solicitudes y devuelve las
 * representaciones completas entregadas por los contratos HTTP.
 */

export class ErrorAPI extends Error {
  constructor(status, data) {
    super(data?.message ?? data?.detail ?? "No fue posible completar la solicitud.");
    this.name = "ErrorAPI";
    this.status = status;
    this.data = data;
    this.codigo = data?.error ?? null;
  }
}

async function solicitar(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : null;

  if (!response.ok) {
    throw new ErrorAPI(response.status, data);
  }

  return data;
}

export function crearPartida(mode) {
  return solicitar("/api/games", {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
}

export function obtenerPartida(gameId) {
  return solicitar(`/api/games/${encodeURIComponent(gameId)}`);
}

export function aplicarJugada(gameId, jugada) {
  return solicitar(`/api/games/${encodeURIComponent(gameId)}/moves`, {
    method: "POST",
    body: JSON.stringify(jugada),
  });
}

export function obtenerJugadaAgente(nivel, solicitud) {
  return solicitar(`/api/agents/${encodeURIComponent(nivel)}/move`, {
    method: "POST",
    body: JSON.stringify(solicitud),
  });
}
