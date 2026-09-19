"""Configuración centralizada de la aplicación."""

from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    """Valores de configuración cargados desde variables de entorno o un archivo .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: PostgresDsn = Field(validation_alias="DATABASE_URL")
    jwt_secret: str = Field(min_length=32, validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    tmdb_api_token: str | None = Field(default=None, validation_alias="TMDB_API_TOKEN")
    tmdb_language: str = Field(default="es-ES", validation_alias="TMDB_LANGUAGE")


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve una única instancia de configuración durante la ejecución."""

    return Configuracion()
