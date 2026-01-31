from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database.session import get_db
from app.models.configuracion_vehiculo import ConfiguracionVehiculo
from app.models.marca_vehiculo import MarcaVehiculo
from app.models.enums import EstadoGeneral
from app.schemas.configuracion_vehiculo import ConfiguracionVehiculoResponse

router = APIRouter(
    prefix="/configuracion-vehiculos",
    tags=["Configuración Vehículos"]
)


class ConfiguracionVehiculoCreate(BaseModel):
    """Para crear una configuración de vehículo"""
    marca_id: int
    modelo: int  # año (ej: 2020, 2022)


class ConfiguracionVehiculoUpdate(BaseModel):
    """Para actualizar configuración"""
    marca_id: int = None
    modelo: int = None
    estado: str = None


# ============================================
# OBTENER CONFIGURACIONES
# ============================================

@router.get("/", response_model=list[ConfiguracionVehiculoResponse], summary="Listar Configuraciones")
def listar_configuraciones(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista todas las configuraciones de vehículos activas.
    
    GET /configuracion-vehiculos/
    GET /configuracion-vehiculos/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(ConfiguracionVehiculo)
    
    if not incluir_inactivos:
        query = query.filter(ConfiguracionVehiculo.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/{config_id}", response_model=ConfiguracionVehiculoResponse, summary="Obtener Configuración")
def obtener_configuracion(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una configuración de vehículo específica por su ID.
    
    GET /configuracion-vehiculos/1
    """
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == config_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )

    return config


# ============================================
# CREAR CONFIGURACIÓN
# ============================================

@router.post(
    "/",
    response_model=ConfiguracionVehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Configuración"
)
def crear_configuracion(
    config: ConfiguracionVehiculoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva configuración de vehículo.
    
    POST /configuracion-vehiculos/
    Body:
    {
        "marca_id": 1,
        "modelo": 2020
    }
    
    Esto combina marca + año
    ⚠️ No puede haber duplicada (marca + modelo)
    """
    
    # Validar que la marca exista
    marca = db.query(MarcaVehiculo).filter(
        MarcaVehiculo.id == config.marca_id
    ).first()

    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )

    # Validar que no exista duplicada
    existente = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.marca_id == config.marca_id,
        ConfiguracionVehiculo.modelo == config.modelo
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe configuración para {marca.nombre} modelo {config.modelo}"
        )

    # Crear
    nueva_config = ConfiguracionVehiculo(**config.model_dump())
    db.add(nueva_config)
    db.commit()
    db.refresh(nueva_config)

    return nueva_config


# ============================================
# ACTUALIZAR CONFIGURACIÓN
# ============================================

@router.put("/{config_id}", response_model=ConfiguracionVehiculoResponse)
def actualizar_configuracion(
    config_id: int,
    config_update: ConfiguracionVehiculoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una configuración.
    
    PUT /configuracion-vehiculos/1
    Body:
    {
        "estado": "inactivo"
    }
    """
    
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == config_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )

    # Actualizar solo los campos enviados
    for campo, valor in config_update.model_dump(exclude_unset=True).items():
        setattr(config, campo, valor)

    db.add(config)
    db.commit()
    db.refresh(config)

    return config


# ============================================
# ELIMINAR CONFIGURACIÓN
# ============================================

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_configuracion(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca una configuración como INACTIVA (soft delete).
    
    DELETE /configuracion-vehiculos/1
    
    No elimina los datos, los marca como inactivos. Preserva la auditoría
    y permite recuperación si es necesario.
    """
    
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == config_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )

    # Soft Delete: cambiar estado a inactivo
    config.estado = EstadoGeneral.inactivo
    db.add(config)
    db.commit()

    return None
