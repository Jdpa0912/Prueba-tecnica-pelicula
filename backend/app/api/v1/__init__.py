"""Versión 1 de la API pública."""

from app.api.v1.autenticacion import router as autenticacion_router
from app.api.v1.favoritos import router as favoritos_router
from app.api.v1.peliculas import router as peliculas_router

__all__ = ["autenticacion_router", "favoritos_router", "peliculas_router"]
