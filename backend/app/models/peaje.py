from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base
from app.models.enums import EstadoGeneral


class Peaje(Base):
    __tablename__ = "peajes"

    id = Column(Integer, primary_key=True, index=True)

    # Campo legado (mantener por compatibilidad)
    nombre = Column(String(100), nullable=False)  # Se mantiene sincronizado con nombre_peaje
    
    # Datos de API oficial
    nombre_peaje = Column(String(200), nullable=False, index=True)
    id_peaje_api = Column(String(20))
    categoria_tarifa = Column(String(10))
    fecha_ultima_tarifa = Column(DateTime)
    
    # Ubicación
    ubicacion = Column(String(200))  # Ej: "Mediacanoa - Ansermanuevo"
    sector = Column(String(200))     # Ej: "Mediacanoa - Roldanillo"
    
    # Coordenadas geográficas
    longitud = Column(Numeric(12, 8))
    latitud = Column(Numeric(12, 8))
    
    # Costo para Categoría V (camiones)
    costo = Column(Numeric(8, 2), nullable=False)
    
    # Códigos oficiales
    codigo_peaje = Column(String(20))
    codigo_tramo = Column(String(20))
    
    # Metadata de sincronización
    fuente = Column(String(50), default="API_GOBIERNO")  # "API_GOBIERNO" o "MANUAL"
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow)
    
    # Estado
    estado = Column(
        Enum(EstadoGeneral, name="estado_general"),
        default=EstadoGeneral.activo,
        nullable=False
    )

    # Relaciones
    tramos = relationship(
        "TramoPeaje",
        back_populates="peaje",
        cascade="all, delete-orphan"
    )
