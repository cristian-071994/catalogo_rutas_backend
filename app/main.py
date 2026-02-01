from fastapi import FastAPI

from app.routers import (
    rutas, clientes, configuracion, peajes, tramos, 
    tramo_detalle, marcas_vehiculos, configuracion_vehiculos,
    rendimiento_configuracion, vehiculos, auth, usuarios, roles, permisos
)
from app.database.init_db import init_db
from app.database.session import get_db
from app.auth import create_test_users
from app.scheduler import iniciar_tareas_programadas, detener_tareas_programadas

app = FastAPI(
    title="Catálogo de Rutas",
    description="""
## 🚀 Backend para gestión de rutas, combustible y costos

### 🔐 Autenticación
Esta API requiere autenticación JWT para la mayoría de endpoints.

**Pasos para autenticarte:**
1. Usa el endpoint `POST /login` con credenciales válidas
2. Copia el `access_token` de la respuesta
3. Click en el botón 🔒 **Authorize** (arriba a la derecha)
4. Pega el token en el campo que aparece
5. Click en **Authorize** y luego **Close**

**Usuarios de prueba disponibles:**
- `admin@test.com` / `admin123` (acceso total)
- `supervisor@test.com` / `supervisor123` (todo excepto DELETE)
- `gestor_clientes@test.com` / `gestor123` (solo clientes)
- `consultor@test.com` / `consultor123` (solo lectura)

### 🔄 Sincronización Automática
Los peajes se sincronizan automáticamente desde la API oficial del gobierno
todos los días a las 3:00 AM (hora de Colombia).
    """,
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_db()
    # Crear usuarios de prueba
    db = next(get_db())
    create_test_users(db)
    db.close()
    # Iniciar tareas programadas (sincronización diaria)
    iniciar_tareas_programadas()

@app.on_event("shutdown")
def shutdown_event():
    # Detener tareas programadas limpiamente
    detener_tareas_programadas()

# Routers - Autenticación (primero)
app.include_router(auth.router)

# Routers - Gestión de Usuarios y Roles (después de auth)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(permisos.router)

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
