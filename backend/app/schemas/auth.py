from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, Any
from datetime import datetime


class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    refresh_token: str  # Nuevo: token de renovación
    token_type: str = "bearer"
    usuario_nombre: str
    usuario_rol: str
    empresa_nombre: str  # Agregamos nombre de empresa
    usuario_permisos: list[str] = []


class RefreshTokenRequest(BaseModel):
    """Esquema para refrescar token"""
    refresh_token: str


class RegistroRequest(BaseModel):
    """Esquema para solicitud de registro público (sin autenticación)"""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña (mín. 6 caracteres)")
    empresa_nit: str = Field(..., min_length=5, max_length=20, description="NIT de la empresa sin guiones (debe existir)")
    
    @field_validator('empresa_nit')
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
    
    class Config:
        from_attributes = True


class RegistroResponse(BaseModel):
    """Respuesta al registrarse"""
    mensaje: str
    email: str
    empresa: str
    
    class Config:
        from_attributes = True


class UsuarioResponse(BaseModel):
    """Esquema para respuesta de usuario (lectura)"""
    id: int
    nombre: str
    email: str
    empresa_id: Optional[int] = None  # None para super_admin
    empresa_nombre: Optional[str] = None
    rol: Optional[str] = None
    activo: int
    aprobado: int
    permisos: Optional[list[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    @classmethod
    def extract_relationships(cls, data: Any) -> Any:
        """Extrae información de las relaciones empresa y rol"""
        if isinstance(data, dict):
            return data
        
        # Si es un objeto SQLAlchemy
        result = {
            'id': data.id,
            'nombre': data.nombre,
            'email': data.email,
            'empresa_id': data.empresa_id,
            'empresa_nombre': data.empresa.nombre if data.empresa else None,
            'rol': data.rol.nombre if data.rol else None,
            'activo': data.activo,
            'aprobado': data.aprobado,
            'created_at': data.created_at,
            'updated_at': data.updated_at
        }
        return result

    class Config:
        from_attributes = True


class AprobarUsuarioRequest(BaseModel):
    """Esquema para aprobar un usuario pendiente"""
    rol_nombre: str = Field(..., description="Rol a asignar (admin, supervisor, gestor_rutas, etc.)")
    
    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    """Esquema para crear un nuevo usuario"""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña (mín. 6 caracteres)")
    rol: str = Field(default="consultor", description="Rol del usuario (admin, supervisor, gestor_rutas, gestor_peajes, gestor_clientes, consultor)")
    rol_id: Optional[int] = Field(None, description="ID del rol (alternativo al nombre)")
    empresa_id: Optional[int] = Field(None, description="ID de la empresa (requerido para super_admin)")

    class Config:
        from_attributes = True


class UsuarioUpdate(BaseModel):
    """Esquema para actualizar un usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None)
    rol: Optional[str] = Field(None)
    activo: Optional[int] = Field(None, ge=0, le=1)
    password: Optional[str] = Field(None, min_length=6, max_length=100)

    class Config:
        from_attributes = True


class CambiarPasswordRequest(BaseModel):
    """Esquema para cambiar contraseña"""
    password_actual: str = Field(..., description="Contraseña actual")
    password_nueva: str = Field(..., min_length=6, max_length=100, description="Nueva contraseña (mín. 6 caracteres)")
    password_confirmar: str = Field(..., description="Confirmar nueva contraseña")

    class Config:
        from_attributes = True

class UsuariosListaResponse(BaseModel):
    """Esquema para respuesta paginada de usuarios"""
    items: list[UsuarioResponse] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios (sin paginación)")
    skip: int = Field(..., description="Registros saltados")
    limit: int = Field(..., description="Límite de registros por página")
    total_pages: int = Field(..., description="Total de páginas")
    current_page: int = Field(..., description="Página actual (comenzando en 1)")
    has_next: bool = Field(..., description="¿Hay página siguiente?")
    has_prev: bool = Field(..., description="¿Hay página anterior?")

    class Config:
        from_attributes = True