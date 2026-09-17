"""Cliente de integración con la API pública iTunes Search."""

from typing import Any

import httpx

from app.esquemas.favorito import PeliculaRespuesta

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
ITUNES_TIMEOUT_SECONDS = 8.0


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
    """Busca películas en iTunes y devuelve una lista vacía ante fallos externos."""

    try:
        async with httpx.AsyncClient(timeout=ITUNES_TIMEOUT_SECONDS) as cliente:
            respuesta = await cliente.get(
                ITUNES_SEARCH_URL,
                params={"term": termino, "media": "movie", "limit": 20},
            )
            respuesta.raise_for_status()
            contenido = respuesta.json()
    except (httpx.HTTPError, ValueError):
        return []

    resultados = contenido.get("results", []) if isinstance(contenido, dict) else []
    if not isinstance(resultados, list):
        return []
    peliculas: list[PeliculaRespuesta] = []
    for resultado in resultados:
        if isinstance(resultado, dict) and (pelicula := normalizar_pelicula(resultado)) is not None:
            peliculas.append(pelicula)
    return peliculas
