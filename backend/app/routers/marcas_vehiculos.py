from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.marca_vehiculo import MarcaVehiculo
from app.models.usuario import Usuario
from app.models.enums import EstadoGeneral
from app.schemas.marca_vehiculo import MarcaVehiculoResponse
from app.auth import get_current_user, require_permission
from pydantic import BaseModel

router = APIRouter(
    prefix="/marcas-vehiculos",
    tags=["Marcas Vehículos"]
)


class MarcaVehiculoCreate(BaseModel):
    """Para crear una marca de vehículo"""
    nombre: str


class MarcaVehiculoUpdate(BaseModel):
    """Para actualizar una marca"""
    nombre: str = None
    estado: str = None


# ============================================
# OBTENER MARCAS
# ============================================

@router.get("/", response_model=list[MarcaVehiculoResponse], summary="Listar Marcas")
def listar_marcas(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas las marcas de vehículos activas.
    
    GET /marcas-vehiculos/
    GET /marcas-vehiculos/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(MarcaVehiculo)
    
    if not incluir_inactivos:
        query = query.filter(MarcaVehiculo.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/{marca_id}", response_model=MarcaVehiculoResponse, summary="Obtener Marca")
def obtener_marca(
    marca_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una marca específica por su ID.
    
    GET /marcas-vehiculos/1
    """
    marca = db.query(MarcaVehiculo).filter(MarcaVehiculo.id == marca_id).first()

    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca de vehículo no encontrada"
        )

    return marca


# ============================================
# CREAR MARCA
# ============================================

@router.post(
    "/",
    response_model=MarcaVehiculoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_marca(
    marca: MarcaVehiculoCreate,
    current_user: Usuario = Depends(require_permission("crear_marca")),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva marca de vehículo.
    
    POST /marcas-vehiculos/
    Body:
    {
        "nombre": "Chevrolet"
    }
    
    ⚠️ El nombre debe ser ÚNICO
    """
    
    # Validar que no exista (case-insensitive)
    existente = db.query(MarcaVehiculo).filter(
        func.lower(MarcaVehiculo.nombre) == func.lower(marca.nombre)
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe marca '{marca.nombre}'"
        )

    # Crear
    nueva_marca = MarcaVehiculo(**marca.model_dump())
    db.add(nueva_marca)
    db.commit()
    db.refresh(nueva_marca)

    return nueva_marca


# ============================================
# ACTUALIZAR MARCA
# ============================================

@router.put("/{marca_id}", response_model=MarcaVehiculoResponse)
def actualizar_marca(
    marca_id: int,
    marca_update: MarcaVehiculoUpdate,
    current_user: Usuario = Depends(require_permission("super_admin")),
    db: Session = Depends(get_db)
):
    """
    Actualiza una marca.
    Solo super_admin puede actualizar marcas.
    
    PUT /marcas-vehiculos/1
    Body:
    {
        "nombre": "Chevrolet Actualizada"
    }
    """
    
    marca = db.query(MarcaVehiculo).filter(MarcaVehiculo.id == marca_id).first()

    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )

    # Actualizar solo los campos enviados
    for campo, valor in marca_update.model_dump(exclude_unset=True).items():
        setattr(marca, campo, valor)

    db.add(marca)
    db.commit()
    db.refresh(marca)

    return marca


# ============================================
# ELIMINAR MARCA
# ============================================

@router.delete("/{marca_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_marca(
    marca_id: int,
    current_user: Usuario = Depends(require_permission("super_admin")),
    db: Session = Depends(get_db)
):
    """
    Marca una marca como INACTIVA (soft delete).
    Solo super_admin puede eliminar marcas.
    
    DELETE /marcas-vehiculos/1
    
    No elimina los datos, los marca como inactivos. Preserva la auditoría
    y permite recuperación si es necesario.
    """
    
    marca = db.query(MarcaVehiculo).filter(MarcaVehiculo.id == marca_id).first()

    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )

    # Soft Delete: cambiar estado a inactivo
    marca.estado = EstadoGeneral.inactivo
    db.add(marca)
    db.commit()

    return None
