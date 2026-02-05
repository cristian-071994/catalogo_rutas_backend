# 📋 Listado Completo de Endpoints - API v1

**Base URL:** `http://localhost:8000/api/v1`

---

## 🔐 Autenticación (`/auth`)

### 1. Onboarding - Crear Super Admin
- **POST** `/onboarding`
- **Descripción:** Primera instalación del sistema. Crea la primera empresa y super admin.
- **Público:** ✅ Sí (solo funciona cuando no hay empresas)
- **Requiere:** `OnboardingRequest` (email, password, nombre_completo, empresa_nombre, empresa_nit)

### 2. Login
- **POST** `/login`
- **Descripción:** Iniciar sesión con email y contraseña
- **Público:** ✅ Sí
- **Requiere:** `LoginRequest` (email, password)
- **Retorna:** JWT access_token + refresh_token

### 3. Renovar Token
- **POST** `/refresh`
- **Descripción:** Obtener nuevo access_token usando refresh_token
- **Público:** ✅ Sí
- **Requiere:** `RefreshRequest` (refresh_token)

### 4. Obtener Usuario Actual
- **GET** `/me`
- **Descripción:** Obtiene información del usuario autenticado
- **Autenticado:** 🔒 Sí
- **Retorna:** `UsuarioResponse`

### 5. Registro Público
- **POST** `/registro`
- **Descripción:** Registro de nuevos usuarios (queda pendiente de aprobación)
- **Público:** ✅ Sí
- **Requiere:** `RegistroRequest` (email, password, nombre_completo, empresa_nit, rol_solicitado)

### 6. Aprobar Usuario Pendiente
- **POST** `/usuarios/{usuario_id}/aprobar`
- **Descripción:** Aprueba un usuario registrado pero pendiente
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:aprobar` (admin/super_admin de la misma empresa)

---

## 👥 Usuarios (`/usuarios`)

### 7. Listar Usuarios Pendientes
- **GET** `/usuarios/pendientes`
- **Descripción:** Lista usuarios registrados pero no aprobados
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:read`

### 8. Listar Todos los Usuarios
- **GET** `/usuarios/`
- **Descripción:** Lista todos los usuarios de la empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:read`

### 9. Actualizar Usuario
- **PUT** `/usuarios/{usuario_id}`
- **Descripción:** Actualiza datos de un usuario
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:write`

### 10. Obtener Usuario por ID
- **GET** `/usuarios/{usuario_id}`
- **Descripción:** Obtiene detalles de un usuario específico
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:read`

### 11. Crear Usuario
- **POST** `/usuarios/`
- **Descripción:** Crea un nuevo usuario (ya aprobado)
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:write`

