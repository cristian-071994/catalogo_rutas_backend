# 🚀 GUÍA DE ONBOARDING - ARRANQUE DESDE CERO

## 🎯 ¿Qué es el Onboarding?

El **onboarding** es el proceso de **primera instalación** del sistema cuando la base de datos está completamente vacía.

En producción, cuando lances la aplicación por primera vez, NO habrá empresas ni usuarios. Esta guía te muestra cómo arrancar correctamente.

---

## 📋 FLUJO PROFESIONAL DE ARRANQUE

### 🔹 ESCENARIO 1: Base de Datos Vacía (Primera Vez)

```
Usuario interesado → Usa /onboarding → Crea empresa + admin → Listo ✅
```

**Pasos:**

1. **Usuario accede al sistema** (primera vez)
2. **NO puede hacer login** (no hay usuarios)
3. **Usa endpoint público: `POST /api/v1/onboarding`**
4. Ingresa:
   - Datos de su empresa (nombre, NIT, contacto)
   - Datos del primer administrador (nombre, email, contraseña)
5. **Sistema crea:**
   - ✅ Empresa
   - ✅ Usuario administrador (aprobado automáticamente)
6. **Usuario hace login** con sus credenciales ✅

---

### 🔹 ESCENARIO 2: Después del Onboarding

```
Nuevo usuario → Usa /registro → Pendiente → Admin aprueba → Login ✅
```

**Pasos:**

1. **Nuevo empleado** quiere registrarse
2. **Usa: `POST /api/v1/registro`**
   - Necesita el **NIT de su empresa**
3. **Queda pendiente de aprobación**
4. **Admin de la empresa** aprueba con `POST /api/v1/usuarios/{id}/aprobar`
5. **Usuario hace login** ✅

---

## 🔧 ENDPOINT DE ONBOARDING

### `POST /api/v1/onboarding`

**Características:**
- ✅ **Público** (no requiere autenticación)
- ✅ **Solo funciona UNA VEZ** (si no hay empresas)
- ✅ **Crea empresa + admin** en una transacción
- ✅ **Auto-cierre** después de la primera empresa

### Request:

```json
POST /api/v1/onboarding
Content-Type: application/json

{
  "empresa_nombre": "Mi Empresa de Transporte S.A.S.",
  "empresa_nit": "9001234567",
  "empresa_contacto": "Juan Pérez - Gerente General",
  "empresa_email": "contacto@miempresa.com",
  "empresa_telefono": "3001234567",
  "admin_nombre": "Juan Pérez",
  "admin_email": "admin@miempresa.com",
  "admin_password": "MiPassword123!"
}
```

### Response (201 Created):

```json
{
  "mensaje": "¡Onboarding exitoso! Empresa 'Mi Empresa de Transporte S.A.S.' creada. Ya puede iniciar sesión con admin@miempresa.com",
  "empresa": {
    "id": 1,
    "nombre": "Mi Empresa de Transporte S.A.S.",
    "nit": "9001234567",
    "contacto": "Juan Pérez - Gerente General",
    "email": "contacto@miempresa.com",
    "telefono": "3001234567",
    "activo": 1,
    "created_at": "2026-02-03T10:30:00"
  },
  "admin_email": "admin@miempresa.com"
}
```

### Segundo intento (después de crear primera empresa):

```json
POST /api/v1/onboarding
(mismos datos...)

❌ Response (403 Forbidden):
{
  "detail": "El sistema ya está inicializado. Ya existen 1 empresa(s) registrada(s). Use el endpoint /registro para crear nuevos usuarios."
}
```

---

## ✅ VALIDACIONES IMPLEMENTADAS

### 1. **NIT sin guiones (solo números)**

```json
// ✅ VÁLIDO - Sistema auto-sanitiza
"empresa_nit": "900-123-456-7"  → Se convierte a "9001234567"
"empresa_nit": "900.123.456"    → Se convierte a "900123456"
"empresa_nit": "9001234567"     → Se mantiene "9001234567"

// ❌ INVÁLIDO
"empresa_nit": "ABC123"         → Error: debe contener dígitos
"empresa_nit": "12"             → Error: mínimo 5 dígitos
```

### 2. **Empresa única por NIT**

```json
// Primera empresa con NIT 9001234567
POST /api/v1/onboarding
{"empresa_nit": "9001234567", ...}
✅ Creada

// Segunda empresa con MISMO NIT
POST /api/v1/onboarding
{"empresa_nit": "9001234567", ...}
❌ Error: "Ya existe una empresa con NIT 9001234567"
```

### 3. **Email único de administrador**

```json
// Primer admin con email admin@empresa.com
POST /api/v1/onboarding
{"admin_email": "admin@empresa.com", ...}
✅ Creado

// Segundo intento con MISMO email
POST /api/v1/onboarding
{"admin_email": "admin@empresa.com", ...}
❌ Error: "El email admin@empresa.com ya está registrado"
```

---

## 🧪 CÓMO PROBAR EN DESARROLLO

### Opción 1: Recrear BD desde cero

