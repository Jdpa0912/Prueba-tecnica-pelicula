"""Pruebas unitarias del mapeo de resultados de iTunes."""

import asyncio
import logging

import httpx
import pytest
from fastapi import HTTPException

from app.servicios import itunes
from app.servicios.itunes import normalizar_pelicula


def test_normalizar_pelicula_mapea_los_campos_requeridos() -> None:
    pelicula = normalizar_pelicula(
        {
            "trackId": 123,
            "trackName": " Película de prueba ",
            "releaseDate": "2024-01-15T00:00:00Z",
            "artworkUrl100": "https://ejemplo.test/poster-100x100bb.jpg",
        }
    )

    assert pelicula is not None
    assert pelicula.pelicula_id == "123"
    assert pelicula.titulo == "Película de prueba"
    assert pelicula.year == "2024"
    assert pelicula.poster == "https://ejemplo.test/poster-600x600bb.jpg"


def test_normalizar_pelicula_descarta_resultados_incompletos() -> None:
    assert normalizar_pelicula({"trackId": 123}) is None
    assert normalizar_pelicula({"trackName": "Sin identificador"}) is None


def test_buscar_peliculas_devuelve_502_si_itunes_no_esta_disponible(monkeypatch: pytest.MonkeyPatch) -> None:
    class ClienteSinConexion:
        async def __aenter__(self) -> None:
            raise httpx.ConnectError("No se pudo conectar")

        async def __aexit__(self, *args: object) -> None:
            return None

    monkeypatch.setattr(itunes.httpx, "AsyncClient", lambda **_: ClienteSinConexion())

    with pytest.raises(HTTPException) as error:
        asyncio.run(itunes.buscar_peliculas("Mario"))

    assert error.value.status_code == 502
    assert error.value.detail == "El servicio de búsqueda de películas no está disponible. Inténtalo de nuevo más tarde."


def test_buscar_peliculas_registra_cuando_itunes_responde_sin_resultados(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class RespuestaVacia:
        url = "https://itunes.apple.com/search?term=Barbie"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"resultCount": 0, "results": []}

    class ClienteConRespuestaVacia:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, *args: object, **kwargs: object) -> RespuestaVacia:
            return RespuestaVacia()

    monkeypatch.setattr(itunes.httpx, "AsyncClient", lambda **_: ClienteConRespuestaVacia())

    with caplog.at_level(logging.WARNING, logger=itunes.logger.name):
        peliculas = asyncio.run(itunes.buscar_peliculas("Barbie"))

    assert peliculas == []
    assert "iTunes no devolvió resultados" in caplog.text
    assert "resultCount=0" in caplog.text
