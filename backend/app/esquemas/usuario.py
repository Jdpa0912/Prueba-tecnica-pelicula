"""Esquemas Pydantic relacionados con usuarios y autenticación."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UsuarioCrear(BaseModel):
    """Datos requeridos para registrar una cuenta."""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=72)


class UsuarioLogin(BaseModel):
    """Credenciales enviadas durante el inicio de sesión."""

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=72)


class UsuarioRespuesta(BaseModel):
    """Representación pública de un usuario, sin exponer su hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class TokenRespuesta(BaseModel):
    """Respuesta estándar de autenticación basada en Bearer JWT."""

    access_token: str
    token_type: str = "bearer"
