from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import Optional, List

from app.models.ruta import Ruta
from app.models.tramo_ruta import TramoRuta
from app.models.tramo_detalle import TramoDetalle
from app.models.peaje import Peaje
from app.models.rendimiento_configuracion import RendimientoConfiguracion
from app.models.enums import EstadoGeneral


# ============================================
# CLASES PARA LA RESPUESTA DETALLADA
# ============================================

class DetalleTramoResumen:
    """Detalle individual de un tramo (vacio/cargado + plano/montaña + km)"""
    def __init__(
        self,
        tipo_carga: str,
        tipo_terreno: str,
        kilometros: Decimal,
        rendimiento_km_galon: Decimal,
        galones_necesarios: Decimal,
    ):
        self.tipo_carga = tipo_carga
        self.tipo_terreno = tipo_terreno
        self.kilometros = float(kilometros)
        self.rendimiento_km_galon = float(rendimiento_km_galon)
        self.galones_necesarios = float(galones_necesarios)

    def to_dict(self):
        return {
            "tipo_carga": self.tipo_carga,
            "tipo_terreno": self.tipo_terreno,
            "kilometros": self.kilometros,
            "rendimiento_km_galon": self.rendimiento_km_galon,
            "galones_necesarios": self.galones_necesarios,
        }


class TramoResumen:
    """Resumen de un tramo específico en la ruta"""
    def __init__(
        self,
        tramo_id: int,
        origen: str,
        destino: str,
        orden: int,
        km_totales: Decimal,
        galones_totales: Decimal,
        detalles: List[DetalleTramoResumen],
    ):
        self.tramo_id = tramo_id
        self.origen = origen
        self.destino = destino
        self.orden = orden
        self.km_totales = float(km_totales)
        self.galones_totales = float(galones_totales)
        self.detalles = detalles

    def to_dict(self):
        return {
            "tramo_id": self.tramo_id,
            "nombre": f"{self.origen} → {self.destino}",
            "orden": self.orden,
            "km_totales": self.km_totales,
            "galones_totales": self.galones_totales,
            "detalles": [d.to_dict() for d in self.detalles],
        }


class PeajeResumen:
    """Resumen de peajes en la ruta"""
    def __init__(
        self,
        peaje_id: int,
        nombre: str,
        costo: Decimal,
        direccion: str,
        orden: int,
    ):
        self.peaje_id = peaje_id
        self.nombre = nombre
        self.costo = float(costo)
        self.direccion = direccion
        self.orden = orden

    def to_dict(self):
        return {
            "peaje_id": self.peaje_id,
            "nombre": self.nombre,
            "costo": self.costo,
            "direccion": self.direccion,
            "orden": self.orden,
        }


class ResumenRutaDetallado:
    """Resumen COMPLETO y DETALLADO de una ruta"""
    def __init__(
        self,
        ruta_id: int,
        ruta_nombre: str,
        cliente_nombre: str,
        km_totales: Decimal,
        galones_totales: Decimal,
        costo_combustible: Decimal,
        costo_peajes: Decimal,
        cantidad_peajes: int,
        tramos: List[TramoResumen],
        peajes: List[PeajeResumen],
        precio_galon: Decimal,
        config_marca: str,
        config_modelo: int,
        config_rendimientos: dict,
    ):
        self.ruta_id = ruta_id
        self.ruta_nombre = ruta_nombre
        self.cliente_nombre = cliente_nombre
        self.km_totales = km_totales
        self.galones_totales = galones_totales
        self.costo_combustible = costo_combustible
        self.costo_peajes = costo_peajes
        self.cantidad_peajes = cantidad_peajes
        self.tramos = tramos
        self.peajes = peajes
        self.precio_galon = precio_galon
        self.config_marca = config_marca
        self.config_modelo = config_modelo
        self.config_rendimientos = config_rendimientos
        self.costo_total = costo_combustible + costo_peajes

    def to_dict(self):
        return {
            "ruta": {
                "id": self.ruta_id,
                "nombre": self.ruta_nombre,
                "cliente": self.cliente_nombre,
            },
            "configuracion_vehiculo": {
                "marca": self.config_marca,
                "modelo": self.config_modelo,
                "rendimientos_configurados": self.config_rendimientos,
            },
            "resumen_distancia": {
                "km_totales": float(self.km_totales),
            },
            "resumen_combustible": {
                "precio_galon": float(self.precio_galon),
                "galones_totales_requeridos": float(self.galones_totales),
                "costo_total_combustible": float(self.costo_combustible),
            },
            "resumen_peajes": {
                "cantidad_peajes": self.cantidad_peajes,
                "costo_total_peajes": float(self.costo_peajes),
                "detalles_peajes": [p.to_dict() for p in self.peajes],
            },
            "tramos_detalle": [t.to_dict() for t in self.tramos],
            "costo_total_ruta": {
                "km_totales": float(self.km_totales),
                "galones_requeridos": float(self.galones_totales),
                "costo_combustible": float(self.costo_combustible),
                "costo_peajes": float(self.costo_peajes),
                "costo_total": float(self.costo_total),
            },
        }


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def obtener_km_totales(db: Session, ruta_id: int) -> Decimal:
    """Obtiene la suma de kilometros de todos los tramos de una ruta"""
    resultado = db.query(
        func.sum(TramoDetalle.kilometros).label("km_totales")
    ).join(
        TramoRuta, TramoRuta.tramo_id == TramoDetalle.tramo_id
    ).filter(
        TramoRuta.ruta_id == ruta_id,
        TramoDetalle.estado == EstadoGeneral.activo
    ).scalar()

    return resultado if resultado else Decimal(0)


