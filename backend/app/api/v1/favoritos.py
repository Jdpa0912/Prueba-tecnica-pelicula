"""CRUD de favoritos limitado al usuario autenticado."""

from enum import Enum

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError

from app.api.dependencias import SesionDB, UsuarioActual
from app.esquemas.favorito import FavoritoActualizar, FavoritoCrear, FavoritoRespuesta
from app.modelos.favorito import Favorito

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])


class OrdenFavoritos(str, Enum):
    """Campos disponibles para ordenar la colección de favoritos."""

    fecha = "fecha"
    year = "year"
    estrellas = "estrellas"


class DireccionOrden(str, Enum):
    """Direcciones disponibles para el orden de favoritos."""

    asc = "asc"
    desc = "desc"


def obtener_favorito_propietario(favorito_id: int, usuario_id: int, db: SesionDB) -> Favorito:
    """Recupera un favorito solo si pertenece al usuario de la solicitud."""

    favorito = db.scalar(select(Favorito).where(Favorito.id == favorito_id, Favorito.usuario_id == usuario_id))
    if favorito is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorito no encontrado.")
    return favorito


@router.get("", response_model=list[FavoritoRespuesta])
def listar_favoritos(
    usuario_actual: UsuarioActual,
    db: SesionDB,
    ordenar_por: OrdenFavoritos = Query(default=OrdenFavoritos.fecha),
    direccion: DireccionOrden = Query(default=DireccionOrden.desc),
) -> list[Favorito]:
    """Lista favoritos propios, con orden por fecha, año o calificación."""

    columnas_orden = {
        OrdenFavoritos.fecha: Favorito.date_added,
        OrdenFavoritos.year: Favorito.year,
        OrdenFavoritos.estrellas: Favorito.estrellas,
    }
    columna = columnas_orden[ordenar_por]
    orden = columna.asc() if direccion == DireccionOrden.asc else columna.desc()
    consulta: Select[tuple[Favorito]] = (
        select(Favorito)
        .where(Favorito.usuario_id == usuario_actual.id)
        .order_by(orden, Favorito.id.desc())
    )
    return list(db.scalars(consulta).all())


@router.post("", response_model=FavoritoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_favorito(datos: FavoritoCrear, usuario_actual: UsuarioActual, db: SesionDB) -> Favorito:
    """Guarda una película de resultados de búsqueda para el usuario actual."""

    favorito_existente = db.scalar(
        select(Favorito).where(
            Favorito.usuario_id == usuario_actual.id,
            Favorito.pelicula_id == datos.pelicula_id,
        )
    )
    if favorito_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta película ya está en tus favoritos.",
        )

    favorito = Favorito(usuario_id=usuario_actual.id, **datos.model_dump())
    db.add(favorito)
    try:
        db.commit()
    except IntegrityError:
        # La restricción única también cubre dos solicitudes que pasan la comprobación a la vez.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta película ya está en tus favoritos.",
        )
    db.refresh(favorito)
    return favorito


@router.put("/{favorito_id}", response_model=FavoritoRespuesta)
def actualizar_favorito(favorito_id: int, datos: FavoritoActualizar, usuario_actual: UsuarioActual, db: SesionDB) -> Favorito:
    """Actualiza la nota personal de un favorito del propietario."""

    favorito = obtener_favorito_propietario(favorito_id, usuario_actual.id, db)
    favorito.nota = datos.nota
    db.commit()
    db.refresh(favorito)
    return favorito


@router.delete("/{favorito_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_favorito(favorito_id: int, usuario_actual: UsuarioActual, db: SesionDB) -> Response:
    """Elimina un favorito solamente si pertenece al usuario autenticado."""

    favorito = obtener_favorito_propietario(favorito_id, usuario_actual.id, db)
    db.delete(favorito)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
