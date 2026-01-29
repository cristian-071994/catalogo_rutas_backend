from app.database.db import engine
from app.database.base import Base

# 🔴 IMPORTANTE: importar modelos ANTES de create_all
# Esto asegura que SQLAlchemy "registre" los modelos en el Base
from app.models import (
    Cliente, Ruta, Tramo, TramoRuta, TramoDetalle,
    Peaje, RutaPeaje,
    MarcaVehiculo, ConfiguracionVehiculo, Vehiculo,
    RendimientoConfiguracion,
    ConfiguracionGeneral
)


def init_db():
    """
    Crea todas las tablas en la BD si no existen.
    SQLAlchemy verifica inteligentemente y solo crea las que faltan.
    """
    Base.metadata.create_all(bind=engine)
