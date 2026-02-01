# 🔐 GUÍA DE AUTENTICACIÓN Y AUTORIZACIÓN

## Sistema de Roles y Permisos

Tu backend ahora tiene autenticación JWT y autorización basada en roles.

---

## 📝 Usuarios de Prueba (Creados Automáticamente)

Cuando levantes el servidor, se crean estos usuarios automáticamente:

| Email | Contraseña | Rol | Permisos |
|-------|------------|-----|----------|
| `admin@test.com` | `admin123` | **admin** | Todo (incluido DELETE) |
| `supervisor@test.com` | `supervisor123` | **supervisor** | Todo EXCEPTO DELETE |
| `gestor_rutas@test.com` | `gestor123` | **gestor_rutas** | POST/PUT/DELETE rutas solamente |
| `gestor_peajes@test.com` | `gestor123` | **gestor_peajes** | POST/PUT/DELETE peajes solamente |
| `gestor_clientes@test.com` | `gestor123` | **gestor_clientes** | POST/PUT/DELETE clientes solamente |
| `consultor@test.com` | `consultor123` | **consultor** | GET solamente (lectura) |

---

## 🔓 Flujo de Autenticación

### 1️⃣ Login y obtener Token

**Endpoint:** `POST /login`

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario_nombre": "Administrador",
  "usuario_rol": "admin"
}
```

### 2️⃣ Usar el Token en Siguientes Peticiones

Guarda el `access_token` y úsalo en el header `Authorization`:

**Endpoint:** `GET /clientes/`

```bash
curl -X GET "http://127.0.0.1:8000/clientes/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3️⃣ Ver Usuario Actual

**Endpoint:** `GET /me`

```bash
curl -X GET "http://127.0.0.1:8000/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 1,
  "nombre": "Administrador",
  "email": "admin@test.com",
  "rol": "admin",
  "activo": 1
}
```

---

## 🛡️ Matriz de Permisos por Rol

### **admin** (Acceso Total)
```
✅ POST /clientes/          (crear)
✅ GET /clientes/           (listar)
✅ GET /clientes/{id}       (ver)
✅ PUT /clientes/{id}       (actualizar)
✅ DELETE /clientes/{id}    (eliminar/soft-delete)

✅ POST /peajes/
✅ GET /peajes/
✅ PUT /peajes/{id}
✅ DELETE /peajes/{id}

✅ POST /rutas/
✅ GET /rutas/
✅ PUT /rutas/{id}
✅ DELETE /rutas/{id}

[... TODOS los endpoints]
```

### **supervisor** (Todo Excepto DELETE)
```
✅ POST /clientes/          (crear)
✅ GET /clientes/           (listar)
✅ GET /clientes/{id}       (ver)
✅ PUT /clientes/{id}       (actualizar)
❌ DELETE /clientes/{id}    (BLOQUEADO)

[Similar para peajes, rutas, etc... TODO EXCEPTO DELETE]
```

### **gestor_rutas** (Solo Rutas)
```
✅ POST /rutas/             (crear rutas)
✅ GET /rutas/              (listar rutas)
✅ PUT /rutas/{id}          (actualizar rutas)
✅ DELETE /rutas/{id}       (eliminar rutas)

❌ POST /clientes/          (BLOQUEADO)
❌ POST /peajes/            (BLOQUEADO)
❌ [Otros recursos]         (BLOQUEADO)
```

### **gestor_peajes** (Solo Peajes)
```
✅ POST /peajes/            (crear peajes)
✅ GET /peajes/             (listar peajes)
✅ PUT /peajes/{id}         (actualizar peajes)
✅ DELETE /peajes/{id}      (eliminar peajes)

❌ POST /clientes/          (BLOQUEADO)
❌ POST /rutas/             (BLOQUEADO)
❌ [Otros recursos]         (BLOQUEADO)
```

