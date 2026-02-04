"""
Test del flujo completo de onboarding
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Esperar a que el servidor esté listo
print("⏳ Esperando conexión con el servidor...")
for i in range(10):
    try:
        requests.get(BASE_URL.replace("/api/v1", "/docs"))
        print("✅ Servidor conectado\n")
        break
    except:
        if i == 9:
            print("❌ No se pudo conectar al servidor")
            exit(1)
        time.sleep(1)

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print()

def test_onboarding_flow():
    print("\n🚀 INICIANDO PRUEBA DE FLUJO DE ONBOARDING\n")
    
    # 1. ONBOARDING - Crear super_admin
    print("1️⃣ Creando super_admin...")
    onboarding_data = {
        "email": "cgutierrez@admin.com",
        "nombre_completo": "Carlos Gutierrez",
        "password": "Admin123!"
    }
    response = requests.post(f"{BASE_URL}/onboarding", json=onboarding_data)
    print_response("ONBOARDING - Crear Super Admin", response)
    
    if response.status_code != 200:
        print("❌ Error en onboarding, deteniendo prueba")
        return
    
    # 2. LOGIN como super_admin
    print("2️⃣ Login como super_admin...")
    login_data = {
        "username": "cgutierrez@admin.com",
        "password": "Admin123!"
    }
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print_response("LOGIN - Super Admin", response)
    
    if response.status_code != 200:
        print("❌ Error en login, deteniendo prueba")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. CREAR EMPRESA CON ADMIN
    print("3️⃣ Creando primera empresa (Cointra) con su admin...")
    empresa_data = {
        "empresa_nombre": "Cointra S.A.S.",
        "empresa_nit": "900-123-456-7",
        "empresa_contacto": "Juan Pérez",
        "empresa_email": "contacto@cointra.com",
        "empresa_telefono": "+57 300 1234567",
        "admin_email": "admin@cointra.com",
        "admin_nombre": "Juan Pérez",
        "admin_password": "Cointra123!"
    }
    response = requests.post(f"{BASE_URL}/empresas", json=empresa_data, headers=headers)
    print_response("CREAR EMPRESA - Cointra", response)
    
    if response.status_code != 200:
        print("❌ Error creando empresa, deteniendo prueba")
        return
    
    # 4. LOGIN como admin de empresa
    print("4️⃣ Login como admin de Cointra...")
    login_data = {
        "username": "admin@cointra.com",
        "password": "Cointra123!"
    }
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print_response("LOGIN - Admin de Cointra", response)
    
    if response.status_code != 200:
        print("❌ Error en login de empresa")
        return
    
    empresa_token = response.json()["access_token"]
    empresa_headers = {"Authorization": f"Bearer {empresa_token}"}
    
    # 5. VERIFICAR INFO DEL USUARIO
    print("5️⃣ Obteniendo información del usuario logueado...")
    response = requests.get(f"{BASE_URL}/me", headers=empresa_headers)
    print_response("USUARIO ACTUAL - Admin Cointra", response)
    
    print("\n" + "="*60)
    print("✅ FLUJO DE ONBOARDING COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("\n📊 RESUMEN:")
    print("  • Super admin creado: cgutierrez@admin.com")
    print("  • Empresa creada: Cointra S.A.S. (NIT: 9001234567)")
    print("  • Admin empresa creado: admin@cointra.com")
    print("  • Login de ambos usuarios: ✅")
    print()

if __name__ == "__main__":
    test_onboarding_flow()
