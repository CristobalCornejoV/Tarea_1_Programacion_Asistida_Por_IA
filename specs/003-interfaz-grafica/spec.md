# Feature Specification: Interfaz Gráfica del Juego Tres en Raya

**Feature Branch**: `003-interfaz-grafica`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "Interfaz gráfica del juego tres en raya. Estados de la UI: Configuración, En juego, Esperando agente, Terminada. Requisitos: configuración de modo/nivel/fichas/modalidad; indicar turno y ficha; resaltar línea ganadora y bloquear tablero; rechazar jugada ilegal con aviso visual; mostrar espera del agente y deshabilitar tablero; en modalidad continua señalar fichas movibles y casillas destino; marcador de sesión y botón de reinicio conservando marcador; operación completa por teclado (Requisito Excelente)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurar una Partida Nueva (Priority: P1)

Antes de jugar, el usuario elige el modo (Humano vs Humano o Humano vs
Agente), el nivel del agente (si aplica), la ficha de cada jugador y la
modalidad (clásica o continua), y luego inicia la partida.

**Why this priority**: Sin una configuración válida no puede existir una
partida; es el punto de entrada obligatorio de toda la interfaz.

**Independent Test**: Se puede probar por completo abriendo la pantalla de
Configuración, seleccionando cada opción disponible, confirmando el inicio, y
verificando que la UI transiciona a En Juego con exactamente los parámetros
elegidos; y verificando también que un intento de inicio con selección
incompleta es rechazado.

**Acceptance Scenarios** (notación EARS):

- **CA-I-01**: LA interfaz SHALL presentar el estado Configuración como
  estado inicial antes de que exista una partida en curso.
- **CA-I-02**: EN el estado Configuración, LA interfaz SHALL permitir
  seleccionar el modo de partida (Humano vs Humano o Humano vs Agente), la
  ficha (X u O) de cada jugador, y la modalidad (clásica o continua); y
  CUANDO el modo seleccionado es Humano vs Agente, LA interfaz SHALL además
  requerir la selección del nivel del agente (Sencillo, Medio o Complejo).
- **CA-I-03**: CUANDO el usuario ha seleccionado modo, fichas y modalidad (y
  el nivel del agente si el modo lo requiere) y confirma el inicio, LA
  interfaz SHALL transicionar al estado En Juego con esos parámetros.
- **CA-I-04**: SI el usuario intenta confirmar el inicio sin haber
  completado alguna selección requerida (modo, fichas, modalidad, o nivel de
  agente cuando corresponda), ENTONCES LA interfaz SHALL rechazar el inicio,
  SHALL indicar visualmente qué selección falta, y SHALL permanecer en el
  estado Configuración.

---

### User Story 2 - Jugar una Partida (Priority: P1)

Durante la partida, el usuario ve en todo momento de quién es el turno y qué
ficha usa, puede intentar jugadas sobre el tablero, recibe un aviso visual
ante una jugada inválida sin que se altere el estado, y al finalizar la
partida (victoria o empate) ve el resultado resaltado y el tablero bloqueado.

**Why this priority**: Es el ciclo central de valor de la interfaz: jugar una
partida completa y percibir claramente su resultado.

**Independent Test**: Se puede probar por completo jugando una partida hasta
victoria y verificando el resaltado de la línea ganadora y el bloqueo del
tablero; jugando otra hasta empate y verificando su indicación; e intentando
una jugada ilegal en medio de una partida y verificando el aviso sin cambios
de estado.

**Acceptance Scenarios** (notación EARS):

- **CA-I-05**: MIENTRAS la partida esté en estado En Juego, LA interfaz SHALL
  indicar visiblemente de quién es el turno actual y qué ficha usa ese
  jugador.
- **CA-I-06**: CUANDO se produce una victoria, LA interfaz SHALL resaltar
  visualmente la línea ganadora (fila, columna o diagonal), SHALL bloquear
  toda interacción adicional con el tablero, y SHALL transicionar al estado
  Terminada.