def obtener_costo_peajes(db: Session, ruta_id: int) -> tuple[Decimal, int]:
    """Obtiene el costo total de peajes y cantidad"""
    resultado = db.query(
        func.sum(Peaje.costo).label("costo_total"),
        func.count(RutaPeaje.id).label("cantidad")
    ).join(
        Peaje, RutaPeaje.peaje_id == Peaje.id
    ).filter(
        RutaPeaje.ruta_id == ruta_id
    ).first()

    if resultado and resultado[0]:
        return (resultado[0], resultado[1] or 0)
    
    return (Decimal(0), 0)


# ============================================
# FUNCIÓN PRINCIPAL: CALCULAR COSTO RUTA DETALLADO
# ============================================

def calcular_costo_ruta_detallado(
    db: Session,
    ruta_id: int,
    configuracion_id: int,
    precio_galon: Decimal
) -> Optional[ResumenRutaDetallado]:
    """
    Calcula el resumen DETALLADO de una ruta.
    
    Devuelve:
    - Información por cada detalle de tramo (km, rendimiento, galones)
    - Información por cada tramo (total km y galones)
    - Información de peajes
    - Resumen final
    """
    
    # Validar que la ruta exista
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        return None

    # Obtener todos los tramos de la ruta (en orden)
    tramos_ruta = db.query(TramoRuta).filter(
        TramoRuta.ruta_id == ruta_id
    ).order_by(TramoRuta.orden).all()

    if not tramos_ruta:
        return None

    # Variables totales
    km_totales_ruta = Decimal(0)
    galones_totales_ruta = Decimal(0)
    tramos_resumen = []

    # Procesar cada tramo
    for tramo_ruta in tramos_ruta:
        tramo = tramo_ruta.tramo

        # Obtener detalles del tramo
        detalles = db.query(TramoDetalle).filter(
            TramoDetalle.tramo_id == tramo.id,
            TramoDetalle.estado == EstadoGeneral.activo
        ).all()

        km_tramo = Decimal(0)
        galones_tramo = Decimal(0)
        detalles_resumen = []

        # Procesar cada detalle del tramo
        for detalle in detalles:
            km_tramo += detalle.kilometros

            # Obtener rendimiento del vehículo para este detalle
            rendimiento = db.query(
                RendimientoConfiguracion.rendimiento_km_galon
            ).filter(
                RendimientoConfiguracion.configuracion_id == configuracion_id,
                RendimientoConfiguracion.tipo_carga == detalle.tipo_carga,
                RendimientoConfiguracion.tipo_terreno == detalle.tipo_terreno,
                RendimientoConfiguracion.estado == EstadoGeneral.activo
            ).scalar()

            if rendimiento:
                galones_detalle = detalle.kilometros / Decimal(rendimiento)
                galones_tramo += galones_detalle
            else:
                galones_detalle = Decimal(0)

            # Crear resumen del detalle
            detalle_resumen = DetalleTramoResumen(
                tipo_carga=detalle.tipo_carga.value,
                tipo_terreno=detalle.tipo_terreno.value,
                kilometros=detalle.kilometros,
                rendimiento_km_galon=Decimal(rendimiento) if rendimiento else Decimal(0),
                galones_necesarios=galones_detalle,
            )
            detalles_resumen.append(detalle_resumen)

        # Agregar totales del tramo
        km_totales_ruta += km_tramo
        galones_totales_ruta += galones_tramo

        tramo_resumen = TramoResumen(
            tramo_id=tramo.id,
            origen=tramo.origen,
            destino=tramo.destino,
            orden=tramo_ruta.orden,
            km_totales=km_tramo,
            galones_totales=galones_tramo,
            detalles=detalles_resumen,
        )
        tramos_resumen.append(tramo_resumen)

    # NUEVO: Obtener peajes de TODOS los tramos de la ruta (sin duplicados)
    from app.models.tramo_peaje import TramoPeaje
    
    peajes_unicos = {}  # dict para evitar duplicados: {peaje_id: peaje}
    costo_peajes = Decimal(0)
    
    # Recorrer todos los tramos de la ruta
    for tramo_ruta in tramos_ruta:
        # Obtener peajes del tramo
        tramos_peajes = db.query(TramoPeaje).filter(
            TramoPeaje.tramo_id == tramo_ruta.tramo_id
        ).all()
        
        # Agregar peajes únicos
        for tramo_peaje in tramos_peajes:
            peaje = tramo_peaje.peaje
            if peaje.id not in peajes_unicos and peaje.estado == EstadoGeneral.activo:
                peajes_unicos[peaje.id] = peaje
                costo_peajes += peaje.costo

    # Convertir dict a lista de resúmenes
    peajes_resumen = []
    for peaje in peajes_unicos.values():
        peaje_resumen = PeajeResumen(
            peaje_id=peaje.id,
            nombre=peaje.nombre_peaje,  # Actualizado: nombre_peaje
            costo=peaje.costo,
            direccion="AMBAS",  # Ya no hay concepto de ida/regreso
            orden=None,  # Ya no hay orden
        )
        peajes_resumen.append(peaje_resumen)

    # Calcular costo combustible
    costo_combustible = galones_totales_ruta * precio_galon

    # Obtener configuración del vehículo
    from app.models.configuracion_vehiculo import ConfiguracionVehiculo
    from app.models.marca_vehiculo import MarcaVehiculo
    
    config = db.query(ConfiguracionVehiculo).filter(
        ConfiguracionVehiculo.id == configuracion_id
    ).first()

    config_marca = "No configurada"
    config_modelo = 0
    config_rendimientos = {}

    if config:
        marca = db.query(MarcaVehiculo).filter(
            MarcaVehiculo.id == config.marca_id
        ).first()
        
        config_marca = marca.nombre if marca else "Desconocida"
        config_modelo = config.modelo

        # Obtener todos los rendimientos de esta configuración
        rendimientos = db.query(RendimientoConfiguracion).filter(
            RendimientoConfiguracion.configuracion_id == configuracion_id,
            RendimientoConfiguracion.estado == EstadoGeneral.activo
        ).all()

        for rend in rendimientos:
            clave = f"{rend.tipo_carga.value}-{rend.tipo_terreno.value}"
            config_rendimientos[clave] = float(rend.rendimiento_km_galon)

    # Crear resumen final
    resumen = ResumenRutaDetallado(
        ruta_id=ruta_id,
        ruta_nombre=ruta.nombre,
        cliente_nombre=ruta.cliente.nombre,
        km_totales=km_totales_ruta,
        galones_totales=galones_totales_ruta,
        costo_combustible=costo_combustible,
        costo_peajes=costo_peajes,
        cantidad_peajes=len(peajes_ruta),
        tramos=tramos_resumen,
        peajes=peajes_resumen,
        precio_galon=precio_galon,
        config_marca=config_marca,
        config_modelo=config_modelo,
        config_rendimientos=config_rendimientos,
    )

    return resumen

