"""
Router de Gestión de Permisos
Sistema dinámico de roles y permisos
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.usuario import Usuario
# from app.models.rol import RolEnum  # Ya no se usa Enum
from app.models.rol_permiso import Permiso
from app.schemas.rol_permiso import (
    PermisoCreate,
    PermisoResponse,
    PermisoUpdate
)
from app.auth import get_current_user, require_role

router = APIRouter(
    prefix="/permisos",
    tags=["Gestión de Permisos"]
)


# ============================================
# LISTAR PERMISOS
# ============================================

@router.get(
    "/",
    response_model=list[PermisoResponse],
    summary="Listar Permisos"
)
def listar_permisos(
    categoria: str | None = Query(None, description="Filtrar por categoría"),
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Lista todos los permisos del sistema.
    
    **Parámetros opcionales:**
    - categoria: Filtrar por categoría (ej: "usuarios", "rutas", "peajes")
    
    ⚠️ Solo administradores
    """
    query = db.query(Permiso)
    
    if categoria:
        query = query.filter(Permiso.categoria == categoria)
    
    permisos = query.all()
    return permisos


# ============================================
# OBTENER PERMISO
# ============================================

@router.get(
    "/{permiso_id}",
    response_model=PermisoResponse,
    summary="Obtener Permiso"
)
def obtener_permiso(
    permiso_id: int,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Obtiene un permiso específico.
    
    ⚠️ Solo administradores
    """
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado"
        )
    
    return permiso


# ============================================
# CREAR PERMISO
# ============================================

@router.post(
    "/",
    response_model=PermisoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Permiso"
)
def crear_permiso(
    permiso_data: PermisoCreate,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo permiso en el sistema.
    
    ⚠️ Solo administradores
    
    **Validaciones:**
    - Nombre debe ser único
    - Categoría es requerida
    - Descripción es recomendada
    
    **Categorías comunes:**
    - usuarios
    - rutas
    - peajes
    - clientes
    - marcas_vehiculos
    - vehiculos
    - configuracion
    """
    
    # Validar nombre único (case-insensitive)
    existente = db.query(Permiso).filter(
        func.lower(Permiso.nombre) == func.lower(permiso_data.nombre)
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un permiso con nombre '{permiso_data.nombre}'"
        )
    
    # Crear permiso
    nuevo_permiso = Permiso(
        nombre=permiso_data.nombre,
        descripcion=permiso_data.descripcion,
        categoria=permiso_data.categoria,
        es_sistema=0  # Los permisos creados dinámicamente no son del sistema
    )
    
    db.add(nuevo_permiso)
    db.commit()
    db.refresh(nuevo_permiso)
    
    return nuevo_permiso


# ============================================
# ACTUALIZAR PERMISO
# ============================================

@router.put(
    "/{permiso_id}",
    response_model=PermisoResponse,
    summary="Actualizar Permiso"
)
def actualizar_permiso(
    permiso_id: int,
    permiso_update: PermisoUpdate,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Actualiza un permiso existente.
    
    ⚠️ Solo administradores
    ⚠️ Los permisos del sistema no pueden ser editados
    """
    
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado"
        )
    
    # Protección: no permitir editar permisos del sistema
    if permiso.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pueden editar los permisos del sistema"
        )
    
    # Validar nombre único si se intenta cambiar
    if permiso_update.nombre and permiso_update.nombre.lower() != permiso.nombre.lower():
        existente = db.query(Permiso).filter(
            func.lower(Permiso.nombre) == func.lower(permiso_update.nombre)
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un permiso con nombre '{permiso_update.nombre}'"
            )
    
    # Actualizar campos
    if permiso_update.nombre:
        permiso.nombre = permiso_update.nombre
    if permiso_update.descripcion is not None:
        permiso.descripcion = permiso_update.descripcion
    if permiso_update.categoria:
        permiso.categoria = permiso_update.categoria
    if permiso_update.activo is not None:
        permiso.activo = permiso_update.activo
    
    db.add(permiso)
    db.commit()
    db.refresh(permiso)
    
    return permiso


# ============================================
# ELIMINAR PERMISO
# ============================================

@router.delete(
    "/{permiso_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Permiso"
)
def eliminar_permiso(
    permiso_id: int,
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Elimina un permiso (soft delete - lo marca como inactivo).
    
    ⚠️ Solo administradores
    ⚠️ Los permisos del sistema no pueden ser eliminados
    
    **Restricciones:**
    - No se pueden eliminar permisos del sistema
    - Se limpian automáticamente de todos los roles
    """
    
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado"
        )
    
    if permiso.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pueden eliminar los permisos del sistema"
        )
    
    # Soft delete
    permiso.activo = 0
    db.add(permiso)
    db.commit()
    
    return None
