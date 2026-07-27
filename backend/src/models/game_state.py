"""Modelos inmutables de estado de partida, jugada y error, según data-model.md."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Ficha = Literal["X", "O"]
Casilla = Optional[Ficha]


class Coordenada(BaseModel):
    """Posición de una casilla del tablero (fila/columna, 0-2)."""

    model_config = ConfigDict(frozen=True)

    row: int = Field(ge=0, le=2)
    col: int = Field(ge=0, le=2)


class GameState(BaseModel):
    """Estado inmutable de una partida. Toda jugada produce una instancia nueva."""

    model_config = ConfigDict(frozen=True)

    game_id: str
    mode: Literal["clasica", "continua"]
    board: list[list[Casilla]]
    turn: Ficha
    phase: Optional[Literal["colocacion", "movimiento"]] = None
    fichas_disponibles: Optional[dict[Ficha, int]] = None
    status: Literal["en_curso", "victoria", "empate"] = "en_curso"
    winner: Optional[Ficha] = None
    winning_line: Optional[list[Coordenada]] = None

    @field_validator("board")
    @classmethod
    def _tablero_3x3(cls, board: list[list[Casilla]]) -> list[list[Casilla]]:
        if len(board) != 3 or any(len(fila) != 3 for fila in board):
            raise ValueError("board debe ser una matriz de exactamente 3x3 casillas")
        return board

    @field_validator("winning_line")
    @classmethod
    def _linea_de_tres(
        cls, linea: Optional[list[Coordenada]]
    ) -> Optional[list[Coordenada]]:
        if linea is not None and len(linea) != 3:
            raise ValueError("winning_line debe tener exactamente 3 coordenadas")
        return linea


class Jugada(BaseModel):
    """Jugada solicitada por un jugador: colocar una ficha o mover una propia."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    player: Ficha
    type: Literal["colocar", "mover"]
    to: Coordenada
    from_: Optional[Coordenada] = Field(default=None, alias="from")

    @model_validator(mode="after")
    def _from_requerido_si_mover(self) -> "Jugada":
        if self.type == "mover" and self.from_ is None:
            raise ValueError("una jugada de tipo 'mover' requiere el campo 'from'")
        return self


class ErrorJugada(BaseModel):
    """Respuesta de error ante una jugada inválida (HTTP 422)."""

    model_config = ConfigDict(frozen=True)

    error: Literal[
        "casilla_ocupada",
        "fuera_de_turno",
        "ficha_ajena",
        "fase_incorrecta",
        "fuera_de_rango",
        "partida_finalizada",
    ]
    message: str
