# 🔐 Cómo Probar la Autenticación

## Método 1: Swagger UI (Recomendado)

### Paso 1: Obtener el Token
1. Ve a http://127.0.0.1:8000/docs
2. Busca la sección **"Autenticación"**
3. Expande `POST /login` (Iniciar Sesión)
4. Click en **"Try it out"**
5. Ingresa:
```json
{
  "email": "admin@test.com",
  "password": "admin123"
}
```
6. Click **"Execute"**
7. **Copia el valor de `access_token`** (texto largo, algo como: `eyJhbGciOiJIUzI1NiIs...`)

### Paso 2: Autorizar en Swagger
8. Click en el botón 🔒 **"Authorize"** (esquina superior derecha)
9. En el campo que aparece, **pega solo el token** (sin comillas, sin "Bearer")
10. Click **"Authorize"**
11. Click **"Close"**

### Paso 3: Probar un Endpoint
12. Ve a la sección **"Clientes"**
13. Expande `POST /clientes/` (Crear Cliente)
14. Click **"Try it out"**
15. Ingresa:
```json
{
  "nombre": "Mi Primer Cliente"
}
```
16. Click **"Execute"**
17. ✅ Deberías ver una respuesta exitosa con el cliente creado

---

## Método 2: PowerShell (Si Swagger no funciona)

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 1. Login
$body = @{
    email = "admin@test.com"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/login" -Method Post -Body $body -ContentType "application/json"
$token = $response.access_token
Write-Host "Token obtenido: $($token.Substring(0,50))..."

# 2. Crear un cliente (usando el token)
$headers = @{
    "Authorization" = "Bearer $token"
}

$clienteBody = @{
    nombre = "Cliente desde PowerShell"
} | ConvertTo-Json

$cliente = Invoke-RestMethod -Uri "http://127.0.0.1:8000/clientes/" -Method Post -Headers $headers -Body $clienteBody -ContentType "application/json"

Write-Host "Cliente creado:"
$cliente | Format-List
```

---

## Método 3: Python (Script de Prueba)

Ejecuta el archivo `test_login_rapido.py`:

```bash
python test_login_rapido.py
```

Esto probará automáticamente:
- Login
- Verificación del token
- Acceso a endpoints protegidos

---

## 👥 Usuarios Disponibles

| Email | Contraseña | Rol | Permisos |
|-------|-----------|-----|----------|
| `admin@test.com` | `admin123` | admin | ✅ Todo |
| `supervisor@test.com` | `supervisor123` | supervisor | ✅ Todo excepto DELETE |
| `gestor_clientes@test.com` | `gestor123` | gestor_clientes | ✅ Solo CRUD en clientes |
| `gestor_rutas@test.com` | `gestor123` | gestor_rutas | ✅ Solo CRUD en rutas |
| `gestor_peajes@test.com` | `gestor123` | gestor_peajes | ✅ Solo CRUD en peajes |
| `consultor@test.com` | `consultor123` | consultor | 📖 Solo lectura (GET) |

---

## ❓ Preguntas Frecuentes

**¿Dónde se crean los usuarios?**
- Se crean automáticamente al iniciar el servidor
- Ver función `create_test_users()` en `app/auth.py`

**¿El token expira?**
- Sí, expira en 30 minutos
- Debes hacer login de nuevo para obtener uno nuevo

**¿Cómo sé si estoy autenticado?**
- Prueba el endpoint `GET /me`
- Si funciona, estás autenticado correctamente

**¿Por qué me sale "Not authenticated"?**
- No estás enviando el token
- El token expiró
- El token es inválido
- Asegúrate de incluir `Bearer ` antes del token en el header Authorization
