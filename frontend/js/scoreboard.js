// Marcador de sesión y reinicio (CA-I-13 a CA-I-15).
// No importa game-screen.js (evita ciclo de imports): el botón "Reiniciar"
// solo se renderiza aquí; game-screen.js escucha sus clics por delegación
// de eventos sobre el contenedor del marcador.
import { MarcadorSesion } from "./state.js";

let contenedor = null;

export function inicializarMarcador() {
  contenedor = document.getElementById("marcador-sesion");
  renderizarMarcador();
}

export function renderizarMarcador() {
  if (!contenedor) return;
  contenedor.innerHTML = `
    <span id="marcador-victorias-x">Victorias X: ${MarcadorSesion.victorias_x}</span>
    <span id="marcador-victorias-o">Victorias O: ${MarcadorSesion.victorias_o}</span>
    <span id="marcador-empates">Empates: ${MarcadorSesion.empates}</span>
    <button type="button" id="btn-reiniciar">Reiniciar partida</button>
  `;
}

/** CA-I-14: incrementa el marcador exactamente una vez por GameState finalizado. */
export function registrarResultado(gameState) {
  if (gameState.status === "victoria") {
    if (gameState.winner === "X") {
      MarcadorSesion.victorias_x += 1;
    } else {
      MarcadorSesion.victorias_o += 1;
    }
  } else if (gameState.status === "empate") {
    MarcadorSesion.empates += 1;
  }
  renderizarMarcador();
}
