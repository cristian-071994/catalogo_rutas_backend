"""
Servicio de sincronización de peajes desde API oficial del gobierno
https://www.datos.gov.co/resource/68qj-5xux.json
"""
import httpx
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Dict, List

from app.models.peaje import Peaje
from app.models.enums import EstadoGeneral


API_URL = "https://www.datos.gov.co/resource/68qj-5xux.json"
TIMEOUT = 60.0  # segundos


async def sincronizar_peajes_desde_api(db: Session) -> Dict:
    """
    Descarga peajes desde API oficial y actualiza/crea en base de datos.
    Retorna resumen de la sincronización.
    """
    try:
        # Descargar datos de la API
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(API_URL, params={"$limit": 10000})
            response.raise_for_status()
            peajes_api = response.json()
        
        stats = {
            "total_api": len(peajes_api),
            "creados": 0,
            "actualizados": 0,
            "errores": 0,
            "errores_detalle": []
        }
        
        for peaje_data in peajes_api:
            try:
                # Extraer datos de la API
                nombre_peaje = peaje_data.get("nombre_peaje", "").strip()
                
                # Validar que tenga nombre
                if not nombre_peaje:
                    stats["errores"] += 1
                    continue
                
                # Extraer coordenadas
                coordinates = peaje_data.get("point", {}).get("coordinates", [])
                longitud = Decimal(str(coordinates[0])) if len(coordinates) > 0 else None
                latitud = Decimal(str(coordinates[1])) if len(coordinates) > 1 else None
                
                # Extraer costo de categoría V (camiones)
                categoria_v = peaje_data.get("categoria_v", "0")
                try:
                    costo = Decimal(str(categoria_v))
                except (ValueError, TypeError):
                    costo = Decimal("0")
                
                # Si el costo es 0, usar categoria_ii como fallback
                if costo == 0:
                    categoria_ii = peaje_data.get("categoria_ii", "0")
                    try:
                        costo = Decimal(str(categoria_ii))
                    except (ValueError, TypeError):
                        costo = Decimal("0")
                
                # Verificar si el peaje ya existe (buscar por nombre_peaje O por nombre)
                peaje_existente = db.query(Peaje).filter(
                    (Peaje.nombre_peaje == nombre_peaje) | (Peaje.nombre == nombre_peaje)
                ).first()
                
                if peaje_existente:
                    # Actualizar peaje existente
                    peaje_existente.nombre = nombre_peaje  # Compatibilidad con campo viejo
                    peaje_existente.ubicacion = peaje_data.get("ubicaci_n", "")[:200]
                    peaje_existente.sector = peaje_data.get("sector", "")[:200]
                    peaje_existente.longitud = longitud
                    peaje_existente.latitud = latitud
                    peaje_existente.costo = costo
                    peaje_existente.codigo_peaje = peaje_data.get("c_digo_peaje", "")[:20]
                    peaje_existente.codigo_tramo = peaje_data.get("c_digo_tramo", "")[:20]
                    peaje_existente.fuente = "API_GOBIERNO"
                    peaje_existente.ultima_actualizacion = datetime.utcnow()
                    peaje_existente.estado = EstadoGeneral.activo
                    
                    stats["actualizados"] += 1
                else:
                    # Crear nuevo peaje
                    nuevo_peaje = Peaje(
                        nombre=nombre_peaje,  # Compatibilidad con campo viejo
                        nombre_peaje=nombre_peaje,
                        ubicacion=peaje_data.get("ubicaci_n", "")[:200],
                        sector=peaje_data.get("sector", "")[:200],
                        longitud=longitud,
                        latitud=latitud,
                        costo=costo,
                        codigo_peaje=peaje_data.get("c_digo_peaje", "")[:20],
                        codigo_tramo=peaje_data.get("c_digo_tramo", "")[:20],
                        fuente="API_GOBIERNO",
                        ultima_actualizacion=datetime.utcnow(),
                        estado=EstadoGeneral.activo
                    )
                    db.add(nuevo_peaje)
                    stats["creados"] += 1
                    
            except Exception as e:
                stats["errores"] += 1
                stats["errores_detalle"].append({
                    "peaje": peaje_data.get("nombre_peaje", "DESCONOCIDO"),
                    "error": str(e)
                })
        
        # Guardar cambios
        db.commit()
        
        return {
            "success": True,
            "fecha_sincronizacion": datetime.utcnow().isoformat(),
            "estadisticas": stats
        }
        
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Error al conectar con la API: {str(e)}",
            "estadisticas": {
                "total_api": 0,
                "creados": 0,
                "actualizados": 0,
                "errores": 1
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}",
            "estadisticas": {
                "total_api": 0,
                "creados": 0,
                "actualizados": 0,
                "errores": 1
            }
        }


