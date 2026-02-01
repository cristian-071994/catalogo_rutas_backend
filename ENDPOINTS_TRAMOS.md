# 📚 Endpoints de Tramos - Documentación Completa
#
## 📋 Lista de Endpoints

### 🔍 LECTURA (GET)

#### 1. Listar todos los tramos
```http
GET /tramos/
GET /tramos/?incluir_inactivos=true
```
**Descripción:** Lista todos los tramos activos del sistema  
**Parámetros:**
- `incluir_inactivos` (boolean, opcional): incluir tramos marcados como inactivos

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "origen": "Mediacanoa",
    "destino": "Buenaventura",
    "detalles": [],
    "peajes": [
      {
        "id": 1,
        "nombre_peaje": "Peaje Lobo Guerrero",
        "sector": "Lobo Guerrero",
        "costo": 15000.0,
        "ubicacion": "km 45"
      }
    ]
  }
]
```

---

#### 2. Obtener un tramo específico
```http
GET /tramos/{tramo_id}
```
**Descripción:** Obtiene los detalles completos de un tramo específico  
**Parámetros:**
- `tramo_id` (integer, requerido): ID del tramo

**Respuesta (200):**
```json
{
  "id": 1,
  "origen": "Mediacanoa",
  "destino": "Buenaventura",
  "detalles": [],
  "peajes": [
    {
      "id": 1,
      "nombre_peaje": "Peaje Lobo Guerrero",
      "sector": "Lobo Guerrero",
      "costo": 15000.0,
      "ubicacion": "km 45"
    }
  ]
}
```

---

#### 3. Listar peajes de un tramo
```http
GET /tramos/{tramo_id}/peajes
```
**Descripción:** Lista todos los peajes asociados a un tramo  
**Parámetros:**
- `tramo_id` (integer, requerido): ID del tramo

**Respuesta (200):**
```json
{
  "tramo": "Mediacanoa - Buenaventura",
  "total_peajes": 2,
  "costo_total_peajes": 30000.0,
  "peajes": [
    {
      "id": 1,
      "nombre_peaje": "Peaje Lobo Guerrero",
      "sector": "Lobo Guerrero",
      "costo": 15000.0,
      "ubicacion": "km 45",
      "fuente": "ANI"
    },
    {
      "id": 2,
      "nombre_peaje": "Peaje Loboguerrero",
      "sector": "Lobo Guerrero",
      "costo": 15000.0,
      "ubicacion": "km 45",
      "fuente": "ANI"
    }
  ]
}
```

---

### ✏️ CREACIÓN (POST)

#### 1. Crear un tramo (sin peajes)
```http
POST /tramos/
```
**Descripción:** Crea un nuevo tramo vacío  
**Permisos requeridos:** `crear_tramo`  
**Body:**
```json
{
  "origen": "Mediacanoa",
  "destino": "Buenaventura"
}
```

**Respuesta (201):**
```json
{
  "id": 3,
  "origen": "Mediacanoa",
  "destino": "Buenaventura",
  "detalles": [],
  "peajes": []
}
```

**Errores:**
- **400:** Ya existe un tramo con ese origen y destino
- **401:** No autenticado

---

#### 2. Crear un tramo con peajes
```http
POST /tramos/
```
**Descripción:** Crea un nuevo tramo y asocia peajes en una sola operación  
**Permisos requeridos:** `crear_tramo`  
**Body:**
```json
{
  "origen": "Mediacanoa",
  "destino": "Buenaventura",
  "peaje_ids": [1, 2, 3]
}
```

**Respuesta (201):**
```json
{
  "id": 3,
  "origen": "Mediacanoa",
  "destino": "Buenaventura",
  "detalles": [],
  "peajes": [
    {
      "id": 1,
      "nombre_peaje": "Peaje Lobo Guerrero",
      "sector": "Lobo Guerrero",
      "costo": 15000.0,
      "ubicacion": "km 45"
    },
    {
      "id": 2,
      "nombre_peaje": "Peaje Loboguerrero",
      "sector": "Lobo Guerrero",
      "costo": 15000.0,
      "ubicacion": "km 45"
    },
    {
      "id": 3,
      "nombre_peaje": "Peaje Lobo",
      "sector": "Lobo",
      "costo": 18000.0,
      "ubicacion": "km 42"
    }
  ]
}
```

**Errores:**
- **400:** Ya existe un tramo con ese origen y destino
- **404:** Uno de los peajes no existe o está inactivo
- **401:** No autenticado

---

#### 3. Asociar un peaje a un tramo
```http
POST /tramos/{tramo_id}/peajes/{peaje_id}
```
**Descripción:** Asocia un peaje a un tramo existente  
**Permisos requeridos:** `editar_tramo`  
**Parámetros:**
- `tramo_id` (integer, requerido): ID del tramo
- `peaje_id` (integer, requerido): ID del peaje

**Respuesta (200):**
```json
{
  "mensaje": "Peaje asociado al tramo exitosamente",
  "tramo": "Mediacanoa - Buenaventura",
  "peaje": "Peaje Lobo Guerrero",
  "costo": 15000.0
}
```

**Errores:**
- **404:** Tramo o peaje no encontrado
- **400:** El peaje ya está asociado a este tramo
- **401:** No autenticado

---

### 🔄 ACTUALIZACIÓN (PUT)

#### Actualizar un tramo
```http
PUT /tramos/{tramo_id}
```
**Descripción:** Actualiza los datos de un tramo (origen y/o destino)  
**Permisos requeridos:** `editar_tramo`  
**Parámetros:**
- `tramo_id` (integer, requerido): ID del tramo

**Body (todos los campos son opcionales):**
```json
{
  "origen": "Mediacanoa",
  "destino": "Buenaventura"
}
```

**Respuesta (200):**
```json
{
  "id": 1,
  "origen": "Mediacanoa Actualizado",
  "destino": "Buenaventura",
  "detalles": [],
  "peajes": [
    {
      "id": 1,
      "nombre_peaje": "Peaje Lobo Guerrero",
      "sector": "Lobo Guerrero",
      "costo": 15000.0,
      "ubicacion": "km 45"
    }
  ]
}
```

**Errores:**
- **404:** Tramo no encontrado
- **400:** Ya existe un tramo con ese origen y destino
- **401:** No autenticado

---

### ❌ ELIMINACIÓN (DELETE)

#### 1. Eliminar un tramo (Soft Delete)
```http
DELETE /tramos/{tramo_id}
```
**Descripción:** Marca un tramo como inactivo (no lo elimina de la BD)  
**Permisos requeridos:** `eliminar_tramo`  
**Parámetros:**
- `tramo_id` (integer, requerido): ID del tramo

**Respuesta (204):** Sin contenido

**Errores:**
- **404:** Tramo no encontrado
- **401:** No autenticado

---

#### 2. Quitar un peaje de un tramo
```http
DELETE /tramos/{tramo_id}/peajes/{peaje_id}
```
**Descripción:** Desasocia un peaje de un tramo  
**Permisos requeridos:** `editar_tramo`  
**Parámetros:**
- `tramo_id` (integer, requerido): ID del tramo
- `peaje_id` (integer, requerido): ID del peaje

**Respuesta (204):** Sin contenido

**Errores:**
- **404:** Asociación tramo-peaje no encontrada
- **401:** No autenticado

---

## 🔐 Matriz de Permisos

| Endpoint | Método | Permiso Requerido | Descripción |
|----------|--------|------------------|-------------|
| `/tramos/` | GET | - (solo auth) | Listar tramos |
| `/tramos/{id}` | GET | - (solo auth) | Obtener un tramo |
| `/tramos/` | POST | `crear_tramo` | Crear tramo |
| `/tramos/{id}` | PUT | `editar_tramo` | Actualizar tramo |
| `/tramos/{id}` | DELETE | `eliminar_tramo` | Eliminar tramo |
| `/tramos/{id}/peajes` | GET | - (solo auth) | Listar peajes de un tramo |
| `/tramos/{id}/peajes/{pid}` | POST | `editar_tramo` | Asociar peaje a tramo |
| `/tramos/{id}/peajes/{pid}` | DELETE | `editar_tramo` | Quitar peaje de tramo |

---

## 📝 Ejemplos de Uso Completo

### Flujo 1: Crear tramo con peajes
```bash
# 1. Crear el tramo con 2 peajes
curl -X POST http://localhost:8000/tramos/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "Mediacanoa",
    "destino": "Buenaventura",
    "peaje_ids": [1, 2]
  }'

