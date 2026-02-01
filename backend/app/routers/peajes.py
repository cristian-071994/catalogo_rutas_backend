from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.peaje import Peaje
from app.models.usuario import Usuario
from app.models.enums import EstadoGeneral
from app.schemas.peaje import (
    PeajeCreate,
    PeajeUpdate,
    PeajeResponse
)
from app.auth import get_current_user, require_permission
from app.services.peaje_sync_service import sincronizar_peajes_desde_api

router = APIRouter(
    prefix="/peajes",
    tags=["Peajes"]
)


# ============================================
# SINCRONIZACIÓN
# ============================================

@router.post("/sincronizar", summary="Sincronizar Peajes desde API Oficial")
async def sincronizar_peajes(
    current_user: Usuario = Depends(require_permission("crear_peaje")),
    db: Session = Depends(get_db)
):
    """
    Sincroniza peajes desde la API oficial del gobierno colombiano.
    
    POST /peajes/sincronizar
    
    Descarga todos los peajes de https://www.datos.gov.co/resource/68qj-5xux.json
    y actualiza/crea en la base de datos.
    
    Solo actualiza peajes de fuente "API_GOBIERNO", respeta los manuales.
    Usa la tarifa de Categoría V (camiones).
    
    Requiere permiso: crear_peaje
    """
    resultado = await sincronizar_peajes_desde_api(db)
    
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resultado.get("error", "Error desconocido en sincronización")
        )
    
    return {
        "message": "Sincronización completada exitosamente",
        **resultado
    }


# ============================================
# OBTENER PEAJES
# ============================================

@router.get("/", response_model=list[PeajeResponse], summary="Listar Peajes")
def listar_peajes(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
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
    current_user: Usuario = Depends(get_current_user),
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


@router.get("/buscar/por-nombre", response_model=list[PeajeResponse], summary="Buscar Peajes")
def buscar_peajes(
    q: str = "",
    limite: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca peajes por nombre (búsqueda LIKE, case-insensitive).
    
    GET /peajes/buscar/por-nombre?q=lobo
    GET /peajes/buscar/por-nombre?q=lobo&limite=100
    
    Ejemplos:
    - ?q=lobo → devuelve "Lobo Guerrero", "Lobo Sur", etc.
    - ?q=la mesa → devuelve todos con "la mesa" en nombre
    - ?q= (vacío) → devuelve todos
    
    Requiere: estar autenticado
    Parámetros:
    - q: término de búsqueda (LIKE)
    - limite: máximo de resultados (default: 50)
    """
    if not q or q.strip() == "":
        # Si no hay búsqueda, devuelve los primeros N activos
        return db.query(Peaje).filter(
            Peaje.estado == EstadoGeneral.activo
        ).limit(limite).all()
    
    # Búsqueda LIKE case-insensitive
    termino = f"%{q.strip()}%"
    peajes = db.query(Peaje).filter(
        Peaje.estado == EstadoGeneral.activo,
        Peaje.nombre_peaje.ilike(termino)
    ).limit(limite).all()
    
    return peajes


# ============================================
# CREAR PEAJE
# ============================================

@router.post(
    "/",
    response_model=PeajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Peaje Manual"
)
def crear_peaje(
    peaje: PeajeCreate,
    current_user: Usuario = Depends(require_permission("crear_peaje")),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo peaje MANUAL en el sistema.
    
    POST /peajes/
    Body:
    {
        "nombre_peaje": "Peaje La Loma",
        "sector": "Cali - Buga",
        "costo": 15000,
        "longitud": -76.328497,
        "latitud": 3.995509
    }
    
    ⚠️ El nombre debe ser ÚNICO
    ⚠️ Los peajes creados manualmente no se sobrescriben en sincronización
    """
    
    # Validar que no exista con el mismo nombre (case-insensitive)
    existente = db.query(Peaje).filter(
        func.lower(Peaje.nombre_peaje) == func.lower(peaje.nombre_peaje)
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un peaje con nombre '{peaje.nombre_peaje}'"
        )

    # Crear nuevo peaje
    nuevo_peaje = Peaje(
        **peaje.model_dump(),
        fuente="MANUAL"  # Marcar como manual
    )
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
    current_user: Usuario = Depends(require_permission("editar_peaje")),
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
    current_user: Usuario = Depends(require_permission("eliminar_peaje")),
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
