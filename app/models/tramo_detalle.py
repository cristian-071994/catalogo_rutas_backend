from sqlalchemy import Column, Integer, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import TipoCarga, TipoTerreno, EstadoGeneral


class TramoDetalle(Base):
    __tablename__ = "tramo_detalle"

    id = Column(Integer, primary_key=True, index=True)

    tramo_id = Column(
        Integer,
        ForeignKey("tramos.id", ondelete="CASCADE"),
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
    
    kilometros = Column(
        Numeric(8, 2),
        nullable=False
    )

    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    tramo = relationship(
        "Tramo",
        back_populates="detalles"
    )

    __table_args__ = (
        UniqueConstraint(
            "tramo_id",
            "tipo_carga",
            "tipo_terreno",
            name="uq_tramo_tipo_carga_terreno"
        ),
    )