```powershell
# 1. Detener backend
Ctrl+C

# 2. Eliminar BD
cd C:\Users\cgutierrez\proyectos\catalogo_rutas_backend\backend
Remove-Item catalogo_rutas.db

# 3. Reiniciar backend
uvicorn app.main:app --reload

# 4. Probar onboarding
curl -X POST http://localhost:8000/api/v1/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "empresa_nombre": "Test Company",
    "empresa_nit": "9999999999",
    "empresa_contacto": "Test Contact",
    "empresa_email": "test@test.com",
    "empresa_telefono": "3001234567",
    "admin_nombre": "Admin Test",
    "admin_email": "admin@test.com",
    "admin_password": "test123"
  }'
```

### Opción 2: Con datos de prueba (desarrollo)

El sistema crea automáticamente 3 empresas de prueba:
- Cointra (NIT: 9001234567)
- Geotab (NIT: 9002345678)
- Satena (NIT: 9003456789)

Para probar onboarding, primero elimina la BD.

---

## 📱 FLUJO EN EL FRONTEND

### Pantalla de Bienvenida (BD vacía)

```tsx
// Detectar si el sistema está vacío
const checkSistemaVacio = async () => {
  try {
    await api.login("test@test.com", "test"); // Intentar login
  } catch (error) {
    // Si no hay usuarios, mostrar formulario de onboarding
    setMostrarOnboarding(true);
  }
};

// Formulario de onboarding
<OnboardingForm>
  <h1>Bienvenido - Primera Instalación</h1>
  <p>Crea tu empresa y cuenta de administrador</p>
  
  <Section title="Datos de la Empresa">
    <Input name="empresa_nombre" />
    <Input name="empresa_nit" placeholder="9001234567" />
    <Input name="empresa_contacto" />
  </Section>
  
  <Section title="Datos del Administrador">
    <Input name="admin_nombre" />
    <Input name="admin_email" />
    <Input name="admin_password" type="password" />
  </Section>
  
  <Button onClick={handleOnboarding}>
    Crear Empresa y Administrador
  </Button>
</OnboardingForm>
```

---

## 🎯 CASOS DE USO REALES

### Caso 1: Empresa Nueva (Producción)

**Situación:** Cointra compra tu sistema por primera vez.

1. **Instalan la aplicación** (BD vacía)
2. **Gerente de Cointra accede** a la URL
3. **Ve formulario de onboarding**
4. Completa:
   - Empresa: "Cointra S.A.S."
   - NIT: "9001234567"
   - Email admin: "admin@cointra.com"
5. **Sistema crea todo**
6. **Gerente hace login** ✅
7. **Gerente aprueba** a sus empleados

### Caso 2: Segunda Empresa (SaaS Multi-tenant)

**Situación:** Geotab también compra tu sistema.

**❌ NO pueden usar /onboarding** (ya hay empresas)

**Opciones:**

**Opción A: Admin global crea empresa**
```json
POST /api/v1/empresas (requiere super-admin)
{
  "nombre": "Geotab",
  "nit": "9002345678",
  ...
}
```

**Opción B: Extender onboarding** (futuro)
- Crear endpoint `/onboarding-nueva-empresa`
- Requiere código de invitación
- Crea empresa + primer admin

---

## 🔒 SEGURIDAD

### ✅ Protecciones Implementadas

1. **Auto-cierre:** Onboarding solo funciona una vez
2. **Validación de unicidad:** NIT y email únicos
3. **Transacciones:** Todo se crea o nada (rollback)
4. **Sanitización:** NIT se limpia automáticamente
5. **Password hasheado:** Nunca se almacena en texto plano

### ⚠️ Consideraciones

**En producción:**
- Considera agregar **CAPTCHA** en onboarding
- Implementar **rate limiting** (anti-spam)
- **Email de verificación** antes de activar
- **Logs de auditoría** de empresas creadas

---

## 📊 COMPARACIÓN CON OTROS SISTEMAS

| Sistema | Onboarding |
|---------|-----------|
| **Stripe** | Público, auto-servicio |
| **Shopify** | Público, auto-servicio |
| **AWS** | Público, verificación por email |
| **Tu Sistema** | ✅ Público, auto-servicio (primera vez) |

**Tu implementación sigue estándares profesionales SaaS.** ✅

---

## 🚀 PRÓXIMOS PASOS (Opcional)

### Mejoras Futuras

1. **Email de bienvenida**
   ```python
   # Después del onboarding
   send_email(
     to=admin_email,
     subject="¡Bienvenido a Catálogo de Rutas!",
     template="onboarding_success"
   )
   ```

2. **Dashboard de onboarding**
   - Wizard paso a paso
   - Progreso visual
   - Tutorial integrado

3. **Onboarding multi-empresa**
   - Para SaaS true multi-tenant
   - Con códigos de invitación
   - Sin límite de empresas

---

## 📞 RESUMEN

**¿Base de datos vacía?**
→ Usa `POST /api/v1/onboarding`

**¿Ya hay empresas?**
→ Usa `POST /api/v1/registro` (requiere NIT)

**¿Soy admin?**
→ Aprueba usuarios con `POST /api/v1/usuarios/{id}/aprobar`

---

**¡Sistema listo para arranque profesional desde cero!** 🎉
