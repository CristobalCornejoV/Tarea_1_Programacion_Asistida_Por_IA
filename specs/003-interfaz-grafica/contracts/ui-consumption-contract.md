# Contrato de Consumo de API: Interfaz Gráfica

**Feature**: [../spec.md](../spec.md) | **Modelo de datos**: [../data-model.md](../data-model.md)

Esta spec no define endpoints HTTP propios (la interfaz no expone servicios,
solo los consume). Este documento fija el **contrato de secuencia** —qué
llamadas hace la interfaz, en qué orden, y qué hace con cada respuesta—
referenciando los contratos HTTP reales definidos en las specs 001 y 002.

## Secuencia: Configurar e iniciar partida (CA-I-01 a CA-I-04)

1. Usuario completa `ConfiguracionPartida` en la pantalla de Configuración.
2. Al confirmar, la interfaz llama
   `POST /api/games` ([`../../001-motor-tres-en-raya/contracts/games-api.md`](../../001-motor-tres-en-raya/contracts/games-api.md))
   con `{ "mode": configuracion.modalidad }`.
3. La interfaz guarda la respuesta (`GameState`) en `EstadoUI.game_state` y
   transiciona `pantalla` a `"en_juego"`.

## Secuencia: Turno de un jugador humano (CA-I-05, CA-I-08, CA-I-11, CA-I-12)

1. La interfaz lee `game_state.turn` y determina, vía `ConfiguracionPartida`,
   que corresponde a un jugador humano.
2. El usuario interactúa con el tablero (clic o teclado). La interfaz arma
   una `Jugada` (colocar o mover, según `game_state.phase`) y llama
   `POST /api/games/{game_id}/moves` ([contrato del motor](../../001-motor-tres-en-raya/contracts/games-api.md)).
3. **Si la respuesta es `200 OK`**: la interfaz reemplaza `game_state` con la
   respuesta y reevalúa `pantalla` (`"en_juego"` si `status = "en_curso"`,
   `"terminada"` si no).
4. **Si la respuesta es `422`**: la interfaz muestra el aviso visual de error
   (CA-I-08) usando el campo `error` de la respuesta, y **no** modifica
   `EstadoUI.game_state`.

## Secuencia: Turno de un agente (CA-I-09, CA-I-10)

1. La interfaz lee `game_state.turn` y determina, vía `ConfiguracionPartida`,
   que corresponde a un agente. Transiciona `pantalla` a
   `"esperando_agente"` y deshabilita el tablero.
2. Llama `POST /api/agents/{nivel_agente}/move` ([contrato de agentes](../../002-agentes-de-juego/contracts/agents-api.md))
   enviando el subconjunto de `game_state` que ese contrato requiere.
3. Con la `Jugada` recibida, añade `player: game_state.turn` y llama
   `POST /api/games/{game_id}/moves` (mismo contrato del motor que en la
   secuencia anterior).
4. Al recibir la respuesta, oculta la indicación de espera y aplica el mismo
   tratamiento del paso 3 de la secuencia anterior (actualizar
   `game_state`, reevaluar `pantalla`).

## Secuencia: Reinicio conservando marcador (CA-I-13 a CA-I-15)

1. Al finalizar una partida (`pantalla = "terminada"`), la interfaz ya
   actualizó `MarcadorSesion` (ver `data-model.md`) a partir de
   `game_state.status`/`winner`.
2. Al activar "reiniciar", la interfaz repite la secuencia de "Configurar e
   iniciar partida" (paso 2 en adelante) usando la misma
   `ConfiguracionPartida` vigente, sin tocar `MarcadorSesion`.

## Regla transversal

En ninguna de estas secuencias la interfaz evalúa victoria, empate,
legalidad de jugada, ni heurística de agente: esos resultados llegan
siempre resueltos en la respuesta HTTP del motor (spec 001) o del agente
(spec 002). La interfaz únicamente enruta datos y refleja los campos ya
resueltos (`status`, `winner`, `winning_line`, `error`).
