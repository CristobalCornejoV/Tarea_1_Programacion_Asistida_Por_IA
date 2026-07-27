// Pantalla de Configuración (CA-I-01 a CA-I-04).
import { crearPartida } from "./api.js";
import { manejarNuevoEstado } from "./game-screen.js";
import {
  EstadoUI,
  configuracionEstaCompleta,
  crearConfiguracionVacia,
} from "./state.js";

const contenedor = document.getElementById("pantalla-configuracion");

function inicializar() {
  EstadoUI.configuracion = crearConfiguracionVacia();
  renderizar();
}

function renderizar() {
  contenedor.innerHTML = `
    <h2>Configuración</h2>
    <fieldset>
      <legend>Modo</legend>
      <label><input type="radio" name="modo" value="humano_vs_humano"> Humano vs Humano</label>
      <label><input type="radio" name="modo" value="humano_vs_agente"> Humano vs Agente</label>
    </fieldset>
    <fieldset id="grupo-nivel-agente" hidden>
      <legend>Nivel del agente</legend>
      <label for="nivel_agente">Nivel</label>
      <select id="nivel_agente" name="nivel_agente">
        <option value="">-- elegir --</option>
        <option value="sencillo">Sencillo</option>
        <option value="medio">Medio</option>
        <option value="complejo">Complejo</option>
      </select>
    </fieldset>
    <fieldset>
      <legend>Ficha del jugador 1</legend>
      <label><input type="radio" name="ficha_jugador_1" value="X"> X</label>
      <label><input type="radio" name="ficha_jugador_1" value="O"> O</label>
    </fieldset>
    <fieldset>
      <legend>Modalidad</legend>
      <label><input type="radio" name="modalidad" value="clasica"> Clásica</label>
      <label><input type="radio" name="modalidad" value="continua"> Continua</label>
    </fieldset>
    <button id="btn-iniciar" type="button">Iniciar partida</button>
    <p id="config-error" role="alert"></p>
  `;
  vincularEventos();
}

function vincularEventos() {
  contenedor.querySelectorAll('input[name="modo"]').forEach((el) => {
    el.addEventListener("change", (evento) => {
      EstadoUI.configuracion.modo = evento.target.value;
      const esHumanoVsAgente = evento.target.value === "humano_vs_agente";
      document.getElementById("grupo-nivel-agente").hidden = !esHumanoVsAgente;
      if (!esHumanoVsAgente) {
        EstadoUI.configuracion.nivel_agente = null;
      }
    });
  });

  document.getElementById("nivel_agente").addEventListener("change", (evento) => {
    EstadoUI.configuracion.nivel_agente = evento.target.value || null;
  });

  contenedor.querySelectorAll('input[name="ficha_jugador_1"]').forEach((el) => {
    el.addEventListener("change", (evento) => {
      EstadoUI.configuracion.ficha_jugador_1 = evento.target.value;
    });
  });

  contenedor.querySelectorAll('input[name="modalidad"]').forEach((el) => {
    el.addEventListener("change", (evento) => {
      EstadoUI.configuracion.modalidad = evento.target.value;
    });
  });

  document.getElementById("btn-iniciar").addEventListener("click", iniciarPartida);
}

function mensajeDeSeleccionFaltante() {
  const { modo, nivel_agente, ficha_jugador_1, modalidad } = EstadoUI.configuracion;
  const faltantes = [];
  if (!modo) faltantes.push("modo");
  if (modo === "humano_vs_agente" && !nivel_agente) faltantes.push("nivel del agente");
  if (!ficha_jugador_1) faltantes.push("ficha");
  if (!modalidad) faltantes.push("modalidad");
  return `Falta seleccionar: ${faltantes.join(", ")}.`;
}

async function iniciarPartida() {
  const errorEl = document.getElementById("config-error");

  // CA-I-04: selección incompleta se rechaza sin salir de Configuración.
  if (!configuracionEstaCompleta(EstadoUI.configuracion)) {
    errorEl.textContent = mensajeDeSeleccionFaltante();
    return;
  }
  errorEl.textContent = "";

  // CA-I-03: confirmar con selección completa crea la partida y transiciona.
  const resultado = await crearPartida(EstadoUI.configuracion.modalidad);
  if (!resultado.ok) {
    errorEl.textContent = "No se pudo crear la partida. Intenta de nuevo.";
    return;
  }
  manejarNuevoEstado(resultado.body); // decide en_juego / esperando_agente
}

inicializar();
