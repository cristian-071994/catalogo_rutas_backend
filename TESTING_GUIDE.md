# Plan de Testing - Catalogo Rutas Backend

## Orden Recomendado de Testing

El siguiente orden garantiza que cada endpoint funcione correctamente basándose en los anteriores.

---

## 1. CONFIGURACIÓN GENERAL (Sistema)

### POST /configuracion/
Crear configuración del sistema (precio por galón)
```bash
POST http://127.0.0.1:8000/configuracion/
Content-Type: application/json

{
  "clave": "precio_galon",
  "valor": "12000",
  "descripcion": "Precio por galón de combustible"
}
```
**Response esperado:** 201 Created
**Usar:** `clave` y `id` para referencia posterior

---

### GET /configuracion/
Listar toda la configuración del sistema
```bash
GET http://127.0.0.1:8000/configuracion/
```
**Response esperado:** 200 OK, lista con items

---

### GET /configuracion/{config_id}
Obtener un item de configuración específico
```bash
GET http://127.0.0.1:8000/configuracion/{id_del_item}
```
**Response esperado:** 200 OK

---

## 2. CLIENTES

### POST /clientes/
Crear un cliente
```bash
POST http://127.0.0.1:8000/clientes/
Content-Type: application/json

{
  "nombre": "Cliente A"
}
```
**Response esperado:** 201 Created
**Guardar:** `id` para usarlo en rutas

---

### GET /clientes/
Listar todos los clientes
```bash
GET http://127.0.0.1:8000/clientes/
```
**Response esperado:** 200 OK, lista de clientes

---

### GET /clientes/{cliente_id}
Obtener cliente específico
```bash
GET http://127.0.0.1:8000/clientes/{id}
```
**Response esperado:** 200 OK

---

### PUT /clientes/{cliente_id}
Actualizar cliente
```bash
PUT http://127.0.0.1:8000/clientes/{id}
Content-Type: application/json

{
  "nombre": "Cliente A Actualizado"
}
```
**Response esperado:** 200 OK

---

### DELETE /clientes/{cliente_id}
Eliminar cliente (soft delete)
```bash
DELETE http://127.0.0.1:8000/clientes/{id}
```
**Response esperado:** 204 No Content
**Verificar:** GET /clientes/{id} debe mostrar estado="inactivo"

---

## 3. TRAMOS (Segmentos de Ruta)

### POST /tramos/
Crear un tramo
```bash
POST http://127.0.0.1:8000/tramos/
Content-Type: application/json

{
  "origen": "Mediacanoa",
  "destino": "Buenaventura"
}
```
**Response esperado:** 201 Created
**Guardar:** `id` para usarlo en detalles

---

### GET /tramos/
Listar todos los tramos
```bash
GET http://127.0.0.1:8000/tramos/
```
**Response esperado:** 200 OK

---

### GET /tramos/{tramo_id}
Obtener tramo específico
```bash
GET http://127.0.0.1:8000/tramos/{id}
```
**Response esperado:** 200 OK

---

## 4. TRAMO DETALLE (Configuraciones por Tramo)

### POST /tramo-detalle/
Crear detalle de tramo (combinación: carga + terreno + km)
```bash
POST http://127.0.0.1:8000/tramo-detalle/
Content-Type: application/json

{
  "tramo_id": 1,
  "tipo_carga": "VACIO",
  "tipo_terreno": "PLANO",
  "kilometros": 150.5
}
```
**Response esperado:** 201 Created
**Nota:** Las combinaciones (tramo_id + tipo_carga + tipo_terreno) deben ser únicas

---

### GET /tramo-detalle/tramo/{tramo_id}
Listar todos los detalles de un tramo
```bash
GET http://127.0.0.1:8000/tramo-detalle/tramo/{tramo_id}
```
**Response esperado:** 200 OK

---

### GET /tramo-detalle/{detalle_id}
Obtener detalle específico
```bash
GET http://127.0.0.1:8000/tramo-detalle/{id}
```
**Response esperado:** 200 OK

---

### PUT /tramo-detalle/{detalle_id}
Actualizar detalle
```bash
PUT http://127.0.0.1:8000/tramo-detalle/{id}
Content-Type: application/json

{
  "kilometros": 160.0
}
```
**Response esperado:** 200 OK

---

### DELETE /tramo-detalle/{detalle_id}
Eliminar detalle (soft delete)
```bash
DELETE http://127.0.0.1:8000/tramo-detalle/{id}
```
**Response esperado:** 204 No Content

