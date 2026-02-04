from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from pydantic import BaseModel

from app.database.session import get_db
from app.models.ruta import Ruta
from app.models.cliente import Cliente
from app.models.tramo_ruta import TramoRuta
from app.models.vehiculo import Vehiculo
from app.models.tramo import Tramo
from app.models.ruta_peaje import RutaPeaje
from app.models.peaje import Peaje
from app.models.usuario import Usuario
from app.models.enums import DireccionPeaje, EstadoGeneral
from app.schemas.ruta import RutaCreate, RutaResponse, RutaUpdate
from app.services.ruta_service import calcular_costo_ruta_detallado
from app.auth import get_current_user, require_permission


router = APIRouter(prefix="/rutas", tags=["Rutas"])

# Crear ruta
@router.post(
    "/",
    response_model=RutaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Ruta"
)
def crear_ruta(
    ruta: RutaCreate,
    current_user: Usuario = Depends(require_permission("crear_ruta")),
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
    
    # 2. Validar multi-tenancy: el cliente debe ser de la misma empresa
    # Super admin puede asociar cualquier cliente
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if cliente.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes asociar clientes de otra empresa"
            )

    # 3. Crear la ruta
    nueva_ruta = Ruta(
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
        cliente_id=ruta.cliente_id,
        empresa_id=current_user.empresa_id  # Multi-tenancy: asignar empresa del usuario
    )

    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    return nueva_ruta


# Consultar las rutas - Listar
@router.get("/", response_model=list[RutaResponse], summary="Listar Rutas")
def listar_rutas(
    incluir_inactivos: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas las rutas activas del sistema.
    
    GET /rutas/
    GET /rutas/?incluir_inactivos=true  <- Para incluir inactivos (soporte)
    
    Por defecto solo devuelve estado="activo".
    Agregue ?incluir_inactivos=true solo si necesita ver registros eliminados.
    """
    query = db.query(Ruta)
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(Ruta.empresa_id == current_user.empresa_id)
    
    if not incluir_inactivos:
        query = query.filter(Ruta.estado == EstadoGeneral.activo)
    
    return query.all()



# Consultar ruta por id
@router.get("/{ruta_id}", response_model=RutaResponse, summary="Obtener Ruta")
def obtener_ruta(
    ruta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if ruta.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
            )

    return ruta


# ============================================
# AGREGAR TRAMO A RUTA
# ============================================

@router.post("/{ruta_id}/tramos/{tramo_id}", summary="Agregar Tramo a Ruta")
def agregar_tramo_a_ruta(
    ruta_id: int,
    tramo_id: int,
    orden: int,
    current_user: Usuario = Depends(require_permission("editar_ruta")),
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

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if ruta.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
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
# VER RESUMEN DE RUTA (CON COSTOS)
# ============================================

@router.get("/{ruta_id}/resumen")
def obtener_resumen_ruta(
    ruta_id: int,
    vehiculo_id: int,
    precio_galon: Decimal = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ENDPOINT PRINCIPAL: Obtiene el resumen DETALLADO de costos de una ruta.
    
    GET /rutas/1/resumen?vehiculo_id=1&precio_galon=9500
    
    Retorna información desmenuzada:
    - Por cada detalle de tramo: km, rendimiento, galones
    - Por cada tramo: total km y galones
    - Por cada peaje: nombre, costo, sector
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

    # Validar vehículo
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == vehiculo_id,
        Vehiculo.estado == EstadoGeneral.activo
    ).first()

    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o inactivo"
        )

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if vehiculo.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este vehículo"
            )

    # Calcular costo detallado
    resumen = calcular_costo_ruta_detallado(
        db=db,
        ruta_id=ruta_id,
        vehiculo_id=vehiculo_id,
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
    current_user: Usuario = Depends(require_permission("editar_ruta")),
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

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if ruta.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
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
    current_user: Usuario = Depends(require_permission("eliminar_ruta")),
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

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if ruta.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
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
    current_user: Usuario = Depends(get_current_user),
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
    
    # Multi-tenancy: filtrar por empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        query = query.filter(Ruta.empresa_id == current_user.empresa_id)
    
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
    current_user: Usuario = Depends(require_permission("editar_ruta")),
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

    # Multi-tenancy: verificar pertenencia a empresa excepto super_admin
    if current_user.rol and current_user.rol.nombre != "super_admin":
        if ruta.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
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