### 12. Cambiar Contraseña
- **PUT** `/usuarios/{usuario_id}/cambiar-password`
- **Descripción:** Cambia la contraseña de un usuario
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:write`

### 13. Eliminar Usuario
- **DELETE** `/usuarios/{usuario_id}`
- **Descripción:** Elimina (soft delete) un usuario
- **Autenticado:** 🔒 Sí
- **Permisos:** `usuarios:delete`

---

## 🏢 Empresas (`/empresas`)

### 14. Listar Empresas
- **GET** `/empresas/`
- **Descripción:** Lista todas las empresas
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 15. Obtener Empresa
- **GET** `/empresas/{empresa_id}`
- **Descripción:** Obtiene detalles de una empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 16. Crear Empresa con Administrador
- **POST** `/empresas/`
- **Descripción:** Crea una nueva empresa y su primer administrador
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 17. Actualizar Empresa
- **PUT** `/empresas/{empresa_id}`
- **Descripción:** Actualiza datos de una empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 18. Eliminar Empresa
- **DELETE** `/empresas/{empresa_id}`
- **Descripción:** Elimina (soft delete) una empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

---

## 🛡️ Roles (`/roles`)

### 19. Listar Roles
- **GET** `/roles/`
- **Descripción:** Lista todos los roles del sistema
- **Autenticado:** 🔒 Sí
- **Permisos:** `roles:read`

### 20. Obtener Rol
- **GET** `/roles/{rol_id}`
- **Descripción:** Obtiene detalles de un rol específico
- **Autenticado:** 🔒 Sí
- **Permisos:** `roles:read`

### 21. Crear Rol
- **POST** `/roles/`
- **Descripción:** Crea un nuevo rol
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 22. Actualizar Rol
- **PUT** `/roles/{rol_id}`
- **Descripción:** Actualiza un rol existente
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 23. Asignar Permisos a Rol
- **POST** `/roles/{rol_id}/permisos`
- **Descripción:** Asigna permisos a un rol
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 24. Eliminar Rol
- **DELETE** `/roles/{rol_id}`
- **Descripción:** Elimina un rol (no se puede eliminar roles de sistema)
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

---

## 🔐 Permisos (`/permisos`)

### 25. Listar Permisos
- **GET** `/permisos/`
- **Descripción:** Lista todos los permisos del sistema
- **Autenticado:** 🔒 Sí
- **Permisos:** `permisos:read`

### 26. Obtener Permiso
- **GET** `/permisos/{permiso_id}`
- **Descripción:** Obtiene detalles de un permiso
- **Autenticado:** 🔒 Sí
- **Permisos:** `permisos:read`

### 27. Crear Permiso
- **POST** `/permisos/`
- **Descripción:** Crea un nuevo permiso
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 28. Actualizar Permiso
- **PUT** `/permisos/{permiso_id}`
- **Descripción:** Actualiza un permiso existente
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

### 29. Eliminar Permiso
- **DELETE** `/permisos/{permiso_id}`
- **Descripción:** Elimina un permiso
- **Autenticado:** 🔒 Sí
- **Permisos:** Solo super_admin

---

## ⚙️ Configuración (`/configuracion`)

### 30. Obtener Configuración por Clave
- **GET** `/configuracion/{clave}`
- **Descripción:** Obtiene valor de configuración (ej: precio_combustible)
- **Autenticado:** 🔒 Sí
- **Permisos:** `configuracion:read`

### 31. Listar Todas las Configuraciones
- **GET** `/configuracion/`
- **Descripción:** Lista todas las configuraciones del sistema
- **Autenticado:** 🔒 Sí
- **Permisos:** `configuracion:read`

### 32. Crear Configuración
- **POST** `/configuracion/`
- **Descripción:** Crea una nueva configuración
- **Autenticado:** 🔒 Sí
- **Permisos:** `configuracion:write`

### 33. Actualizar Configuración
- **PUT** `/configuracion/{clave}`
- **Descripción:** Actualiza una configuración existente
- **Autenticado:** 🔒 Sí
- **Permisos:** `configuracion:write`

### 34. Eliminar Configuración
- **DELETE** `/configuracion/{clave}`
- **Descripción:** Elimina una configuración
- **Autenticado:** 🔒 Sí
- **Permisos:** `configuracion:delete`

---

## 👤 Clientes (`/clientes`)

### 35. Crear Cliente
- **POST** `/clientes/`
- **Descripción:** Crea un nuevo cliente
- **Autenticado:** 🔒 Sí
- **Permisos:** `clientes:write`

### 36. Listar Clientes
- **GET** `/clientes/`
- **Descripción:** Lista todos los clientes de la empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** `clientes:read`

### 37. Obtener Cliente
- **GET** `/clientes/{cliente_id}`
- **Descripción:** Obtiene detalles de un cliente
- **Autenticado:** 🔒 Sí
- **Permisos:** `clientes:read`

### 38. Actualizar Cliente
- **PUT** `/clientes/{cliente_id}`
- **Descripción:** Actualiza datos de un cliente
- **Autenticado:** 🔒 Sí
- **Permisos:** `clientes:write`

### 39. Eliminar Cliente
- **DELETE** `/clientes/{cliente_id}`
- **Descripción:** Elimina (soft delete) un cliente
- **Autenticado:** 🔒 Sí
- **Permisos:** `clientes:delete`

---

## 🏷️ Marcas de Vehículos (`/marcas`)

### 40. Listar Marcas
- **GET** `/marcas/`
- **Descripción:** Lista todas las marcas de vehículos
- **Autenticado:** 🔒 Sí
- **Permisos:** `marcas:read`

### 41. Obtener Marca
- **GET** `/marcas/{marca_id}`
- **Descripción:** Obtiene detalles de una marca
- **Autenticado:** 🔒 Sí
- **Permisos:** `marcas:read`

### 42. Crear Marca
- **POST** `/marcas/`
- **Descripción:** Crea una nueva marca de vehículo
- **Autenticado:** 🔒 Sí
- **Permisos:** `marcas:write`

### 43. Actualizar Marca
- **PUT** `/marcas/{marca_id}`
- **Descripción:** Actualiza una marca existente
- **Autenticado:** 🔒 Sí
- **Permisos:** `marcas:write`

### 44. Eliminar Marca
- **DELETE** `/marcas/{marca_id}`
- **Descripción:** Elimina (soft delete) una marca
- **Autenticado:** 🔒 Sí
- **Permisos:** `marcas:delete`

---

## ⚙️ Configuración de Vehículos (`/configuracion-vehiculos`)

### 45. Listar Configuraciones
- **GET** `/configuracion-vehiculos/`
- **Descripción:** Lista todas las configuraciones de vehículos (ej: camión 2 ejes)
- **Autenticado:** 🔒 Sí
- **Permisos:** `config_vehiculos:read`

### 46. Obtener Configuración
- **GET** `/configuracion-vehiculos/{config_id}`
- **Descripción:** Obtiene detalles de una configuración
- **Autenticado:** 🔒 Sí
- **Permisos:** `config_vehiculos:read`

### 47. Crear Configuración
- **POST** `/configuracion-vehiculos/`
- **Descripción:** Crea una nueva configuración de vehículo
- **Autenticado:** 🔒 Sí
- **Permisos:** `config_vehiculos:write`

### 48. Actualizar Configuración
- **PUT** `/configuracion-vehiculos/{config_id}`
- **Descripción:** Actualiza una configuración existente
- **Autenticado:** 🔒 Sí
- **Permisos:** `config_vehiculos:write`

### 49. Eliminar Configuración
- **DELETE** `/configuracion-vehiculos/{config_id}`
- **Descripción:** Elimina (soft delete) una configuración
- **Autenticado:** 🔒 Sí
- **Permisos:** `config_vehiculos:delete`

---

## ⛽ Rendimiento de Configuraciones (`/rendimiento`)

### 50. Listar Rendimientos
- **GET** `/rendimiento/`
- **Descripción:** Lista todos los rendimientos (galones/km por configuración)
- **Autenticado:** 🔒 Sí
- **Permisos:** `rendimiento:read`

### 51. Listar por Configuración
- **GET** `/rendimiento/configuracion/{config_id}`
- **Descripción:** Lista rendimientos de una configuración específica
- **Autenticado:** 🔒 Sí
- **Permisos:** `rendimiento:read`

### 52. Obtener Rendimiento
- **GET** `/rendimiento/{rendimiento_id}`
- **Descripción:** Obtiene detalles de un rendimiento
- **Autenticado:** 🔒 Sí
- **Permisos:** `rendimiento:read`

### 53. Crear Rendimiento
- **POST** `/rendimiento/`
- **Descripción:** Crea un nuevo rendimiento
- **Autenticado:** 🔒 Sí
- **Permisos:** `rendimiento:write`

### 54. Actualizar Rendimiento
- **PUT** `/rendimiento/{rendimiento_id}`
- **Descripción:** Actualiza un rendimiento existente
- **Autenticado:** 🔒 Sí
- **Permisos:** `rendimiento:write`

### 55. Eliminar Rendimiento
- **DELETE** `/rendimiento/{rendimiento_id}`
- **Descripción:** Elimina (soft delete) un rendimiento
- **Autenticado:** 🔒 Sí
- **Permisos:** `rendimiento:delete`

---

## 🚗 Vehículos (`/vehiculos`)

### 56. Listar Vehículos
- **GET** `/vehiculos/`
- **Descripción:** Lista todos los vehículos de la empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** `vehiculos:read`

### 57. Obtener Vehículo
- **GET** `/vehiculos/{vehiculo_id}`
- **Descripción:** Obtiene detalles de un vehículo
- **Autenticado:** 🔒 Sí
- **Permisos:** `vehiculos:read`

### 58. Crear Vehículo
- **POST** `/vehiculos/`
- **Descripción:** Crea un nuevo vehículo
- **Autenticado:** 🔒 Sí
- **Permisos:** `vehiculos:write`

### 59. Actualizar Vehículo
- **PUT** `/vehiculos/{vehiculo_id}`
- **Descripción:** Actualiza datos de un vehículo
- **Autenticado:** 🔒 Sí
- **Permisos:** `vehiculos:write`

### 60. Eliminar Vehículo
- **DELETE** `/vehiculos/{vehiculo_id}`
- **Descripción:** Elimina (soft delete) un vehículo
- **Autenticado:** 🔒 Sí
- **Permisos:** `vehiculos:delete`

---

## 🗺️ Rutas (`/rutas`)

### 61. Crear Ruta
- **POST** `/rutas/`
- **Descripción:** Crea una nueva ruta para un cliente
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:write`

