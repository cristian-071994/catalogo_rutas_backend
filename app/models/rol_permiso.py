"""
Modelos de Rol y Permiso
Sistema dinámico de roles y permisos en la BD
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


# Tabla relacional: Rol-Permiso (muchos a muchos)
rol_permiso = Table(
    'rol_permiso',
    Base.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id'), primary_key=True)
)


class Rol(Base):
    """Modelo de Rol del Sistema"""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre único del rol (admin, supervisor, gestor_rutas, etc)
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    
    # Descripción para documentación
    descripcion = Column(Text, nullable=True)
    
    # Roles del sistema (no se pueden eliminar)
    es_sistema = Column(Integer, default=0)  # 1 = sistema, 0 = personalizado
    
    # Estado
    activo = Column(Integer, default=1)
    
    # Relación muchos a muchos con Permiso
    permisos = relationship(
        "Permiso",
        secondary=rol_permiso,
        back_populates="roles",
        cascade="all, delete"
    )
    
    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre={self.nombre})>"


class Permiso(Base):
    """Modelo de Permiso del Sistema"""
    
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre único del permiso (crear_usuarios, eliminar_rutas, etc)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    
    # Descripción detallada
    descripcion = Column(Text, nullable=True)
    
    # Categoría del permiso (usuarios, rutas, clientes, etc)
    categoria = Column(String(50), nullable=False, index=True)
    
    # Permisos del sistema (no se pueden eliminar)
    es_sistema = Column(Integer, default=0)  # 1 = sistema, 0 = personalizado
    
    # Estado
    activo = Column(Integer, default=1)
    
    # Relación muchos a muchos con Rol
    roles = relationship(
        "Rol",
        secondary=rol_permiso,
        back_populates="permisos"
    )
    
    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Permiso(id={self.id}, nombre={self.nombre})>"
