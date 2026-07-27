# Quickstart: Interfaz Gráfica del Juego Tres en Raya

**Feature**: [spec.md](./spec.md) | **Contrato**: [contracts/ui-consumption-contract.md](./contracts/ui-consumption-contract.md)

## Prerrequisitos

- Backend de las specs 001 y 002 corriendo y sirviendo `frontend/` como
  estáticos: `uvicorn backend.src.main:app --reload --port 8000`
- Navegador de escritorio moderno

## Validación manual: flujo completo con mouse

1. Abrir `http://localhost:8000/` → SHALL mostrar la pantalla de
   Configuración (CA-I-01).
2. Elegir modo "Humano vs Agente", nivel "Medio", ficha X para el humano,
   modalidad "clásica", y confirmar → SHALL pasar a En Juego (CA-I-03).
3. Intentar confirmar el inicio en una nueva partida sin elegir modalidad →
   SHALL rechazarse y permanecer en Configuración (CA-I-04).
4. Jugar hasta ganar o perder contra el agente Medio → verificar indicación
   de turno (CA-I-05), indicación de espera del agente (CA-I-09), resaltado
   de línea ganadora o indicación de empate, y bloqueo del tablero
   (CA-I-06/CA-I-07).
5. Intentar clicar una casilla ya ocupada durante la partida → SHALL
   mostrarse un aviso visual sin alterar el tablero (CA-I-08).
6. Repetir configurando modalidad "continua" → tras colocar 3 fichas por
   jugador, verificar que se señalan las fichas movibles propias (CA-I-11)
   y, al elegir una, las casillas destino disponibles (CA-I-12).
7. Verificar que el marcador de sesión (victorias/empates) se actualiza tras
   cada partida (CA-I-13/CA-I-14) y que "Reiniciar" conserva ese marcador
   (CA-I-15).

## Validación manual: operación completa por teclado (Requisito Excelente)

1. Sin usar el mouse, navegar con Tab hasta cada control de Configuración,
   seleccionar opciones con flechas/Enter/Espacio, y confirmar el inicio.
2. Navegar al tablero con Tab, mover el foco entre casillas con las flechas
   de dirección, y confirmar una jugada con Enter o Espacio.
3. Verificar que el elemento con foco siempre tiene una indicación visual
   clara (CA-I-17), incluidas las flechas en los bordes del tablero (el foco
   SHALL permanecer dentro de las 9 casillas, ver Edge Cases de `spec.md`).
4. Intentar seleccionar una casilla por teclado mientras el tablero está
   deshabilitado (estado Esperando Agente) → SHALL ignorarse sin cambios
   (CA-I-18).
5. Completar una partida y reiniciarla usando solo el botón de reinicio
   activado por teclado.

## Ejecutar la suite automatizada (Pytest + navegador controlado)

```bash
pytest tests/e2e/test_ui_flows.py -v
```

**Resultado esperado**: todos los flujos críticos (CA-I-01 a CA-I-18) en
verde contra el `frontend/` servido localmente, sin necesidad de un
framework de testing JS (ver `research.md` Decisión 4).