- **CA-I-07**: CUANDO se produce un empate, LA interfaz SHALL indicar
  visualmente el resultado de empate, SHALL bloquear toda interacción
  adicional con el tablero, y SHALL transicionar al estado Terminada.
- **CA-I-08**: SI el usuario intenta una jugada ilegal (casilla ocupada,
  fuera de turno, fase incorrecta u otra regla violada), ENTONCES LA interfaz
  SHALL rechazar la jugada, SHALL mostrar un aviso visual del error, y SHALL
  mantener sin alteración el estado visible del tablero y del turno.

---

### User Story 3 - Esperar la Jugada del Agente (Priority: P2)

Cuando le corresponde jugar a un agente, el usuario ve una indicación visual
de que el agente está calculando su jugada y no puede interactuar con el
tablero mientras tanto.

**Why this priority**: Depende de que exista ya una partida En Juego contra
un agente (US1 y US2); comunica al usuario que el sistema está procesando y
evita jugadas humanas fuera de turno mientras el agente responde.

**Independent Test**: Se puede probar por completo iniciando una partida
Humano vs Agente, llegando al turno del agente, y verificando que la interfaz
muestra la indicación de espera y deshabilita el tablero hasta que el agente
entrega su jugada.

**Acceptance Scenarios** (notación EARS):

- **CA-I-09**: MIENTRAS el agente esté calculando su jugada, LA interfaz
  SHALL transicionar al estado Esperando Agente, SHALL mostrar una
  indicación visual de espera, y SHALL deshabilitar toda interacción con el
  tablero.
- **CA-I-10**: CUANDO el agente entrega su jugada, LA interfaz SHALL ocultar
  la indicación de espera, SHALL aplicar la jugada recibida sobre el
  tablero, y SHALL retornar al estado En Juego (o transicionar a Terminada
  si la jugada del agente finaliza la partida, según CA-I-06/CA-I-07).

---

### User Story 4 - Mover Fichas en Modalidad Continua (Priority: P2)

En modalidad continua, durante la fase de movimiento, el usuario ve
señaladas visualmente cuáles de sus fichas puede mover y, al elegir una,
hacia qué casillas vacías puede moverla.

**Why this priority**: Es una capacidad específica de la modalidad continua y
depende de que la partida ya esté En Juego (US2); sin esta señalización el
usuario no puede distinguir con claridad sus opciones de movimiento válidas.

**Independent Test**: Se puede probar por completo iniciando una partida en
modalidad continua, avanzando hasta la fase de movimiento, y verificando que
la interfaz señala las fichas propias movibles y, al seleccionar una, las
casillas vacías disponibles como destino.

**Acceptance Scenarios** (notación EARS):

- **CA-I-11**: MIENTRAS la partida esté en modalidad continua, en fase de
  movimiento, y sea el turno del jugador humano, LA interfaz SHALL señalar
  visualmente cuáles de las fichas propias de ese jugador pueden moverse.
- **CA-I-12**: CUANDO el jugador humano selecciona una de sus fichas
  movibles durante la fase de movimiento, LA interfaz SHALL señalar
  visualmente todas las casillas vacías disponibles como destino válido para
  esa ficha.

---

### User Story 5 - Marcador de Sesión y Reinicio (Priority: P3)

El usuario ve un marcador acumulado de la sesión (victorias de cada jugador y
empates) y puede reiniciar la partida actual sin perder ese marcador.

**Why this priority**: Añade valor de continuidad entre partidas sucesivas,
pero no es necesaria para completar una única partida (US1-US2); por eso se
prioriza después de las capacidades de juego.

**Independent Test**: Se puede probar por completo jugando varias partidas
consecutivas con distintos resultados y verificando que el marcador acumula
correctamente victorias y empates, y que reiniciar la partida actual
mantiene el marcador acumulado sin cambios.

**Acceptance Scenarios** (notación EARS):

- **CA-I-13**: LA interfaz SHALL mantener visible, durante toda la sesión,
  un marcador con el número de victorias de cada jugador y el número de
  empates acumulados desde que se abrió la sesión.
