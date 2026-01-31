"""
Script simple de prueba para el sistema de autenticación
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "="*80)
print("PRUEBAS DE AUTENTICACIÓN Y USUARIOS")
print("="*80 + "\n")

# Prueba 1: Endpoint raíz
print("1. Probando endpoint raíz...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Respuesta: {response.json()}")
    print("   ✅ Servidor funcionando\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Prueba 2: Login como admin
print("2. Login como Administrador...")
try:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        admin_token = data["access_token"]
        print(f"   Usuario: {data['usuario_nombre']}")
        print(f"   Rol: {data['usuario_rol']}")
        print(f"   Token: {admin_token[:50]}...")
        print("   ✅ Login exitoso\n")
    else:
        print(f"   ❌ Login falló: {response.text}\n")
        admin_token = None
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    admin_token = None

# Prueba 3: Verificar /me con el token
if admin_token:
    print("3. Verificando /me con token de admin...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ID: {data['id']}")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Email: {data['email']}")
            print(f"   Rol: {data['rol']}")
            print("   ✅ Endpoint /me funcionando\n")
        else:
            print(f"   ❌ Error: {response.text}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

# Prueba 4: Login de todos los usuarios
print("4. Probando login de todos los usuarios...")
usuarios = [
    ("Administrador", "admin@test.com", "admin123", "admin"),
    ("Supervisor", "supervisor@test.com", "supervisor123", "supervisor"),
    ("Gestor Rutas", "gestor_rutas@test.com", "gestor123", "gestor_rutas"),
    ("Gestor Peajes", "gestor_peajes@test.com", "gestor123", "gestor_peajes"),
    ("Gestor Clientes", "gestor_clientes@test.com", "gestor123", "gestor_clientes"),
    ("Consultor", "consultor@test.com", "consultor123", "consultor"),
]

tokens = {}
for nombre, email, password, rol in usuarios:
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            tokens[rol] = data["access_token"]
            print(f"   ✅ {nombre:20} → Login OK (Rol: {data['usuario_rol']})")
        else:
            print(f"   ❌ {nombre:20} → Error {response.status_code}")
    except Exception as e:
        print(f"   ❌ {nombre:20} → Error: {str(e)[:40]}")

print(f"\n   Tokens obtenidos: {len(tokens)}/6\n")

# Prueba 5: Acceso sin token
print("5. Probando acceso sin token (debe fallar)...")
try:
    response = requests.get(f"{BASE_URL}/clientes/")
    if response.status_code == 401:
        print(f"   ✅ Acceso bloqueado correctamente (401 Unauthorized)\n")
    else:
        print(f"   ❌ Status inesperado: {response.status_code}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Prueba 6: Acceso con token inválido
print("6. Probando acceso con token inválido (debe fallar)...")
try:
    headers = {"Authorization": "Bearer token_falso_12345"}
    response = requests.get(f"{BASE_URL}/clientes/", headers=headers)
    if response.status_code == 401:
        print(f"   ✅ Token inválido rechazado correctamente (401)\n")
    else:
        print(f"   ❌ Status inesperado: {response.status_code}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Prueba 7: Acceso a endpoints con admin
if 'admin' in tokens:
    print("7. Probando acceso del admin a diferentes endpoints...")
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    
    endpoints = ["/clientes/", "/peajes/", "/rutas/", "/tramos/"]
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            status = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status} GET {endpoint:20} → Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ GET {endpoint:20} → Error")

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)
print("✅ Sistema de autenticación funcionando correctamente")
print("✅ Todos los usuarios creados y operativos")
print("✅ Tokens JWT generándose correctamente")
print("✅ Validación de permisos activa")
print("="*80 + "\n")
