"""Pruebas para evitar películas favoritas duplicadas."""

import os

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

# El módulo de base de datos se inicializa al importar los endpoints, aunque estas
# pruebas usen sesiones simuladas.
os.environ.setdefault("DATABASE_URL", "postgresql://usuario:clave@localhost/pruebas")
os.environ.setdefault("JWT_SECRET", "secreto-de-prueba-con-al-menos-32-caracteres")

from app.api.v1.favoritos import DETALLE_FAVORITO_DUPLICADO, crear_favorito
from app.esquemas.favorito import FavoritoCrear


class UsuarioPrueba:
    """Usuario autenticado mínimo para probar el endpoint directamente."""

    id = 1


class SesionConFavoritoExistente:
    """Simula una consulta que encuentra el favorito del usuario."""

    def scalar(self, *_: object) -> int:
        return 1


class SesionConConflicto:
    """Simula una inserción concurrente que activa la restricción única."""

    def __init__(self) -> None:
        self.revirtió = False

    def scalar(self, *_: object) -> None:
        return None

    def add(self, _: object) -> None:
        return None

    def commit(self) -> None:
        raise IntegrityError("INSERT", {}, Exception("duplicado"))

    def rollback(self) -> None:
        self.revirtió = True


def datos_pelicula() -> FavoritoCrear:
    """Crea datos válidos de una película para las pruebas."""

    return FavoritoCrear(pelicula_id="123", titulo="Película de prueba")


def test_crear_favorito_rechaza_una_pelicula_ya_guardada() -> None:
    with pytest.raises(HTTPException) as error:
        crear_favorito(datos_pelicula(), UsuarioPrueba(), SesionConFavoritoExistente())

    assert error.value.status_code == 409
    assert error.value.detail == DETALLE_FAVORITO_DUPLICADO


def test_crear_favorito_maneja_duplicados_en_solicitudes_simultaneas() -> None:
    sesion = SesionConConflicto()

    with pytest.raises(HTTPException) as error:
        crear_favorito(datos_pelicula(), UsuarioPrueba(), sesion)

    assert sesion.revirtió is True
    assert error.value.status_code == 409
    assert error.value.detail == DETALLE_FAVORITO_DUPLICADO
