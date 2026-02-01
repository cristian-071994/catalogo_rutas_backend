from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from app.database.base import Base


class ConfiguracionGeneral(Base):
    """
    Tabla para almacenar configuraciones globales del sistema.
    
    Por ahora: precio del combustible
    Futuro: impuestos, márgenes, etc
    """
    __tablename__ = "configuracion_general"

    id = Column(Integer, primary_key=True, index=True)

    # La "clave" de la configuración (ej: "precio_galon")
    clave = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    # El valor (ej: "9500")
    valor = Column(
        String(255),
        nullable=False
    )

    # Descripción amigable
    descripcion = Column(
        String(255),
        nullable=True
    )

    # Cuándo se creó/actualizó
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<ConfiguracionGeneral(clave={self.clave}, valor={self.valor})>"
