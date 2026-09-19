"""Cliente de integración con la API pública iTunes Search."""

import logging
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.esquemas.favorito import PeliculaRespuesta

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
ITUNES_TIMEOUT_SECONDS = 8.0
logger = logging.getLogger(__name__)


def normalizar_pelicula(resultado: dict[str, Any]) -> PeliculaRespuesta | None:
    """Convierte un resultado de iTunes al contrato público de la aplicación."""

    track_id = resultado.get("trackId")
    titulo = resultado.get("trackName")
    if track_id is None or not isinstance(titulo, str) or not titulo.strip():
        return None

    release_date = resultado.get("releaseDate")
    year = release_date[:4] if isinstance(release_date, str) and release_date else None
    artwork_url = resultado.get("artworkUrl100")
    poster = artwork_url.replace("100x100bb", "600x600bb") if isinstance(artwork_url, str) else None
    return PeliculaRespuesta(pelicula_id=str(track_id), titulo=titulo.strip(), year=year, poster=poster)


async def buscar_peliculas(termino: str) -> list[PeliculaRespuesta]:
    """Busca películas en iTunes.

    Devuelve una lista vacía únicamente si iTunes responde sin coincidencias. Si el
    proveedor no está disponible, registra el detalle técnico y expone un 502.
    """

    try:
        async with httpx.AsyncClient(timeout=ITUNES_TIMEOUT_SECONDS) as cliente:
            respuesta = await cliente.get(
                ITUNES_SEARCH_URL,
                params={"term": termino, "media": "movie", "limit": 20},
            )
            respuesta.raise_for_status()
            contenido = respuesta.json()
    except httpx.HTTPError as error:
        logger.exception("No fue posible consultar iTunes para la búsqueda %r: %s", termino, error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servicio de búsqueda de películas no está disponible. Inténtalo de nuevo más tarde.",
        ) from error
    except ValueError as error:
        logger.exception("iTunes devolvió una respuesta JSON inválida para la búsqueda %r: %s", termino, error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servicio de búsqueda de películas no está disponible. Inténtalo de nuevo más tarde.",
        ) from error

    if not isinstance(contenido, dict):
        logger.warning(
            "iTunes devolvió un JSON que no es un objeto para la búsqueda %r: tipo=%s, URL=%s",
            termino,
            type(contenido).__name__,
            respuesta.url,
        )
        return []

    resultados = contenido.get("results", [])
    if not isinstance(resultados, list):
        logger.warning(
            "iTunes devolvió una estructura de resultados inválida para la búsqueda %r: "
            "resultCount=%r, tipo de results=%s, URL=%s",
            termino,
            contenido.get("resultCount"),
            type(resultados).__name__,
            respuesta.url,
        )
        return []
    if not resultados:
        logger.warning(
            "iTunes no devolvió resultados para la búsqueda %r: resultCount=%r, URL=%s",
            termino,
            contenido.get("resultCount"),
            respuesta.url,
        )
        return []

    peliculas: list[PeliculaRespuesta] = []
    for resultado in resultados:
        if isinstance(resultado, dict) and (pelicula := normalizar_pelicula(resultado)) is not None:
            peliculas.append(pelicula)
    logger.info(
        "Búsqueda en iTunes completada para %r: %d resultados recibidos, %d películas válidas",
        termino,
        len(resultados),
        len(peliculas),
    )
    return peliculas
