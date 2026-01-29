from pydantic import BaseModel, EmailStr
from typing import Optional


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
    """Esquema para respuesta de usuario"""
    id: int
    nombre: str
    email: str
    rol: str
    activo: int

    class Config:
        from_attributes = True
