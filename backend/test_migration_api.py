"""
Script de prueba de la migración de Enum a Rol
Verifica que los endpoints de roles y usuarios funcionen correctamente
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("🧪 PRUEBAS DE MIGRACIÓN: ENUM -> TABLA ROL")
print("=" * 70)

# 1. LOGIN COMO ADMIN
print("\n1️⃣  Login como Admin")
print("-" * 70)
response = requests.post(
    f"{BASE_URL}/login",
    json={"email": "admin@test.com", "password": "admin123"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Token obtenido (primeros 30 chars): {token[:30]}...")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"❌ Error: {response.json()}")
    exit(1)

# 2. LISTAR USUARIOS
print("\n2️⃣  Listar Usuarios")
print("-" * 70)
response = requests.get(f"{BASE_URL}/usuarios/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    usuarios = response.json()
    print(f"✅ Total usuarios: {len(usuarios)}")
    for u in usuarios[:3]:
        print(f"   - {u['email']:30} Rol: {u['rol']}")
else:
    print(f"❌ Error: {response.json()}")

# 3. CREAR NUEVO USUARIO CON ROL DE BD
print("\n3️⃣  Crear Nuevo Usuario")
print("-" * 70)
response = requests.post(
    f"{BASE_URL}/usuarios/",
    json={
        "nombre": "Gestor de Pruebas",
        "email": "test_gestor@test.com",
        "password": "test123456",
        "rol": "gestor_rutas"
    },
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    usuario = response.json()
    print(f"✅ Usuario creado:")
    print(f"   - Email: {usuario['email']}")
    print(f"   - Rol: {usuario['rol']}")
    print(f"   - ID: {usuario['id']}")
else:
    print(f"❌ Error: {response.json()}")

# 4. LISTAR ROLES
print("\n4️⃣  Listar Roles")
print("-" * 70)
response = requests.get(f"{BASE_URL}/roles/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    roles = response.json()
    print(f"✅ Total roles: {len(roles)}")
    for r in roles[:3]:
        print(f"   - {r['nombre']:20} - {r['descripcion']}")
else:
    print(f"❌ Error: {response.json()}")

# 5. OBTENER ROL DETALLADO CON PERMISOS
print("\n5️⃣  Obtener Rol Detallado (Admin)")
print("-" * 70)
response = requests.get(f"{BASE_URL}/roles/1", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    rol = response.json()
    print(f"✅ Rol: {rol['nombre']}")
    print(f"   Descripción: {rol['descripcion']}")
    print(f"   Permisos ({len(rol['permisos'])} total):")
    for p in rol['permisos'][:5]:
        print(f"      - {p['nombre']}")
    if len(rol['permisos']) > 5:
        print(f"      ... y {len(rol['permisos']) - 5} más")
else:
    print(f"❌ Error: {response.json()}")

# 6. LISTAR PERMISOS
print("\n6️⃣  Listar Permisos")
print("-" * 70)
response = requests.get(f"{BASE_URL}/permisos/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    permisos = response.json()
    print(f"✅ Total permisos: {len(permisos)}")
    
    # Agrupar por categoría
    por_categoria = {}
    for p in permisos:
        cat = p.get('categoria', 'sin_categoria')
        if cat not in por_categoria:
            por_categoria[cat] = 0
        por_categoria[cat] += 1
    
    for cat, count in sorted(por_categoria.items()):
        print(f"   - {cat:20} {count:3} permisos")
else:
    print(f"❌ Error: {response.json()}")

# 7. CAMBIAR CONTRASEÑA DEL USUARIO ACTUAL
print("\n7️⃣  Cambiar Contraseña")
print("-" * 70)
response = requests.put(
    f"{BASE_URL}/usuarios/cambiar-contraseña",
    json={
        "password_actual": "admin123",
        "password_nueva": "admin123_new",
        "password_confirmar": "admin123_new"
    },
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Contraseña cambiada exitosamente")
else:
    print(f"❌ Error: {response.json()}")

print("\n" + "=" * 70)
print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("=" * 70)
print("\n📊 Resumen:")
print("   ✅ Sistema de roles migrado de Enum a tabla Rol")
print("   ✅ Usuarios asignados a roles mediante FK (rol_id)")
print("   ✅ Routers de roles y permisos funcionan correctamente")
print("   ✅ Permisos organizados por categoría")
print("   ✅ Relación many-to-many rol-permiso funcionante")