def sincronizar_peajes_sync(db: Session) -> Dict:
    """
    Versión síncrona de sincronización de peajes.
    Usada para tareas programadas.
    """
    import requests
    
    try:
        # Descargar datos de la API
        response = requests.get(API_URL, params={"$limit": 10000}, timeout=TIMEOUT)
        response.raise_for_status()
        peajes_api = response.json()
        
        stats = {
            "total_api": len(peajes_api),
            "creados": 0,
            "actualizados": 0,
            "errores": 0,
            "errores_detalle": []
        }
        
        for peaje_data in peajes_api:
            try:
                nombre_peaje = peaje_data.get("nombre_peaje", "").strip()
                if not nombre_peaje:
                    stats["errores"] += 1
                    continue
                
                coordinates = peaje_data.get("point", {}).get("coordinates", [])
                longitud = Decimal(str(coordinates[0])) if len(coordinates) > 0 else None
                latitud = Decimal(str(coordinates[1])) if len(coordinates) > 1 else None
                
                categoria_v = peaje_data.get("categoria_v", "0")
                try:
                    costo = Decimal(str(categoria_v))
                except (ValueError, TypeError):
                    costo = Decimal("0")
                
                if costo == 0:
                    categoria_ii = peaje_data.get("categoria_ii", "0")
                    try:
                        costo = Decimal(str(categoria_ii))
                    except (ValueError, TypeError):
                        costo = Decimal("0")
                
                peaje_existente = db.query(Peaje).filter(
                    (Peaje.nombre_peaje == nombre_peaje) | (Peaje.nombre == nombre_peaje)
                ).first()
                
                if peaje_existente:
                    peaje_existente.nombre = nombre_peaje  # Compatibilidad con campo viejo
                    peaje_existente.ubicacion = peaje_data.get("ubicaci_n", "")[:200]
                    peaje_existente.sector = peaje_data.get("sector", "")[:200]
                    peaje_existente.longitud = longitud
                    peaje_existente.latitud = latitud
                    peaje_existente.costo = costo
                    peaje_existente.codigo_peaje = peaje_data.get("c_digo_peaje", "")[:20]
                    peaje_existente.codigo_tramo = peaje_data.get("c_digo_tramo", "")[:20]
                    peaje_existente.fuente = "API_GOBIERNO"
                    peaje_existente.ultima_actualizacion = datetime.utcnow()
                    peaje_existente.estado = EstadoGeneral.activo
                    stats["actualizados"] += 1
                else:
                    nuevo_peaje = Peaje(
                        nombre=nombre_peaje,  # Compatibilidad con campo viejo
                        nombre_peaje=nombre_peaje,
                        ubicacion=peaje_data.get("ubicaci_n", "")[:200],
                        sector=peaje_data.get("sector", "")[:200],
                        longitud=longitud,
                        latitud=latitud,
                        costo=costo,
                        codigo_peaje=peaje_data.get("c_digo_peaje", "")[:20],
                        codigo_tramo=peaje_data.get("c_digo_tramo", "")[:20],
                        fuente="API_GOBIERNO",
                        ultima_actualizacion=datetime.utcnow(),
                        estado=EstadoGeneral.activo
                    )
                    db.add(nuevo_peaje)
                    stats["creados"] += 1
                    
            except Exception as e:
                stats["errores"] += 1
                stats["errores_detalle"].append({
                    "peaje": peaje_data.get("nombre_peaje", "DESCONOCIDO"),
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "success": True,
            "fecha_sincronizacion": datetime.utcnow().isoformat(),
            "estadisticas": stats
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error al conectar con la API: {str(e)}",
            "estadisticas": {
                "total_api": 0,
                "creados": 0,
                "actualizados": 0,
                "errores": 1
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}",
            "estadisticas": {
                "total_api": 0,
                "creados": 0,
                "actualizados": 0,
                "errores": 1
            }
        }
