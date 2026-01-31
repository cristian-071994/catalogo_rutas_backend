"""
Módulo de autenticación y autorización con JWT
Maneja tokens, validación de permisos y decoradores
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.usuario import Usuario
from app.models.rol import RolEnum, PERMISOS_POR_ROL

# ============================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================

# Secreto para firmar JWTs (EN PRODUCCIÓN usar variable de entorno)
SECRET_KEY = "tu-clave-secreta-super-segura-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de hashing para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema HTTP Bearer - Swagger UI mostrará un campo simple para el token
security = HTTPBearer(
    description="Ingresa el token JWT obtenido del endpoint /login"
)


# ============================================
# FUNCIONES DE HASHING DE CONTRASEÑAS
# ============================================

def hash_password(password: str) -> str:
    """Hash una contraseña usando bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# FUNCIONES DE JWT
# ============================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT con los datos proporcionados.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": email})
        expires_delta: Tiempo de expiración (default: 30 minutos)
    
    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a validar
    
    Returns:
        Datos contenidos en el token
    
    Raises:
        HTTPException: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================
# DEPENDENCIAS PARA ENDPOINTS
# ============================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario actual desde el token JWT.
    
    Se usa como dependencia en endpoints que requieren autenticación.
    
    Raises:
        HTTPException 401: Si el token es inválido
        HTTPException 404: Si el usuario no existe
    """
    token = credentials.credentials
    payload = decode_token(token)
    email: str = payload.get("sub")
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    
    return usuario


def require_role(*roles: RolEnum):
    """
    Decorador para requerir un rol específico en un endpoint.
    
    Uso:
        @router.get("/admin-only")
        def endpoint_admin_only(
            current_user: Usuario = Depends(require_role(RolEnum.admin))
        ):
            ...
    
    Args:
        *roles: Uno o más roles permitidos
    
    Returns:
        Función que valida el rol del usuario
    """
    async def check_role(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {', '.join([r.value for r in roles])}",
            )
        return current_user
    
    return check_role


def require_permission(permission: str):
    """
    Decorador para requerir un permiso específico.
    
    Valida contra PERMISOS_POR_ROL.
    
    Uso:
        @router.post("/crear")
        def crear(
            current_user: Usuario = Depends(require_permission("crear"))
        ):
            ...
    
    Args:
        permission: Nombre del permiso (ej: "crear", "eliminar")
    
    Returns:
        Función que valida el permiso
    """
    async def check_permission(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        permisos = PERMISOS_POR_ROL.get(current_user.rol, {})
        
        if not permisos.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para: {permission}",
            )
        return current_user
    
    return check_permission


# ============================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional[Usuario]:
    """
    Autentica un usuario verificando email y contraseña.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano
    
    Returns:
        Usuario si las credenciales son válidas, None si no
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return None
    
    if not verify_password(password, usuario.password_hash):
        return None
    
    return usuario


def create_test_users(db: Session):
    """
    Crea usuarios de prueba en la base de datos.
    
    Solo crea si no existen.
    
    Usuarios creados:
    - admin@test.com / admin123 (Rol: admin)
    - supervisor@test.com / supervisor123 (Rol: supervisor)
    - gestor_rutas@test.com / gestor123 (Rol: gestor_rutas)
    - gestor_peajes@test.com / gestor123 (Rol: gestor_peajes)
    - gestor_clientes@test.com / gestor123 (Rol: gestor_clientes)
    - consultor@test.com / consultor123 (Rol: consultor)
    """
    usuarios_predefinidos = [
        {
            "nombre": "Administrador",
            "email": "admin@test.com",
            "password": "admin123",
            "rol": RolEnum.admin,
        },
        {
            "nombre": "Supervisor General",
            "email": "supervisor@test.com",
            "password": "supervisor123",
            "rol": RolEnum.supervisor,
        },
        {
            "nombre": "Gestor de Rutas",
            "email": "gestor_rutas@test.com",
            "password": "gestor123",
            "rol": RolEnum.gestor_rutas,
        },
        {
            "nombre": "Gestor de Peajes",
            "email": "gestor_peajes@test.com",
            "password": "gestor123",
            "rol": RolEnum.gestor_peajes,
        },
        {
            "nombre": "Gestor de Clientes",
            "email": "gestor_clientes@test.com",
            "password": "gestor123",
            "rol": RolEnum.gestor_clientes,
        },
        {
            "nombre": "Consultor (Lectura)",
            "email": "consultor@test.com",
            "password": "consultor123",
            "rol": RolEnum.consultor,
        },
    ]
    
    for datos in usuarios_predefinidos:
        # Verificar si ya existe
        existente = db.query(Usuario).filter(
            Usuario.email == datos["email"]
        ).first()
        
        if not existente:
            usuario = Usuario(
                nombre=datos["nombre"],
                email=datos["email"],
                password_hash=hash_password(datos["password"]),
                rol=datos["rol"],
                activo=1,
            )
            db.add(usuario)
    
    db.commit()
