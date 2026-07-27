export const PANTALLAS = Object.freeze({
  CONFIGURACION: "configuracion",
  EN_JUEGO: "en_juego",
  ESPERANDO_AGENTE: "esperando_agente",
  TERMINADA: "terminada",
});

export function crearConfiguracionBorrador() {
  return {
    modo: null,
    nivel_agente: null,
    ficha_jugador_1: null,
    modalidad: null,
  };
}

export const estadoUI = {
  pantalla: PANTALLAS.CONFIGURACION,
  configuracion: null,
  configuracion_borrador: crearConfiguracionBorrador(),
  game_state: null,
  foco_actual: "cell-0-0",
  casilla_seleccionada: null,
  solicitud_en_curso: false,
  aviso: null,
};

export const marcadorSesion = {
  victorias_x: 0,
  victorias_o: 0,
  empates: 0,
};

const observadores = new Set();

export function suscribirEstado(observador) {
  observadores.add(observador);
  return () => observadores.delete(observador);
}

export function notificarEstado() {
  for (const observador of observadores) {
    observador(estadoUI);
  }
}

export function actualizarEstadoUI(cambios, { notificar = true } = {}) {
  Object.assign(estadoUI, cambios);
  if (notificar) {
    notificarEstado();
  }
}

export function actualizarConfiguracionBorrador(cambios) {
  Object.assign(estadoUI.configuracion_borrador, cambios);
  notificarEstado();
}

export function establecerAviso(tipo, mensaje) {
  actualizarEstadoUI({
    aviso: mensaje ? { tipo, mensaje } : null,
  });
}

export function limpiarAviso({ notificar = true } = {}) {
  actualizarEstadoUI({ aviso: null }, { notificar });
}

export function volverAConfiguracion() {
  actualizarEstadoUI({
    pantalla: PANTALLAS.CONFIGURACION,
    game_state: null,
    casilla_seleccionada: null,
    solicitud_en_curso: false,
    aviso: null,
    configuracion_borrador:
      estadoUI.configuracion === null
        ? estadoUI.configuracion_borrador
        : { ...estadoUI.configuracion },
  });
}
