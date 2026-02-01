# Catálogo de Rutas

Sistema de gestión de rutas de transporte con cálculo de costos de combustible y peajes para Colombia.

## Estructura del Proyecto (Monorepo)

```
catalogo_rutas_backend/
├── backend/          # API FastAPI + SQLAlchemy
├── frontend/         # Aplicación web (próximamente)
├── venv/            # Entorno virtual Python
└── README.md        # Este archivo
```

## Backend

API REST construida con FastAPI para gestionar:
- **Clientes**: Empresas de transporte
- **Vehículos**: Flota con configuraciones de rendimiento
- **Rutas**: Origen, destino y tramos intermedios
- **Peajes**: Sincronización con API de ANI Colombia
- **Cálculos**: Costos de combustible y peajes por ruta/vehículo
- **Autenticación**: JWT con sistema de roles y 45 permisos

### Tecnologías
- FastAPI + Uvicorn
- SQLAlchemy ORM + SQLite
- Pydantic v2
- JWT Authentication
- APScheduler (sincronización peajes)

### Documentación Completa
Ver [backend/README.md](backend/README.md) para instrucciones detalladas de instalación y uso.

### Inicio Rápido

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload

# Acceder a documentación
http://localhost:8000/docs
```

### Endpoints Principales
- `/auth/login` - Autenticación JWT
- `/rutas/{ruta_id}/resumen?vehiculo_id=X` - Cálculo detallado de costos
- `/peajes` - Gestión de peajes (sincroniza con ANI)
- `/tramos` - Gestión de tramos de ruta
- `/clientes`, `/vehiculos`, `/usuarios`, etc.

## Frontend

**Estado**: 🚧 En planificación

Tecnologías propuestas:
- React + TypeScript + Vite
- TanStack Query (React Query)
- React Router
- Tailwind CSS + Shadcn/ui

## Desarrollo

### Requisitos
- Python 3.9+
- Node.js 18+ (para frontend)
- SQLite

### Configuración Inicial

1. Clonar repositorio
```bash
git clone https://github.com/cristian-071994/catalogo_rutas_backend.git
cd catalogo_rutas_backend
```

2. Configurar backend
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configurar variables de entorno
```

3. Iniciar base de datos
```bash
# La BD se crea automáticamente al ejecutar el servidor por primera vez
uvicorn app.main:app --reload
```

4. Usuario por defecto
```
Email: admin@example.com
Password: admin123
```

## Estado del Proyecto

**Backend**: ~65% completo (MVP funcional)
- ✅ Sistema de autenticación y permisos
- ✅ CRUD completo de todas las entidades
- ✅ Cálculo de costos detallado
- ✅ Sincronización con API ANI
- ✅ Soft delete pattern
- ⚠️ Falta: Tests unitarios, logging avanzado, caché

**Frontend**: 0% (por iniciar)

## Licencia

Proyecto privado - Todos los derechos reservados

## Contacto

GitHub: [@cristian-071994](https://github.com/cristian-071994)