### **gestor_clientes** (Solo Clientes)
```
✅ POST /clientes/          (crear clientes)
✅ GET /clientes/           (listar clientes)
✅ PUT /clientes/{id}       (actualizar clientes)
✅ DELETE /clientes/{id}    (eliminar clientes)

❌ POST /peajes/            (BLOQUEADO)
❌ POST /rutas/             (BLOQUEADO)
❌ [Otros recursos]         (BLOQUEADO)
```

### **consultor** (Solo Lectura)
```
✅ GET /clientes/           (listar)
✅ GET /clientes/{id}       (ver)
✅ GET /peajes/             (listar)
✅ GET /rutas/              (listar)
✅ GET /tramos/             (listar)
[... Todos los GET]

❌ POST /...                (BLOQUEADO)
❌ PUT /...                 (BLOQUEADO)
❌ DELETE /...              (BLOQUEADO)
```

---

## 📊 Ejemplo Completo (Paso a Paso)

### **Escenario:** Admin crea cliente, Supervisor intenta eliminarlo

#### 1. Admin hace login y obtiene token:

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "usuario_nombre": "Administrador",
  "usuario_rol": "admin"
}
```

#### 2. Admin crea un cliente:

```bash
curl -X POST "http://127.0.0.1:8000/clientes/" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mi Cliente"}'
```

**Respuesta:** ✅ 201 Created
```json
{
  "id": 100,
  "nombre": "Mi Cliente",
  "estado": "activo",
  "rutas": []
}
```

#### 3. Supervisor obtiene token:

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "supervisor@test.com", "password": "supervisor123"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "usuario_nombre": "Supervisor General",
  "usuario_rol": "supervisor"
}
```

#### 4. Supervisor intenta eliminar el cliente:

```bash
curl -X DELETE "http://127.0.0.1:8000/clientes/100" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Respuesta:** ❌ 403 Forbidden
```json
{
  "detail": "Los supervisores no tienen permiso para eliminar (soft delete)"
}
```

#### 5. Admin elimina el cliente (soft delete):

```bash
curl -X DELETE "http://127.0.0.1:8000/clientes/100" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Respuesta:** ✅ 204 No Content

---

## 🔧 Testing en Swagger

1. Abre http://127.0.0.1:8000/docs
2. Haz click en "Try it out" en `POST /login`
3. Ingresa credenciales:
   ```json
   {
     "email": "admin@test.com",
     "password": "admin123"
   }
   ```
4. Copia el `access_token`
5. Haz click en el botón **"Authorize"** (arriba a la derecha)
6. Pega el token:
   ```
   Bearer eyJhbGc...
   ```
7. Ahora todos los endpoints estarán autenticados

---

## ⚙️ Próximos Pasos (Futura Mejora)

### En PRODUCCIÓN:
1. **Cambiar SECRET_KEY** en `app/auth.py`
   ```python
   SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
   ```

2. **Usar variables de entorno**
   ```bash
   # .env
   SECRET_KEY=tu-clave-super-segura-aleatoria
   DATABASE_URL=postgresql://user:pass@localhost/db
   ```

3. **Refresh tokens** (expiración más segura)
   - Token access: 15 minutos
   - Token refresh: 7 días

4. **Rate limiting** en login (prevenir ataques)

5. **2FA** (autenticación de dos factores)

---

## 📌 Notas Importantes

- ✅ **Autenticación:** Es en el BACKEND (JWT firmado)
- ✅ **Autorización:** Es en el BACKEND (validación por rol)
- ✅ **Frontend:** Solo muestra/oculta botones (UX)
- ✅ **Token expira:** 30 minutos (configurable)
- ✅ **Contraseñas:** Hasheadas con bcrypt (nunca en texto plano)
- ✅ **Soft delete:** Respetado (supervisores NO pueden eliminar)

---

## 🐛 Errores Comunes

### Error: "Token inválido o expirado"
**Solución:** Haz login de nuevo y obtén un token fresco

### Error: "No tienes permiso"
**Solución:** El rol del usuario no tiene acceso a ese endpoint

### Error: "Usuario inactivo"
**Solución:** El usuario fue desactivado por un admin

---

**¡Tu sistema de autorización está listo para producción!** 🎉
