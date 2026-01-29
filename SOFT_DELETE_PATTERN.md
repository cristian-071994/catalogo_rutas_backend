# Patrón de Soft Delete - Guía Profesional

## 📌 ¿Qué es Soft Delete?

**Soft Delete** es un patrón donde **NO eliminas registros físicamente** de la base de datos, sino que los marcas como "inactivos" con un campo de estado.

**Datos duros (hard delete):**
```sql
DELETE FROM clientes WHERE id = 5;  -- ❌ El registro desaparece
```

**Soft delete:**
```sql
UPDATE clientes SET estado = 'inactivo' WHERE id = 5;  -- ✅ El registro sigue ahí pero marcado
```

---

## 🎯 ¿Por Qué se Usa en el Mundo Profesional?

### 1. **Auditoría e Historial**
```
Si un cliente se "elimina", necesitas poder:
- Ver quién lo eliminó
- Cuándo se eliminó  
- Recuperarlo si es un error
- Rastrear su historial de transacciones
```

### 2. **Integridad Referencial**
```
Si un cliente tiene rutas/pedidos pasados, no puedes eliminarlos sin romper el historial.
Con soft delete:
- El registro sigue existiendo
- Las rutas antiguas siguen vinculadas correctamente
- Se preserva la relación histórica
```

### 3. **Requisitos Legales**
```
Algunos países (GDPR, LGPD) requieren mantener registros 
para auditoría aunque "se eliminen" para el usuario.
```

### 4. **Operaciones Reversibles**
```
Si alguien elimina algo por error:
- Con hard delete: **PERDIDO**
- Con soft delete: UPDATE ... SET estado = 'activo'  ✅
```

---

## 🏗️ Arquitectura en Tu Backend

### **Patrón Implementado: GET Filtra Activos + Query Parameter para Soporte**

**Comportamiento:**
```
GET /clientes/                     → Retorna SOLO clientes activos
GET /clientes/?incluir_inactivos=true  → Retorna activos + inactivos (soporte/admin)
```

### **Código Ejemplo:**
```python
@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Cliente)
    
    if not incluir_inactivos:
        query = query.filter(Cliente.estado == EstadoGeneral.activo)
    
    return query.all()
```

**¿Qué pasa?**
1. Por defecto `incluir_inactivos=False`
2. Si es `False`, filtra `estado="activo"`
3. Si es `True`, devuelve TODO (se usa en panel de soporte)

---

## 🛡️ Responsabilidades por Capa

### **Frontend (Usuario Normal)**
```
- Llama GET /clientes/
- Recibe SOLO registros activos
- Ve la lista "limpia" sin eliminados
- ✅ No necesita lógica especial
```

### **Backend (Developers)**
```
- GET endpoints filtran inactivos por defecto
- DELETE endpoints cambian estado a "inactivo" 
- CRUD endpoints solo usan registros activos
- ✅ Lógica centralizada
```

### **Admin/Support (Panel Especial)**
```
- Usa GET /clientes/?incluir_inactivos=true
- Ve TODO incluyendo eliminados
- Puede recuperar con PUT /clientes/{id} (estado=activo)
- ✅ Control total para soporte
```

---

## 📋 Endpoints en Tu Backend

### **USO NORMAL (Usuarios):**

```bash
# Listar activos (lo que ve el usuario)
GET /clientes/

# Respuesta:
[
  { "id": 1, "nombre": "Cliente A", "estado": "activo" },
  { "id": 2, "nombre": "Cliente B", "estado": "activo" }
]

# Los clientes inactivos NO aparecen aquí
```

### **USO CON INACTIVOS (Soporte/Admin):**

```bash
# Ver TODO (incluyendo eliminados)
GET /clientes/?incluir_inactivos=true

# Respuesta:
[
  { "id": 1, "nombre": "Cliente A", "estado": "activo" },
  { "id": 2, "nombre": "Cliente B", "estado": "activo" },
  { "id": 3, "nombre": "Cliente Eliminado", "estado": "inactivo" }  ← Aquí aparece
]
```