---

## 5. PEAJES (Tolls)

### POST /peajes/
Crear un peaje
```bash
POST http://127.0.0.1:8000/peajes/
Content-Type: application/json

{
  "nombre": "Peaje Buenaventura",
  "costo": 25000.00
}
```
**Response esperado:** 201 Created
**Guardar:** `id` para usarlo en rutas

---

### GET /peajes/
Listar todos los peajes
```bash
GET http://127.0.0.1:8000/peajes/
```
**Response esperado:** 200 OK

---

### GET /peajes/{peaje_id}
Obtener peaje específico
```bash
GET http://127.0.0.1:8000/peajes/{id}
```
**Response esperado:** 200 OK

---

### PUT /peajes/{peaje_id}
Actualizar peaje
```bash
PUT http://127.0.0.1:8000/peajes/{id}
Content-Type: application/json

{
  "costo": 27000.00
}
```
**Response esperado:** 200 OK

---

### DELETE /peajes/{peaje_id}
Eliminar peaje (soft delete)
```bash
DELETE http://127.0.0.1:8000/peajes/{id}
```
**Response esperado:** 204 No Content

---

## 6. MARCAS DE VEHÍCULOS

### POST /marcas-vehiculos/
Crear marca
```bash
POST http://127.0.0.1:8000/marcas-vehiculos/
Content-Type: application/json

{
  "nombre": "Chevrolet"
}
```
**Response esperado:** 201 Created
**Guardar:** `id`

---

### GET /marcas-vehiculos/
Listar marcas
```bash
GET http://127.0.0.1:8000/marcas-vehiculos/
```
**Response esperado:** 200 OK

---

### GET /marcas-vehiculos/{marca_id}
Obtener marca específica
```bash
GET http://127.0.0.1:8000/marcas-vehiculos/{id}
```
**Response esperado:** 200 OK

---

### PUT /marcas-vehiculos/{marca_id}
Actualizar marca
```bash
PUT http://127.0.0.1:8000/marcas-vehiculos/{id}
Content-Type: application/json

{
  "nombre": "Chevrolet Actualizada"
}
```
**Response esperado:** 200 OK

---

### DELETE /marcas-vehiculos/{marca_id}
Eliminar marca (soft delete)
```bash
DELETE http://127.0.0.1:8000/marcas-vehiculos/{id}
```
**Response esperado:** 204 No Content

---

## 7. CONFIGURACIÓN DE VEHÍCULOS

### POST /configuracion-vehiculos/
Crear configuración (marca + año)
```bash
POST http://127.0.0.1:8000/configuracion-vehiculos/
Content-Type: application/json

{
  "marca_id": 1,
  "modelo": 2020
}
```
**Response esperado:** 201 Created
**Guardar:** `id`

---

### GET /configuracion-vehiculos/
Listar configuraciones
```bash
GET http://127.0.0.1:8000/configuracion-vehiculos/
```
**Response esperado:** 200 OK

---

### GET /configuracion-vehiculos/{config_id}
Obtener configuración específica
```bash
GET http://127.0.0.1:8000/configuracion-vehiculos/{id}
```
**Response esperado:** 200 OK

---

### PUT /configuracion-vehiculos/{config_id}
Actualizar configuración
```bash
PUT http://127.0.0.1:8000/configuracion-vehiculos/{id}
Content-Type: application/json

{
  "modelo": 2021
}
```
**Response esperado:** 200 OK

---

### DELETE /configuracion-vehiculos/{config_id}
Eliminar configuración (soft delete)
```bash
DELETE http://127.0.0.1:8000/configuracion-vehiculos/{id}
```
**Response esperado:** 204 No Content

---

## 8. RENDIMIENTO DE CONFIGURACIÓN

### POST /rendimiento-configuracion/
Crear rendimiento (km/galón para configuración + carga + terreno)
```bash
POST http://127.0.0.1:8000/rendimiento-configuracion/
Content-Type: application/json

{
  "configuracion_id": 1,
  "tipo_carga": "VACIO",
  "tipo_terreno": "PLANO",
  "rendimiento_km_galon": 12.5
}
```
**Response esperado:** 201 Created
**Nota:** Crear múltiples combinaciones para el mismo vehículo

**Ejemplo 2:**
```bash
POST http://127.0.0.1:8000/rendimiento-configuracion/
Content-Type: application/json

{
  "configuracion_id": 1,
  "tipo_carga": "CARGADO",
  "tipo_terreno": "PLANO",
  "rendimiento_km_galon": 8.5
}
```

---

### GET /rendimiento-configuracion/
Listar todos los rendimientos
```bash
GET http://127.0.0.1:8000/rendimiento-configuracion/
```
**Response esperado:** 200 OK

---

### GET /rendimiento-configuracion/configuracion/{config_id}
Listar rendimientos de una configuración
```bash
GET http://127.0.0.1:8000/rendimiento-configuracion/configuracion/{config_id}
```
**Response esperado:** 200 OK

---

### GET /rendimiento-configuracion/{rendimiento_id}
Obtener rendimiento específico
```bash
GET http://127.0.0.1:8000/rendimiento-configuracion/{id}
```
**Response esperado:** 200 OK

---

### PUT /rendimiento-configuracion/{rendimiento_id}
Actualizar rendimiento
```bash
PUT http://127.0.0.1:8000/rendimiento-configuracion/{id}
Content-Type: application/json

{
  "rendimiento_km_galon": 13.0
}
```
**Response esperado:** 200 OK

---

### DELETE /rendimiento-configuracion/{rendimiento_id}
Eliminar rendimiento (soft delete)
```bash
DELETE http://127.0.0.1:8000/rendimiento-configuracion/{id}
```
**Response esperado:** 204 No Content

---

## 9. VEHÍCULOS

### POST /vehiculos/
Crear vehículo
```bash
POST http://127.0.0.1:8000/vehiculos/
Content-Type: application/json

{
  "placa": "ABC123",
  "configuracion_id": 1
}
```
**Response esperado:** 201 Created
**Guardar:** `id`

---

### GET /vehiculos/
Listar vehículos
```bash
GET http://127.0.0.1:8000/vehiculos/
```
**Response esperado:** 200 OK

---

### GET /vehiculos/{vehiculo_id}
Obtener vehículo específico
```bash
GET http://127.0.0.1:8000/vehiculos/{id}
```
**Response esperado:** 200 OK

---

### PUT /vehiculos/{vehiculo_id}
Actualizar vehículo
```bash
PUT http://127.0.0.1:8000/vehiculos/{id}
Content-Type: application/json

{
  "placa": "ABC124"
}
```
**Response esperado:** 200 OK

---

### DELETE /vehiculos/{vehiculo_id}
Eliminar vehículo (soft delete)
```bash
DELETE http://127.0.0.1:8000/vehiculos/{id}
```
**Response esperado:** 204 No Content

---

## 10. RUTAS (Lo más importante)

### POST /rutas/
Crear ruta
```bash
POST http://127.0.0.1:8000/rutas/
Content-Type: application/json

{
  "cliente_id": 1,
  "nombre": "Ruta Mediacanoa - Buenaventura",
  "descripcion": "Ruta de carga regular"
}
```
**Response esperado:** 201 Created
**Guardar:** `id`

---

### GET /rutas/
Listar todas las rutas
```bash
GET http://127.0.0.1:8000/rutas/
```
**Response esperado:** 200 OK

---

### GET /rutas/{ruta_id}
Obtener ruta específica
```bash
GET http://127.0.0.1:8000/rutas/{id}
```
**Response esperado:** 200 OK

---

### GET /rutas/cliente/{cliente_id}
Listar rutas de un cliente específico
```bash
GET http://127.0.0.1:8000/rutas/cliente/{cliente_id}
```
**Response esperado:** 200 OK

---

### POST /rutas/{ruta_id}/tramos/{tramo_id}
Agregar un tramo a la ruta
```bash
POST http://127.0.0.1:8000/rutas/1/tramos/1
Content-Type: application/json

{
  "orden": 1
}
```
**Response esperado:** 201 Created
**Nota:** El `orden` define la secuencia de tramos

---

### POST /rutas/{ruta_id}/peajes/{peaje_id}
Agregar un peaje a la ruta (con dirección)
```bash
POST http://127.0.0.1:8000/rutas/1/peajes/1
Content-Type: application/json

{
  "direccion": "IDA",
  "orden": 1
}
```
**Response esperado:** 201 Created
**Nota:** `direccion` puede ser "IDA" o "REGRESO" (permite repetir peaje)

