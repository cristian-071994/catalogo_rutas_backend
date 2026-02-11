import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    rutas, clientes, configuracion, peajes, tramos, 
    tramo_detalle, marcas_vehiculos, configuracion_vehiculos,
    rendimiento_configuracion, vehiculos, auth, usuarios, roles, permisos, empresas
)
from app.database.init_db import init_db
from app.database.session import get_db
from app.auth import create_test_users
from app.scheduler import iniciar_tareas_programadas, detener_tareas_programadas

app = FastAPI(
    title="Catálogo de Rutas API",
    description="""
## 🚀 API v1 - Backend para gestión de rutas, combustible y costos

### 🏢 Multi-Tenancy
Este sistema soporta múltiples empresas de transporte.
Cada empresa tiene sus propios usuarios, clientes, rutas y vehículos aislados.

### 🎯 Primera Instalación (Onboarding)
**Si es la primera vez que usas el sistema:**
1. Usa `POST /api/v1/onboarding` para crear tu empresa y primer administrador
2. Este endpoint solo funciona UNA VEZ (cuando no hay empresas)
3. Después, inicia sesión con las credenciales creadas

### 🔐 Autenticación
Esta API requiere autenticación JWT para la mayoría de endpoints.

**Pasos para autenticarte:**
1. Usa el endpoint `POST /api/v1/login` con credenciales válidas
2. Copia el `access_token` de la respuesta
3. Click en el botón 🔒 **Authorize** (arriba a la derecha)
4. Pega el token en el campo que aparece
5. Click en **Authorize** y luego **Close**

**Usuarios de prueba disponibles (solo desarrollo):**
- `admin@cointra.com` / `admin123` (Admin Cointra - acceso total)
- `admin@geotab.com` / `admin123` (Admin Geotab - acceso total)

### 📝 Registro de Nuevos Usuarios
Los usuarios pueden registrarse usando `POST /api/v1/registro`.
Necesitan el **NIT de su empresa** (sin guiones, solo números).
El registro queda **pendiente de aprobación** por un administrador de la empresa.

### 🔄 Sincronización Automática
Los peajes se sincronizan automáticamente desde la API oficial del gobierno
todos los días a las 3:00 AM (hora de Colombia).
    """,
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configurar CORS para permitir peticiones desde el frontend
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allow_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Frontend permitido por entorno
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

@app.on_event("startup")
def startup_event():
    init_db()
    # NO crear usuarios automáticamente en producción
    # El super admin se crea vía /onboarding
    # Las empresas se crean vía super admin
    
    # Solo en desarrollo: crear datos de prueba
    if os.getenv("ENVIRONMENT", "development") == "development":
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
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])

# Routers - Gestión de Usuarios y Roles (después de auth)
app.include_router(empresas.router, prefix="/api/v1")
app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(permisos.router, prefix="/api/v1")

# Routers - Recursos
app.include_router(configuracion.router, prefix="/api/v1")
app.include_router(clientes.router, prefix="/api/v1")
app.include_router(peajes.router, prefix="/api/v1")
app.include_router(tramos.router, prefix="/api/v1")
app.include_router(tramo_detalle.router, prefix="/api/v1")
app.include_router(marcas_vehiculos.router, prefix="/api/v1")
app.include_router(configuracion_vehiculos.router, prefix="/api/v1")
app.include_router(rendimiento_configuracion.router, prefix="/api/v1")
app.include_router(vehiculos.router, prefix="/api/v1")
app.include_router(rutas.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "status": "ok",
        "mensaje": "Backend con DB funcionando"
    }