### **ELIMINAR (Soft Delete):**

```bash
# "Eliminar" un cliente
DELETE /clientes/3

# Respuesta: 204 No Content

# En BD:
UPDATE clientes SET estado='inactivo' WHERE id=3;
```

### **RECUPERAR (Desde Soporte):**

```bash
# Reactivar un cliente que fue eliminado
PUT /clientes/3
Body:
{
  "estado": "activo"
}

# Respuesta: 200 OK
{ "id": 3, "nombre": "Cliente Recuperado", "estado": "activo" }
```

---

## 🔧 Endpoints Disponibles en Tu API

### **Endpoints con Filtro Automático:**

| Endpoint | GET | GET ?incluir_inactivos=true | DELETE |
|----------|-----|----------------------------|---------|
| `/clientes/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/peajes/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/tramos/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/vehiculos/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/marcas-vehiculos/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/configuracion-vehiculos/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/rendimiento-configuracion/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/rutas/` | ✅ Activos | ✅ Todo | ✅ Soft delete |
| `/tramo-detalle/tramo/{id}` | ✅ Activos | ✅ Todo | Cascade |
| `/rendimiento-configuracion/configuracion/{id}` | ✅ Activos | ✅ Todo | Cascade |

---

## 📱 Ejemplo Práctico: Flujo Completo

### **Escenario: Usuario Elimina un Peaje**

**1️⃣ Usuario ve peaje activo:**
```bash
GET /peajes/
[
  { "id": 1, "nombre": "Peaje La Loma", "estado": "activo" },
  { "id": 2, "nombre": "Peaje Buena Vista", "estado": "activo" }
]
```

**2️⃣ Usuario lo "elimina":**
```bash
DELETE /peajes/2
Response: 204 No Content
```

**3️⃣ Usuario consulta de nuevo:**
```bash
GET /peajes/
[
  { "id": 1, "nombre": "Peaje La Loma", "estado": "activo" }
  # Peaje 2 NO aparece aquí
]
```

**4️⃣ 3 horas después... ¡Error! Necesitaban ese peaje**

**5️⃣ Support puede ver TODO:**
```bash
GET /peajes/?incluir_inactivos=true
[
  { "id": 1, "nombre": "Peaje La Loma", "estado": "activo" },
  { "id": 2, "nombre": "Peaje Buena Vista", "estado": "inactivo" }  ← Aquí está!
]
```

**6️⃣ Support lo reactiva:**
```bash
PUT /peajes/2
Body: { "estado": "activo" }
Response: 200 OK
{ "id": 2, "nombre": "Peaje Buena Vista", "estado": "activo" }
```

**7️⃣ Usuario lo ve de nuevo:**
```bash
GET /peajes/
[
  { "id": 1, "nombre": "Peaje La Loma", "estado": "activo" },
  { "id": 2, "nombre": "Peaje Buena Vista", "estado": "activo" }  ← Recuperado!
]
```

---

## 🎓 Buenas Prácticas

### ✅ HACER:
```python
# GET siempre filtra inactivos por defecto
query = db.query(Peaje).filter(Peaje.estado == EstadoGeneral.activo)

# DELETE cambia estado
peaje.estado = EstadoGeneral.inactivo

# Soporte puede ver TODO
query = db.query(Peaje)  # Sin filtro si incluir_inactivos=True

# PUT puede reactivar
peaje.estado = EstadoGeneral.activo
```

### ❌ NO HACER:
```python
# ❌ No devolver inactivos en GET normal
return db.query(Peaje).all()  # Mala práctica

# ❌ No eliminar físicamente datos
db.delete(peaje)  # No, usa soft delete

# ❌ No tener filtrado inconsistente
# Si en un endpoint filtras inactivos, todos deben hacerlo
```

---

## 🏢 En el Mundo Real (Empresas Grandes)

### **LinkedIn:**
- Cuando "eliminas" tu perfil → `estado='deleted'`
- Datos siguen ahí por 30 días
- Si cambias de opinión → reactivación

