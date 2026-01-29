# 🚀 Catálogo Rutas Backend

API REST para gestión de rutas, peajes, clientes y vehículos con soporte de cálculo de rendimiento.

## 📋 Características

- ✅ **Gestión de Clientes** - CRUD completo con soft delete
- ✅ **Gestión de Rutas** - Crear, editar y eliminar rutas
- ✅ **Gestión de Peajes** - Administración de peajes en rutas
- ✅ **Gestión de Tramos** - Segmentos de ruta con validación case-insensitive
- ✅ **Gestión de Vehículos** - Registro de vehículos con configuraciones
- ✅ **Cálculo de Rendimiento** - km/galón por configuración de vehículo
- ✅ **Validación Case-Insensitive** - Evita duplicados independiente de mayúsculas
- ✅ **Soft Delete Pattern** - Registros inactivos sin pérdida de datos
- ✅ **Swagger/OpenAPI** - Documentación interactiva

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.128.0
- **ORM**: SQLAlchemy 2.0.45
- **Validación**: Pydantic 2.12.5
- **Base Datos**: SQLite
- **Python**: 3.13.5
- **Server**: Uvicorn

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/catalogo_rutas_backend.git
cd catalogo_rutas_backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source venv/bin/activate     # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el servidor
```bash
python -m uvicorn app.main:app --reload
```

El servidor estará disponible en: **http://127.0.0.1:8000**

## 📚 Documentación API

Una vez el servidor está corriendo:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🎯 Endpoints Principales

### Clientes
```
GET    /clientes/              # Listar clientes activos
GET    /clientes/?incluir_inactivos=true  # Ver todos (incluyendo inactivos)
POST   /clientes/              # Crear cliente
GET    /clientes/{id}          # Ver detalle
PUT    /clientes/{id}          # Editar
DELETE /clientes/{id}          # Marcar como inactivo (soft delete)
```

### Rutas
```
GET    /rutas/                 # Listar rutas activas
GET    /rutas/cliente/{cliente_id}  # Rutas de un cliente
POST   /rutas/                 # Crear ruta
PUT    /rutas/{id}             # Editar
DELETE /rutas/{id}             # Marcar como inactivo
```

### Peajes
```
GET    /peajes/                # Listar peajes activos
POST   /peajes/                # Crear peaje
PUT    /peajes/{id}            # Editar
DELETE /peajes/{id}            # Marcar como inactivo
```

### Tramos
```
GET    /tramos/                # Listar tramos activos
POST   /tramos/                # Crear tramo
GET    /tramos/{id}            # Detalle con detalles
PUT    /tramos/{id}            # Editar
DELETE /tramos/{id}            # Marcar como inactivo
```

### Vehículos
```
GET    /vehiculos/             # Listar vehículos activos
POST   /vehiculos/             # Crear vehículo
PUT    /vehiculos/{id}         # Editar
DELETE /vehiculos/{id}         # Marcar como inactivo
```

## 🔄 Patrón Soft Delete

Este backend implementa el patrón **soft delete** profesional:

### Comportamiento
- **DELETE** no elimina datos, marca como `estado='inactivo'`
- **GET** filtra automáticamente solo activos
- **GET?incluir_inactivos=true** muestra todo (para support/admin)
- Los datos se pueden **recuperar** con PUT `{"estado": "activo"}`

### Ciclo de vida
```
1. POST /clientes/          → estado='activo' (nuevo)
2. GET /clientes/           → Aparece en lista
3. DELETE /clientes/{id}    → estado='inactivo'
4. GET /clientes/           → NO aparece
5. GET /clientes/?incluir_inactivos=true  → Aparece como inactivo
6. PUT /clientes/{id} {"estado": "activo"}  → Recuperado
```

## 🎓 Validaciones

### Case-Insensitive
Los campos que evitan duplicados con validación case-insensitive:
- **Tramos**: `origen`, `destino`
- **Peajes**: `nombre`
- **Marcas**: `nombre`
- **Vehículos**: `placa`
- **Configuración**: `clave`

**Ejemplo**: "Mediacanoa" ≠ "mediacanoa" → Mismo valor (no se duplica)

### Enumeraciones
- **EstadoGeneral**: `activo`, `inactivo`
- **TipoTerreno**: `plano`, `ondulado`, `montañoso`
- **TipoCarga**: `vacio`, `parcial`, `lleno`

## 📁 Estructura del Proyecto

```
catalogo_rutas_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── config.py               # Configuración
│   ├── database/
│   │   ├── base.py             # Base de modelos
│   │   ├── db.py               # Configuración DB
│   │   ├── init_db.py          # Inicialización
│   │   └── session.py          # Sesiones
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── cliente.py
│   │   ├── ruta.py
│   │   ├── peaje.py
│   │   ├── tramo.py
│   │   ├── vehiculo.py
│   │   ├── marca_vehiculo.py
│   │   ├── configuracion_vehiculo.py
│   │   ├── rendimiento_configuracion.py
│   │   ├── tramo_ruta.py
│   │   ├── ruta_peaje.py
│   │   ├── tramo_detalle.py
│   │   └── enums.py
│   ├── routers/                # Endpoints
│   │   ├── clientes.py
│   │   ├── rutas.py
│   │   └── ... (otros)
│   └── schemas/                # Pydantic schemas
│       └── ... (validación)
├── .gitignore
├── requirements.txt            # Dependencias
├── README.md                   # Este archivo
└── catalogo_rutas.db          # Base de datos (local)
```

## 🧪 Testing

### Con Swagger UI
1. Abre http://127.0.0.1:8000/docs
2. Expande un endpoint
3. Click "Try it out"
4. Completa los campos
5. Click "Execute"

### Con curl
```bash
# Crear cliente
curl -X POST http://127.0.0.1:8000/clientes/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mi Cliente"}'

# Listar clientes
curl http://127.0.0.1:8000/clientes/

# Listar incluyendo inactivos
curl "http://127.0.0.1:8000/clientes/?incluir_inactivos=true"
```

## 📝 Notas Importantes

### Enums Válidos
```python
EstadoGeneral: "activo" | "inactivo"
TipoTerreno: "plano" | "ondulado" | "montañoso"
TipoCarga: "vacio" | "parcial" | "lleno"
```

### Validaciones Automáticas
- Campos requeridos: FastAPI devuelve 422 si faltan
- Enums inválidos: FastAPI devuelve 422
- Duplicados case-insensitive: Backend devuelve 400 con mensaje
- Registros no encontrados: Backend devuelve 404

## 📚 Documentación Adicional

En la raíz del proyecto encontrarás documentación detallada:

- **SOFT_DELETE_PATTERN.md** - Guía completa del patrón soft delete
- **SOFT_DELETE_EXAMPLES.md** - Ejemplos prácticos paso a paso
- **SOFT_DELETE_FAQ.md** - Preguntas frecuentes y respuestas
- **CHANGELOG_SOFT_DELETE.md** - Registro de cambios
- **RESUMEN_VISUAL_FINAL.md** - Resumen visual con diagramas

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para detalles.

## 📧 Contacto

Creado con ❤️ para la gestión de rutas y peajes.

---

**Última actualización**: Enero 2026
