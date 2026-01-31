from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.peaje import Peaje
from app.models.enums import EstadoGeneral
from app.schemas.peaje import (
    PeajeCreate,
    PeajeUpdate,
    PeajeResponse
)

router = APIRouter(
    prefix="/peajes",
    tags=["Peajes"]
)


# ============================================
# OBTENER PEAJES
# ============================================

@router.get("/", response_model=list[PeajeResponse], summary="Listar Peajes")
def listar_peajes(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista todos los peajes activos del sistema.
    
    GET /peajes/
    GET /peajes/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(Peaje)
    
    if not incluir_inactivos:
        query = query.filter(Peaje.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/{peaje_id}", response_model=PeajeResponse, summary="Obtener Peaje")
def obtener_peaje(
    peaje_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un peaje específico por su ID.
    
    GET /peajes/1
    """
    peaje = db.query(Peaje).filter(Peaje.id == peaje_id).first()

    if not peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peaje no encontrado"
        )

    return peaje


# ============================================
# CREAR PEAJE
# ============================================

@router.post(
    "/",
    response_model=PeajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Peaje"
)
def crear_peaje(
    peaje: PeajeCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo peaje en el sistema.
    
    POST /peajes/
    Body:
    {
        "nombre": "Peaje La Loma",
        "costo": 5500
    }
    
    ⚠️ El nombre debe ser ÚNICO
    """
    
    # Validar que no exista con el mismo nombre (case-insensitive)
    existente = db.query(Peaje).filter(
        func.lower(Peaje.nombre) == func.lower(peaje.nombre)
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un peaje con nombre '{peaje.nombre}'"
        )

    # Crear nuevo peaje
    nuevo_peaje = Peaje(**peaje.model_dump())
    db.add(nuevo_peaje)
    db.commit()
    db.refresh(nuevo_peaje)

    return nuevo_peaje


# ============================================
# ACTUALIZAR PEAJE
# ============================================

@router.put("/{peaje_id}", response_model=PeajeResponse, summary="Actualizar Peaje")
def actualizar_peaje(
    peaje_id: int,
    peaje_update: PeajeUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un peaje existente.
    
    PUT /peajes/1
    Body:
    {
        "nombre": "Peaje La Loma (Actualizado)",
        "costo": 6000
    }
    """
    
    peaje = db.query(Peaje).filter(Peaje.id == peaje_id).first()

    if not peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peaje no encontrado"
        )

    # Si cambian el nombre, validar que sea único
    if peaje_update.nombre and peaje_update.nombre.lower() != peaje.nombre.lower():
        existente = db.query(Peaje).filter(
            func.lower(Peaje.nombre) == func.lower(peaje_update.nombre)
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un peaje con nombre '{peaje_update.nombre}'"
            )

    # Actualizar solo los campos enviados
    for campo, valor in peaje_update.model_dump(exclude_unset=True).items():
        setattr(peaje, campo, valor)

    db.add(peaje)
    db.commit()
    db.refresh(peaje)

    return peaje


# ============================================
# ELIMINAR PEAJE
# ============================================

@router.delete("/{peaje_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Peaje")
def eliminar_peaje(
    peaje_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca un peaje como inactivo (eliminación lógica).
    
    DELETE /peajes/1
    
    No elimina los datos, los marca como inactivos.
    Se preserva auditoría e historial.
    """
    
    peaje = db.query(Peaje).filter(Peaje.id == peaje_id).first()

    if not peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peaje no encontrado"
        )

    # Soft Delete: cambiar estado a inactivo
    peaje.estado = EstadoGeneral.inactivo
    db.add(peaje)
    db.commit()

    return None
