from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base



class TramoRuta(Base):
    __tablename__ = "tramos_ruta"

    id = Column(Integer, primary_key=True, index=True)

    ruta_id = Column(
        Integer,
        ForeignKey("rutas.id", ondelete="CASCADE"),
        nullable=False
    )

    tramo_id = Column(
        Integer,
        ForeignKey("tramos.id", ondelete="RESTRICT"),
        nullable=False
    )

    orden = Column(Integer, nullable=False)
    
    # relacion ORM
    ruta = relationship(
        "Ruta",
        back_populates="tramos"
    )

    tramo = relationship(
        "Tramo",
        back_populates="rutas"
    )
    
    __table_args__ = (
        # Un tramo no puede repetirse en la misma ruta
        UniqueConstraint(
            "ruta_id",
            "tramo_id",
            name="uq_ruta_tramo"
        ),
        # El orden no puede repetirse dentro de una ruta
        UniqueConstraint(
            "ruta_id",
            "orden",
            name="uq_ruta_orden"
        ),
    )
