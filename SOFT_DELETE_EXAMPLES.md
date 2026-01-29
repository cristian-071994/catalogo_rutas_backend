# Ejemplos Prácticos: Soft Delete en Acción

## 📱 Usando Swagger UI (Frontend)

Abre `http://127.0.0.1:8000/docs` para probar en vivo.

---

## Ejemplo 1: Ciclo Completo de Peajes

### **Paso 1: Crear dos peajes**

```bash
POST /peajes/
Content-Type: application/json

{
  "nombre": "Peaje Buenaventura",
  "costo": 25000.00
}
```

**Response:**
```json
{
  "id": 1,
  "nombre": "Peaje Buenaventura",
  "costo": 25000.0,
  "estado": "activo"
}
```

Repetir para crear un segundo peaje:
```bash
POST /peajes/
{
  "nombre": "Peaje Cali",
  "costo": 15000.00
}
```

**Response:**
```json
{
  "id": 2,
  "nombre": "Peaje Cali",
  "costo": 15000.0,
  "estado": "activo"
}
```

### **Paso 2: Usuario ve peajes (lista normal)**

```bash
GET /peajes/
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "nombre": "Peaje Buenaventura",
    "costo": 25000.0,
    "estado": "activo"
  },
  {
    "id": 2,
    "nombre": "Peaje Cali",
    "costo": 15000.0,
    "estado": "activo"
  }
]
```

✅ **Frontend muestra ambos peajes**

### **Paso 3: Usuario "elimina" un peaje**

```bash
DELETE /peajes/2
```

**Response: 204 No Content**

¿Qué pasa en la BD?
```sql
UPDATE peajes SET estado='inactivo' WHERE id=2;
-- El peaje sigue en la BD pero marcado como inactivo
```

### **Paso 4: Usuario consulta peajes de nuevo**

```bash
GET /peajes/
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "nombre": "Peaje Buenaventura",
    "costo": 25000.0,
    "estado": "activo"
  }
]
```

✅ **Peaje Cali DESAPARECIÓ de la vista del usuario**

### **Paso 5: Support necesita recuperar el peaje**

```bash
GET /peajes/?incluir_inactivos=true
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "nombre": "Peaje Buenaventura",
    "costo": 25000.0,
    "estado": "activo"
  },
  {
    "id": 2,
    "nombre": "Peaje Cali",
    "costo": 15000.0,
    "estado": "inactivo"  ← Aquí está!
  }
]
```

✅ **Support ve TODO incluyendo eliminados**

### **Paso 6: Support reactiva el peaje**

```bash
PUT /peajes/2
Content-Type: application/json

{
  "estado": "activo"
}
```

**Response: 200 OK**
```json
{
  "id": 2,
  "nombre": "Peaje Cali",
  "costo": 15000.0,
  "estado": "activo"
}
```

¿Qué pasa en la BD?
```sql
UPDATE peajes SET estado='activo' WHERE id=2;
```

### **Paso 7: Usuario lo ve de nuevo**

```bash
GET /peajes/
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "nombre": "Peaje Buenaventura",
    "costo": 25000.0,
    "estado": "activo"
  },
  {
    "id": 2,
    "nombre": "Peaje Cali",
    "costo": 15000.0,
    "estado": "activo"
  }
]
```

✅ **Peaje Cali REAPARECIÓ automáticamente**

---

## Ejemplo 2: Clientes Activos e Inactivos

### **Crear 3 clientes**

```bash
POST /clientes/
{ "nombre": "Cliente A" }  → ID: 1

POST /clientes/
{ "nombre": "Cliente B" }  → ID: 2

POST /clientes/
{ "nombre": "Cliente C" }  → ID: 3
```

### **Vista Normal (Usuario)**

```bash
GET /clientes/
```

**Response:**
```json
[
  { "id": 1, "nombre": "Cliente A", "estado": "activo" },
  { "id": 2, "nombre": "Cliente B", "estado": "activo" },
  { "id": 3, "nombre": "Cliente C", "estado": "activo" }
]
```

### **"Eliminar" Cliente B**

```bash
DELETE /clientes/2
```

**Response: 204 No Content**

### **Usuario ve lista actualizada**

```bash
GET /clientes/
```

**Response:**
```json
[
  { "id": 1, "nombre": "Cliente A", "estado": "activo" },
  { "id": 3, "nombre": "Cliente C", "estado": "activo" }
]
```

❌ **Cliente B desapareció para usuario**

### **Support ve TODO (incluyendo eliminados)**

```bash
GET /clientes/?incluir_inactivos=true
```

**Response:**
```json
[
  { "id": 1, "nombre": "Cliente A", "estado": "activo" },
  { "id": 2, "nombre": "Cliente B", "estado": "inactivo" },
  { "id": 3, "nombre": "Cliente C", "estado": "activo" }
]
```

✅ **Support puede ver Cliente B y sus historial de rutas**

---

## Ejemplo 3: Tramos (Segmentos de Ruta)

### **Crear tramos**

```bash
POST /tramos/
{
  "origen": "Mediacanoa",
  "destino": "Buenaventura"
}
→ ID: 1

POST /tramos/
{
  "origen": "Buenaventura", 
  "destino": "Cali"
}
→ ID: 2

POST /tramos/
{
  "origen": "Cali",
  "destino": "Popayán"
}
→ ID: 3
```

### **Listar tramos activos (Usuario)**

```bash
GET /tramos/
```

