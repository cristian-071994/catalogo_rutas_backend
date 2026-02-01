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
    token_type: str = "bearer"
    usuario_nombre: str
    usuario_rol: str


class UsuarioResponse(BaseModel):
    """Esquema para respuesta de usuario (lectura)"""
    id: int
    nombre: str
    email: str
    rol: str
    activo: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('rol', mode='before')
    @classmethod
    def extract_rol_nombre(cls, v: Any) -> str:
        """Extrae el nombre del rol del objeto Rol"""
        if hasattr(v, 'nombre'):
            return v.nombre
        return str(v)

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    """Esquema para crear un nuevo usuario"""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña (mín. 6 caracteres)")
    rol: str = Field(default="consultor", description="Rol del usuario (admin, supervisor, gestor_rutas, gestor_peajes, gestor_clientes, consultor)")

    class Config:
        from_attributes = True


class UsuarioUpdate(BaseModel):
    """Esquema para actualizar un usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None)
    rol: Optional[str] = Field(None)
    activo: Optional[int] = Field(None, ge=0, le=1)

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