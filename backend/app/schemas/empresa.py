"""
Schemas para Empresa
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class EmpresaBase(BaseModel):
    """Base para Empresa"""
    nombre: str = Field(..., min_length=2, max_length=100)
    nit: str = Field(..., min_length=5, max_length=20, description="NIT sin guiones (solo números)")
    contacto: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    
    @field_validator('nit')
    @classmethod
    def validar_nit(cls, v: str) -> str:
        """Valida y sanitiza el NIT (solo números)"""
        # Eliminar guiones, espacios y otros caracteres
        nit_limpio = ''.join(filter(str.isdigit, v))
        
        if not nit_limpio:
            raise ValueError('El NIT debe contener al menos un dígito')
        
        if len(nit_limpio) < 5:
            raise ValueError('El NIT debe tener al menos 5 dígitos')
        
        return nit_limpio


class EmpresaCreate(EmpresaBase):
    """Esquema para crear una empresa"""
    pass


class EmpresaUpdate(BaseModel):
    """Esquema para actualizar una empresa"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    nit: Optional[str] = Field(None, min_length=5, max_length=20)
    contacto: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[int] = None


class EmpresaResponse(EmpresaBase):
    """Esquema de respuesta de empresa"""
    id: int
    activo: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OnboardingRequest(BaseModel):
    """Esquema para onboarding inicial - Crear SUPER ADMIN (solo primera vez)"""
    # Datos del super administrador del sistema
    nombre: str = Field(..., min_length=2, max_length=100, description="Tu nombre completo")
    email: str = Field(..., description="Tu email (para login como super admin)")
    password: str = Field(..., min_length=6, max_length=100, description="Tu contraseña (mín. 6 caracteres)")
    
    class Config:
        from_attributes = True


class OnboardingResponse(BaseModel):
    """Respuesta del onboarding"""
    mensaje: str
    super_admin_email: str
    
    class Config:
        from_attributes = True


class CrearEmpresaConAdminRequest(BaseModel):
    """Esquema para que Super Admin cree empresa con su administrador"""
    # Datos de la empresa
    empresa_nombre: str = Field(..., min_length=2, max_length=100, description="Nombre de la empresa")
    empresa_nit: str = Field(..., min_length=5, max_length=20, description="NIT sin guiones (solo números)")
    empresa_contacto: Optional[str] = Field(None, max_length=100, description="Nombre del contacto")
    empresa_email: Optional[str] = Field(None, description="Email de contacto de la empresa")
    empresa_telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    
    # Datos del administrador de la empresa
    admin_nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del administrador")
    admin_email: str = Field(..., description="Email del administrador (para login)")
    admin_password: str = Field(..., min_length=6, max_length=100, description="Contraseña del administrador")
    
    @field_validator('empresa_nit')
    @classmethod
    def validar_nit(cls, v: str) -> str:
        """Valida y sanitiza el NIT (solo números)"""
        nit_limpio = ''.join(filter(str.isdigit, v))
        
        if not nit_limpio:
            raise ValueError('El NIT debe contener al menos un dígito')
        
        if len(nit_limpio) < 5:
            raise ValueError('El NIT debe tener al menos 5 dígitos')
        
        return nit_limpio
    
    class Config:
        from_attributes = True


class CrearEmpresaConAdminResponse(BaseModel):
    """Respuesta al crear empresa con admin"""
    mensaje: str
    empresa: EmpresaResponse
    admin_email: str
    
    class Config:
        from_attributes = True