**Response: 200 OK**
```json
[
  { "id": 1, "origen": "Mediacanoa", "destino": "Buenaventura", "estado": "activo" },
  { "id": 2, "origen": "Buenaventura", "destino": "Cali", "estado": "activo" },
  { "id": 3, "origen": "Cali", "destino": "Popayán", "estado": "activo" }
]
```

### **Usuario "elimina" ruta intermedia**

```bash
DELETE /tramos/2
```

**Response: 204 No Content**

### **Consultar de nuevo**

```bash
GET /tramos/
```

**Response:**
```json
[
  { "id": 1, "origen": "Mediacanoa", "destino": "Buenaventura", "estado": "activo" },
  { "id": 3, "origen": "Cali", "destino": "Popayán", "estado": "activo" }
]
```

❌ **Tramo intermedio desapareció**

### **Support busca historial completo**

```bash
GET /tramos/?incluir_inactivos=true
```

**Response:**
```json
[
  { "id": 1, "origen": "Mediacanoa", "destino": "Buenaventura", "estado": "activo" },
  { "id": 2, "origen": "Buenaventura", "destino": "Cali", "estado": "inactivo" },
  { "id": 3, "origen": "Cali", "destino": "Popayán", "estado": "activo" }
]
```

✅ **Tramo 2 sigue existiendo en el sistema**

---

## Ejemplo 4: Recuperación en Cascada

### **Escenario Complejo**

1. Se eliminan varias rutas
2. Se eliminan tramos usados por esas rutas
3. Support necesita ver qué se eliminó

### **Ver todo el historial**

```bash
GET /rutas/?incluir_inactivos=true
```

```bash
GET /tramos/?incluir_inactivos=true
```

```bash
GET /peajes/?incluir_inactivos=true
```

---

## 🔍 Comparación: Antes vs Después

### **Antes (Hard Delete - ❌ Malo)**
```
Usuario elimina Ruta ID 5
│
└─ DELETE ruta (id=5)
   ├─ Historial se pierde
   ├─ No se sabe cuándo se eliminó
   ├─ No se puede recuperar
   └─ Si había auditoría de costos, falta información
```

### **Después (Soft Delete - ✅ Bien)**
```
Usuario elimina Ruta ID 5
│
└─ UPDATE ruta SET estado='inactivo' WHERE id=5
   ├─ Ruta sigue en BD
   ├─ Se conoce fecha de eliminación
   ├─ Se puede recuperar fácilmente
   └─ Auditoría de costos intacta
```

---

## 💡 Testing desde Swagger

### **1. Abre Swagger UI**
```
http://127.0.0.1:8000/docs
```

### **2. Busca el endpoint GET /clientes/**
- Haz clic en "Try it out"
- Verás que aparece el parámetro `incluir_inactivos`
- Prueba con `false` (defecto) y `true`

### **3. Observa la Diferencia**

**Sin parámetro (o false):**
```
GET /clientes/
→ 3 registros
```

**Con incluir_inactivos=true:**
```
GET /clientes/?incluir_inactivos=true
→ 5 registros (incluyendo 2 inactivos)
```

---

## 🧪 Script de Testing Completo

```bash
#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

# 1. Crear peaje
echo "1️⃣ Crear peaje..."
PEAJE=$(curl -X POST "$BASE_URL/peajes/" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Peaje Test","costo":20000}')
PEAJE_ID=$(echo $PEAJE | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "Creado: ID $PEAJE_ID"

# 2. Ver que aparece
echo -e "\n2️⃣ Ver peaje en lista normal..."
curl -X GET "$BASE_URL/peajes/"

# 3. Eliminarlo
echo -e "\n3️⃣ Eliminar peaje..."
curl -X DELETE "$BASE_URL/peajes/$PEAJE_ID"

# 4. Verificar que desapareció
echo -e "\n4️⃣ Ver lista sin inactivos (desapareció)..."
curl -X GET "$BASE_URL/peajes/"

# 5. Ver TODO con soporte
echo -e "\n5️⃣ Ver TODO incluyendo inactivos..."
curl -X GET "$BASE_URL/peajes/?incluir_inactivos=true"

# 6. Reactivar
echo -e "\n6️⃣ Reactivar peaje..."
curl -X PUT "$BASE_URL/peajes/$PEAJE_ID" \
  -H "Content-Type: application/json" \
  -d '{"estado":"activo"}'

# 7. Ver que reapareció
echo -e "\n7️⃣ Ver lista normal de nuevo (reapareció)..."
curl -X GET "$BASE_URL/peajes/"
```

---

## 🎓 Resumen Visual

```
┌─────────────────────────────────────────────────┐
│           FLUJO DE SOFT DELETE                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Usuario Normal          Admin/Support          │
│  ─────────────────      ──────────────────      │
│  GET /peajes/           GET /peajes/?           │
│  ↓                      incluir_inactivos=true  │
│  [Activos solo]         ↓                       │
│                         [Todo: Activos + Inactivos]
│                                                 │
│  DELETE /peajes/2       ← Soft Delete           │
│  ↓                      ↓                       │
│  UPDATE estado=          UPDATE estado=         │
│  'inactivo'             'inactivo'              │
│                                                 │
│  GET /peajes/           GET /peajes/?           │
│  ↓                      incluir_inactivos=true  │
│  [Sin peaje 2]          ↓                       │
│                         [Incluye peaje 2]       │
│                                                 │
│  Support: PUT /peajes/2 {estado: 'activo'}     │
│  ↓                                              │
│  Peaje se reactiva y usuario lo ve             │
│                                                 │
└─────────────────────────────────────────────────┘
```

