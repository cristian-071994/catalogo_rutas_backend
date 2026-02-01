"""
Script para probar los nuevos endpoints de Roles y Permisos
Fase 2 - Sistema dinámico de roles y permisos
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Credenciales de administrador
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"


def get_token():
    """Obtiene token JWT del administrador"""
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    data = response.json()
    return data["access_token"]


def test_listar_roles():
    """Prueba: GET /roles/ - Listar todos los roles"""
    print("\n" + "="*60)
    print("TEST: Listar Roles")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/roles/", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_obtener_rol():
    """Prueba: GET /roles/{rol_id} - Obtener rol detallado con permisos"""
    print("\n" + "="*60)
    print("TEST: Obtener Rol Detallado (ID=1)")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/roles/1", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_listar_permisos():
    """Prueba: GET /permisos/ - Listar todos los permisos"""
    print("\n" + "="*60)
    print("TEST: Listar Permisos")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/permisos/", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Número de permisos: {len(response.json())}")
    
    # Mostrar categorías
    categorias = set()
    for permiso in response.json():
        categorias.add(permiso.get("categoria"))
    
    print(f"Categorías encontradas: {sorted(categorias)}")


def test_listar_permisos_por_categoria():
    """Prueba: GET /permisos/?categoria=usuarios - Filtrar por categoría"""
    print("\n" + "="*60)
    print("TEST: Listar Permisos por Categoría (usuarios)")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/permisos/",
        headers=headers,
        params={"categoria": "usuarios"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Permisos de usuarios: {len(response.json())}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_crear_rol_personalizado():
    """Prueba: POST /roles/ - Crear un rol personalizado"""
    print("\n" + "="*60)
    print("TEST: Crear Rol Personalizado")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    nuevo_rol = {
        "nombre": "gestor_reportes",
        "descripcion": "Gestor especializado en reportes y análisis",
        "permisos": [20, 21, 22]  # IDs de algunos permisos
    }
    
    response = requests.post(
        f"{BASE_URL}/roles/",
        headers=headers,
        json=nuevo_rol
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_actualizar_rol():
    """Prueba: PUT /roles/{rol_id} - Actualizar rol"""
    print("\n" + "="*60)
    print("TEST: Actualizar Rol (asumiendo que existe ID=7)")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    actualizar_rol = {
        "descripcion": "Gestor de reportes mejorado - actualizado"
    }
    
    response = requests.put(
        f"{BASE_URL}/roles/7",
        headers=headers,
        json=actualizar_rol
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")


def test_crear_permiso_personalizado():
    """Prueba: POST /permisos/ - Crear un permiso personalizado"""
    print("\n" + "="*60)
    print("TEST: Crear Permiso Personalizado")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    nuevo_permiso = {
        "nombre": "exportar_datos",
        "descripcion": "Permitir exportación de datos en formato Excel/CSV",
        "categoria": "reportes"
    }
    
    response = requests.post(
        f"{BASE_URL}/permisos/",
        headers=headers,
        json=nuevo_permiso
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_asignar_permisos_a_rol():
    """Prueba: POST /roles/{rol_id}/permisos - Asignar permisos a rol"""
    print("\n" + "="*60)
    print("TEST: Asignar Permisos a Rol")
    print("="*60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    asignar = {
        "permiso_ids": [1, 2, 3, 4, 5]  # IDs de permisos
    }
    
    response = requests.post(
        f"{BASE_URL}/roles/7/permisos",
        headers=headers,
        json=asignar
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Permisos asignados:")
        rol_data = response.json()
        print(f"  Rol: {rol_data.get('nombre')}")
        print(f"  Permisos: {[p.get('nombre') for p in rol_data.get('permisos', [])]}")
    else:
        print(f"Error: {response.text}")


def main():
    """Ejecuta todos los tests"""
    print("\n" + "🚀 "*20)
    print("PRUEBAS DE ROUTERS: ROLES Y PERMISOS")
    print("Fase 2 - Sistema dinámico de roles y permisos")
    print("🚀 "*20)
    
    try:
        # Tests básicos
        test_listar_roles()
        test_obtener_rol()
        test_listar_permisos()
        test_listar_permisos_por_categoria()
        
        # Tests de creación
        test_crear_rol_personalizado()
        test_crear_permiso_personalizado()
        
        # Tests de actualización y asignación
        test_actualizar_rol()
        test_asignar_permisos_a_rol()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor en http://127.0.0.1:8000")
        print("   Asegúrate de que el servidor FastAPI está ejecutándose")
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    main()
