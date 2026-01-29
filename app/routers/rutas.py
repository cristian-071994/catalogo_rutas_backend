from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from pydantic import BaseModel

from app.database.session import get_db
from app.models.ruta import Ruta
from app.models.cliente import Cliente
from app.models.tramo_ruta import TramoRuta
from app.models.tramo import Tramo
from app.models.ruta_peaje import RutaPeaje
from app.models.peaje import Peaje
from app.models.enums import DireccionPeaje, EstadoGeneral
from app.schemas.ruta import RutaCreate, RutaResponse, RutaUpdate
from app.services.ruta_service import calcular_costo_ruta_detallado


router = APIRouter(prefix="/rutas", tags=["Rutas"])

# Crear ruta
@router.post(
    "/",
    response_model=RutaResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_ruta(
    ruta: RutaCreate,
    db: Session = Depends(get_db)
):
    # 1. Validar que el cliente exista
    cliente = db.query(Cliente).filter(
        Cliente.id == ruta.cliente_id
    ).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El cliente especificado no existe"
        )

    # 2. Crear la ruta
    nueva_ruta = Ruta(
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
        cliente_id=ruta.cliente_id
    )

    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    return nueva_ruta


# Consultar las rutas - Listar
@router.get("/", response_model=list[RutaResponse])
def listar_rutas(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista rutas ACTIVAS por defecto.
    
    GET /rutas/
    GET /rutas/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(Ruta)
    
    if not incluir_inactivos:
        query = query.filter(Ruta.estado == EstadoGeneral.activo)
    
    return query.all()



# Consultar ruta por id
@router.get("/{ruta_id}", response_model=RutaResponse)
def obtener_ruta(ruta_id: int, db: Session = Depends(get_db)):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    return ruta


# ============================================
# AGREGAR TRAMO A RUTA
# ============================================

@router.post("/{ruta_id}/tramos/{tramo_id}")
def agregar_tramo_a_ruta(
    ruta_id: int,
    tramo_id: int,
    orden: int,
    db: Session = Depends(get_db)
):
    """
    Agrega un tramo a una ruta en una posición específica.
    
    POST /rutas/1/tramos/2?orden=1
    
    Esto crea la relación TramoRuta
    """
    
    # Validar que la ruta exista
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Validar que el tramo exista
    tramo = db.query(Tramo).filter(Tramo.id == tramo_id).first()
    if not tramo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado"
        )

    # Validar que no exista ya
    existente = db.query(TramoRuta).filter(
        TramoRuta.ruta_id == ruta_id,
        TramoRuta.tramo_id == tramo_id
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este tramo ya está en la ruta"
        )

    # Crear TramoRuta
    tramo_ruta = TramoRuta(
        ruta_id=ruta_id,
        tramo_id=tramo_id,
        orden=orden
    )

    db.add(tramo_ruta)
    db.commit()
    db.refresh(tramo_ruta)

    return {
        "mensaje": "Tramo agregado a la ruta",
        "tramo_ruta_id": tramo_ruta.id,
        "orden": tramo_ruta.orden
    }


# ============================================
# AGREGAR PEAJE A RUTA
# ============================================

class AgregarPeajeRequest(BaseModel):
    """Body para agregar peaje a ruta"""
    orden: int = None
    direccion: DireccionPeaje = DireccionPeaje.IDA


@router.post("/{ruta_id}/peajes/{peaje_id}")
def agregar_peaje_a_ruta(
    ruta_id: int,
    peaje_id: int,
    peaje_data: AgregarPeajeRequest,
    db: Session = Depends(get_db)
):
    """
    Agrega un peaje a una ruta, permitiendo el mismo peaje múltiples veces (IDA y REGRESO).
    
    POST /rutas/1/peajes/2
    Body:
    {
        "orden": 1,
        "direccion": "IDA"
    }
    
    Esto crea la relación RutaPeaje
    Ahora PERMITE el mismo peaje dos veces: IDA y REGRESO
    """
    
    # Validar que la ruta exista
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Validar que el peaje exista
    peaje = db.query(Peaje).filter(Peaje.id == peaje_id).first()
    if not peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peaje no encontrado"
        )

    # Validar que no exista CON LA MISMA DIRECCIÓN
    existente = db.query(RutaPeaje).filter(
        RutaPeaje.ruta_id == ruta_id,
        RutaPeaje.peaje_id == peaje_id,
        RutaPeaje.direccion == peaje_data.direccion
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Este peaje ya está en la ruta en dirección {peaje_data.direccion}"
        )

    # Crear RutaPeaje con dirección
    ruta_peaje = RutaPeaje(
        ruta_id=ruta_id,
        peaje_id=peaje_id,
        orden=peaje_data.orden,
        direccion=peaje_data.direccion
    )

    db.add(ruta_peaje)
    db.commit()
    db.refresh(ruta_peaje)

    return {
        "mensaje": "Peaje agregado a la ruta",
        "ruta_peaje_id": ruta_peaje.id,
        "peaje_nombre": peaje.nombre,
        "peaje_costo": float(peaje.costo),
        "direccion": ruta_peaje.direccion
    }
        


