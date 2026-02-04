"""
Router de Gestión de Usuarios
Maneja creación, lectura, actualización y eliminación de usuarios
Solo admin puede gestionar todos los usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from app.database.session import get_db
from app.models.usuario import Usuario
from app.models.rol_permiso import Rol
from app.schemas.auth import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    CambiarPasswordRequest,
    UsuariosListaResponse
)
from app.auth import (
    get_current_user,
    hash_password,
    verify_password,
    require_role
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Gestión de Usuarios"]
)


# ============================================
# LISTAR USUARIOS PENDIENTES DE APROBACIÓN
# ============================================

@router.get(
    "/pendientes",
    response_model=UsuariosListaResponse,
    summary="Listar Usuarios Pendientes de Aprobación"
)
def listar_usuarios_pendientes(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros por página"),
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Lista usuarios pendientes de aprobación.
    
    ⚠️ Solo administradores
    
    Super admin ve todos los pendientes del sistema.
    Admin solo ve pendientes de su empresa.
    """
    
    # Construir query base
    query = db.query(Usuario).options(
        joinedload(Usuario.empresa),
        joinedload(Usuario.rol)
    ).filter(Usuario.aprobado == 0)
    
    # Multi-tenancy: Admin solo ve pendientes de su empresa
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(Usuario.empresa_id == current_user.empresa_id)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginación
    usuarios = query.order_by(Usuario.created_at.desc()).offset(skip).limit(limit).all()
    
    # Calcular metadatos
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1 if total > 0 else 1
    has_next = (skip + limit) < total
    has_prev = skip > 0
    
    return UsuariosListaResponse(
        items=usuarios,
        total=total,
        skip=skip,
        limit=limit,
        total_pages=total_pages,
        current_page=current_page,
        has_next=has_next,
        has_prev=has_prev
    )


# ============================================
# LISTAR USUARIOS
# ============================================

@router.get(
    "/",
    response_model=UsuariosListaResponse,
    summary="Listar Usuarios (Paginado)"
)
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Registros a saltar (para paginación)"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros por página (máx 100)"),
    search: str = Query(None, description="Buscar por nombre o email"),
    rol_id: int = Query(None, description="Filtrar por ID de rol"),
    activo: int = Query(None, ge=0, le=1, description="Filtrar por estado (1=activo, 0=inactivo)"),
    sort_by: str = Query("created_at", description="Ordenar por: id, nombre, email, created_at, updated_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Orden: asc (ascendente) o desc (descendente)"),
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Lista usuarios del sistema con paginación, filtros y búsqueda.
    
    ⚠️ Solo administradores
    
    **Parámetros:**
    - `skip`: Registros a saltar (ej: para página 2 con limit=10, usar skip=10)
    - `limit`: Registros por página (máximo 100)
    - `search`: Buscar en nombre o email (búsqueda parcial)
    - `rol_id`: Filtrar por rol específico
    - `activo`: Filtrar por estado (1=activo, 0=inactivo)
    - `sort_by`: Campo para ordenamiento
    - `sort_order`: asc (A→Z) o desc (Z→A)
    
    **Ejemplo:**
    - GET /usuarios/?skip=0&limit=10&search=admin&sort_by=nombre&sort_order=asc
    - GET /usuarios/?rol_id=1&activo=1
    """
    
    # Validar sort_by
    campos_validos = ["id", "nombre", "email", "created_at", "updated_at"]
    if sort_by not in campos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"sort_by inválido. Válidos: {', '.join(campos_validos)}"
        )
    
    # Construir query base con eager loading de relaciones
    query = db.query(Usuario).options(
        joinedload(Usuario.empresa),
        joinedload(Usuario.rol)
    )
    
    # Multi-tenancy: Super admin ve todos, admin solo ve usuarios de su empresa
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(Usuario.empresa_id == current_user.empresa_id)
    
    # Aplicar filtros
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                func.lower(Usuario.nombre).ilike(search_pattern),
                func.lower(Usuario.email).ilike(search_pattern)
            )
        )
    
    if rol_id is not None:
        query = query.filter(Usuario.rol_id == rol_id)
    
    if activo is not None:
        query = query.filter(Usuario.activo == activo)
    
    # Contar total antes de paginación
    total = query.count()
    
    # Aplicar ordenamiento
    sort_column = getattr(Usuario, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Aplicar paginación
    usuarios = query.offset(skip).limit(limit).all()
    
    # Calcular metadatos de paginación
    total_pages = (total + limit - 1) // limit  # Redondear hacia arriba
    current_page = (skip // limit) + 1 if total > 0 else 1
    has_next = (skip + limit) < total
    has_prev = skip > 0
    
    return UsuariosListaResponse(
        items=usuarios,
        total=total,
        skip=skip,
        limit=limit,
        total_pages=total_pages,
        current_page=current_page,
        has_next=has_next,
        has_prev=has_prev
    )


# ============================================
# CAMBIAR CONTRASEÑA (ANTES de /{usuario_id})
# ============================================

@router.put(
    "/cambiar-contraseña",
    summary="Cambiar Mi Contraseña"
)
def cambiar_contraseña(
    cambio: CambiarPasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permite que un usuario autenticado cambie su contraseña.
    
    ⚠️ Requiere la contraseña actual para validación de seguridad
    
    **Validaciones:**
    - Contraseña actual debe ser correcta
    - Nueva contraseña debe ser diferente a la actual
    - Las contraseñas confirmar debe coincidir
    """
    
    # Validar que las contraseñas coincidan
    if cambio.password_nueva != cambio.password_confirmar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las nuevas contraseñas no coinciden"
        )
    
    # Validar que la contraseña actual sea correcta
    if not verify_password(cambio.password_actual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar que no sea la misma contraseña
    if cambio.password_actual == cambio.password_nueva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la actual"
        )
    
    # Actualizar contraseña
    current_user.password_hash = hash_password(cambio.password_nueva)
    db.add(current_user)
    db.commit()
    
    return {
        "mensaje": "Contraseña actualizada exitosamente",
        "usuario_id": current_user.id,
        "email": current_user.email
    }


