from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Usuario(Base):
    """Modelo de usuario para autenticación y autorización"""
    
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenancy: Empresa a la que pertenece (NULL para super_admin)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=True, index=True)
    
    # Datos básicos
    nombre = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    
    # Contraseña hasheada (NUNCA almacenar en texto plano)
    password_hash = Column(String(255), nullable=False)
    
    # Rol del usuario (FK a tabla roles - sistema profesional)
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=True)  # Nullable hasta aprobación
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="usuarios", lazy="joined")
    rol = relationship("Rol", foreign_keys=[rol_id], lazy="joined")
    
    # Estado y aprobación
    activo = Column(Integer, default=0)  # 0 = pendiente aprobación, 1 = activo
    aprobado = Column(Integer, default=0)  # 0 = pendiente, 1 = aprobado
    aprobado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=True)  # Admin que aprobó
    aprobado_en = Column(DateTime, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, rol={self.rol.nombre if self.rol else 'N/A'})>"

