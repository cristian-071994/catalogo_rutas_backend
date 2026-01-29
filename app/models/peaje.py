from sqlalchemy import Column, Integer, String, Numeric, Enum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import EstadoGeneral


class Peaje(Base):
    __tablename__ = "peajes"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    costo = Column(
        Numeric(8, 2),
        nullable=False
    )

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    rutas = relationship(
        "RutaPeaje",
        back_populates="peaje",
        cascade="all, delete-orphan"
    )
