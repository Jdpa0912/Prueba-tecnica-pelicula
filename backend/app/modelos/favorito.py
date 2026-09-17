"""Modelo ORM para la tabla `favoritas`."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_datos.conexion import Base

if TYPE_CHECKING:
    from app.modelos.usuario import Usuario


class Favorito(Base):
    """Película guardada por un usuario autenticado."""

    __tablename__ = "favoritas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pelicula_id: Mapped[str] = mapped_column(String(50), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[str | None] = mapped_column(String(10), nullable=True)
    poster: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nota: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="favoritas")
