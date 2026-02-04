from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import EstadoGeneral


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenancy: Empresa a la que pertenece este vehículo
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False, index=True)

    placa = Column(
        String(6),
        nullable=False,
        index=True
    )

    configuracion_id = Column(
        Integer,
        ForeignKey("configuracion_vehiculo.id", ondelete="RESTRICT"),
        nullable=False
    )

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    empresa = relationship("Empresa", back_populates="vehiculos")
    configuracion = relationship(
        "ConfiguracionVehiculo",
        back_populates="vehiculos"
    )
