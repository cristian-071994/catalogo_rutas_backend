from fastapi import FastAPI

from app.routers import (
    rutas, clientes, configuracion, peajes, tramos, 
    tramo_detalle, marcas_vehiculos, configuracion_vehiculos,
    rendimiento_configuracion, vehiculos, auth
)
from app.database.init_db import init_db
from app.database.session import get_db
from app.auth import create_test_users

app = FastAPI(
    title="Catálogo de Rutas",
    description="Backend para gestión de rutas, combustible y costos",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_db()
    # Crear usuarios de prueba
    db = next(get_db())
    create_test_users(db)
    db.close()

# Routers - Autenticación (primero)
app.include_router(auth.router)

# Routers - Recursos
app.include_router(configuracion.router)
app.include_router(clientes.router)
app.include_router(peajes.router)
app.include_router(tramos.router)
app.include_router(tramo_detalle.router)
app.include_router(marcas_vehiculos.router)
app.include_router(configuracion_vehiculos.router)
app.include_router(rendimiento_configuracion.router)
app.include_router(vehiculos.router)
app.include_router(rutas.router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "mensaje": "Backend con DB funcionando"
    }
