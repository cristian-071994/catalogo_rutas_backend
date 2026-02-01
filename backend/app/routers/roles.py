"""
Router de Gestión de Roles
Sistema dinámico de roles y permisos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.usuario import Usuario
# from app.models.rol import RolEnum  # Ya no se usa Enum
from app.models.rol_permiso import Rol, Permiso
from app.schemas.rol_permiso import (
    RolCreate,
    RolResponse,
    RolUpdate,
    RolDetallado,
    AsignarPermisosRequest
)
from app.auth import get_current_user, require_role

router = APIRouter(
    prefix="/roles",
    tags=["Gestión de Roles"]
)


# ============================================
# LISTAR ROLES
# ============================================

@router.get(
    "/",
    response_model=list[RolResponse],
    summary="Listar Roles"
)
def listar_roles(
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Lista todos los roles del sistema.
    
    ⚠️ Solo administradores
    """
    roles = db.query(Rol).all()
    return roles


# ============================================
# OBTENER ROL DETALLADO (CON PERMISOS)
# ============================================

@router.get(
    "/{rol_id}",
    response_model=RolDetallado,
    summary="Obtener Rol Detallado"
)
def obtener_rol(
    rol_id: int,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Obtiene un rol con todos sus permisos asignados.
    
    ⚠️ Solo administradores
    """
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    return rol


# ============================================
# CREAR ROL
# ============================================

@router.post(
    "/",
    response_model=RolDetallado,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Rol"
)
def crear_rol(
    rol_data: RolCreate,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo rol en el sistema.
    
    ⚠️ Solo administradores
    
    **Validaciones:**
    - Nombre debe ser único
    - Los permisos deben existir
    """
    
    # Validar nombre único (case-insensitive)
    existente = db.query(Rol).filter(
        func.lower(Rol.nombre) == func.lower(rol_data.nombre)
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un rol con nombre '{rol_data.nombre}'"
        )
    
    # Crear rol
    nuevo_rol = Rol(
        nombre=rol_data.nombre,
        descripcion=rol_data.descripcion,
        es_sistema=0  # Roles creados dinámicamente no son del sistema
    )
    
    # Agregar permisos si se proporcionan
    if rol_data.permisos:
        permisos = db.query(Permiso).filter(Permiso.id.in_(rol_data.permisos)).all()
        
        if len(permisos) != len(rol_data.permisos):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más permisos no existen"
            )
        
        nuevo_rol.permisos = permisos
    
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    
    return nuevo_rol


# ============================================
# ACTUALIZAR ROL
# ============================================

@router.put(
    "/{rol_id}",
    response_model=RolDetallado,
    summary="Actualizar Rol"
)
def actualizar_rol(
    rol_id: int,
    rol_update: RolUpdate,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Actualiza un rol existente.
    
    ⚠️ Solo administradores
    ⚠️ Los roles del sistema no pueden ser editados
    
    **Restricciones:**
    - No se pueden editar roles del sistema
    - El nombre debe ser único
    """
    
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Protección: no permitir editar roles del sistema
    if rol.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pueden editar los roles del sistema"
        )
    
    # Validar nombre único si se intenta cambiar
    if rol_update.nombre and rol_update.nombre.lower() != rol.nombre.lower():
        existente = db.query(Rol).filter(
            func.lower(Rol.nombre) == func.lower(rol_update.nombre)
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un rol con nombre '{rol_update.nombre}'"
            )
    
    # Actualizar campos básicos
    if rol_update.nombre:
        rol.nombre = rol_update.nombre
    if rol_update.descripcion is not None:
        rol.descripcion = rol_update.descripcion
    if rol_update.activo is not None:
        rol.activo = rol_update.activo
    
    # Actualizar permisos si se proporcionan
    if rol_update.permisos is not None:
        permisos = db.query(Permiso).filter(Permiso.id.in_(rol_update.permisos)).all()
        
        if len(permisos) != len(rol_update.permisos):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más permisos no existen"
            )
        
        rol.permisos = permisos
    
    db.add(rol)
    db.commit()
    db.refresh(rol)
    
    return rol


# ============================================
# ASIGNAR PERMISOS A ROL
# ============================================

@router.post(
    "/{rol_id}/permisos",
    response_model=RolDetallado,
    summary="Asignar Permisos a Rol"
)
def asignar_permisos(
    rol_id: int,
    request: AsignarPermisosRequest,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Asigna permisos a un rol (reemplaza los anteriores).
    
    ⚠️ Solo administradores
    ⚠️ Los roles del sistema no pueden ser editados
    """
    
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    if rol.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pueden editar los permisos de roles del sistema"
        )
    
    # Obtener permisos
    permisos = db.query(Permiso).filter(Permiso.id.in_(request.permiso_ids)).all()
    
    if len(permisos) != len(request.permiso_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uno o más permisos no existen"
        )
    
    # Asignar permisos
    rol.permisos = permisos
    db.add(rol)
    db.commit()
    db.refresh(rol)
    
    return rol


# ============================================
# ELIMINAR ROL
# ============================================

@router.delete(
    "/{rol_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Rol"
)
def eliminar_rol(
    rol_id: int,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Elimina un rol (soft delete - lo marca como inactivo).
    
    ⚠️ Solo administradores
    ⚠️ Los roles del sistema no pueden ser eliminados
    
    **Restricciones:**
    - No se pueden eliminar roles del sistema
    - No se pueden eliminar roles con usuarios asignados
    """
    
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    if rol.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pueden eliminar los roles del sistema"
        )
    
    # Protección: verificar que no haya usuarios con este rol
    usuarios_con_rol = db.query(Usuario).filter(
        Usuario.rol == rol.nombre  # Comparar con el nombre del rol (mientras usemos Enum)
    ).count()
    
    if usuarios_con_rol > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el rol porque hay {usuarios_con_rol} usuario(s) asignado(s)"
        )
    
    # Soft delete
    rol.activo = 0
    db.add(rol)
    db.commit()
    
    return None
