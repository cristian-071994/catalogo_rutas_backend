from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.models.rol import RolEnum


class Usuario(Base):
    """Modelo de usuario para autenticación y autorización"""
    
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    # Datos básicos
    nombre = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    
    # Contraseña hasheada (NUNCA almacenar en texto plano)
    password_hash = Column(String(255), nullable=False)
    
    # Rol del usuario
    rol = Column(
        Enum(RolEnum, name="rol_enum"),
        default=RolEnum.consultor,
        nullable=False
    )
    
    # Estado
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    
    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, rol={self.rol})>"
