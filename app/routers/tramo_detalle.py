from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from app.database.session import get_db
from app.models.tramo_detalle import TramoDetalle
from app.models.tramo import Tramo
from app.schemas.tramo_detalle import TramoDetalleResponse
from app.models.enums import TipoCarga, TipoTerreno, EstadoGeneral

router = APIRouter(
    prefix="/tramo-detalle",
    tags=["Tramo Detalle"]
)


class TramoDetalleCreate(BaseModel):
    """Para crear un detalle de tramo"""
    tramo_id: int
    tipo_carga: TipoCarga
    tipo_terreno: TipoTerreno
    kilometros: Decimal


# ============================================
# OBTENER DETALLES DE TRAMO
# ============================================

@router.get("/tramo/{tramo_id}", response_model=list[TramoDetalleResponse], summary="Listar Detalles de Tramo")
def listar_detalles_tramo(
    tramo_id: int,
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista los detalles de un tramo específico.
    
    GET /tramo-detalle/tramo/1
    GET /tramo-detalle/tramo/1?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Retorna: Lista de configuraciones (vacio/cargado + plano/montaña + km)
    Por defecto solo devuelve estado="activo".
    """
    
    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )

    query = db.query(TramoDetalle).filter(TramoDetalle.tramo_id == tramo_id)
    
    if not incluir_inactivos:
        query = query.filter(TramoDetalle.estado == EstadoGeneral.activo)

    return query.all()


@router.get("/{detalle_id}", response_model=TramoDetalleResponse, summary="Obtener Detalle de Tramo")
def obtener_detalle(
    detalle_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un detalle de tramo específico por su ID.
    
    GET /tramo-detalle/1
    """
    detalle = db.query(TramoDetalle).filter(
        TramoDetalle.id == detalle_id
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle de tramo no encontrado"
        )

    return detalle


# ============================================
# CREAR DETALLE DE TRAMO
# ============================================

@router.post(
    "/",
    response_model=TramoDetalleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Detalle de Tramo"
)
def crear_detalle_tramo(
    detalle: TramoDetalleCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo detalle de tramo.
    
    POST /tramo-detalle/
    Body:
    {
        "tramo_id": 1,
        "tipo_carga": "VACIO",
        "tipo_terreno": "PLANO",
        "kilometros": 10.5
    }
    
    ⚠️ No puedes tener dos detalles iguales en el mismo tramo
    """
    
    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == detalle.tramo_id).first()
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )

    # Validar que no exista
    existente = db.query(TramoDetalle).filter(
        TramoDetalle.tramo_id == detalle.tramo_id,
        TramoDetalle.tipo_carga == detalle.tipo_carga,
        TramoDetalle.tipo_terreno == detalle.tipo_terreno,
        TramoDetalle.estado == EstadoGeneral.activo
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe detalle para {detalle.tipo_carga} + {detalle.tipo_terreno} en este tramo"
        )

    # Crear
    nuevo_detalle = TramoDetalle(**detalle.model_dump())
    db.add(nuevo_detalle)
    db.commit()
    db.refresh(nuevo_detalle)

    return nuevo_detalle


# ============================================
# ACTUALIZAR DETALLE DE TRAMO
# ============================================

@router.put("/{detalle_id}", response_model=TramoDetalleResponse)
def actualizar_detalle_tramo(
    detalle_id: int,
    detalle_update: TramoDetalleCreate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un detalle de tramo.
    
    PUT /tramo-detalle/1
    Body:
    {
        "tramo_id": 1,
        "tipo_carga": "VACIO",
        "tipo_terreno": "PLANO",
        "kilometros": 15.0
    }
    """
    
    detalle = db.query(TramoDetalle).filter(
        TramoDetalle.id == detalle_id
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle de tramo no encontrado"
        )

    # Actualizar campos
    detalle.kilometros = detalle_update.kilometros
    
    db.add(detalle)
    db.commit()
    db.refresh(detalle)

    return detalle


# ============================================
# ELIMINAR DETALLE DE TRAMO
# ============================================

@router.delete("/{detalle_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_detalle_tramo(
    detalle_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca un detalle de tramo como INACTIVO (soft delete).
    
    DELETE /tramo-detalle/1
    
    No elimina los datos, los marca como inactivos.
    """
    
    detalle = db.query(TramoDetalle).filter(
        TramoDetalle.id == detalle_id
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle de tramo no encontrado"
        )

    # Soft Delete: cambiar estado a inactivo
    detalle.estado = EstadoGeneral.inactivo
    db.add(detalle)
    db.commit()

    return None
