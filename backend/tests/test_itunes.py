"""Pruebas unitarias del mapeo de resultados de iTunes."""

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
