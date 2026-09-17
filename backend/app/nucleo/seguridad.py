"""Utilidades de contraseñas y tokens JWT."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.nucleo.configuracion import obtener_configuracion

contexto_contrasenas = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_contrasena(contrasena: str) -> str:
    """Genera un hash bcrypt de una contraseña que nunca debe persistirse en texto plano."""

    return contexto_contrasenas.hash(contrasena)


def verificar_contrasena(contrasena_plana: str, password_hash: str) -> bool:
    """Comprueba una contraseña contra su hash almacenado."""

    return contexto_contrasenas.verify(contrasena_plana, password_hash)


def crear_token_acceso(datos: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Crea un JWT de acceso que contiene la identidad del usuario en `sub`."""

    configuracion = obtener_configuracion()
    expiracion = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=configuracion.access_token_expire_minutes)
    )
    payload = datos.copy()
    payload.update({"exp": expiracion})
    return jwt.encode(payload, configuracion.jwt_secret, algorithm=configuracion.jwt_algorithm)
