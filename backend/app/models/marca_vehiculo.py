from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import EstadoGeneral


class MarcaVehiculo(Base):
    __tablename__ = "marcas_vehiculos"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(
        String(60),
        nullable=False,
        unique=True,
        index=True
    )

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    configuraciones = relationship(
        "ConfiguracionVehiculo",
        back_populates="marca",
        cascade="all, delete-orphan"
    )