# ============================================
# VER RESUMEN DE RUTA (CON COSTOS)
# ============================================

@router.get("/{ruta_id}/resumen")
def obtener_resumen_ruta(
    ruta_id: int,
    configuracion_id: int,
    precio_galon: Decimal = None,
    db: Session = Depends(get_db)
):
    """
    ENDPOINT PRINCIPAL: Obtiene el resumen DETALLADO de costos de una ruta.
    
    GET /rutas/1/resumen?configuracion_id=1&precio_galon=9500
    
    Retorna información desmenuzada:
    - Por cada detalle de tramo: km, rendimiento, galones
    - Por cada tramo: total km y galones
    - Por cada peaje: nombre, costo, dirección
    - Resumen final: galones y costos totales
    """
    
    # Si no envían precio_galon, obtenerlo de la BD
    if not precio_galon:
        from app.models.configuracion import ConfiguracionGeneral
        config = db.query(ConfiguracionGeneral).filter(
            ConfiguracionGeneral.clave == "precio_galon"
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontró precio_galon en configuración. Envíalo como parámetro."
            )
        
        precio_galon = Decimal(config.valor)

    # Calcular costo detallado
    resumen = calcular_costo_ruta_detallado(
        db=db,
        ruta_id=ruta_id,
        configuracion_id=configuracion_id,
        precio_galon=precio_galon
    )

    if not resumen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    return resumen.to_dict()


# ============================================
# ACTUALIZAR RUTA
# ============================================

@router.put("/{ruta_id}", response_model=RutaResponse)
def actualizar_ruta(
    ruta_id: int,
    ruta_update: RutaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una ruta.
    
    PUT /rutas/1
    Body:
    {
        "nombre": "Nueva Ruta",
        "descripcion": "Descripción actualizada",
        "estado": "inactivo"
    }
    """
    
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Actualizar solo los campos enviados
    for campo, valor in ruta_update.model_dump(exclude_unset=True).items():
        setattr(ruta, campo, valor)

    db.add(ruta)
    db.commit()
    db.refresh(ruta)

    return ruta


# ============================================
# ELIMINAR RUTA (Soft Delete - cambiar a inactivo)
# ============================================

@router.delete("/{ruta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ruta(
    ruta_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca una ruta como INACTIVA (soft delete).
    
    DELETE /rutas/1
    
    Esto NO elimina los datos, solo los marca como inactivos.
    Así se preserva auditoría e historial.
    
    Para recuperar: PUT /rutas/1 con estado="activo"
    """
    
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Soft Delete: cambiar estado a inactivo
    ruta.estado = EstadoGeneral.inactivo
    db.add(ruta)
    db.commit()

    return None


# ============================================
# LISTAR RUTAS POR CLIENTE
# ============================================

@router.get("/cliente/{cliente_id}", response_model=list[RutaResponse])
def listar_rutas_por_cliente(
    cliente_id: int,
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista rutas ACTIVAS de un cliente por defecto.
    
    GET /rutas/cliente/1
    GET /rutas/cliente/1?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    
    # Validar que el cliente exista
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    query = db.query(Ruta).filter(Ruta.cliente_id == cliente_id)
    
    if not incluir_inactivos:
        query = query.filter(Ruta.estado == EstadoGeneral.activo)
    
    return query.all()


# ============================================
# ELIMINAR TRAMO DE UNA RUTA
# ============================================

@router.delete("/{ruta_id}/tramos/{tramo_ruta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tramo_de_ruta(
    ruta_id: int,
    tramo_ruta_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un tramo de una ruta (rompe la relación TramoRuta).
    
    DELETE /rutas/1/tramos/5
    
    Esto NO elimina el tramo en sí, solo lo saca de la ruta.
    """
    
    # Validar que la ruta exista
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Obtener la relación TramoRuta
    tramo_ruta = db.query(TramoRuta).filter(
        TramoRuta.id == tramo_ruta_id,
        TramoRuta.ruta_id == ruta_id
    ).first()

    if not tramo_ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tramo no encontrado en esta ruta"
        )

    db.delete(tramo_ruta)
    db.commit()

    return None


# ============================================
# ELIMINAR PEAJE DE UNA RUTA
# ============================================

@router.delete("/{ruta_id}/peajes/{ruta_peaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_peaje_de_ruta(
    ruta_id: int,
    ruta_peaje_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un peaje de una ruta (rompe la relación RutaPeaje).
    
    DELETE /rutas/1/peajes/3
    
    Esto NO elimina el peaje en sí, solo lo saca de la ruta.
    """
    
    # Validar que la ruta exista
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Obtener la relación RutaPeaje
    ruta_peaje = db.query(RutaPeaje).filter(
        RutaPeaje.id == ruta_peaje_id,
        RutaPeaje.ruta_id == ruta_id
    ).first()

    if not ruta_peaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peaje no encontrado en esta ruta"
        )

    db.delete(ruta_peaje)
    db.commit()

    return None