- **CA-I-14**: CUANDO una partida finaliza con victoria o empate, LA
  interfaz SHALL actualizar el marcador de la sesión sumando ese resultado.
- **CA-I-15**: CUANDO el usuario activa el control de reiniciar partida, LA
  interfaz SHALL iniciar una nueva partida con los mismos parámetros de
  configuración vigentes y SHALL conservar sin modificar el marcador
  acumulado de la sesión.

---

### User Story 6 - Operación Completa por Teclado (Requisito Excelente) (Priority: P3)

El usuario puede configurar, jugar y reiniciar una partida completa
utilizando únicamente el teclado, sin depender del mouse: navegando entre
controles y casillas con Tab y las flechas de dirección, y seleccionando o
confirmando con Enter o Espacio.

**Why this priority**: Es un requisito de accesibilidad adicional ("Requisito
Excelente") que se apoya sobre todas las demás historias ya funcionando con
mouse/puntero; se prioriza al final porque extiende, sin modificar, el
comportamiento ya definido en US1-US5.

**Independent Test**: Se puede probar por completo desconectando o
ignorando el mouse y completando, solo con teclado, el flujo de
configuración, una partida completa (incluyendo una jugada rechazada por
ilegal) y un reinicio, verificando en cada paso que el foco de teclado es
visible y que toda acción disponible por mouse tiene equivalente por
teclado.

**Acceptance Scenarios** (notación EARS):

- **CA-I-16**: LA interfaz SHALL permitir operar la totalidad de sus
  controles de Configuración, el tablero de juego, y el control de
  reiniciar, exclusivamente mediante teclado: navegación con Tab y con las
  flechas de dirección, y selección o confirmación con Enter o con la tecla
  Espacio.
- **CA-I-17**: MIENTRAS un control de Configuración, una casilla del
  tablero, o el botón de reiniciar tengan el foco de teclado, LA interfaz
  SHALL mostrar una indicación visual clara de cuál elemento tiene el foco.
- **CA-I-18**: SI el usuario intenta seleccionar, mediante teclado, una
  casilla del tablero mientras este está deshabilitado (estado Esperando
  Agente, o partida Terminada), ENTONCES LA interfaz SHALL ignorar esa
  entrada sin alterar el estado ni el foco actual.

---

### User Story 7 - Uso en Pantallas de Distinto Tamaño (Responsive) (Priority: P3)

El usuario puede configurar y jugar una partida completa desde un
navegador de escritorio, tablet o móvil: el tablero, el marcador y los
controles de Configuración permanecen legibles, alcanzables y operables
sin necesidad de desplazamiento horizontal ni de hacer zoom manual, sea
cual sea el tamaño de la ventana o dispositivo.

**Why this priority**: Es un requisito de alcance de dispositivo adicional
que se apoya sobre todas las demás historias ya funcionando en escritorio
(US1-US6); se prioriza al final porque adapta la presentación visual sin
modificar el comportamiento funcional ya definido.

**Independent Test**: Se puede probar por completo abriendo la interfaz en
al menos tres anchos de viewport representativos (móvil, tablet,
escritorio), completando en cada uno el flujo de configurar, jugar hasta
el final, y reiniciar una partida, y verificando que ningún control queda
oculto, cortado, o requiere desplazamiento horizontal.

**Acceptance Scenarios** (notación EARS):

- **CA-I-19**: LA interfaz SHALL permanecer completamente utilizable —
  tablero, marcador y controles de Configuración visibles y operables sin
  desplazamiento horizontal— en anchos de viewport típicos de dispositivos
  móviles, tablets y escritorio (aproximadamente 320px a 1920px de ancho).
- **CA-I-20**: MIENTRAS el ancho de viewport sea reducido (dispositivo
  móvil o ventana angosta), LA interfaz SHALL reorganizar la disposición
  de sus elementos (tablero, marcador, controles de Configuración) para
  que el tablero y los controles imprescindibles para la jugada actual
  permanezcan visibles sin necesidad de que el usuario haga zoom manual.
- **CA-I-21**: EN cualquier tamaño de viewport soportado, LA interfaz SHALL
  mantener cada casilla del tablero con un tamaño suficiente para una
  interacción táctil precisa (objetivo de toque), evitando que dos
  casillas adyacentes sean indistinguibles al tacto.
- **CA-I-22**: CUANDO el usuario redimensiona la ventana o rota el
  dispositivo durante una partida en curso, LA interfaz SHALL reajustar su
  disposición visual sin alterar el estado de la partida (tablero, turno,
  fase, marcador) ni, si aplica, el foco de teclado vigente.

---

### Edge Cases

- ¿Qué ocurre si el usuario cambia una selección de Configuración
  (modo, ficha, modalidad o nivel de agente) antes de confirmar el inicio?
  La interfaz SHALL reflejar la selección más reciente sin restricciones
  adicionales, siempre que la partida no haya iniciado aún.
- ¿Qué ocurre si el usuario navega con las flechas de dirección más allá del
  borde del tablero (por ejemplo, hacia la derecha desde la última columna)?
  La interfaz SHALL mantener el foco dentro de los límites del tablero, sin
  desplazarlo fuera de las 9 casillas.
- ¿Qué ocurre si el jugador humano intenta seleccionar, en modalidad
  continua, una ficha propia que no está señalada como movible? La interfaz
  SHALL rechazar la jugada resultante con el mismo aviso visual de jugada
  ilegal definido en CA-I-08.
- ¿Qué ocurre con el marcador de sesión si el usuario cambia los parámetros
  de Configuración (por ejemplo, cambia de modalidad) en lugar de solo
  reiniciar? La interfaz SHALL conservar igualmente el marcador acumulado de
  la sesión, dado que este se asocia a la sesión y no a una configuración
  específica.
- ¿Qué ocurre si el ancho de viewport es más angosto que el mínimo
  soportado (por debajo de ~320px)? La interfaz SHALL priorizar mantener el
  tablero y el control de jugada actual operables, permitiendo en ese caso
  extremo que elementos secundarios (p. ej. el marcador histórico completo)
  requieran desplazamiento vertical, pero nunca horizontal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La interfaz MUST implementar exactamente cuatro estados
  observables: Configuración, En Juego, Esperando Agente y Terminada, con
  transiciones exclusivas entre ellos según lo definido en los criterios de
  aceptación anteriores.
- **FR-002**: En el estado Configuración, la interfaz MUST permitir elegir
  modo (Humano vs Humano / Humano vs Agente), nivel de agente (cuando
  aplique), ficha de cada jugador y modalidad (clásica/continua) antes de
  permitir iniciar la partida.
- **FR-003**: La interfaz MUST indicar en todo momento, durante el estado En
  Juego, de quién es el turno actual y qué ficha usa.
- **FR-004**: La interfaz MUST resaltar visualmente la línea ganadora
  (fila, columna o diagonal) al producirse una victoria, y MUST bloquear el
  tablero ante cualquier resultado final (victoria o empate).
- **FR-005**: La interfaz MUST rechazar visualmente toda jugada ilegal
  mediante un aviso, sin alterar el estado del tablero, del turno, ni de la
  partida.
- **FR-006**: La interfaz MUST mostrar una indicación visual de espera y
  MUST deshabilitar el tablero durante todo el tiempo en que un agente esté
  calculando su jugada.
- **FR-007**: En modalidad continua, durante la fase de movimiento, la
  interfaz MUST señalar visualmente las fichas propias movibles del jugador
  humano y, al seleccionar una, las casillas vacías disponibles como
  destino.
- **FR-008**: La interfaz MUST mantener un marcador de sesión con victorias
  por jugador y empates, MUST actualizarlo al finalizar cada partida, y MUST
  ofrecer un control para reiniciar la partida actual sin modificar dicho
  marcador.
- **FR-009**: La interfaz MUST permitir operar la totalidad de sus controles
  (Configuración, tablero, reinicio) exclusivamente mediante teclado,
  incluyendo navegación (Tab, flechas de dirección) y selección/confirmación
  (Enter, Espacio), y MUST mostrar en todo momento una indicación visual del
  elemento con foco de teclado.
- **FR-010**: La interfaz MUST presentar un diseño responsive: tablero,
  marcador y controles de Configuración MUST permanecer visibles y
  operables, sin desplazamiento horizontal, en anchos de viewport típicos
  de móvil, tablet y escritorio (aproximadamente 320px a 1920px), y MUST
  reajustar su disposición ante un cambio de tamaño de ventana sin alterar
  el estado de la partida en curso.

### Key Entities

- **Sesión**: Agrupa una o más partidas jugadas consecutivamente con el
  mismo marcador acumulado (victorias por jugador y empates), que persiste
  entre reinicios de partida dentro de la misma sesión.
- **Configuración de Partida**: Conjunto de parámetros elegidos antes de
  iniciar: modo (Humano vs Humano / Humano vs Agente), nivel de agente (si
  aplica), ficha de cada jugador y modalidad (clásica/continua).
- **Estado de UI**: Uno de Configuración, En Juego, Esperando Agente o
  Terminada, que determina qué controles están disponibles y qué información
  se muestra en cada momento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de iniciar una partida con selección
  de configuración incompleta son rechazados sin transicionar fuera de
  Configuración.
- **SC-002**: El 100% de las partidas finalizadas (victoria o empate) dejan
  el tablero visualmente bloqueado y, en caso de victoria, la línea ganadora
  resaltada.
- **SC-003**: El 100% de las jugadas ilegales intentadas por el usuario
  reciben un aviso visual sin modificar el estado previo del tablero o del
  turno.
- **SC-004**: El tablero permanece deshabilitado durante el 100% del tiempo
  en que un agente está calculando su jugada, y se habilita nuevamente en
  menos de 1 segundo después de recibir la jugada del agente.
- **SC-005**: Un usuario puede completar, usando exclusivamente el teclado,
  el flujo completo de configurar, jugar hasta el final, y reiniciar una
  partida, sin necesidad de usar el mouse en ningún paso.
- **SC-006**: El marcador de sesión refleja, sin pérdida ni reinicio
  accidental, el resultado acumulado de todas las partidas jugadas en la
  sesión, incluyendo tras cualquier número de reinicios de partida.
- **SC-007**: Un usuario puede completar el flujo completo de configurar,
  jugar hasta el final, y reiniciar una partida en cualquier ancho de
  viewport entre 320px y 1920px, sin necesidad de desplazamiento horizontal
  ni de hacer zoom manual en ningún paso.

## Assumptions

- Esta especificación describe el comportamiento observable de la interfaz
  (estados, indicaciones visuales, controles y su disponibilidad); no
  define las reglas del motor de juego ni la lógica de los agentes, que se
  especifican por separado y sobre las cuales esta interfaz únicamente
  consume resultados.
- El marcador de sesión (victorias/empates) es volátil y vive mientras dure
  la sesión de uso de la interfaz; no se especifica en este documento ningún
  requisito de persistencia entre sesiones (por ejemplo, tras cerrar y volver
  a abrir la aplicación).
- "Aviso visual" ante una jugada ilegal se refiere a una señal perceptible
  (por ejemplo, resaltado, mensaje o ícono) sin especificar su forma exacta,
  que queda a criterio de la implementación visual concreta.
- El "Requisito Excelente" de operación completa por teclado (US6) aplica
  como capa adicional sobre el resto de historias de usuario y no reemplaza
  ni restringe la operación equivalente mediante puntero (mouse/touch).
- El diseño responsive (US7) no fija breakpoints exactos ni un catálogo de
  dispositivos soportados; el rango de referencia (320px-1920px de ancho de
  viewport) es un estándar razonable de la industria para cubrir móvil,
  tablet y escritorio, y la adaptación entre esos anchos SHOULD ser fluida
  (sin saltos bruscos de utilizabilidad) en lugar de basarse en un número
  fijo de puntos de quiebre.
