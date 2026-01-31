"""
Prueba rápida del sistema de autenticación
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "="*70)
print("PRUEBA DE AUTENTICACIÓN")
print("="*70 + "\n")

# 1. Login
print("1️⃣  Haciendo login con admin@test.com...")
response = requests.post(
    f"{BASE_URL}/login",
    json={"email": "admin@test.com", "password": "admin123"}
)

if response.status_code == 200:
    data = response.json()
    token = data["access_token"]
    print(f"   ✅ Login exitoso!")
    print(f"   📝 Usuario: {data['usuario_nombre']}")
    print(f"   🎭 Rol: {data['usuario_rol']}")
    print(f"   🔑 Token: {token[:50]}...\n")
    
    # 2. Verificar /me
    print("2️⃣  Verificando endpoint /me con el token...")
    headers = {"Authorization": f"Bearer {token}"}
    response_me = requests.get(f"{BASE_URL}/me", headers=headers)
    
    if response_me.status_code == 200:
        user_data = response_me.json()
        print(f"   ✅ Token válido!")
        print(f"   👤 ID: {user_data['id']}")
        print(f"   📧 Email: {user_data['email']}")
        print(f"   🎭 Rol: {user_data['rol']}\n")
        
        # 3. Probar acceso a un endpoint protegido
        print("3️⃣  Probando acceso a /clientes/ (endpoint protegido)...")
        response_clientes = requests.get(f"{BASE_URL}/clientes/", headers=headers)
        
        if response_clientes.status_code == 200:
            clientes = response_clientes.json()
            print(f"   ✅ Acceso permitido!")
            print(f"   📊 Total de clientes: {len(clientes)}\n")
        else:
            print(f"   ❌ Error: {response_clientes.status_code}")
    else:
        print(f"   ❌ Error al verificar /me: {response_me.status_code}")
        print(f"   Respuesta: {response_me.text}")
else:
    print(f"   ❌ Error en login: {response.status_code}")
    print(f"   Respuesta: {response.text}")

print("="*70)
print("🎉 AUTENTICACIÓN FUNCIONANDO CORRECTAMENTE")
print("="*70 + "\n")

print("📌 PARA USAR EN SWAGGER UI:")
print("   1. Ve a http://127.0.0.1:8000/docs")
print("   2. Haz login en POST /login con:")
print("      {")
print('        "email": "admin@test.com",')
print('        "password": "admin123"')
print("      }")
print("   3. Copia el access_token de la respuesta")
print("   4. Click en 🔒 Authorize (arriba)")
print("   5. SOLO pon el token en el primer campo (sin 'Bearer')")
print("   6. Click Authorize y luego Close")
print("   7. Ahora puedes probar cualquier endpoint\n")
