from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import Optional, List

from app.models.ruta import Ruta
from app.models.tramo_ruta import TramoRuta
from app.models.tramo_detalle import TramoDetalle
from app.models.peaje import Peaje
from app.models.rendimiento_configuracion import RendimientoConfiguracion
from app.models.vehiculo import Vehiculo
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
        self.kilometros = round(float(kilometros), 2)
        self.rendimiento_km_galon = round(float(rendimiento_km_galon), 2)
        self.galones_necesarios = round(float(galones_necesarios), 2)

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
        peajes: List = None,
        costo_peajes: Decimal = Decimal(0),
    ):
        self.tramo_id = tramo_id
        self.origen = origen
        self.destino = destino
        self.orden = orden
        self.km_totales = round(float(km_totales), 2)
        self.galones_totales = round(float(galones_totales), 2)
        self.detalles = detalles
        self.peajes = peajes or []
        self.costo_peajes = round(float(costo_peajes), 2)
        self.cantidad_peajes = len(self.peajes)

    def to_dict(self):
        return {
            "tramo_id": self.tramo_id,
            "nombre": f"{self.origen} → {self.destino}",
            "orden": self.orden,
            "km_totales": self.km_totales,
            "galones_totales": self.galones_totales,
            "cantidad_peajes": self.cantidad_peajes,
            "costo_peajes": self.costo_peajes,
            "peajes": [p.to_dict() for p in self.peajes],
            "detalles": [d.to_dict() for d in self.detalles],
        }


class PeajeResumen:
    """Resumen de peajes en la ruta"""
    def __init__(
        self,
        peaje_id: int,
        nombre: str,
        costo: Decimal,
        sector: str = None,
    ):
        self.peaje_id = peaje_id
        self.nombre = nombre
        self.costo = round(float(costo), 2)
        self.sector = sector

    def to_dict(self):
        return {
            "peaje_id": self.peaje_id,
            "nombre": self.nombre,
            "costo": self.costo,
            "sector": self.sector,
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
        vehiculo_placa: str,
    ):
        self.ruta_id = ruta_id
        self.ruta_nombre = ruta_nombre
        self.cliente_nombre = cliente_nombre
        self.km_totales = round(float(km_totales), 2)
        self.galones_totales = round(float(galones_totales), 2)
        self.costo_combustible = round(float(costo_combustible), 2)
        self.costo_peajes = round(float(costo_peajes), 2)
        self.cantidad_peajes = cantidad_peajes
        self.tramos = tramos
        self.peajes = peajes
        self.precio_galon = round(float(precio_galon), 2)
        self.config_marca = config_marca
        self.config_modelo = config_modelo
        self.config_rendimientos = config_rendimientos
        self.vehiculo_placa = vehiculo_placa
        self.costo_total = round(self.costo_combustible + self.costo_peajes, 2)

    def to_dict(self):
        return {
            "ruta": {
                "id": self.ruta_id,
                "nombre": self.ruta_nombre,
                "cliente": self.cliente_nombre,
            },
            "vehiculo": {
                "placa": self.vehiculo_placa,
            },
            "configuracion_vehiculo": {
                "marca": self.config_marca,
                "modelo": self.config_modelo,
                "rendimientos_configurados": self.config_rendimientos,
            },
            "resumen_distancia": {
                "km_totales": self.km_totales,
            },
            "resumen_combustible": {
                "precio_galon": self.precio_galon,
                "galones_totales_requeridos": self.galones_totales,
                "costo_total_combustible": self.costo_combustible,
            },
            "resumen_peajes": {
                "cantidad_peajes": self.cantidad_peajes,
                "costo_total_peajes": self.costo_peajes,
                "detalles_peajes": [p.to_dict() for p in self.peajes],
            },
            "tramos_detalle": [t.to_dict() for t in self.tramos],
            "costo_total_ruta": {
                "km_totales": self.km_totales,
                "galones_requeridos": self.galones_totales,
                "costo_combustible": self.costo_combustible,
                "costo_peajes": self.costo_peajes,
                "costo_total": self.costo_total,
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
    vehiculo_id: int,
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

    # Validar que el vehículo exista
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == vehiculo_id,
        Vehiculo.estado == EstadoGeneral.activo
    ).first()

    if not vehiculo:
        return None

    configuracion_id = vehiculo.configuracion_id

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

        # ============================================
        # OBTENER PEAJES DE ESTE TRAMO
        # ============================================
        from app.models.tramo_peaje import TramoPeaje
        
        tramos_peajes = db.query(TramoPeaje).filter(
            TramoPeaje.tramo_id == tramo.id
        ).all()
        
        peajes_tramo = []
        costo_peajes_tramo = Decimal(0)
        
        for tramo_peaje in tramos_peajes:
            peaje = tramo_peaje.peaje
            if peaje.estado == EstadoGeneral.activo:
                peaje_resumen = PeajeResumen(
                    peaje_id=peaje.id,
                    nombre=peaje.nombre_peaje,
                    costo=peaje.costo,
                    sector=peaje.sector,
                )
                peajes_tramo.append(peaje_resumen)
                costo_peajes_tramo += peaje.costo

        # Agregar totales del tramo
        km_totales_ruta += km_tramo
        galones_totales_ruta += galones_tramo

        # Crear resumen del tramo CON SUS PEAJES
        tramo_resumen = TramoResumen(
            tramo_id=tramo.id,
            origen=tramo.origen,
            destino=tramo.destino,
            orden=tramo_ruta.orden,
            km_totales=km_tramo,
            galones_totales=galones_tramo,
            detalles=detalles_resumen,
            peajes=peajes_tramo,
            costo_peajes=costo_peajes_tramo,
        )
        tramos_resumen.append(tramo_resumen)

    # ============================================
    # OBTENER PEAJES ÚNICOS DE TODA LA RUTA
    # ============================================
    # ============================================
    # CONSOLIDAR TODOS LOS PEAJES DE LA RUTA
    # ============================================
    # La ruta suma TODOS los peajes de TODOS los tramos
    # Si un peaje aparece en varios tramos, se cuenta varias veces
    
    peajes_totales_ruta = []
    costo_peajes_total = Decimal(0)
    
    # Recorrer todos los tramos y sumar TODOS sus peajes
    for tramo_resumen in tramos_resumen:
        for peaje_info in tramo_resumen.peajes:
            peajes_totales_ruta.append(peaje_info)
            costo_peajes_total += Decimal(peaje_info.costo)

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
        costo_peajes=costo_peajes_total,
        cantidad_peajes=len(peajes_totales_ruta),
        tramos=tramos_resumen,
        peajes=peajes_totales_ruta,
        precio_galon=precio_galon,
        config_marca=config_marca,
        config_modelo=config_modelo,
        config_rendimientos=config_rendimientos,
        vehiculo_placa=vehiculo.placa,
    )

    return resumen

