from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import DireccionPeaje


class RutaPeaje(Base):
    """
    DEPRECATED: Esta tabla se mantiene por compatibilidad.
    Usar TramoPeaje en su lugar.
    Los peajes ahora pertenecen a tramos, no a rutas.
    """
    __tablename__ = "ruta_peajes"

    id = Column(Integer, primary_key=True, index=True)

    ruta_id = Column(
        Integer,
        ForeignKey("rutas.id", ondelete="CASCADE"),
        nullable=False
    )

    peaje_id = Column(
        Integer,
        ForeignKey("peajes.id"),
        nullable=False
    )

    orden = Column(Integer, nullable=True)
    
    # DEPRECATED: Ya no se usa ida/regreso
    direccion = Column(
        Enum(DireccionPeaje, name="direccion_peaje"),
        default=DireccionPeaje.IDA,
        nullable=False
    )

    # Relaciones
    ruta = relationship(
        "Ruta",
        back_populates="peajes"
    )

    # Nota: peaje ya no tiene back_populates a rutas, usar foreign_keys
    peaje = relationship(
        "Peaje",
        foreign_keys=[peaje_id]
    )

