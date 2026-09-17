"""Dependencias compartidas por los endpoints protegidos."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.base_datos.conexion import obtener_db
from app.modelos.usuario import Usuario
from app.nucleo.configuracion import obtener_configuracion

esquema_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
CredencialesBearer = Annotated[str, Depends(esquema_bearer)]
SesionDB = Annotated[Session, Depends(obtener_db)]


def obtener_usuario_actual(token: CredencialesBearer, db: SesionDB) -> Usuario:
    """Valida el JWT y obtiene el usuario propietario de la solicitud."""

    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No fue posible validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        configuracion = obtener_configuracion()
        payload = jwt.decode(token, configuracion.jwt_secret, algorithms=[configuracion.jwt_algorithm])
        usuario_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise credenciales_invalidas

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise credenciales_invalidas
    return usuario


UsuarioActual = Annotated[Usuario, Depends(obtener_usuario_actual)]
