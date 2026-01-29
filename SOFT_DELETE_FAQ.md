# ❓ Preguntas Frecuentes - Soft Delete Pattern

## P1: ¿Por qué no simplemente borrar el registro de la BD?

**R:** Hay varias razones críticas:

### 1. **Integridad Referencial**
Si eliminas un cliente que tiene 50 rutas asociadas:
```sql
DELETE FROM clientes WHERE id = 5;  -- ❌ Error: Constraint violation
```
Las rutas quedan huérfanas.

Con soft delete:
```sql
UPDATE clientes SET estado='inactivo' WHERE id=5;  -- ✅ Las rutas siguen vinculadas
```

### 2. **Auditoría Legal**
```
Si alguien paga un peaje y lo eliminas:
❌ Hard delete: "¿Cuál fue el peaje?" - No hay registro
✅ Soft delete: Puedo ver que fue el Peaje Buenaventura a $25,000
```

### 3. **Historial de Negocio**
```
Reporte: "Cuántos clientes tuvimos en 2023?"
❌ Hard delete: No puedo contar (desaparecieron)
✅ Soft delete: Puedo contar todos que estuvieron activos
```

---

## P2: ¿Y si necesito ver un cliente eliminado?

**R:** Úsalo en el endpoint GET:

```bash
GET /clientes/5?incluir_inactivos=true

Response: 200
{
  "id": 5,
  "nombre": "Cliente Eliminado",
  "estado": "inactivo"  ← Aquí ves que está inactivo
}
```

O si quieres VER TODOS:
```bash
GET /clientes/?incluir_inactivos=true

Response: 200
[
  { "id": 1, "nombre": "Cliente A", "estado": "activo" },
  { "id": 5, "nombre": "Cliente Eliminado", "estado": "inactivo" }
]
```

---

## P3: ¿Cuál es la diferencia entre "soft delete" y "hard delete"?

**Soft Delete:**
```sql
UPDATE clientes SET estado='inactivo' WHERE id=5;
-- Datos permanecen
-- Se puede recuperar
-- Auditoría intacta
```

**Hard Delete:**
```sql
DELETE FROM clientes WHERE id=5;
-- Datos desaparecen
-- NO se puede recuperar
-- Auditoría incompleta
```

**Comparación:**
| Aspecto | Soft Delete | Hard Delete |
|---------|-------------|------------|
| Datos | Se preservan | Se pierden |
| Recuperación | Fácil | Imposible |
| Auditoría | Completa | Incompleta |
| Referencias | Intactas | Rotas |
| GDPR | Compatible | Problemático |
| Producción | Recomendado | Evitar |

---

## P4: ¿Qué pasa con las FK (claves foráneas)?

**Escenario:** Eliminas un cliente que tiene rutas

```python
# Sin soft delete:
DELETE FROM clientes WHERE id=1;  # ❌ Error: Foreign Key Constraint
```

```python
# Con soft delete:
UPDATE clientes SET estado='inactivo' WHERE id=1;  # ✅ Funciona
# Las rutas siguen apuntando a cliente 1
# Pero ese cliente no aparece en GET /clientes/ normal
```

Si quieres **eliminar en cascada** (borrar cliente y sus rutas):
```python
# En el modelo:
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    rutas = relationship(
        "Ruta",
        back_populates="cliente",
        cascade="all, delete-orphan"  # ← Esto hace el cascada
    )

# Con soft delete:
UPDATE clientes SET estado='inactivo' WHERE id=1;
# Así todas las rutas de ese cliente también pueden marcarse como inactivas
```

---

## P5: ¿Cómo evito que el frontend acceda a datos inactivos?

**R:** El filtrado ocurre en el backend:

```python
# ❌ MALO: Frontend filtra
fetch('/clientes/')  # Get ALL
.then(data => data.filter(c => c.estado === 'activo'))  # Filter en JS

# ✅ BIEN: Backend filtra
fetch('/clientes/')  # Backend retorna solo activos
.then(data => data)  # Ya está filtrado
```

En tu caso **ya está bien** porque:
```python
@router.get("/")
def listar_clientes(incluir_inactivos: bool = False, db: Session = Depends(get_db)):
    query = db.query(Cliente)
    if not incluir_inactivos:
        query = query.filter(Cliente.estado == EstadoGeneral.activo)  # ← Backend filtra
    return query.all()
```

---

## P6: ¿Puedo tener usuarios "inactivos" en soft delete?

**Sí, pero con cuidado:**

```python
# ✅ BIEN: Clientes inactivos
GET /clientes/        # No muestra eliminados
DELETE /clientes/1    # Marca como inactivo

# ⚠️ CONSIDERAR: Usuarios del sistema inactivos
# Si el usuario no puede acceder ¿por qué sigue en la BD?
# Opciones:
# 1. Soft delete (como clientes)
# 2. Hard delete (si son datos no-críticos)
# 3. Archivo/Backup (si es para auditoría legal)
```

---

## P7: ¿Qué pasa después de 30 días con un "eliminado"?

**R:** Depende de tu política:

### **Opción 1: Permanente**
Quedá inactivo para siempre:
```python
# Un cliente inactivo hace 5 años:
GET /clientes/?incluir_inactivos=true
# Sigue apareciendo
```

