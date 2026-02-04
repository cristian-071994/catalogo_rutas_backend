from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.models.enums import EstadoGeneral


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenancy: Empresa a la que pertenece este cliente
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False, index=True)

    nombre = Column(
        String(100),
        nullable=False,
        index=True
    )

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    # Relaciones
    empresa = relationship("Empresa", back_populates="clientes")
    rutas = relationship(
        "Ruta",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )
