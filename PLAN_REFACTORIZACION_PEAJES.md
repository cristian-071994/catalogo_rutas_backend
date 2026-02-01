# 🔧 PLAN DE REFACTORIZACIÓN - PEAJES

## ❌ PROBLEMAS ACTUALES

### 1. Estructura Incorrecta
- **Problema**: Peajes pertenecen a RUTAS (tabla `ruta_peajes`)
- **Correcto**: Peajes deben pertenecer a TRAMOS
- **Razón**: Un peaje está físicamente ubicado en un tramo específico, no en una ruta completa

### 2. Concepto de Ida/Regreso Innecesario
- **Problema**: Campo `direccion` (IDA/REGRESO) en `ruta_peajes`
- **Correcto**: El peaje se paga en ambas direcciones, no necesita dirección
- **Razón**: Si un tramo tiene un peaje, se paga al pasar por ese tramo, independiente de la dirección

### 3. Datos Manuales
- **Problema**: Peajes se crean manualmente con nombre y costo
- **Correcto**: Datos oficiales desde API del gobierno
- **Razón**: Datos actualizados, estandarizados y confiables

## ✅ SOLUCIÓN PROPUESTA

### 1. Nueva Estructura de Datos

#### Modelo Peaje (Actualizado)
```python
class Peaje(Base):
    __tablename__ = "peajes"
    
    id = Column(Integer, primary_key=True)
    
    # Datos de API oficial
    nombre_peaje = Column(String(200), nullable=False)
    sector = Column(String(200))
    categoria_v = Column(String(100))  # Categoría de vehículo
    longitud = Column(Numeric(10, 7))
    latitud = Column(Numeric(10, 7))
    
    # Datos calculados/manuales
    costo = Column(Numeric(8, 2))  # Se actualiza desde API o manual
    
    # Metadata
    ultima_actualizacion = Column(DateTime)
    fuente = Column(String(50))  # "API_GOBIERNO" o "MANUAL"
    estado = Column(Enum(EstadoGeneral))
    
    # Relación con tramos
    tramos = relationship("TramoPeaje", back_populates="peaje")
```

#### Nueva Tabla TramoPeaje (reemplaza RutaPeaje)
```python
class TramoPeaje(Base):
    __tablename__ = "tramo_peajes"
    
    id = Column(Integer, primary_key=True)
    tramo_id = Column(Integer, ForeignKey("tramos.id"))
    peaje_id = Column(Integer, ForeignKey("peajes.id"))
    
    # Constraint: Un peaje no se puede repetir en el mismo tramo
    __table_args__ = (
        UniqueConstraint("tramo_id", "peaje_id", name="uq_tramo_peaje"),
    )
    
    # Relaciones
    tramo = relationship("Tramo", back_populates="peajes")
    peaje = relationship("Peaje", back_populates="tramos")
```

### 2. API de Sincronización

#### Endpoint de Sincronización
```
POST /peajes/sincronizar
- Descarga datos de API oficial
- Actualiza/crea peajes en base de datos
- Retorna resumen de sincronización
```

#### Servicio de Sincronización Diaria
```python
# app/services/peaje_sync_service.py
async def sincronizar_peajes_desde_api():
    """
    Descarga peajes de API oficial y actualiza BD
    """
    url = "https://www.datos.gov.co/resource/68qj-5xux.json"
    # Lógica de sincronización
```

### 3. Cálculo de Costos (Actualizado)

#### Lógica Nueva
```
Ruta -> Tramos -> Peajes
1. Obtener tramos de la ruta
2. Para cada tramo, obtener sus peajes
3. Sumar costos de peajes únicos (sin duplicar)
```

## 📋 TAREAS DE IMPLEMENTACIÓN

### Fase 1: Actualizar Modelos
- [ ] Actualizar modelo Peaje con nuevos campos
- [ ] Crear modelo TramoPeaje
- [ ] Agregar relación peajes en modelo Tramo
- [ ] Eliminar/deprecar modelo RutaPeaje
- [ ] Actualizar enums (eliminar DireccionPeaje)

### Fase 2: Migración de Datos
- [ ] Script para migrar datos de ruta_peajes a tramo_peajes
- [ ] Lógica: asociar peajes a tramos según la ruta
- [ ] Backup de datos antes de migrar

### Fase 3: Servicio de Sincronización
- [ ] Crear peaje_sync_service.py
- [ ] Implementar descarga desde API
- [ ] Mapear campos de API a modelo
- [ ] Manejo de errores y logging
- [ ] Endpoint POST /peajes/sincronizar

### Fase 4: Actualizar Cálculos
- [ ] Actualizar calcular_costo_ruta_detallado()
- [ ] Cambiar lógica: rutas -> tramos -> peajes
- [ ] Eliminar duplicados de peajes
- [ ] Actualizar tests

### Fase 5: Actualizar Endpoints
- [ ] Actualizar POST /rutas/{id}/tramos (asociar peajes)
- [ ] Eliminar endpoints de ruta_peajes
- [ ] Crear endpoints de tramo_peajes
- [ ] Actualizar Swagger docs

### Fase 6: Testing
- [ ] Tests de sincronización
- [ ] Tests de cálculo con nueva estructura
- [ ] Tests de endpoints actualizados

## 🎯 RESULTADO ESPERADO

### Flujo de Uso
1. **Sincronizar peajes** (automático diario o manual)
2. **Crear tramo**: Ej. "Cali - Buga"
3. **Asociar peajes al tramo**: Buscar peajes cercanos por coordenadas o nombre
4. **Crear ruta**: Agregar tramos (peajes ya vienen incluidos)
5. **Calcular costo**: Automático, suma peajes de todos los tramos sin duplicar

### Ventajas
- ✅ Datos oficiales actualizados
- ✅ Estructura lógica (peaje pertenece a tramo)
- ✅ Sin duplicación de peajes en cálculos
- ✅ Geolocalización de peajes (lat/lon)
- ✅ Sincronización automática

## ⏱️ TIEMPO ESTIMADO

- Fase 1: 2 horas
- Fase 2: 1 hora
- Fase 3: 3 horas
- Fase 4: 2 horas
- Fase 5: 2 horas
- Fase 6: 2 horas
**Total: ~12 horas**

## 🚨 RIESGOS

1. **Pérdida de datos**: Hacer backup antes de migrar
2. **Cambio en API**: API puede cambiar estructura
3. **Costos desactualizados**: API puede no tener costos actuales
4. **Coordenadas inexactas**: Peajes pueden estar en ubicaciones aproximadas

## 📝 NOTAS

- La API retorna coordinates como `[longitud, latitud]`
- El campo `categoria_v` puede tener múltiples valores (Cat I, Cat II, etc.)
- Necesitamos decidir qué categoría usar para el costo
- Posible tabla adicional: `peaje_tarifas` (peaje_id, categoria, costo)
