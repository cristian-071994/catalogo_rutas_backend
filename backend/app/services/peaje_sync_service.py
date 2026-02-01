"""
Servicio de sincronización de peajes desde API oficial (ANI)
https://www.datos.gov.co/resource/7gj8-j6i3.json
"""
import httpx
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Dict, List

from app.models.peaje import Peaje
from app.models.enums import EstadoGeneral


API_URL = "https://www.datos.gov.co/resource/7gj8-j6i3.json"
TIMEOUT = 60.0  # segundos
PAGE_LIMIT = 1000


async def sincronizar_peajes_desde_api(db: Session) -> Dict:
    """
    Descarga peajes desde API oficial y actualiza/crea en base de datos.
    Retorna resumen de la sincronización.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            stats = {
                "total_api": 0,
                "filtrados_categoria_v": 0,
                "creados": 0,
                "actualizados": 0,
                "errores": 0,
                "errores_detalle": []
            }

            offset = 0
            while True:
                response = await client.get(
                    API_URL,
                    params={"$limit": PAGE_LIMIT, "$offset": offset}
                )
                response.raise_for_status()
                peajes_api = response.json()

                if not peajes_api:
                    break

                stats["total_api"] += len(peajes_api)

                for peaje_data in peajes_api:
                    try:
                        categoria = str(peaje_data.get("idcategoriatarifa", "")).strip().upper()
                        if categoria != "V":
                            continue

                        stats["filtrados_categoria_v"] += 1

                        nombre_raw = peaje_data.get("peaje", "")
                        nombre_peaje = " ".join(str(nombre_raw).split()).strip()
                        if not nombre_peaje:
                            stats["errores"] += 1
                            continue

                        id_peaje_api = str(peaje_data.get("idpeaje", "")).strip()

                        try:
                            costo = Decimal(str(peaje_data.get("valor", "0")))
                        except (ValueError, TypeError):
                            costo = Decimal("0")

                        fecha_str = peaje_data.get("ultimofechacambiopeaje")
                        fecha_tarifa = None
                        if fecha_str:
                            try:
                                fecha_tarifa = datetime.fromisoformat(str(fecha_str).replace("Z", ""))
                            except ValueError:
                                fecha_tarifa = None

                        peaje_existente = db.query(Peaje).filter(
                            (Peaje.id_peaje_api == id_peaje_api) |
                            (Peaje.nombre_peaje == nombre_peaje) |
                            (Peaje.nombre == nombre_peaje)
                        ).first()

                        if peaje_existente:
                            peaje_existente.nombre = nombre_peaje
                            peaje_existente.nombre_peaje = nombre_peaje
                            peaje_existente.costo = costo
                            peaje_existente.id_peaje_api = id_peaje_api
                            peaje_existente.categoria_tarifa = categoria
                            peaje_existente.fecha_ultima_tarifa = fecha_tarifa
                            peaje_existente.fuente = "API_GOBIERNO"
                            peaje_existente.ultima_actualizacion = datetime.utcnow()
                            peaje_existente.estado = EstadoGeneral.activo
                            stats["actualizados"] += 1
                        else:
                            nuevo_peaje = Peaje(
                                nombre=nombre_peaje,
                                nombre_peaje=nombre_peaje,
                                costo=costo,
                                id_peaje_api=id_peaje_api,
                                categoria_tarifa=categoria,
                                fecha_ultima_tarifa=fecha_tarifa,
                                fuente="API_GOBIERNO",
                                ultima_actualizacion=datetime.utcnow(),
                                estado=EstadoGeneral.activo
                            )
                            db.add(nuevo_peaje)
                            stats["creados"] += 1

                    except Exception as e:
                        stats["errores"] += 1
                        stats["errores_detalle"].append({
                            "peaje": peaje_data.get("peaje", "DESCONOCIDO"),
                            "error": str(e)
                        })

                offset += PAGE_LIMIT
        
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
        stats = {
            "total_api": 0,
            "filtrados_categoria_v": 0,
            "creados": 0,
            "actualizados": 0,
            "errores": 0,
            "errores_detalle": []
        }

        offset = 0
        while True:
            response = requests.get(
                API_URL,
                params={"$limit": PAGE_LIMIT, "$offset": offset},
                timeout=TIMEOUT
            )
            response.raise_for_status()
            peajes_api = response.json()

            if not peajes_api:
                break

            stats["total_api"] += len(peajes_api)

            for peaje_data in peajes_api:
                try:
                    categoria = str(peaje_data.get("idcategoriatarifa", "")).strip().upper()
                    if categoria != "V":
                        continue

                    stats["filtrados_categoria_v"] += 1

                    nombre_raw = peaje_data.get("peaje", "")
                    nombre_peaje = " ".join(str(nombre_raw).split()).strip()
                    if not nombre_peaje:
                        stats["errores"] += 1
                        continue

                    id_peaje_api = str(peaje_data.get("idpeaje", "")).strip()

                    try:
                        costo = Decimal(str(peaje_data.get("valor", "0")))
                    except (ValueError, TypeError):
                        costo = Decimal("0")

                    fecha_str = peaje_data.get("ultimofechacambiopeaje")
                    fecha_tarifa = None
                    if fecha_str:
                        try:
                            fecha_tarifa = datetime.fromisoformat(str(fecha_str).replace("Z", ""))
                        except ValueError:
                            fecha_tarifa = None

                    peaje_existente = db.query(Peaje).filter(
                        (Peaje.id_peaje_api == id_peaje_api) |
                        (Peaje.nombre_peaje == nombre_peaje) |
                        (Peaje.nombre == nombre_peaje)
                    ).first()

                    if peaje_existente:
                        peaje_existente.nombre = nombre_peaje
                        peaje_existente.nombre_peaje = nombre_peaje
                        peaje_existente.costo = costo
                        peaje_existente.id_peaje_api = id_peaje_api
                        peaje_existente.categoria_tarifa = categoria
                        peaje_existente.fecha_ultima_tarifa = fecha_tarifa
                        peaje_existente.fuente = "API_GOBIERNO"
                        peaje_existente.ultima_actualizacion = datetime.utcnow()
                        peaje_existente.estado = EstadoGeneral.activo
                        stats["actualizados"] += 1
                    else:
                        nuevo_peaje = Peaje(
                            nombre=nombre_peaje,
                            nombre_peaje=nombre_peaje,
                            costo=costo,
                            id_peaje_api=id_peaje_api,
                            categoria_tarifa=categoria,
                            fecha_ultima_tarifa=fecha_tarifa,
                            fuente="API_GOBIERNO",
                            ultima_actualizacion=datetime.utcnow(),
                            estado=EstadoGeneral.activo
                        )
                        db.add(nuevo_peaje)
                        stats["creados"] += 1

                except Exception as e:
                    stats["errores"] += 1
                    stats["errores_detalle"].append({
                        "peaje": peaje_data.get("peaje", "DESCONOCIDO"),
                        "error": str(e)
                    })

            offset += PAGE_LIMIT
        
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
