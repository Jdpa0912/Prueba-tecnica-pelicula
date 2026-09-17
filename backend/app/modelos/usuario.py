"""Modelo ORM para la tabla `usuarios`."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_datos.conexion import Base

if TYPE_CHECKING:
    from app.modelos.favorito import Favorito


class Usuario(Base):
    """Usuario que puede crear y administrar sus películas favoritas."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    favoritas: Mapped[list["Favorito"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
