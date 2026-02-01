from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional

from app.database.session import get_db
from app.models.tramo import Tramo
from app.models.peaje import Peaje
from app.models.tramo_peaje import TramoPeaje
from app.models.usuario import Usuario
from app.schemas.tramo import TramoResponse, TramoCreate, TramoUpdate
from app.models.enums import EstadoGeneral
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/tramos",
    tags=["Tramos"]
)


# ============================================
# OBTENER TRAMOS
# ============================================

@router.get("/", response_model=list[TramoResponse], summary="Listar Tramos")
def listar_tramos(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los tramos activos del sistema.
    
    GET /tramos/
    GET /tramos/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(Tramo)
    
    if not incluir_inactivos:
        query = query.filter(Tramo.estado == EstadoGeneral.activo)
    
    return query.all()


@router.get("/{tramo_id}", response_model=TramoResponse, summary="Obtener Tramo")
def obtener_tramo(
    tramo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un tramo específico por su ID.
    
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
    status_code=status.HTTP_201_CREATED,
    summary="Crear Tramo"
)
def crear_tramo(
    tramo: TramoCreate,
    current_user: Usuario = Depends(require_permission("crear_tramo")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo tramo con opción de asociar peajes.
    
    POST /tramos/
    
    Body sin peajes:
    {
        "origen": "Mediacanoa",
        "destino": "Buenaventura"
    }
    
    Body con peajes:
    {
        "origen": "Mediacanoa",
        "destino": "Buenaventura",
        "peaje_ids": [1, 2, 3]
    }
    
    ⚠️ No puede haber dos tramos con origen+destino iguales
    ⚠️ Los peajes deben existir en la base de datos
    ⚠️ Se valida que no haya duplicados de peajes en el mismo tramo
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

    # Crear tramo
    nuevo_tramo = Tramo(
        origen=tramo.origen,
        destino=tramo.destino
    )
    db.add(nuevo_tramo)
    db.flush()  # Flush para obtener el ID sin commit
    
    # Asociar peajes si se proporcionan
    if tramo.peaje_ids:
        peajes_validos = []
        
        for peaje_id in tramo.peaje_ids:
            # Validar que el peaje exista
            peaje = db.query(Peaje).filter(
                Peaje.id == peaje_id,
                Peaje.estado == EstadoGeneral.activo
            ).first()
            
            if not peaje:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Peaje con ID {peaje_id} no encontrado o inactivo"
                )
            
            # Validar que no haya duplicados
            if peaje_id not in peajes_validos:
                peajes_validos.append(peaje_id)
        
        # Crear relaciones TramoPeaje
        for peaje_id in peajes_validos:
            tramo_peaje = TramoPeaje(
                tramo_id=nuevo_tramo.id,
                peaje_id=peaje_id
            )
            db.add(tramo_peaje)
    
    db.commit()
    db.refresh(nuevo_tramo)

    return nuevo_tramo


# ============================================
# ACTUALIZAR TRAMO
# ============================================

@router.put(
    "/{tramo_id}",
    response_model=TramoResponse,
    summary="Actualizar Tramo"
)
def actualizar_tramo(
    tramo_id: int,
    tramo_update: TramoUpdate,
    current_user: Usuario = Depends(require_permission("editar_tramo")),
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un tramo existente.
    
    PUT /tramos/1
    
    Body (todos los campos son opcionales):
    {
        "origen": "Mediacanoa",
        "destino": "Buenaventura"
    }
    
    ⚠️ No puede cambiar origen+destino a valores que ya existan en otro tramo activo
    """
    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()
    
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )
    
    # Si cambian origen o destino, validar que no exista otro tramo con esa combinación
    if tramo_update.origen or tramo_update.destino:
        nuevo_origen = tramo_update.origen or tramo.origen
        nuevo_destino = tramo_update.destino or tramo.destino
        
        # Validar que la nueva combinación sea única (case-insensitive)
        existente = db.query(Tramo).filter(
            func.lower(Tramo.origen) == func.lower(nuevo_origen),
            func.lower(Tramo.destino) == func.lower(nuevo_destino),
            Tramo.estado == EstadoGeneral.activo,
            Tramo.id != tramo_id  # Excluir el tramo actual
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un tramo de {nuevo_origen} a {nuevo_destino}"
            )
    
    # Actualizar solo los campos que se enviaron
    actualizar_datos = tramo_update.model_dump(exclude_unset=True)
    
    for campo, valor in actualizar_datos.items():
        setattr(tramo, campo, valor)
    
    db.add(tramo)
    db.commit()
    db.refresh(tramo)
    
    return tramo


# ============================================
# GESTIÓN DE PEAJES EN TRAMOS
# ============================================

@router.post("/{tramo_id}/peajes/{peaje_id}", summary="Asociar Peaje a Tramo")
def agregar_peaje_a_tramo(
    tramo_id: int,
    peaje_id: int,
    current_user: Usuario = Depends(require_permission("editar_tramo")),
    db: Session = Depends(get_db)
):
    """
    Asocia un peaje a un tramo.
    
    POST /tramos/1/peajes/5
    
    Un peaje NO se puede repetir en el mismo tramo.
    Esto permite calcular automáticamente los peajes de una ruta
    sumando los peajes de todos sus tramos.
    """
    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )
    
    # Validar que el peaje exista
    peaje = db.query(Peaje).filter(Peaje.id == peaje_id).first()
    if not peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peaje no encontrado"
        )
    
    # Validar que no exista la asociación
    existente = db.query(TramoPeaje).filter(
        TramoPeaje.tramo_id == tramo_id,
        TramoPeaje.peaje_id == peaje_id
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este peaje ya está asociado a este tramo"
        )
    
    # Crear asociación
    tramo_peaje = TramoPeaje(
        tramo_id=tramo_id,
        peaje_id=peaje_id
    )
    db.add(tramo_peaje)
    db.commit()
    db.refresh(tramo_peaje)
    
    return {
        "mensaje": "Peaje asociado al tramo exitosamente",
        "tramo": f"{tramo.origen} - {tramo.destino}",
        "peaje": peaje.nombre_peaje,
        "costo": float(peaje.costo)
    }


@router.get("/{tramo_id}/peajes", summary="Listar Peajes de un Tramo")
def listar_peajes_de_tramo(
    tramo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los peajes asociados a un tramo.
    
    GET /tramos/1/peajes
    """
    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )
    
    # Obtener peajes del tramo
    tramos_peajes = db.query(TramoPeaje).filter(
        TramoPeaje.tramo_id == tramo_id
    ).all()
    
    peajes = []
    for tp in tramos_peajes:
        peaje = tp.peaje
        peajes.append({
            "id": peaje.id,
            "nombre_peaje": peaje.nombre_peaje,
            "sector": peaje.sector,
            "costo": float(peaje.costo),
            "ubicacion": peaje.ubicacion,
            "fuente": peaje.fuente
        })
    
    return {
        "tramo": f"{tramo.origen} - {tramo.destino}",
        "total_peajes": len(peajes),
        "costo_total_peajes": sum(p["costo"] for p in peajes),
        "peajes": peajes
    }


@router.delete("/{tramo_id}/peajes/{peaje_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Quitar Peaje de Tramo")
def quitar_peaje_de_tramo(
    tramo_id: int,
    peaje_id: int,
    current_user: Usuario = Depends(require_permission("editar_tramo")),
    db: Session = Depends(get_db)
):
    """
    Quita la asociación de un peaje con un tramo.
    
    DELETE /tramos/1/peajes/5
    """
    # Buscar la asociación
    tramo_peaje = db.query(TramoPeaje).filter(
        TramoPeaje.tramo_id == tramo_id,
        TramoPeaje.peaje_id == peaje_id
    ).first()
    
    if not tramo_peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asociación tramo-peaje no encontrada"
        )
    
    db.delete(tramo_peaje)
    db.commit()
    
    return None


# ============================================
# ELIMINAR TRAMO (Soft Delete)
# ============================================

@router.delete("/{tramo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Tramo")
def eliminar_tramo(
    tramo_id: int,
    current_user: Usuario = Depends(require_permission("eliminar_tramo")),
    db: Session = Depends(get_db)
):
    """
    Marca un tramo como inactivo (eliminación lógica).
    
    DELETE /tramos/1
    
    ⚠️ El tramo no se elimina de la BD, solo se marca como inactivo
    """
    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()
    
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )
    
    # Realizar soft delete
    tramo.estado = EstadoGeneral.inactivo
    db.add(tramo)
    db.commit()
    
    return None
