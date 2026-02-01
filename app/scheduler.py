"""
Scheduler para tareas programadas
Sincronización diaria de peajes a las 3:00 AM
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.database.session import SessionLocal
from app.services.peaje_sync_service import sincronizar_peajes_sync

# Configurar logging
logger = logging.getLogger(__name__)


def tarea_sincronizacion_peajes():
    """
    Tarea programada para sincronizar peajes desde API oficial.
    Se ejecuta diariamente a las 3:00 AM.
    """
    logger.info(f"[{datetime.now()}] Iniciando sincronización diaria de peajes...")
    
    db = SessionLocal()
    try:
        resultado = sincronizar_peajes_sync(db)
        
        if resultado["success"]:
            stats = resultado["estadisticas"]
            logger.info(
                f"[{datetime.now()}] Sincronización completada exitosamente: "
                f"{stats['creados']} creados, {stats['actualizados']} actualizados, "
                f"{stats['errores']} errores"
            )
        else:
            logger.error(
                f"[{datetime.now()}] Error en sincronización: {resultado.get('error')}"
            )
    except Exception as e:
        logger.error(f"[{datetime.now()}] Error inesperado en sincronización: {str(e)}")
    finally:
        db.close()


# Crear scheduler
scheduler = BackgroundScheduler(timezone="America/Bogota")


def iniciar_tareas_programadas():
    """
    Inicia el scheduler con todas las tareas programadas.
    Debe ser llamado al iniciar la aplicación.
    """
    # Tarea diaria a las 3:00 AM (hora de Colombia)
    scheduler.add_job(
        tarea_sincronizacion_peajes,
        trigger=CronTrigger(hour=3, minute=0),
        id="sincronizacion_peajes_diaria",
        name="Sincronización Diaria de Peajes",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler iniciado. Tareas programadas:")
    logger.info("  - Sincronización de peajes: Todos los días a las 3:00 AM")


def detener_tareas_programadas():
    """
    Detiene el scheduler limpiamente.
    Debe ser llamado al apagar la aplicación.
    """
    scheduler.shutdown()
    logger.info("Scheduler detenido")
