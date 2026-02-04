"""
Modelo de Empresa
Representa las empresas de transporte que usan el sistema (multi-tenancy)
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Empresa(Base):
    """
    Empresas de transporte que usan el sistema.
    Cada empresa tiene sus propios usuarios, clientes, rutas, vehículos, etc.
    Ejemplos: Cointra, Geotab, Satena
    """
    
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Datos de la empresa
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    nit = Column(String(20), nullable=False, unique=True, index=True)
    contacto = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Estado
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    
    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="empresa")
    clientes = relationship("Cliente", back_populates="empresa")
    vehiculos = relationship("Vehiculo", back_populates="empresa")
    rutas = relationship("Ruta", back_populates="empresa")
    tramos = relationship("Tramo", back_populates="empresa")

    def __repr__(self):
        return f"<Empresa(id={self.id}, nombre={self.nombre}, nit={self.nit})>"
