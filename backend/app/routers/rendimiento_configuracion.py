from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from app.database.session import get_db
from app.models.rendimiento_configuracion import RendimientoConfiguracion
from app.models.configuracion_vehiculo import ConfiguracionVehiculo
from app.models.usuario import Usuario
from app.models.enums import TipoCarga, TipoTerreno, EstadoGeneral
from app.schemas.rendimiento_configuracion import RendimientoConfiguracionResponse
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/rendimiento-configuracion",
    tags=["Rendimiento Configuración"]
)


class RendimientoConfiguracionCreate(BaseModel):
    """Para crear un rendimiento de configuración"""
    configuracion_id: int
    tipo_carga: TipoCarga
    tipo_terreno: TipoTerreno
    rendimiento_km_galon: Decimal


class RendimientoConfiguracionUpdate(BaseModel):
    """Para actualizar rendimiento"""
    rendimiento_km_galon: Decimal = None
    estado: str = None


# ============================================
# OBTENER RENDIMIENTOS
# ============================================

@router.get("/", response_model=list[RendimientoConfiguracionResponse], summary="Listar Rendimientos")
def listar_rendimientos(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los rendimientos de configuraciones activos.
    
    GET /rendimiento-configuracion/
    GET /rendimiento-configuracion/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(RendimientoConfiguracion)
    
    if not incluir_inactivos:
        query = query.filter(RendimientoConfiguracion.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/configuracion/{config_id}", response_model=list[RendimientoConfiguracionResponse], summary="Listar Rendimientos por Configuración")
def listar_rendimientos_por_configuracion(
    config_id: int,
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista los rendimientos de una configuración específica.
    
    GET /rendimiento-configuracion/configuracion/1
    GET /rendimiento-configuracion/configuracion/1?incluir_inactivos=true  <- Para incluir inactivos
    
    Retorna: Lista de km/galón para cada combinación carga+terreno
    Por defecto solo devuelve estado="activo".
    """
    
    # Validar que la configuración exista
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == config_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )

    query = db.query(RendimientoConfiguracion).filter(
        RendimientoConfiguracion.configuracion_id == config_id
    )
    
    if not incluir_inactivos:
        query = query.filter(RendimientoConfiguracion.estado == EstadoGeneral.activo)

    return query.all()


@router.get("/{rendimiento_id}", response_model=RendimientoConfiguracionResponse, summary="Obtener Rendimiento")
def obtener_rendimiento(
    rendimiento_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un rendimiento específico.
    
    GET /rendimiento-configuracion/1
    """
    rendimiento = db.query(RendimientoConfiguracion).filter(
        RendimientoConfiguracion.id == rendimiento_id
    ).first()

    if not rendimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendimiento no encontrado"
        )

    return rendimiento


# ============================================
# CREAR RENDIMIENTO
# ============================================

@router.post(
    "/",
    response_model=RendimientoConfiguracionResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_rendimiento(
    rendimiento: RendimientoConfiguracionCreate,
    current_user: Usuario = Depends(require_permission("crear_rendimiento")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo rendimiento para una configuración.
    
    POST /rendimiento-configuracion/
    Body:
    {
        "configuracion_id": 1,
        "tipo_carga": "VACIO",
        "tipo_terreno": "PLANO",
        "rendimiento_km_galon": 12.5
    }
    
    Esto significa:
    - Chevrolet 2020 (config 1)
    - Yendo VACIO (sin carga)
    - En terreno PLANO
    - Rinde 12.5 km/galón
    
    ⚠️ No puede haber duplicada (config + carga + terreno)
    """
    
    # Validar que la configuración exista
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == rendimiento.configuracion_id
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )

    # Validar que no exista duplicada
    existente = db.query(RendimientoConfiguracion).filter(
        RendimientoConfiguracion.configuracion_id == rendimiento.configuracion_id,
        RendimientoConfiguracion.tipo_carga == rendimiento.tipo_carga,
        RendimientoConfiguracion.tipo_terreno == rendimiento.tipo_terreno
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe rendimiento para {rendimiento.tipo_carga} + {rendimiento.tipo_terreno}"
        )

    # Crear
    nuevo_rendimiento = RendimientoConfiguracion(**rendimiento.model_dump())
    db.add(nuevo_rendimiento)
    db.commit()
    db.refresh(nuevo_rendimiento)

    return nuevo_rendimiento


# ============================================
# ACTUALIZAR RENDIMIENTO
# ============================================

@router.put("/{rendimiento_id}", response_model=RendimientoConfiguracionResponse)
def actualizar_rendimiento(
    rendimiento_id: int,
    rendimiento_update: RendimientoConfiguracionUpdate,
    current_user: Usuario = Depends(require_permission("super_admin")),
    db: Session = Depends(get_db)
):
    """
    Actualiza el rendimiento.
    Solo super_admin puede actualizar rendimientos.
    
    PUT /rendimiento-configuracion/1
    Body:
    {
        "rendimiento_km_galon": 13.0
    }
    """
    
    rendimiento = db.query(RendimientoConfiguracion).filter(
        RendimientoConfiguracion.id == rendimiento_id
    ).first()

    if not rendimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendimiento no encontrado"
        )

    # Actualizar solo los campos enviados
    for campo, valor in rendimiento_update.model_dump(exclude_unset=True).items():
        setattr(rendimiento, campo, valor)

    db.add(rendimiento)
    db.commit()
    db.refresh(rendimiento)

    return rendimiento


# ============================================
# ELIMINAR RENDIMIENTO
# ============================================

@router.delete("/{rendimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rendimiento(
    rendimiento_id: int,
    current_user: Usuario = Depends(require_permission("super_admin")),
    db: Session = Depends(get_db)
):
    """
    Marca un rendimiento como INACTIVO (soft delete).
    Solo super_admin puede eliminar rendimientos.
    
    DELETE /rendimiento-configuracion/1
    
    No elimina los datos, los marca como inactivos. Preserva la auditoría
    y permite recuperación si es necesario.
    """
    
    rendimiento = db.query(RendimientoConfiguracion).filter(
        RendimientoConfiguracion.id == rendimiento_id
    ).first()

    if not rendimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendimiento no encontrado"
        )

    # Soft Delete: cambiar estado a inactivo
    rendimiento.estado = EstadoGeneral.inactivo
    db.add(rendimiento)
    db.commit()

    return None