# ============================================
# OBTENER UN USUARIO POR ID
# ============================================

@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener Usuario"
)
def obtener_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un usuario específico por su ID.
    
    ⚠️ Super admin puede ver cualquier usuario
    ⚠️ Admin puede ver usuarios de su empresa
    ⚠️ Usuarios comunes solo pueden ver su propio perfil
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Super admin puede ver cualquier usuario
    if current_user.rol and current_user.rol.nombre == "super_admin":
        return usuario
    
    # Admin puede ver usuarios de su empresa
    es_admin = current_user.rol and current_user.rol.nombre == "admin"
    if es_admin and usuario.empresa_id == current_user.empresa_id:
        return usuario
    
    # Usuarios comunes solo ven su propio perfil
    if current_user.id == usuario_id:
        return usuario
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para ver este usuario"
    )


# ============================================
# CREAR USUARIO
# ============================================

@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Usuario"
)
def crear_usuario(
    usuario_data: UsuarioCreate,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema.
    
    ⚠️ Solo administradores pueden crear usuarios
    
    **Validaciones:**
    - Email debe ser único
    - Contraseña mínimo 6 caracteres
    - Rol debe existir en la BD
    
    **Roles disponibles:**
    - `admin` - Acceso total
    - `supervisor` - Todo excepto DELETE
    - `gestor_rutas` - Solo rutas
    - `gestor_peajes` - Solo peajes
    - `gestor_clientes` - Solo clientes
    - `consultor` - Solo lectura
    """
    
    # Validar que el email sea único (case-insensitive)
    existente = db.query(Usuario).filter(
        func.lower(Usuario.email) == func.lower(usuario_data.email)
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{usuario_data.email}' ya está registrado"
        )
    
    # Buscar el rol en la BD
    rol = db.query(Rol).filter(
        func.lower(Rol.nombre) == func.lower(usuario_data.rol)
    ).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol '{usuario_data.rol}' no encontrado"
        )
    
    # Super admin no puede crear usuarios directamente sin asignar empresa
    if current_user.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admin debe crear usuarios a través de la creación de empresas"
        )
    
    # Crear el usuario con la empresa del admin actual
    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        email=usuario_data.email,
        password_hash=hash_password(usuario_data.password),
        empresa_id=current_user.empresa_id,  # Asignar empresa del admin
        rol_id=rol.id,
        activo=1,
        aprobado=1  # Auto-aprobado por admin
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


# ============================================
# ACTUALIZAR USUARIO
# ============================================

@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar Usuario"
)
def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza un usuario existente.
    
    ⚠️ Super admin puede editar cualquier usuario
    ⚠️ Admin puede editar usuarios de su empresa
    ⚠️ Usuarios comunes solo pueden editar su propio perfil (excepto rol)
    
    **Restricciones:**
    - Usuario común NO puede cambiar su propio rol (solo admin/super_admin)
    - Usuario común NO puede cambiar estado (activo/inactivo)
    - El email debe ser único si se intenta cambiar
    """
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar que el usuario actual tenga rol
    if not current_user.rol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin rol asignado"
        )
    
    # Validar permisos
    es_super_admin = current_user.rol.nombre == "super_admin"
    es_admin = current_user.rol.nombre == "admin"
    es_su_perfil = current_user.id == usuario_id
    
    # Super admin puede editar cualquier usuario
    if es_super_admin:
        pass  # Permitir todo
    # Admin solo puede editar usuarios de su empresa
    elif es_admin:
        if usuario.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes editar usuarios de tu empresa"
            )
    # Usuarios comunes solo pueden editar su propio perfil
    elif not es_su_perfil:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar este usuario"
        )
    
    # Si no es admin/super_admin y está editando su perfil, no puede cambiar rol ni estado
    if not es_super_admin and not es_admin and es_su_perfil:
        if usuario_update.rol is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes cambiar tu propio rol"
            )
        if usuario_update.activo is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes cambiar tu propio estado (solo admin)"
            )
    
    # Validar email único si se intenta cambiar
    if usuario_update.email and usuario_update.email.lower() != usuario.email.lower():
        existente = db.query(Usuario).filter(
            func.lower(Usuario.email) == func.lower(usuario_update.email)
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{usuario_update.email}' ya está registrado"
            )
    
    # Validar y buscar rol si se intenta cambiar
    if usuario_update.rol:
        rol = db.query(Rol).filter(
            func.lower(Rol.nombre) == func.lower(usuario_update.rol)
        ).first()
        
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol '{usuario_update.rol}' no encontrado"
            )
        
        usuario.rol_id = rol.id
    
    # Actualizar otros campos
    if usuario_update.nombre:
        usuario.nombre = usuario_update.nombre
    if usuario_update.email:
        usuario.email = usuario_update.email
    if usuario_update.activo is not None:
        usuario.activo = usuario_update.activo
    
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    return usuario


# ============================================
# ELIMINAR USUARIO (Soft Delete)
# ============================================

@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Usuario"
)
def eliminar_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario (lo marca como inactivo - soft delete).
    
    ⚠️ Solo administradores pueden eliminar usuarios
    
    **Restricciones:**
    - No se puede eliminar el último admin (protección)
    - El usuario se marca como inactivo, no se elimina de la BD
    """
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Super admin puede eliminar cualquier usuario
    if current_user.rol and current_user.rol.nombre != "super_admin":
        # Admin solo puede eliminar usuarios de su empresa
        if usuario.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes eliminar usuarios de tu empresa"
            )
    
    # Protección: no permitir eliminar el último admin de una empresa
    if usuario.rol and usuario.rol.nombre == "admin":
        # Buscar el rol admin
        rol_admin = db.query(Rol).filter(Rol.nombre == "admin").first()
        
        if rol_admin:
            admins_activos = db.query(Usuario).filter(
                Usuario.rol_id == rol_admin.id,
                Usuario.activo == 1,
                Usuario.id != usuario_id
            ).count()
            
            if admins_activos == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede eliminar el último administrador del sistema"
                )
    
    # Soft delete
    usuario.activo = 0
    db.add(usuario)
    db.commit()
    
    return None
