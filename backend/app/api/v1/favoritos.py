"""CRUD de favoritos limitado al usuario autenticado."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.dependencias import SesionDB, UsuarioActual
from app.esquemas.favorito import FavoritoActualizar, FavoritoCrear, FavoritoRespuesta
from app.modelos.favorito import Favorito

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])

DETALLE_FAVORITO_DUPLICADO = "Esta película ya está en tus favoritos."


def obtener_favorito_propietario(favorito_id: int, usuario_id: int, db: SesionDB) -> Favorito:
    """Recupera un favorito solo si pertenece al usuario de la solicitud."""

    favorito = db.scalar(select(Favorito).where(Favorito.id == favorito_id, Favorito.usuario_id == usuario_id))
    if favorito is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorito no encontrado.")
    return favorito


@router.get("", response_model=list[FavoritoRespuesta])
def listar_favoritos(usuario_actual: UsuarioActual, db: SesionDB) -> list[Favorito]:
    """Lista únicamente los favoritos del usuario autenticado."""

    consulta = select(Favorito).where(Favorito.usuario_id == usuario_actual.id).order_by(Favorito.date_added.desc())
    return list(db.scalars(consulta).all())


@router.post("", response_model=FavoritoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_favorito(datos: FavoritoCrear, usuario_actual: UsuarioActual, db: SesionDB) -> Favorito:
    """Guarda una película de resultados de búsqueda para el usuario actual."""

    favorito_existente = db.scalar(
        select(Favorito.id).where(
            Favorito.usuario_id == usuario_actual.id,
            Favorito.pelicula_id == datos.pelicula_id,
        )
    )
    if favorito_existente is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DETALLE_FAVORITO_DUPLICADO)

    favorito = Favorito(usuario_id=usuario_actual.id, **datos.model_dump())
    db.add(favorito)
    try:
        db.commit()
    except IntegrityError:
        # La restricción única también cubre solicitudes simultáneas.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DETALLE_FAVORITO_DUPLICADO)
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
