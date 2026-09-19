"""Pruebas de creación de favoritos, incluidos intentos simultáneos."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi import HTTPException, status
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.v1.favoritos import crear_favorito
from app.base_datos.conexion import Base
from app.esquemas.favorito import FavoritoCrear
from app.modelos.favorito import Favorito
from app.modelos.usuario import Usuario


class SesionSincronizada:
    """Retrasa el primer SELECT para que dos solicitudes compitan por el INSERT."""

    def __init__(self, sesion: Session, barrera: Barrier) -> None:
        self.sesion = sesion
        self.barrera = barrera

    def scalar(self, consulta: object) -> object:
        resultado = self.sesion.scalar(consulta)
        self.barrera.wait(timeout=5)
        return resultado

    def __getattr__(self, nombre: str) -> object:
        return getattr(self.sesion, nombre)


@pytest.fixture
def fabrica_sesiones(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'favoritos.db'}",
        connect_args={"check_same_thread": False, "timeout": 5},
    )
    Base.metadata.create_all(engine)
    fabrica = sessionmaker(bind=engine, expire_on_commit=False)
    with fabrica() as sesion:
        sesion.add(Usuario(id=1, username="ana", password_hash="hash"))
        sesion.commit()
    yield fabrica
    engine.dispose()


@pytest.fixture
def pelicula() -> FavoritoCrear:
    return FavoritoCrear(pelicula_id="603", titulo="The Matrix", year="1999")


def test_crear_favorito_y_rechazar_duplicado(fabrica_sesiones, pelicula: FavoritoCrear) -> None:
    usuario = type("UsuarioActual", (), {"id": 1})()
    with fabrica_sesiones() as sesion:
        creado = crear_favorito(pelicula, usuario, sesion)
        assert creado.pelicula_id == "603"

        with pytest.raises(HTTPException) as error:
            crear_favorito(pelicula, usuario, sesion)

    assert error.value.status_code == status.HTTP_409_CONFLICT
    assert error.value.detail == "Esta película ya está en tus favoritos."


def test_solicitudes_simultaneas_crean_un_solo_favorito(fabrica_sesiones, pelicula: FavoritoCrear) -> None:
    barrera = Barrier(2)
    usuario = type("UsuarioActual", (), {"id": 1})()

    def crear_en_paralelo() -> int:
        with fabrica_sesiones() as sesion:
            try:
                crear_favorito(pelicula, usuario, SesionSincronizada(sesion, barrera))
                return status.HTTP_201_CREATED
            except HTTPException as error:
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(lambda _: crear_en_paralelo(), range(2)))

    assert sorted(resultados) == [status.HTTP_201_CREATED, status.HTTP_409_CONFLICT]
    with fabrica_sesiones() as sesion:
        assert len(sesion.scalars(select(Favorito)).all()) == 1