### **Google/Gmail:**
- Trash folder → `estado='trashed'`
- Permanentemente elimina después de 30 días
- Antes de eso → puede recuperarse

### **Stripe (Pagos):**
- Clientes nunca se eliminan → `deleted=true`
- Necesario para auditoría de transacciones
- Si necesitas "borrar" → soft delete

### **Shopify:**
- Tiendas "eliminadas" → `status='archived'`
- Historial de órdenes se preserva
- Clientes pueden reactivar la tienda

---

## 📊 Decisiones Arquitectónicas en Tu Caso

### **¿Backend o Frontend Filtra?**
✅ **Backend (Decisión Correcta)**
- Frontend solo ve datos filtrados
- No requiere lógica duplicada en frontend
- Más seguro (no hay HTML comentado con datos inactivos)

### **¿Parámetro Query o Endpoint Separado?**
✅ **Parámetro Query (Decisión Correcta)**
- Un endpoint (`GET /clientes/`) reutilizado
- Control fino con `?incluir_inactivos=true`
- Menos mantenimiento

Alternativa:
```python
GET /clientes/         # Activos
GET /admin/clientes/   # Todo incluyendo inactivos
```

### **¿Hard Delete Nunca?**
✅ **Nunca para datos de negocio (Decisión Correcta)**
- Clientes, Rutas, Peajes → Soft delete siempre
- Logs/Auditoría → Podrían ser hard delete después de años
- Configuración del sistema → Generalmente soft delete

---

## 🔍 Testing: Verificar el Comportamiento

```bash
# 1. Crear peaje
POST /peajes/
Body: { "nombre": "Peaje Test", "costo": 5000 }
Response: 201 { "id": 1, ... }

# 2. Ver que aparece
GET /peajes/
Response: 200 [ { "id": 1, "estado": "activo" } ]

# 3. "Eliminarlo"
DELETE /peajes/1
Response: 204

# 4. Verificar que desapareció para usuario normal
GET /peajes/
Response: 200 [ ]  # ← Vacío!

# 5. Soporte lo busca
GET /peajes/?incluir_inactivos=true
Response: 200 [ { "id": 1, "estado": "inactivo" } ]  # ← Aquí está

# 6. Soporte lo reactiva
PUT /peajes/1
Body: { "estado": "activo" }
Response: 200 { "id": 1, "estado": "activo" }

# 7. Usuario lo ve de nuevo
GET /peajes/
Response: 200 [ { "id": 1, "estado": "activo" } ]
```

---

## 💾 Base de Datos

### **Campos Necesarios:**
```python
estado = Column(
    Enum(EstadoGeneral, name="estado_general"),
    default=EstadoGeneral.activo,
    nullable=False
)
```

### **Índices Recomendados:**
```python
# Para que búsquedas por estado sean rápidas
__table_args__ = (
    Index('idx_estado', 'estado'),  # Buscar activos/inactivos
    Index('idx_cliente_estado', 'cliente_id', 'estado'),  # Rutas de un cliente
)
```

### **Queries Típicas:**
```python
# Usuarios normales ven solo activos
db.query(Peaje).filter(Peaje.estado == 'activo')

# Admin ve todo
db.query(Peaje)

# Recuperación
db.query(Peaje).filter(Peaje.estado == 'inactivo')
```

---

## 🎯 Resumen: Lo Importante

| Aspecto | Tu Implementación |
|--------|------------------|
| **Filtrado** | Backend filtra automáticamente ✅ |
| **Control** | Parámetro `incluir_inactivos` ✅ |
| **Seguridad** | Frontend NO ve inactivos por defecto ✅ |
| **Auditoría** | Datos se preservan para historial ✅ |
| **Recuperación** | PUT con `estado='activo'` ✅ |
| **Profesional** | Como usan grandes empresas ✅ |

---

## 📚 Referencias

- **GDPR**: Requiere auditoría (soft delete preferred)
- **ACID Compliance**: Soft delete mantiene integridad referencial
- **Event Sourcing**: Registro completo de cambios
- **CQRS Pattern**: Query y Command separados

