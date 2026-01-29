from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.models.enums import EstadoGeneral  # luego lo revisamos si no existe


class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    nombre = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=True)

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relaciones
    cliente = relationship("Cliente", back_populates="rutas")

    tramos = relationship(
        "TramoRuta",
        back_populates="ruta",
        cascade="all, delete-orphan",
        order_by="TramoRuta.orden"
    )

    peajes = relationship(
        "RutaPeaje",
        back_populates="ruta",
        cascade="all, delete-orphan"
    )
