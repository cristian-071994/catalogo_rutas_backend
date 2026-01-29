from sqlalchemy import Column, Integer, String, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import EstadoGeneral


class Tramo(Base):
    __tablename__ = "tramos"
    
    __table_args__ = (
    UniqueConstraint("origen", "destino", name="uq_tramo_origen_destino"),
    )

    id = Column(Integer, primary_key=True, index=True)

    origen = Column(String(80), nullable=False)
    destino = Column(String(80), nullable=False)

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relación con rutas (vía tabla puente)
    rutas = relationship(
        "TramoRuta",
        back_populates="tramo"
    )
    
    detalles = relationship(
        "TramoDetalle",
        back_populates="tramo",
        cascade="all, delete-orphan"
    )
