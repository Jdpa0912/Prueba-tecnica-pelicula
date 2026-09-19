"""Endpoints de búsqueda interna de películas."""

from fastapi import APIRouter, Query

from app.api.dependencias import UsuarioActual
from app.esquemas.favorito import PeliculaRespuesta
from app.servicios.tmdb import buscar_peliculas

router = APIRouter(prefix="/peliculas", tags=["Películas"])


@router.get("/buscar", response_model=list[PeliculaRespuesta])
async def buscar(usuario_actual: UsuarioActual, q: str = Query(min_length=1, max_length=100)) -> list[PeliculaRespuesta]:
    """Busca películas mediante el backend, sin exponer TMDb al frontend."""

    del usuario_actual
    return await buscar_peliculas(q.strip())