### 62. Listar Rutas
- **GET** `/rutas/`
- **Descripción:** Lista todas las rutas de la empresa
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:read`

### 63. Obtener Ruta
- **GET** `/rutas/{ruta_id}`
- **Descripción:** Obtiene detalles de una ruta
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:read`

### 64. Agregar Tramo a Ruta
- **POST** `/rutas/{ruta_id}/tramos/{tramo_id}`
- **Descripción:** Asocia un tramo existente a una ruta
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:write`

### 65. Obtener Resumen de Ruta
- **GET** `/rutas/{ruta_id}/resumen`
- **Descripción:** Calcula costos totales de una ruta con un vehículo (query param: vehiculo_id)
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:read`

### 66. Actualizar Ruta
- **PUT** `/rutas/{ruta_id}`
- **Descripción:** Actualiza datos de una ruta
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:write`

### 67. Eliminar Ruta
- **DELETE** `/rutas/{ruta_id}`
- **Descripción:** Elimina (soft delete) una ruta
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:delete`

### 68. Listar Rutas por Cliente
- **GET** `/rutas/cliente/{cliente_id}`
- **Descripción:** Lista todas las rutas de un cliente específico
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:read`

### 69. Quitar Tramo de Ruta
- **DELETE** `/rutas/{ruta_id}/tramos/{tramo_ruta_id}`
- **Descripción:** Elimina un tramo de una ruta
- **Autenticado:** 🔒 Sí
- **Permisos:** `rutas:write`

---

## 🛣️ Tramos (`/tramos`)

### 70. Listar Tramos
- **GET** `/tramos/`
- **Descripción:** Lista todos los tramos disponibles
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:read`

