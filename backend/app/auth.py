"""
Módulo de autenticación y autorización con JWT
Maneja tokens, validación de permisos y decoradores
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database.session import get_db
from app.models.usuario import Usuario

# Cargar variables de entorno desde .env
load_dotenv()

# ============================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================

# Configuración desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "clave-por-defecto-solo-desarrollo")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Access token corto (30 minutos) - para operaciones
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
# Refresh token (1 día) - para renovar automáticamente
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "1"))

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
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un refresh token JWT con expiración larga.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": email})
        expires_delta: Tiempo de expiración (default: 1 día)
    
    Returns:
        Refresh token JWT firmado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
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
    
    # Cargar usuario con sus relaciones (rol y empresa)
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol),
        joinedload(Usuario.empresa)
    ).filter(Usuario.email == email).first()
    
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


def require_role(*roles: str):
    """
    Decorador para requerir un rol específico en un endpoint.
    
    Uso:
        @router.get("/admin-only")
        def endpoint_admin_only(
            current_user: Usuario = Depends(require_role("admin"))
        ):
            ...
    
    Args:
        *roles: Uno o más nombres de roles permitidos (strings)
    
    Returns:
        Función que valida el rol del usuario
    """
    async def check_role(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if not current_user.rol:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin rol asignado"
            )
        
        # Super admin tiene acceso a todo
        if current_user.rol.nombre == "super_admin":
            return current_user
        
        if current_user.rol.nombre not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {', '.join(roles)}",
            )
        return current_user
    
    return check_role


def require_permission(permission: str):
    """
    Decorador para requerir un permiso específico.
    
    Valida dinámicamente contra la tabla de permisos en la BD.
    
    Uso:
        @router.post("/crear")
        def crear(
            current_user: Usuario = Depends(require_permission("crear_usuario"))
        ):
            ...
    
    Args:
        permission: Nombre del permiso (ej: "crear_usuario", "eliminar_usuario")
    
    Returns:
        Función que valida el permiso consultando la BD
    """
    async def check_permission(
        current_user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Usuario:
        # Validar que el usuario tiene un rol
        if not current_user.rol:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin rol asignado"
            )
        
        # Super admin tiene todos los permisos
        if current_user.rol.nombre == "super_admin":
            return current_user
        
        # Buscar si el rol tiene el permiso
        tiene_permiso = False
        
        for permiso in current_user.rol.permisos:
            if permiso.nombre == permission and permiso.activo == 1:
                tiene_permiso = True
                break
        
        if not tiene_permiso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para: {permission}",
            )
        return current_user
    
    return check_permission


# ============================================
# FUNCIONES HELPER PARA PERMISOS
# ============================================

def user_has_permission(usuario: Usuario, permission: str) -> bool:
    """
    Verifica si un usuario tiene un permiso específico.
    
    Útil para lógica condicional dentro de endpoints.
    
    Args:
        usuario: Objeto Usuario
        permission: Nombre del permiso
    
    Returns:
        True si el usuario tiene el permiso, False si no
    """
    if not usuario.rol:
        return False
    
    for permiso in usuario.rol.permisos:
        if permiso.nombre == permission and permiso.activo == 1:
            return True
    
    return False


def get_user_permissions(usuario: Usuario) -> list[str]:
    """
    Obtiene la lista de permisos de un usuario.
    
    Args:
        usuario: Objeto Usuario
    
    Returns:
        Lista de nombres de permisos activos del usuario
    """
    if not usuario.rol:
        return []
    
    return [p.nombre for p in usuario.rol.permisos if p.activo == 1]


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
    Crea empresas y usuarios de prueba en la base de datos.
    
    Solo crea si no existen.
    
    Empresas creadas:
    - Cointra (NIT: 900123456-7)
    - Geotab (NIT: 900234567-8)
    - Satena (NIT: 900345678-9)
    
    Usuarios creados:
    - admin@cointra.com / admin123 (Admin Cointra)
    - admin@geotab.com / admin123 (Admin Geotab)
    - admin@satena.com / admin123 (Admin Satena)
    - consultor@cointra.com / consultor123 (Consultor Cointra)
    """
    from app.models.rol_permiso import Rol
    from app.models.empresa import Empresa
    from sqlalchemy import func
    
    # 1. Crear empresas de prueba
    empresas_predefinidas = [
        {
            "nombre": "Cointra",
            "nit": "9001234567",  # Sin guiones
            "contacto": "Gerente General",
            "email": "contacto@cointra.com",
            "telefono": "3001234567",
        },
        {
            "nombre": "Geotab Colombia",
            "nit": "9002345678",  # Sin guiones
            "contacto": "Director Operaciones",
            "email": "contacto@geotab.com",
            "telefono": "3002345678",
        },
        {
            "nombre": "Satena",
            "nit": "9003456789",  # Sin guiones
            "contacto": "Jefe Logística",
            "email": "contacto@satena.com",
            "telefono": "3003456789",
        },
    ]
    
    empresas_creadas = {}
    
    for datos in empresas_predefinidas:
        existente = db.query(Empresa).filter(Empresa.nit == datos["nit"]).first()
        
        if not existente:
            empresa = Empresa(**datos)
            db.add(empresa)
            db.flush()  # Para obtener el ID
            empresas_creadas[datos["nombre"]] = empresa
            print(f"✅ Empresa '{datos['nombre']}' creada")
        else:
            empresas_creadas[datos["nombre"]] = existente
            print(f"ℹ️ Empresa '{datos['nombre']}' ya existe")
    
    db.commit()
    
    # 2. Crear usuarios de prueba
    usuarios_predefinidos = [
        {
            "nombre": "Admin Cointra",
            "email": "admin@cointra.com",
            "password": "admin123",
            "rol_nombre": "admin",
            "empresa_nombre": "Cointra",
        },
        {
            "nombre": "Admin Geotab",
            "email": "admin@geotab.com",
            "password": "admin123",
            "rol_nombre": "admin",
            "empresa_nombre": "Geotab Colombia",
        },
        {
            "nombre": "Admin Satena",
            "email": "admin@satena.com",
            "password": "admin123",
            "rol_nombre": "admin",
            "empresa_nombre": "Satena",
        },
        {
            "nombre": "Consultor Cointra",
            "email": "consultor@cointra.com",
            "password": "consultor123",
            "rol_nombre": "consultor",
            "empresa_nombre": "Cointra",
        },
    ]
    
    for datos in usuarios_predefinidos:
        # Verificar si ya existe
        existente = db.query(Usuario).filter(
            Usuario.email == datos["email"]
        ).first()
        
        if not existente:
            # Buscar el rol en la BD
            rol = db.query(Rol).filter(
                func.lower(Rol.nombre) == func.lower(datos["rol_nombre"])
            ).first()
            
            if not rol:
                print(f"⚠️ Rol '{datos['rol_nombre']}' no encontrado. Saltando usuario {datos['email']}")
                continue
            
            # Obtener la empresa
            empresa = empresas_creadas.get(datos["empresa_nombre"])
            if not empresa:
                print(f"⚠️ Empresa '{datos['empresa_nombre']}' no encontrada. Saltando usuario {datos['email']}")
                continue
            
            usuario = Usuario(
                nombre=datos["nombre"],
                email=datos["email"],
                password_hash=hash_password(datos["password"]),
                rol_id=rol.id,
                empresa_id=empresa.id,
                activo=1,
                aprobado=1,  # Usuarios de prueba pre-aprobados
            )
            db.add(usuario)
            print(f"✅ Usuario '{datos['email']}' creado")
        else:
            print(f"ℹ️ Usuario '{datos['email']}' ya existe")
    
    db.commit()
    print("✅ Empresas y usuarios de prueba inicializados correctamente")
