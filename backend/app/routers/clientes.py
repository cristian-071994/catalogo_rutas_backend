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
    current_user: Usuario = Depends(require_permission("crear_cliente")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo cliente en el sistema.
    
    ⚠️ Requiere autenticación y permiso: crear_cliente
    """
    
    # Super admin no tiene empresa_id, debe rechazarse o asignar una
    if current_user.empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admin no puede crear clientes directamente. Debe asignar una empresa."
        )
    
    # Validar duplicado dentro de la empresa (case-insensitive)
    existente = db.query(Cliente).filter(
        Cliente.empresa_id == current_user.empresa_id,
        func.lower(Cliente.nombre) == func.lower(cliente.nombre)
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con nombre '{cliente.nombre}' en tu empresa"
        )
    
    # Crear cliente con empresa_id del usuario actual
    cliente_data = cliente.model_dump()
    cliente_data['empresa_id'] = current_user.empresa_id
    
    nuevo_cliente = Cliente(**cliente_data)
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente

# Listar cliente
@router.get("/", response_model=list[ClienteResponse], summary="Listar Clientes")
def listar_clientes(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(require_permission("ver_clientes")),
    db: Session = Depends(get_db)
):
    """
    Lista todos los clientes activos del sistema.
    
    GET /clientes/
    GET /clientes/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    ⚠️ Requiere autenticación y permiso: ver_clientes
    
    Super admin ve todos los clientes de todas las empresas.
    Otros usuarios solo ven clientes de su empresa.
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    
    query = db.query(Cliente)
    
    # Super admin ve todos los clientes
    if current_user.rol and current_user.rol.nombre != "super_admin":
        # Otros usuarios solo ven clientes de su empresa
        query = query.filter(Cliente.empresa_id == current_user.empresa_id)
    
    if not incluir_inactivos:
        query = query.filter(Cliente.estado == EstadoGeneral.activo)
    
    return query.all()

# Obtener cliente por ID (con rutas)
@router.get("/{cliente_id}", response_model=ClienteResponse, summary="Obtener Cliente")
def obtener_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(require_permission("ver_clientes")),
    db: Session = Depends(get_db)
):
    """
    Obtiene un cliente específico por su ID.
    
    ⚠️ Requiere autenticación y permiso: ver_clientes
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )
    
    # Super admin puede ver cualquier cliente
    if current_user.rol and current_user.rol.nombre != "super_admin":
        # Otros usuarios solo ven clientes de su empresa
        if cliente.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este cliente"
            )

    return cliente


# ============================================
# ACTUALIZAR CLIENTE
# ============================================


@router.put("/{cliente_id}", response_model=ClienteResponse, summary="Actualizar Cliente")
def actualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    current_user: Usuario = Depends(require_permission("editar_cliente")),
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un cliente existente.

    ⚠️ Requiere autenticación y permiso: editar_cliente

    PUT /clientes/1
    Body:
    {
        "nombre": "Cliente Actualizado"
    }
    """

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Super admin puede actualizar cualquier cliente
    if current_user.rol and current_user.rol.nombre != "super_admin":
        # Otros usuarios solo pueden actualizar clientes de su empresa
        if cliente.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para actualizar este cliente"
            )

    # Si cambian el nombre, validar que sea único en la empresa (case-insensitive)
    if cliente_update.nombre and cliente_update.nombre.lower() != cliente.nombre.lower():
        existente = db.query(Cliente).filter(
            Cliente.empresa_id == cliente.empresa_id,
            func.lower(Cliente.nombre) == func.lower(cliente_update.nombre)
        ).first()
        if existente and existente.id != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un cliente con nombre '{cliente_update.nombre}' en esta empresa"
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
    current_user: Usuario = Depends(require_permission("eliminar_cliente")),
    db: Session = Depends(get_db)
):
    """
    Marca un cliente como inactivo (eliminación lógica).

    ⚠️ Requiere autenticación y permiso: eliminar_cliente

    DELETE /clientes/1
    """

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Super admin puede eliminar cualquier cliente
    if current_user.rol and current_user.rol.nombre != "super_admin":
        # Otros usuarios solo pueden eliminar clientes de su empresa
        if cliente.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar este cliente"
            )

    cliente.estado = EstadoGeneral.inactivo
    db.add(cliente)
    db.commit()

    return None