**Ejemplo 2 - Mismo peaje en REGRESO:**
```bash
POST http://127.0.0.1:8000/rutas/1/peajes/1
Content-Type: application/json

{
  "direccion": "REGRESO",
  "orden": 2
}
```

---

### GET /rutas/{ruta_id}/resumen
**IMPORTANTE** - Obtener cálculo completo de costo de la ruta
```bash
GET http://127.0.0.1:8000/rutas/1/resumen?configuracion_id=1
```
**Response esperado:** 200 OK
**Payload incluye:**
- Total km
- Galones necesarios (cálculo ponderado)
- Costo de combustible
- Total peajes
- Costo total
- Desglose por tramo
- Configuración usada

**Si NO especificas configuracion_id:**
```bash
GET http://127.0.0.1:8000/rutas/1/resumen
```
Usará `configuracion_id` por defecto (1)

---

### PUT /rutas/{ruta_id}
Actualizar ruta
```bash
PUT http://127.0.0.1:8000/rutas/{id}
Content-Type: application/json

{
  "nombre": "Ruta Actualizada",
  "descripcion": "Nueva descripción"
}
```
**Response esperado:** 200 OK

---

### DELETE /rutas/{ruta_id}/tramos/{tramo_ruta_id}
Eliminar un tramo de la ruta (elimina relación, no el tramo)
```bash
DELETE http://127.0.0.1:8000/rutas/1/tramos/1
```
**Response esperado:** 204 No Content

---

### DELETE /rutas/{ruta_id}/peajes/{ruta_peaje_id}
Eliminar un peaje de la ruta (elimina relación, no el peaje)
```bash
DELETE http://127.0.0.1:8000/rutas/1/peajes/1
```
**Response esperado:** 204 No Content

---

### DELETE /rutas/{ruta_id}
Eliminar ruta completamente (soft delete)
```bash
DELETE http://127.0.0.1:8000/rutas/{id}
```
**Response esperado:** 204 No Content
**Verificar:** GET /rutas/{id} debe mostrar estado="inactivo"

---

## FLUJO DE TESTING COMPLETO (Paso a Paso)

Si quieres hacer un test END-TO-END completo, sigue este orden:

1. **POST /configuracion/** - Configurar precio galón
2. **POST /clientes/** - Crear cliente
3. **POST /marcas-vehiculos/** - Crear marca (ej: Chevrolet)
4. **POST /configuracion-vehiculos/** - Crear config (ej: Chevrolet 2020)
5. **POST /rendimiento-configuracion/** - Crear rendimiento VACIO+PLANO (12.5 km/gal)
6. **POST /rendimiento-configuracion/** - Crear rendimiento CARGADO+PLANO (8.5 km/gal)
7. **POST /vehiculos/** - Crear vehículo con la config
8. **POST /tramos/** - Crear tramo
9. **POST /tramo-detalle/** - Agregar VACIO+PLANO al tramo
10. **POST /tramo-detalle/** - Agregar CARGADO+PLANO al tramo
11. **POST /peajes/** - Crear peaje
12. **POST /rutas/** - Crear ruta
13. **POST /rutas/{id}/tramos/{id}** - Agregar tramo a ruta
14. **POST /rutas/{id}/peajes/{id}** - Agregar peaje IDA
15. **POST /rutas/{id}/peajes/{id}** - Agregar peaje REGRESO (mismo peaje)
16. **GET /rutas/{id}/resumen** - Ver cálculo completo
17. **PUT /rutas/{id}** - Actualizar ruta
18. **PUT /tramo-detalle/{id}** - Actualizar detalle
19. **DELETE /rutas/{id}/tramos/{id}** - Eliminar tramo de ruta
20. **DELETE /rutas/{id}/peajes/{id}** - Eliminar peaje de ruta
21. **DELETE /rutas/{id}** - Soft delete ruta

---

## NOTAS IMPORTANTES

- **Soft Delete:** Todos los DELETE endpoints marcan como `estado="inactivo"` en lugar de eliminar
- **Status codes:** 
  - 200 = OK (GET, PUT)
  - 201 = Created (POST)
  - 204 = No Content (DELETE exitoso)
  - 400 = Bad Request (validación)
  - 404 = Not Found
- **IDs:** Siempre guardar los `id` retornados para usarlos en siguientes requests
- **Orden:** Respetar el orden de dependencias (no puedes crear detalle sin tramo)
- **Cálculo de costo:** Solo funciona si la ruta tiene tramos, detalles y rendimientos configurados

