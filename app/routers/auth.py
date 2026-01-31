"""
Router de autenticación
Maneja login y tokens JWT
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioResponse

router = APIRouter(
    prefix="",
    tags=["Autenticación"]
)


@router.post("/login", response_model=TokenResponse, summary="Iniciar Sesión")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión y obtiene un token JWT.

    POST /login
    Body:
    {
        "email": "admin@test.com",
        "password": "admin123"
    }

    Response:
    {
        "access_token": "eyJhbGc...",
        "token_type": "bearer",
        "usuario_nombre": "Administrador",
        "usuario_rol": "admin"
    }

    ⚠️ Guarda el token en localStorage/sessionStorage
    Úsalo en todas las peticiones posteriores:
    Headers:
    Authorization: Bearer {access_token}
    """

    # Autenticar usuario
    usuario = authenticate_user(db, credentials.email, credentials.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token JWT
    access_token = create_access_token(
        data={"sub": usuario.email, "rol": usuario.rol.value}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol.value,
    )


@router.get("/me", response_model=UsuarioResponse, summary="Obtener Usuario Actual")
def get_me(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene la información del usuario autenticado actualmente.

    GET /me
    Headers:
    Authorization: Bearer {access_token}

    Response: Datos del usuario actual
    """
    return UsuarioResponse(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        rol=current_user.rol.value,
        activo=current_user.activo,
    )
