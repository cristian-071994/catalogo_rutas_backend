"""
Modelo TramoPeaje - Relación many-to-many entre tramos y peajes
Reemplaza el modelo RutaPeaje
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base


class TramoPeaje(Base):
    __tablename__ = "tramo_peajes"
    
    # Constraint para evitar duplicados: un peaje no se puede repetir en el mismo tramo
    __table_args__ = (
        UniqueConstraint("tramo_id", "peaje_id", name="uq_tramo_peaje"),
    )

    id = Column(Integer, primary_key=True, index=True)

    tramo_id = Column(
        Integer,
        ForeignKey("tramos.id", ondelete="CASCADE"),
        nullable=False
    )

    peaje_id = Column(
        Integer,
        ForeignKey("peajes.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relaciones
    tramo = relationship("Tramo", back_populates="peajes")
    peaje = relationship("Peaje", back_populates="tramos")
