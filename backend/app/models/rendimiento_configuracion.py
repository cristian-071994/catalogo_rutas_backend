from sqlalchemy import Column, Integer, Numeric, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import (
    EstadoGeneral,
    TipoCarga,
    TipoTerreno
)


class RendimientoConfiguracion(Base):
    __tablename__ = "rendimiento_configuracion"
    
    __table_args__ = (
        UniqueConstraint(
            "configuracion_id",
            "tipo_carga",
            "tipo_terreno",
            name="uq_rendimiento_configuracion"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    configuracion_id = Column(
        Integer,
        ForeignKey("configuracion_vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )

    tipo_carga = Column(
        Enum(TipoCarga, name="tipo_carga"),
        nullable=False
    )

    tipo_terreno = Column(
        Enum(TipoTerreno, name="tipo_terreno"),
        nullable=False
    )

    rendimiento_km_galon = Column(
        Numeric(5, 2),
        nullable=False
    )

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    configuracion = relationship(
        "ConfiguracionVehiculo",
        back_populates="rendimientos"
    )
