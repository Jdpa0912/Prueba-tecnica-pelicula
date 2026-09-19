"""Pruebas unitarias del cliente de TMDb."""

import asyncio

import httpx
import pytest
from fastapi import HTTPException

from app.servicios import tmdb
from app.servicios.tmdb import normalizar_pelicula


def test_normalizar_pelicula_mapea_los_campos_requeridos() -> None:
    pelicula = normalizar_pelicula(
        {
            "id": 123,
            "title": " Película de prueba ",
            "release_date": "2024-01-15",
            "poster_path": "/poster.jpg",
        }
    )

    assert pelicula is not None
    assert pelicula.pelicula_id == "123"
    assert pelicula.titulo == "Película de prueba"
    assert pelicula.year == "2024"
    assert pelicula.poster == "https://image.tmdb.org/t/p/w500/poster.jpg"


def test_normalizar_pelicula_descarta_resultados_incompletos() -> None:
    assert normalizar_pelicula({"id": 123}) is None
    assert normalizar_pelicula({"title": "Sin identificador"}) is None


def test_buscar_peliculas_devuelve_502_si_tmdb_no_esta_disponible(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    class ClienteSinConexion:
        async def __aenter__(self) -> None:
            raise httpx.ConnectError("No se pudo conectar")

        async def __aexit__(self, *args: object) -> None:
            return None

    class ConfiguracionPrueba:
        tmdb_api_token = "token-de-prueba"
        tmdb_language = "es-ES"

    monkeypatch.setattr(tmdb, "obtener_configuracion", lambda: ConfiguracionPrueba())
    monkeypatch.setattr(tmdb.httpx, "AsyncClient", lambda **_: ClienteSinConexion())

    with pytest.raises(HTTPException) as error:
        asyncio.run(tmdb.buscar_peliculas("Mario"))

    assert error.value.status_code == 502


def test_buscar_peliculas_devuelve_503_sin_token_de_tmdb(monkeypatch: pytest.MonkeyPatch) -> None:
    class ConfiguracionSinToken:
        tmdb_api_token = None
        tmdb_language = "es-ES"

    monkeypatch.setattr(tmdb, "obtener_configuracion", lambda: ConfiguracionSinToken())

    with pytest.raises(HTTPException) as error:
        asyncio.run(tmdb.buscar_peliculas("Barbie"))

    assert error.value.status_code == 503
