from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database.session import get_db
from app.models.vehiculo import Vehiculo
from app.models.configuracion_vehiculo import ConfiguracionVehiculo
from app.models.usuario import Usuario
from app.models.enums import EstadoGeneral
from app.schemas.vehiculo import VehiculoResponse
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"]
)


class VehiculoCreate(BaseModel):
    """Para crear un vehículo"""
    placa: str
    configuracion_id: int


class VehiculoUpdate(BaseModel):
    """Para actualizar un vehículo"""
    placa: str = None
    configuracion_id: int = None
    estado: str = None


# ============================================
# OBTENER VEHÍCULOS
# ============================================

@router.get("/", response_model=list[VehiculoResponse], summary="Listar Vehículos")
def listar_vehiculos(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los vehículos activos del sistema.
    
    GET /vehiculos/
    GET /vehiculos/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(Vehiculo)
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(Vehiculo.empresa_id == current_user.empresa_id)
    
    if not incluir_inactivos:
        query = query.filter(Vehiculo.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/{vehiculo_id}", response_model=VehiculoResponse, summary="Obtener Vehículo")
def obtener_vehiculo(
    vehiculo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un vehículo específico por su ID.
    
    GET /vehiculos/1
    """
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if vehiculo.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
            )

    return vehiculo


# ============================================
# CREAR VEHÍCULO
# ============================================

@router.post(
    "/",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_vehiculo(
    vehiculo: VehiculoCreate,
    current_user: Usuario = Depends(require_permission("crear_vehiculo")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo vehículo.
    
    POST /vehiculos/
    Body:
    {
        "placa": "ABC123",
        "configuracion_id": 1
    }
    
    Esto significa:
    - Vehículo con placa ABC123
    - Es un Chevrolet 2020 (configuracion_id 1)
    
    ⚠️ La placa debe ser ÚNICA
    """
    
    # Validar que la configuración exista
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == vehiculo.configuracion_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )

    # Validar que no exista con la misma placa (case-insensitive)
    existente = db.query(Vehiculo).filter(
        func.lower(Vehiculo.placa) == func.lower(vehiculo.placa)
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe vehículo con placa '{vehiculo.placa}'"
        )

    # Crear
    nuevo_vehiculo = Vehiculo(
        **vehiculo.model_dump(),
        empresa_id=current_user.empresa_id  # Multi-tenancy: asignar empresa del usuario
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)

    return nuevo_vehiculo


# ============================================
# ACTUALIZAR VEHÍCULO
# ============================================

@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo_update: VehiculoUpdate,
    current_user: Usuario = Depends(require_permission("editar_vehiculo")),
    db: Session = Depends(get_db)
):
    """
    Actualiza un vehículo.
    
    PUT /vehiculos/1
    Body:
    {
        "estado": "inactivo"
    }
    """
    
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if vehiculo.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
            )

    # Actualizar solo los campos enviados
    for campo, valor in vehiculo_update.model_dump(exclude_unset=True).items():
        setattr(vehiculo, campo, valor)

    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)

    return vehiculo


# ============================================
# ELIMINAR VEHÍCULO
# ============================================

@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(
    vehiculo_id: int,
    current_user: Usuario = Depends(require_permission("eliminar_vehiculo")),
    db: Session = Depends(get_db)
):
    """
    Marca un vehículo como INACTIVO (soft delete).
    
    DELETE /vehiculos/1
    
    No elimina los datos, los marca como inactivos. Preserva la auditoría
    y permite recuperación si es necesario.
    """
    
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado"
        )

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if vehiculo.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
            )

    # Soft Delete: cambiar estado a inactivo
    vehiculo.estado = EstadoGeneral.inactivo
    db.add(vehiculo)
    db.commit()

    return None
