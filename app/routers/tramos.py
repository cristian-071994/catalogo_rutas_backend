from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database.session import get_db
from app.models.tramo import Tramo
from app.schemas.tramo import TramoResponse
from app.models.enums import EstadoGeneral

router = APIRouter(
    prefix="/tramos",
    tags=["Tramos"]
)


class TramoCreate(BaseModel):
    """Para crear un tramo"""
    origen: str
    destino: str


# ============================================
# OBTENER TRAMOS
# ============================================

@router.get("/", response_model=list[TramoResponse])
def listar_tramos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista tramos ACTIVOS por defecto.
    
    GET /tramos/
    GET /tramos/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(Tramo)
    
    if not incluir_inactivos:
        query = query.filter(Tramo.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/{tramo_id}", response_model=TramoResponse)
def obtener_tramo(
    tramo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un tramo específico por ID.
    
    GET /tramos/1
    """
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()

    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )

    return tramo


# ============================================
# CREAR TRAMO
# ============================================

@router.post(
    "/",
    response_model=TramoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_tramo(
    tramo: TramoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo tramo.
    
    POST /tramos/
    Body:
    {
        "origen": "Mediacanoa",
        "destino": "Buenaventura"
    }
    
    ⚠️ No puede haber dos tramos con origen+destino iguales
    """
    
    # Validar que no exista (case-insensitive)
    existente = db.query(Tramo).filter(
        func.lower(Tramo.origen) == func.lower(tramo.origen),
        func.lower(Tramo.destino) == func.lower(tramo.destino),
        Tramo.estado == EstadoGeneral.activo
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe tramo de {tramo.origen} a {tramo.destino}"
        )

    # Crear
    nuevo_tramo = Tramo(**tramo.model_dump())
    db.add(nuevo_tramo)
    db.commit()
    db.refresh(nuevo_tramo)

    return nuevo_tramo
