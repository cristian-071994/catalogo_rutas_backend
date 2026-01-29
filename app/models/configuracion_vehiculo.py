from sqlalchemy import Column, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import EstadoGeneral


class ConfiguracionVehiculo(Base):
    __tablename__ = "configuracion_vehiculo"
    
    __table_args__ = (
    UniqueConstraint("marca_id", "modelo", name="uq_marca_modelo"),
    )


    id = Column(Integer, primary_key=True, index=True)

    marca_id = Column(
        Integer,
        ForeignKey("marcas_vehiculos.id", ondelete="RESTRICT"),
        nullable=False
    )

    modelo = Column(Integer, nullable=False)  # año: 2010, 2020, etc.

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    marca = relationship(
        "MarcaVehiculo",
        back_populates="configuraciones"
    )

    vehiculos = relationship(
        "Vehiculo",
        back_populates="configuracion"
    )

    rendimientos = relationship(
        "RendimientoConfiguracion",
        back_populates="configuracion",
        cascade="all, delete-orphan"
    )
