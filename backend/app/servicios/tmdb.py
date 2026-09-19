"""Cliente de integración con la API de películas de TMDb."""

import logging
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.esquemas.favorito import PeliculaRespuesta
from app.nucleo.configuracion import obtener_configuracion

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_TIMEOUT_SECONDS = 8.0
logger = logging.getLogger(__name__)


def normalizar_pelicula(resultado: dict[str, Any]) -> PeliculaRespuesta | None:
    """Convierte un resultado de TMDb al contrato público de la aplicación."""

    pelicula_id = resultado.get("id")
    titulo = resultado.get("title")
    if pelicula_id is None or not isinstance(titulo, str) or not titulo.strip():
        return None

    release_date = resultado.get("release_date")
    year = release_date[:4] if isinstance(release_date, str) and release_date else None
    poster_path = resultado.get("poster_path")
    poster = f"{TMDB_IMAGE_URL}{poster_path}" if isinstance(poster_path, str) and poster_path else None
    return PeliculaRespuesta(pelicula_id=str(pelicula_id), titulo=titulo.strip(), year=year, poster=poster)


async def buscar_peliculas(termino: str) -> list[PeliculaRespuesta]:
    """Busca películas en TMDb y devuelve sus resultados normalizados."""

    configuracion = obtener_configuracion()
    if not configuracion.tmdb_api_token:
        logger.error("TMDB_API_TOKEN no está configurado; no se puede buscar %r", termino)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El proveedor de películas no está configurado.",
        )

    try:
        async with httpx.AsyncClient(timeout=TMDB_TIMEOUT_SECONDS) as cliente:
            respuesta = await cliente.get(
                TMDB_SEARCH_URL,
                params={"query": termino, "language": configuracion.tmdb_language, "include_adult": "false"},
                headers={"Authorization": f"Bearer {configuracion.tmdb_api_token}"},
            )
            respuesta.raise_for_status()
            contenido = respuesta.json()
    except (httpx.HTTPError, ValueError) as error:
        logger.exception("No fue posible consultar TMDb para la búsqueda %r: %s", termino, error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servicio de búsqueda de películas no está disponible. Inténtalo de nuevo más tarde.",
        ) from error

    resultados = contenido.get("results", []) if isinstance(contenido, dict) else []
    if not isinstance(resultados, list):
        logger.warning("TMDb devolvió una estructura de resultados inválida para la búsqueda %r", termino)
        return []

    peliculas = [
        pelicula
        for resultado in resultados
        if isinstance(resultado, dict) and (pelicula := normalizar_pelicula(resultado)) is not None
    ]
    logger.info("Búsqueda en TMDb completada para %r: %d películas válidas", termino, len(peliculas))
    return peliculas