### **Opción 2: Eliminación Definitiva después de X días**
```python
from datetime import datetime, timedelta

# Hard delete after 30 days
deleted_threshold = datetime.now() - timedelta(days=30)

db.query(Cliente).filter(
    Cliente.estado == EstadoGeneral.inactivo,
    Cliente.deleted_at < deleted_threshold
).delete()  # ← Hard delete después de 30 días
```

Esto es lo que hace **Gmail**, **Google Drive**, etc.

---

## P8: ¿Cómo hago un reporte de "clientes eliminados en los últimos 7 días"?

**R:** Necesitas un campo `deleted_at`:

```python
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    estado = Column(Enum(EstadoGeneral))
    deleted_at = Column(DateTime, nullable=True)  # ← Cuándo se eliminó
```

```python
from datetime import datetime, timedelta

week_ago = datetime.now() - timedelta(days=7)

eliminados_recientes = db.query(Cliente).filter(
    Cliente.estado == EstadoGeneral.inactivo,
    Cliente.deleted_at >= week_ago
).all()
```

Actualmente tus modelos no tienen `deleted_at`, pero es fácil agregar:

---

## P9: ¿Qué pasa con los índices de BD?

**Impacto Mínimo:**

```sql
-- Índice actual
CREATE INDEX idx_cliente_estado ON clientes(estado);

-- Búsqueda normal:
SELECT * FROM clientes WHERE estado='activo'  -- ✅ Rápido (usa índice)

-- Búsqueda de inactivos:
SELECT * FROM clientes WHERE estado='inactivo'  -- ✅ Igual rápido
```

Si esperas **muchos inactivos**, considera:
```sql
-- Índice compuesto para búsquedas comunes
CREATE INDEX idx_cliente_estado_nombre ON clientes(estado, nombre);

-- Búsqueda: "Cliente activo con nombre 'Juan'"
SELECT * FROM clientes 
WHERE estado='activo' AND nombre='Juan'  -- ✅ Muy rápido
```

---

## P10: ¿Necesito cambiar las FK para soft delete?

**No, funcionan igual:**

```python
# Modelo Ruta
class Ruta(Base):
    __tablename__ = "rutas"
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id"),  # ← Sigue igual
        nullable=False
    )
    cliente = relationship("Cliente", back_populates="rutas")

# Cuando gets rutas de un cliente inactivo:
ruta = db.query(Ruta).filter(Ruta.cliente_id == 1).first()
# ✅ Funciona perfectamente
# El cliente 1 está inactivo pero la ruta sigue apuntando a él
```

---

## P11: ¿Es difícil cambiar de hard delete a soft delete?

**Muy fácil:**

```python
# Antes (Hard Delete):
db.delete(cliente)
db.commit()

# Después (Soft Delete):
cliente.estado = EstadoGeneral.inactivo
db.add(cliente)
db.commit()

# Una línea de diferencia
```

**Ya lo hiciste en tu backend:**
```python
@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404)
    
    # Soft delete
    cliente.estado = EstadoGeneral.inactivo  ← Esto
    db.add(cliente)
    db.commit()
    return None
```

---

## P12: ¿Qué pasa con los reportes?

**Problema:**
```python
# Reporte: "Total de clientes"
db.query(Cliente).count()
# Incluye inactivos ❌

# Solución:
db.query(Cliente).filter(Cliente.estado == EstadoGeneral.activo).count()
# Solo activos ✅
```

**En tu TESTING_GUIDE.md, todos los reportes deberían especificar:**
```bash
# Clientes activos
GET /clientes/

# Todos (incluyendo eliminados)
GET /clientes/?incluir_inactivos=true
```

---

## P13: ¿Se ve bien en Swagger?

**Sí, perfectamente:**

1. Abre `http://127.0.0.1:8000/docs`
2. Busca `GET /clientes/`
3. Haz click en "Try it out"
4. Verás el parámetro `incluir_inactivos` ✅

---

## P14: ¿Necesito cambiar el frontend?

**Casi nada:**

```javascript
// Antes (sin soft delete):
fetch('/clientes/')
.then(r => r.json())
.then(data => {
  // Aquí venían clientes activos e inactivos
  // Tenía que filtrar en JS ❌
})

// Después (con soft delete):
fetch('/clientes/')
.then(r => r.json())
.then(data => {
  // Aquí vienen SOLO clientes activos ✅
  // Ya está filtrado en backend
})

// Para support (ver TODO):
fetch('/clientes/?incluir_inactivos=true')
.then(r => r.json())
.then(data => {
  // Aquí vienen todos
})
```

---

## P15: ¿Esto cumple GDPR/LGPD?

**Sí:**

- ✅ Se puede "olvidar" un registro (marcarlo inactivo)
- ✅ Se preserva auditoría (historial de cambios)
- ✅ Es reversible (excepto si eliminas hard después de X días)
- ✅ Legal y profesional

---

## 🎓 Resumen Rápido

| Pregunta | Respuesta |
|----------|-----------|
| ¿Por qué soft delete? | Auditoría, integridad referencial, reversibilidad |
| ¿Cómo recuperar? | `PUT /recurso/{id} { "estado": "activo" }` |
| ¿Ver eliminados? | `GET /recurso/?incluir_inactivos=true` |
| ¿Impacto BD? | Mínimo (solo un campo más en queries) |
| ¿Frontend afectado? | No (backend filtra automáticamente) |
| ¿Producción? | Sí, recomendado |

