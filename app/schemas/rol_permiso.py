"""
Esquemas Pydantic para Roles y Permisos
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# ESQUEMAS DE PERMISO
# ============================================

class PermisoCreate(BaseModel):
    """Esquema para crear un nuevo permiso"""
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre único del permiso")
    descripcion: Optional[str] = Field(None, max_length=500)
    categoria: str = Field(..., min_length=3, max_length=50, description="Categoría del permiso")
    
    class Config:
        from_attributes = True


class PermisoUpdate(BaseModel):
    """Esquema para actualizar un permiso"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    categoria: Optional[str] = Field(None, min_length=3, max_length=50)
    activo: Optional[int] = Field(None, ge=0, le=1)
    
    class Config:
        from_attributes = True


class PermisoResponse(BaseModel):
    """Esquema para respuesta de permiso"""
    id: int
    nombre: str
    descripcion: Optional[str]
    categoria: str
    es_sistema: int
    activo: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMAS DE ROL
# ============================================

class RolCreate(BaseModel):
    """Esquema para crear un nuevo rol"""
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre único del rol")
    descripcion: Optional[str] = Field(None, max_length=500)
    permisos: Optional[List[int]] = Field(None, description="IDs de permisos a asignar")
    
    class Config:
        from_attributes = True


class RolUpdate(BaseModel):
    """Esquema para actualizar un rol"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    permisos: Optional[List[int]] = Field(None, description="IDs de permisos a asignar")
    activo: Optional[int] = Field(None, ge=0, le=1)
    
    class Config:
        from_attributes = True


class RolResponse(BaseModel):
    """Esquema para respuesta de rol (sin permisos)"""
    id: int
    nombre: str
    descripcion: Optional[str]
    es_sistema: int
    activo: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RolDetallado(BaseModel):
    """Esquema para respuesta de rol con todos los detalles (incluye permisos)"""
    id: int
    nombre: str
    descripcion: Optional[str]
    es_sistema: int
    activo: int
    permisos: List[PermisoResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AsignarPermisosRequest(BaseModel):
    """Esquema para asignar permisos a un rol"""
    permiso_ids: List[int] = Field(..., description="Lista de IDs de permisos")
    
    class Config:
        from_attributes = True
