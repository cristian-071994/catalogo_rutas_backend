from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.cliente import Cliente
from app.models.enums import EstadoGeneral
from app.models.usuario import Usuario
from app.models.rol import RolEnum
from app.schemas.cliente import (
    ClienteCreate,
    ClienteResponse,
    ClienteUpdate,
)
from app.auth import get_current_user, require_role, require_permission

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# Crear cliente
@router.post("/", response_model=ClienteResponse, summary="Crear Cliente")
def crear_cliente(
    cliente: ClienteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo cliente en el sistema.
    
    ⚠️ Requiere autenticación
    
    Roles permitidos:
    - admin (todo)
    - supervisor (todo excepto delete)
    - gestor_clientes (solo clientes)
    """
    
    # Validar permisos
    if current_user.rol not in [
        RolEnum.admin,
        RolEnum.supervisor,
        RolEnum.gestor_clientes
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear clientes"
        )
    
    # Validar duplicado (case-insensitive)
    existente = db.query(Cliente).filter(
        func.lower(Cliente.nombre) == func.lower(cliente.nombre)
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con nombre '{cliente.nombre}'"
        )
    
    nuevo_cliente = Cliente(**cliente.model_dump())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente

# Listar cliente
@router.get("/", response_model=list[ClienteResponse], summary="Listar Clientes")
def listar_clientes(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los clientes activos del sistema.
    
    GET /clientes/
    GET /clientes/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    ⚠️ Requiere autenticación
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    
    query = db.query(Cliente)
    
    if not incluir_inactivos:
        query = query.filter(Cliente.estado == EstadoGeneral.activo)
    
    return query.all()

# Obtener cliente por ID (con rutas)
@router.get("/{cliente_id}", response_model=ClienteResponse, summary="Obtener Cliente")
def obtener_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un cliente específico por su ID.
    
    ⚠️ Requiere autenticación
    """
    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id)
        .first()
    )

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return cliente


# ============================================
# ACTUALIZAR CLIENTE
# ============================================


@router.put("/{cliente_id}", response_model=ClienteResponse, summary="Actualizar Cliente")
def actualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un cliente existente.

    ⚠️ Requiere autenticación
    
    Roles permitidos:
    - admin (todo)
    - supervisor (todo excepto delete)
    - gestor_clientes (solo clientes)

    PUT /clientes/1
    Body:
    {
        "nombre": "Cliente Actualizado"
    }
    """
    
    # Validar permisos
    if current_user.rol not in [
        RolEnum.admin,
        RolEnum.supervisor,
        RolEnum.gestor_clientes
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar clientes"
        )

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    # Si cambian el nombre, validar que sea único (case-insensitive)
    if cliente_update.nombre and cliente_update.nombre.lower() != cliente.nombre.lower():
        existente = db.query(Cliente).filter(
            func.lower(Cliente.nombre) == func.lower(cliente_update.nombre)
        ).first()
        if existente and existente.id != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un cliente con nombre '{cliente_update.nombre}'"
            )

    # Actualizar solo los campos enviados
    for campo, valor in cliente_update.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


# ============================================
# ELIMINAR CLIENTE (Soft Delete)
# ============================================


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Cliente")
def eliminar_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marca un cliente como inactivo (eliminación lógica).

    ⚠️ Requiere autenticación
    
    Roles permitidos:
    - admin (todo)
    - supervisor (NO puede usar DELETE - solo crear/actualizar)
    - gestor_clientes (solo clientes)

    DELETE /clientes/1
    """
    
    # Validar permisos - supervisor NO puede eliminar
    if current_user.rol == RolEnum.supervisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los supervisores no tienen permiso para eliminar (soft delete)"
        )
    
    if current_user.rol not in [
        RolEnum.admin,
        RolEnum.gestor_clientes
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar clientes"
        )

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    cliente.estado = EstadoGeneral.inactivo
    db.add(cliente)
    db.commit()

    return None