# Respuesta: {"id": 3, "origen": "Mediacanoa", "destino": "Buenaventura", "peajes": [...]}
```

### Flujo 2: Crear tramo y luego agregar peajes
```bash
# 1. Crear el tramo vacío
curl -X POST http://localhost:8000/tramos/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "Mediacanoa",
    "destino": "Buenaventura"
  }'

# Respuesta: {"id": 3, ...}

# 2. Agregar primer peaje
curl -X POST http://localhost:8000/tramos/3/peajes/1 \
  -H "Authorization: Bearer {token}"

# 3. Agregar segundo peaje
curl -X POST http://localhost:8000/tramos/3/peajes/2 \
  -H "Authorization: Bearer {token}"
```

### Flujo 3: Actualizar y eliminar
```bash
# 1. Actualizar el destino
curl -X PUT http://localhost:8000/tramos/3 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "destino": "Buenaventura Actualizado"
  }'

# 2. Eliminar el tramo (soft delete)
curl -X DELETE http://localhost:8000/tramos/3 \
  -H "Authorization: Bearer {token}"

# 3. Ver tramos incluyendo inactivos
curl -X GET "http://localhost:8000/tramos/?incluir_inactivos=true" \
  -H "Authorization: Bearer {token}"
```

---

## 🛡️ Validaciones

### Al crear un tramo:
- ✅ No puede existir otro tramo activo con el mismo origen + destino
- ✅ Los peajes debe existir y estar activos
- ✅ No se permiten peajes duplicados en el mismo tramo

### Al actualizar un tramo:
- ✅ No puede cambiar a una combinación origen+destino que ya existe (en otro tramo)
- ✅ Solo se actualizan los campos enviados en el body

### Al eliminar un tramo:
- ✅ Se marca como inactivo (no se elimina de la BD)
- ✅ Los peajes asociados se mantienen pero desaparecen del listado

---

**Última actualización:** 2026-02-01  
**Estado:** ✅ Completo