### 71. Obtener Tramo
- **GET** `/tramos/{tramo_id}`
- **Descripción:** Obtiene detalles de un tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:read`

### 72. Crear Tramo
- **POST** `/tramos/`
- **Descripción:** Crea un nuevo tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:write`

### 73. Actualizar Tramo
- **PUT** `/tramos/{tramo_id}`
- **Descripción:** Actualiza un tramo existente
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:write`

### 74. Asociar Peaje a Tramo
- **POST** `/tramos/{tramo_id}/peajes/{peaje_id}`
- **Descripción:** Asocia un peaje a un tramo con su tarifa
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:write`

### 75. Listar Peajes de un Tramo
- **GET** `/tramos/{tramo_id}/peajes`
- **Descripción:** Lista todos los peajes asociados a un tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:read`

### 76. Quitar Peaje de Tramo
- **DELETE** `/tramos/{tramo_id}/peajes/{peaje_id}`
- **Descripción:** Elimina la asociación peaje-tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:write`

### 77. Eliminar Tramo
- **DELETE** `/tramos/{tramo_id}`
- **Descripción:** Elimina (soft delete) un tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:delete`

---

## 📍 Detalles de Tramo (`/tramo-detalle`)

### 78. Listar Detalles de Tramo
- **GET** `/tramo-detalle/tramo/{tramo_id}`
- **Descripción:** Lista todos los detalles (puntos intermedios) de un tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:read`

