"""Esquemas Pydantic para películas y favoritos."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PeliculaRespuesta(BaseModel):
    """Película normalizada a partir de la respuesta de iTunes."""

    pelicula_id: str
    titulo: str
    year: str | None = None
    poster: str | None = None


class FavoritoCrear(PeliculaRespuesta):
    """Datos de una película que se guardará como favorita."""

    nota: str | None = Field(default=None, max_length=5000)


class FavoritoActualizar(BaseModel):
    """Campos que el propietario puede modificar en un favorito."""

    nota: str | None = Field(default=None, max_length=5000)


class FavoritoRespuesta(FavoritoCrear):
    """Favorito persistido, listo para devolver al cliente."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    date_added: datetime
