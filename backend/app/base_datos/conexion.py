"""Configuración de SQLAlchemy y ciclo de vida de las sesiones de base de datos."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.nucleo.configuracion import obtener_configuracion


class Base(DeclarativeBase):
    """Clase base que comparten todos los modelos ORM."""


configuracion = obtener_configuracion()
engine = create_engine(str(configuracion.database_url), pool_pre_ping=True)
SesionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def obtener_db() -> Generator[Session, None, None]:
    """Abre una sesión por solicitud y garantiza su cierre posterior."""

    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()
