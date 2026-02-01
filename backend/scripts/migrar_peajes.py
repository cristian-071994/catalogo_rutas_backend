"""
Script de migración para refactorización de peajes
- Actualiza modelo Peaje con nuevos campos
- Crea tabla tramo_peajes
- Mantiene compatibilidad con ruta_peajes (deprecated)
"""
import sys
sys.path.append('.')

from sqlalchemy import inspect, text
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models import Peaje, TramoPeaje, Tramo, Ruta, RutaPeaje
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verificar_columnas_tabla(tabla_nombre: str):
    """Verifica qué columnas existen en una tabla"""
    inspector = inspect(engine)
    if tabla_nombre in inspector.get_table_names():
        columnas = [col['name'] for col in inspector.get_columns(tabla_nombre)]
        logger.info(f"Columnas en {tabla_nombre}: {columnas}")
        return columnas
    else:
        logger.info(f"Tabla {tabla_nombre} no existe aún")
        return []


def migrar_peajes():
    """
    Migra la tabla peajes para agregar nuevos campos
    """
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("INICIANDO MIGRACIÓN DE PEAJES")
        logger.info("=" * 60)
        
        # Verificar estado actual
        columnas_peajes = verificar_columnas_tabla("peajes")
        
        # Agregar nuevas columnas si no existen
        nuevas_columnas = {
            "nombre_peaje": "VARCHAR(200)",
            "ubicacion": "VARCHAR(200)",
            "sector": "VARCHAR(200)",
            "longitud": "NUMERIC(12, 8)",
            "latitud": "NUMERIC(12, 8)",
            "codigo_peaje": "VARCHAR(20)",
            "codigo_tramo": "VARCHAR(20)",
            "fuente": "VARCHAR(50) DEFAULT 'MANUAL'",
            "ultima_actualizacion": "DATETIME"
        }
        
        for columna, tipo in nuevas_columnas.items():
            if columna not in columnas_peajes:
                try:
                    # SQLite no soporta ALTER TABLE ADD COLUMN con todas las opciones
                    # Hacemos una versión simplificada
                    if columna == "nombre_peaje":
                        # Copiar nombre a nombre_peaje
                        db.execute(text(f"ALTER TABLE peajes ADD COLUMN {columna} {tipo}"))
                        db.commit()
                        # Copiar datos del campo nombre al nuevo campo
                        if "nombre" in columnas_peajes:
                            db.execute(text("UPDATE peajes SET nombre_peaje = nombre WHERE nombre_peaje IS NULL"))
                            db.commit()
                            logger.info(f"  ✅ Columna {columna} agregada y datos migrados")
                    else:
                        db.execute(text(f"ALTER TABLE peajes ADD COLUMN {columna} {tipo.split(' DEFAULT')[0]}"))
                        db.commit()
                        logger.info(f"  ✅ Columna {columna} agregada")
                except Exception as e:
                    logger.warning(f"  ⚠️  No se pudo agregar {columna}: {e}")
        
        # Crear tabla tramo_peajes si no existe
        if "tramo_peajes" not in inspect(engine).get_table_names():
            logger.info("\n  📋 Creando tabla tramo_peajes...")
            TramoPeaje.__table__.create(engine)
            logger.info("  ✅ Tabla tramo_peajes creada")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        logger.info("=" * 60)
        logger.info("\nPróximos pasos:")
        logger.info("1. Reiniciar el servidor")
        logger.info("2. Ejecutar POST /peajes/sincronizar para cargar peajes oficiales")
        logger.info("3. Asociar peajes a tramos usando POST /tramos/{id}/peajes/{peaje_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verificar_migracion():
    """Verifica que la migración se haya completado correctamente"""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICACIÓN POST-MIGRACIÓN")
    logger.info("=" * 60)
    
    columnas_peajes = verificar_columnas_tabla("peajes")
    
    columnas_esperadas = [
        "nombre_peaje", "ubicacion", "sector", "longitud", "latitud",
        "codigo_peaje", "codigo_tramo", "fuente", "ultima_actualizacion"
    ]
    
    logger.info("\n📋 Verificando columnas en tabla peajes:")
    for col in columnas_esperadas:
        if col in columnas_peajes:
            logger.info(f"  ✅ {col}")
        else:
            logger.warning(f"  ❌ {col} - FALTA")
    
    # Verificar tabla tramo_peajes
    inspector = inspect(engine)
    if "tramo_peajes" in inspector.get_table_names():
        logger.info("\n✅ Tabla tramo_peajes existe")
    else:
        logger.warning("\n⚠️  Tabla tramo_peajes NO existe")


if __name__ == "__main__":
    try:
        migrar_peajes()
        verificar_migracion()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)
