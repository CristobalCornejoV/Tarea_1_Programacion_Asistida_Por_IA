import {
  actualizarConfiguracionBorrador,
  estadoUI,
} from "./state.js";

const ETIQUETAS_CAMPOS = Object.freeze({
  modo: "modo de partida",
  nivel_agente: "nivel del agente",
  ficha_jugador_1: "asignación de fichas",
  modalidad: "modalidad",
});

let formulario;
let grupoNivel;
let resumenError;
let botonIniciar;
let alIniciarPartida;

function leerConfiguracion() {
  const data = new FormData(formulario);
  const modo = data.get("modo");
  return {
    modo: modo || null,
    nivel_agente:
      modo === "humano_vs_agente" ? data.get("nivel_agente") || null : null,
    ficha_jugador_1: data.get("ficha_jugador_1") || null,
    modalidad: data.get("modalidad") || null,
  };
}

function camposFaltantes(configuracion) {
  const faltantes = ["modo", "ficha_jugador_1", "modalidad"].filter(
    (campo) => !configuracion[campo],
  );
  if (
    configuracion.modo === "humano_vs_agente" &&
    !configuracion.nivel_agente
  ) {
    faltantes.push("nivel_agente");
  }
  return faltantes;
}

function limpiarErrores() {
  for (const grupo of formulario.querySelectorAll("[data-config-field]")) {
    grupo.classList.remove("has-error");
  }
  for (const error of formulario.querySelectorAll("[data-error-for]")) {
    error.textContent = "";
  }
  resumenError.hidden = true;
  resumenError.textContent = "";
}

function mostrarErrores(faltantes) {
  limpiarErrores();
  for (const campo of faltantes) {
    const grupo = formulario.querySelector(`[data-config-field="${campo}"]`);
    const error = formulario.querySelector(`[data-error-for="${campo}"]`);
    grupo?.classList.add("has-error");
    if (error) {
      error.textContent = `Selecciona ${ETIQUETAS_CAMPOS[campo]}.`;
    }
  }

  const nombres = faltantes.map((campo) => ETIQUETAS_CAMPOS[campo]);
  resumenError.textContent = `Falta completar: ${nombres.join(", ")}.`;
  resumenError.hidden = false;
  resumenError.focus({ preventScroll: true });
}

function actualizarVisibilidadNivel(modo) {
  const requiereNivel = modo === "humano_vs_agente";
  grupoNivel.hidden = !requiereNivel;
  grupoNivel.disabled = !requiereNivel;

  if (!requiereNivel) {
    for (const control of grupoNivel.querySelectorAll("input")) {
      control.checked = false;
    }
  }
}

function restaurarSeleccion(configuracion) {
  for (const [campo, valor] of Object.entries(configuracion)) {
    if (!valor) {
      continue;
    }
    const control = formulario.querySelector(
      `input[name="${campo}"][value="${valor}"]`,
    );
    if (control) {
      control.checked = true;
    }
  }
  actualizarVisibilidadNivel(configuracion.modo);
}

async function manejarEnvio(event) {
  event.preventDefault();
  const configuracion = leerConfiguracion();
  const faltantes = camposFaltantes(configuracion);

  if (faltantes.length > 0) {
    mostrarErrores(faltantes);
    return;
  }

  limpiarErrores();
  botonIniciar.disabled = true;
  botonIniciar.setAttribute("aria-busy", "true");
  const textoOriginal = botonIniciar.innerHTML;
  botonIniciar.textContent = "Creando partida…";

  try {
    await alIniciarPartida(configuracion);
  } catch (error) {
    resumenError.textContent =
      error?.message ?? "No fue posible iniciar la partida.";
    resumenError.hidden = false;
    resumenError.focus({ preventScroll: true });
  } finally {
    botonIniciar.disabled = false;
    botonIniciar.removeAttribute("aria-busy");
    botonIniciar.innerHTML = textoOriginal;
  }
}

function manejarCambio() {
  const configuracion = leerConfiguracion();
  actualizarVisibilidadNivel(configuracion.modo);
  actualizarConfiguracionBorrador(configuracion);

  const faltantes = camposFaltantes(configuracion);
  for (const grupo of formulario.querySelectorAll("[data-config-field]")) {
    const campo = grupo.dataset.configField;
    if (!faltantes.includes(campo)) {
      grupo.classList.remove("has-error");
      const error = formulario.querySelector(`[data-error-for="${campo}"]`);
      if (error) {
        error.textContent = "";
      }
    }
  }
  if (faltantes.length === 0) {
    resumenError.hidden = true;
  }
}

export function inicializarPantallaConfiguracion({ alIniciar }) {
  formulario = document.querySelector("#config-form");
  grupoNivel = document.querySelector("#agent-level-group");
  resumenError = document.querySelector("#config-error-summary");
  botonIniciar = document.querySelector("#start-game");
  alIniciarPartida = alIniciar;

  formulario.addEventListener("change", manejarCambio);
  formulario.addEventListener("submit", manejarEnvio);
  restaurarSeleccion(estadoUI.configuracion_borrador);
}

export function prepararPantallaConfiguracion() {
  limpiarErrores();
  restaurarSeleccion(estadoUI.configuracion_borrador);
  document.querySelector("#config-title")?.focus?.({ preventScroll: true });
}