### 79. Obtener Detalle de Tramo
- **GET** `/tramo-detalle/{detalle_id}`
- **Descripción:** Obtiene un detalle específico
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:read`

### 80. Crear Detalle de Tramo
- **POST** `/tramo-detalle/`
- **Descripción:** Crea un punto intermedio en un tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:write`

### 81. Actualizar Detalle de Tramo
- **PUT** `/tramo-detalle/{detalle_id}`
- **Descripción:** Actualiza un detalle de tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:write`

### 82. Eliminar Detalle de Tramo
- **DELETE** `/tramo-detalle/{detalle_id}`
- **Descripción:** Elimina (soft delete) un detalle de tramo
- **Autenticado:** 🔒 Sí
- **Permisos:** `tramos:delete`

---

## 🚧 Peajes (`/peajes`)

### 83. Sincronizar Peajes
- **POST** `/peajes/sincronizar`
- **Descripción:** Sincroniza peajes desde la API oficial del gobierno
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:write`

### 84. Listar Peajes
- **GET** `/peajes/`
- **Descripción:** Lista todos los peajes disponibles
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:read`

### 85. Obtener Peaje
- **GET** `/peajes/{peaje_id}`
- **Descripción:** Obtiene detalles de un peaje
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:read`

### 86. Buscar Peajes por Nombre
- **GET** `/peajes/buscar/por-nombre`
- **Descripción:** Busca peajes por nombre (query param: nombre)
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:read`

### 87. Crear Peaje
- **POST** `/peajes/`
- **Descripción:** Crea un nuevo peaje manualmente
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:write`

### 88. Actualizar Peaje
- **PUT** `/peajes/{peaje_id}`
- **Descripción:** Actualiza datos de un peaje
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:write`

### 89. Eliminar Peaje
- **DELETE** `/peajes/{peaje_id}`
- **Descripción:** Elimina (soft delete) un peaje
- **Autenticado:** 🔒 Sí
- **Permisos:** `peajes:delete`

---

## 📊 Resumen por Categoría

### Autenticación y Usuarios
- **6** endpoints de autenticación/onboarding
- **7** endpoints de usuarios

### Administración de Empresas y Roles
- **5** endpoints de empresas
- **6** endpoints de roles
- **5** endpoints de permisos

### Configuración del Sistema
- **5** endpoints de configuración general
- **5** endpoints de clientes
- **5** endpoints de marcas de vehículos
- **5** endpoints de configuración de vehículos
- **6** endpoints de rendimiento
- **5** endpoints de vehículos

### Gestión de Rutas y Costos
- **9** endpoints de rutas
- **8** endpoints de tramos
- **5** endpoints de detalles de tramo
- **7** endpoints de peajes

---

## 🔒 Notas de Seguridad

1. **Multi-Tenancy:** Los endpoints filtran automáticamente por empresa_id del usuario autenticado
2. **Soft Delete:** Los recursos eliminados se marcan como `activo=false`, no se eliminan físicamente
3. **Permisos Granulares:** Cada recurso tiene permisos de `read`, `write` y `delete`
4. **Roles de Sistema:** `super_admin`, `admin`, `usuario` tienen diferentes niveles de acceso
5. **JWT Tokens:** Expiran en 30 minutos (access) y 7 días (refresh)

---

## 📝 Documentación Interactiva

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**Total de Endpoints:** **89**
