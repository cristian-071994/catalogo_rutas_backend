from sqlalchemy import Column, Integer, String, Enum, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import EstadoGeneral


class Tramo(Base):
    __tablename__ = "tramos"
    
    __table_args__ = (
    UniqueConstraint("empresa_id", "origen", "destino", name="uq_tramo_empresa_origen_destino"),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenancy: Empresa a la que pertenece este tramo
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False, index=True)

    origen = Column(String(80), nullable=False)
    destino = Column(String(80), nullable=False)

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="tramos")

    # Relación con rutas (vía tabla puente)
    rutas = relationship(
        "TramoRuta",
        back_populates="tramo"
    )
    
    # Relación con peajes (vía tabla puente)
    peajes = relationship(
        "TramoPeaje",
        back_populates="tramo",
        cascade="all, delete-orphan"
    )
    
    detalles = relationship(
        "TramoDetalle",
        back_populates="tramo",
        cascade="all, delete-orphan"
    )

    @property
    def peajes_list(self):
        """Devuelve la lista de objetos Peaje asociados a este tramo"""
        return [tp.peaje for tp in self.peajes if tp.peaje]
