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
    create_refresh_token,  # Nuevo
    get_current_user,
    get_user_permissions,
)
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.rol_permiso import Rol
from app.schemas.auth import (
    LoginRequest, 
    TokenResponse, 
    UsuarioResponse,
    RegistroRequest,
    RegistroResponse,
    AprobarUsuarioRequest,
    RefreshTokenRequest
)
from app.schemas.empresa import OnboardingRequest, OnboardingResponse, CrearEmpresaConAdminRequest, CrearEmpresaConAdminResponse, EmpresaResponse
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="",
    tags=["Autenticación"]
)


@router.post("/onboarding", response_model=OnboardingResponse, summary="🚀 Onboarding - Crear Super Admin", status_code=status.HTTP_201_CREATED)
def onboarding_inicial(
    datos: OnboardingRequest,
    db: Session = Depends(get_db)
):
    """
    **ENDPOINT PÚBLICO DE ONBOARDING** - Solo funciona en primera instalación.
    
    Crea el **SUPER ADMINISTRADOR** del sistema (tú).
    
    **Solo funciona SI NO hay usuarios en el sistema.**
    Este es el primer paso al instalar el sistema.
    
    POST /onboarding
    Body:
    {
        "nombre": "Tu Nombre",
        "email": "tu@email.com",
        "password": "tupassword123"
    }
    
    **Flujo:**
    1. Valida que NO existan usuarios (primera vez)
    2. Crea el super administrador (tú)
    3. Ya puedes hacer login
    4. Como super admin, puedes crear empresas
    
    **⚠️ Importante:**
    - Solo funciona UNA VEZ (primera instalación)
    - Después de esto, tú (super admin) creas las empresas
    """
    
    # 1. Verificar que NO existan usuarios (onboarding solo para primera vez)
    total_usuarios = db.query(Usuario).count()
    
    if total_usuarios > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El sistema ya está inicializado. Ya existen {total_usuarios} usuario(s). El onboarding solo funciona la primera vez."
        )
    
    # 2. Verificar que el email no exista (por si acaso)
    usuario_existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email {datos.email} ya está registrado"
        )
    
    # 3. Buscar el rol "super_admin" (debe existir en seeds)
    rol_super_admin = db.query(Rol).filter(Rol.nombre == "super_admin").first()
    if not rol_super_admin:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error: Rol 'super_admin' no encontrado. Ejecute las migraciones."
        )
    
    try:
        # 4. Crear el super administrador
        password_hash = pwd_context.hash(datos.password)
        
        super_admin = Usuario(
            nombre=datos.nombre,
            email=datos.email,
            password_hash=password_hash,
            empresa_id=None,  # Super admin NO pertenece a ninguna empresa
            rol_id=rol_super_admin.id,
            activo=1,
            aprobado=1,  # Auto-aprobado
            aprobado_por=None,
            aprobado_en=datetime.now()
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        return OnboardingResponse(
            mensaje=f"¡Onboarding exitoso! Super Admin creado. Ya puedes iniciar sesión con {super_admin.email} y comenzar a crear empresas.",
            super_admin_email=super_admin.email
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear super administrador: {str(e)}"
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
    
    # Verificar que el usuario esté aprobado y activo
    if not usuario.aprobado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está pendiente de aprobación por un administrador",
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido desactivada. Contacta al administrador",
        )

    # Crear tokens JWT
    token_data = {
        "sub": usuario.email, 
        "rol": usuario.rol.nombre if usuario.rol else "consultor",
        "empresa_id": usuario.empresa_id  # Puede ser None para super_admin
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    permisos = get_user_permissions(usuario)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol.nombre if usuario.rol else "consultor",
        empresa_nombre=usuario.empresa.nombre if usuario.empresa else "Sistema",
        usuario_permisos=permisos,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Renovar Token")
def refresh_access_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renueva el access token usando un refresh token válido.
    
    POST /refresh
    Body (form-data):
    {
        "refresh_token": "eyJhbGc..."
    }
    
    Response:
    {
        "access_token": "nuevo_token...",
        "refresh_token": "mismo_refresh_token...",
        "token_type": "bearer",
        "usuario_nombre": "...",
        "usuario_rol": "...",
        "empresa_nombre": "..."
    }
    
    **Uso:** El frontend debe llamar este endpoint automáticamente cuando el
    access token expire (30 min) usando el refresh token guardado (1 día).
    """
    from jose import jwt, JWTError
    from app.auth import SECRET_KEY, ALGORITHM, create_access_token
    
    refresh_token = payload.refresh_token

    try:
        # Decodificar el refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validar que sea un refresh token
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Debe usar un refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado o inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar el usuario
    from sqlalchemy.orm import joinedload
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol),
        joinedload(Usuario.empresa)
    ).filter(Usuario.email == email).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validar que siga activo y aprobado
    if not usuario.aprobado or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido desactivada o está pendiente de aprobación",
        )
    
    # Crear nuevo access token (refresh token se mantiene igual)
    token_data = {
        "sub": usuario.email,
        "rol": usuario.rol.nombre if usuario.rol else "consultor",
        "empresa_id": usuario.empresa_id
    }
    
    new_access_token = create_access_token(data=token_data)
    permisos = get_user_permissions(usuario)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_token,  # Devolver el mismo refresh token
        token_type="bearer",
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol.nombre if usuario.rol else "consultor",
        empresa_nombre=usuario.empresa.nombre if usuario.empresa else "Sistema",
        usuario_permisos=permisos,
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
        empresa_id=current_user.empresa_id,
        empresa_nombre=current_user.empresa.nombre if current_user.empresa else None,
        rol=current_user.rol.nombre if current_user.rol else None,
        activo=current_user.activo,
        aprobado=current_user.aprobado,
        permisos=get_user_permissions(current_user),
    )


@router.post("/registro", response_model=RegistroResponse, summary="Registro Público (Sin Autenticación)")
def registro_publico(
    datos: RegistroRequest,
    db: Session = Depends(get_db)
):
    """
    Registro público de nuevos usuarios.
    
    **NO requiere autenticación** - Este es el único endpoint público.
    
    El usuario queda **PENDIENTE DE APROBACIÓN** por un administrador de la empresa.
    
    POST /registro
    Body:
    {
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "password": "mipassword123",
        "empresa_nit": "900123456-7"
    }
    
    **Flujo:**
    1. El usuario se registra con el NIT de su empresa
    2. Si la empresa existe, se crea el usuario con estado "pendiente"
    3. Un administrador de la empresa debe aprobar el usuario
    4. Al aprobar, el admin asigna el rol correspondiente
    5. El usuario recibe notificación (email/sistema) de aprobación
    6. Ya puede hacer login
    """
    
    # 1. Verificar que el email no exista
    usuario_existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email ya está registrado"
        )
    
    # 2. Buscar la empresa por NIT
    empresa = db.query(Empresa).filter(
        Empresa.nit == datos.empresa_nit,
        Empresa.activo == 1
    ).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La empresa con NIT {datos.empresa_nit} no existe en el sistema. Por favor contacta con soporte."
        )
    
    # 3. Crear el usuario (pendiente de aprobación)
    password_hash = pwd_context.hash(datos.password)
    
    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password_hash=password_hash,
        empresa_id=empresa.id,
        rol_id=None,  # Sin rol hasta aprobación
        activo=0,  # Inactivo hasta aprobación
        aprobado=0,  # Pendiente de aprobación
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return RegistroResponse(
        mensaje="Registro exitoso. Tu cuenta está pendiente de aprobación por un administrador de tu empresa.",
        email=nuevo_usuario.email,
        empresa=empresa.nombre
    )


@router.post("/usuarios/{usuario_id}/aprobar", response_model=UsuarioResponse, summary="Aprobar Usuario Pendiente")
def aprobar_usuario(
    usuario_id: int,
    datos: AprobarUsuarioRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Aprueba un usuario pendiente y le asigna un rol.
    
    **Solo administradores** de la misma empresa pueden aprobar usuarios.
    
    POST /usuarios/{usuario_id}/aprobar
    Body:
    {
        "rol_nombre": "consultor"
    }
    
    **Roles disponibles:**
    - admin: Acceso total
    - supervisor: Todo excepto eliminar
    - gestor_rutas: Gestión de rutas
    - gestor_clientes: Gestión de clientes
    - consultor: Solo lectura
    """
    
    # 1. Verificar que el usuario actual es admin o super_admin
    es_super_admin = current_user.rol and current_user.rol.nombre == "super_admin"
    es_admin = current_user.rol and current_user.rol.nombre == "admin"
    
    if not es_super_admin and not es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden aprobar usuarios"
        )
    
    # 2. Buscar el usuario a aprobar
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # 3. Verificar que es de la misma empresa (solo para admin, super_admin puede aprobar cualquiera)
    if not es_super_admin and usuario.empresa_id != current_user.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes aprobar usuarios de tu empresa"
        )
    
    # 4. Verificar que está pendiente
    if usuario.aprobado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario ya está aprobado"
        )
    
    # 5. Buscar el rol
    rol = db.query(Rol).filter(Rol.nombre == datos.rol_nombre).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol '{datos.rol_nombre}' no existe"
        )
    
    # 6. Aprobar y activar usuario
    usuario.rol_id = rol.id
    usuario.aprobado = 1
    usuario.activo = 1
    usuario.aprobado_por = current_user.id
    usuario.aprobado_en = datetime.now()
    
    db.commit()
    db.refresh(usuario)
    
    # TODO: Enviar email de notificación al usuario
    
    return UsuarioResponse(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        empresa_id=usuario.empresa_id,
        empresa_nombre=usuario.empresa.nombre if usuario.empresa else None,
        rol=usuario.rol.nombre if usuario.rol else None,
        activo=usuario.activo,
        aprobado=usuario.aprobado,
    )

