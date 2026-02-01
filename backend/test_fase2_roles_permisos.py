"""
Script de prueba para Fase 2: Roles y Permisos Dinámicos
"""

import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

class TestFase2:
    def __init__(self):
        self.token: Optional[str] = None
        self.admin_user = {
            "email": "admin@test.com",
            "password": "admin123"
        }
    
    def print_section(self, title: str):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    def print_result(self, status: str, message: str, data=None):
        icon = "✅" if status == "OK" else "❌"
        print(f"{icon} {message}")
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def login(self) -> bool:
        """Realizar login y obtener token"""
        self.print_section("1. LOGIN - Obtener Token JWT")
        
        response = requests.post(
            f"{BASE_URL}/login",
            json=self.admin_user
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.print_result("OK", f"Login exitoso como {self.admin_user['email']}")
            self.print_result("OK", f"Token: {self.token[:50]}...")
            return True
        else:
            self.print_result("ERROR", f"Login fallido: {response.status_code}")
            self.print_result("ERROR", response.text)
            return False
    
    def get_headers(self) -> dict:
        """Obtener headers con autorización"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    # ====== PRUEBAS DE ROLES ======
    
    def test_listar_roles(self):
        """Listar todos los roles"""
        self.print_section("2. ROLES - Listar Todos")
        
        response = requests.get(
            f"{BASE_URL}/roles/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            roles = response.json()
            self.print_result("OK", f"Se obtuvieron {len(roles)} roles")
            for rol in roles:
                print(f"  - {rol['nombre']}: {rol['descripcion']}")
            return roles
        else:
            self.print_result("ERROR", f"Error al listar roles: {response.status_code}")
            self.print_result("ERROR", response.text)
            return []
    
    def test_obtener_rol_detallado(self, rol_id: int):
        """Obtener un rol con todos sus permisos"""
        self.print_section(f"3. ROLES - Obtener Rol Detallado (ID: {rol_id})")
        
        response = requests.get(
            f"{BASE_URL}/roles/{rol_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            rol = response.json()
            self.print_result("OK", f"Rol: {rol['nombre']}")
            self.print_result("OK", f"Descripción: {rol['descripcion']}")
            self.print_result("OK", f"Permisos asignados: {len(rol['permisos'])}")
            for perm in rol['permisos'][:5]:  # Mostrar primeros 5
                print(f"  - {perm['nombre']}: {perm['descripcion']}")
            if len(rol['permisos']) > 5:
                print(f"  ... y {len(rol['permisos']) - 5} más")
            return rol
        else:
            self.print_result("ERROR", f"Error al obtener rol: {response.status_code}")
            return None
    
    def test_crear_rol(self):
        """Crear un nuevo rol personalizado"""
        self.print_section("4. ROLES - Crear Nuevo Rol")
        
        nuevo_rol = {
            "nombre": "auditor",
            "descripcion": "Rol para auditar actividades del sistema",
            "permisos": []  # Sin permisos al inicio
        }
        
        response = requests.post(
            f"{BASE_URL}/roles/",
            headers=self.get_headers(),
            json=nuevo_rol
        )
        
        if response.status_code == 201:
            rol = response.json()
            self.print_result("OK", f"Rol creado: {rol['nombre']}")
            self.print_result("OK", f"ID: {rol['id']}")
            return rol
        else:
            self.print_result("ERROR", f"Error al crear rol: {response.status_code}")
            self.print_result("ERROR", response.text)
            return None
    
    # ====== PRUEBAS DE PERMISOS ======
    
    def test_listar_permisos(self):
        """Listar todos los permisos"""
        self.print_section("5. PERMISOS - Listar Todos")
        
        response = requests.get(
            f"{BASE_URL}/permisos/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            permisos = response.json()
            self.print_result("OK", f"Se obtuvieron {len(permisos)} permisos")
            
            # Agrupar por categoría
            by_category = {}
            for perm in permisos:
                cat = perm.get('categoria', 'sin_categoría')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(perm)
            
            for categoria, items in list(by_category.items())[:3]:
                print(f"\n  Categoría: {categoria} ({len(items)} permisos)")
                for perm in items[:2]:
                    print(f"    - {perm['nombre']}")
                if len(items) > 2:
                    print(f"    ... y {len(items) - 2} más")
            
            return permisos
        else:
            self.print_result("ERROR", f"Error al listar permisos: {response.status_code}")
            return []
    
    def test_obtener_permiso(self, permiso_id: int):
        """Obtener un permiso específico"""
        self.print_section(f"6. PERMISOS - Obtener Permiso (ID: {permiso_id})")
        
        response = requests.get(
            f"{BASE_URL}/permisos/{permiso_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            permiso = response.json()
            self.print_result("OK", f"Permiso: {permiso['nombre']}")
            self.print_result("OK", f"Categoría: {permiso['categoria']}")
            self.print_result("OK", f"Descripción: {permiso['descripcion']}")
            return permiso
        else:
            self.print_result("ERROR", f"Error al obtener permiso: {response.status_code}")
            return None
    
    def test_asignar_permisos_a_rol(self, rol_id: int, permiso_ids: list):
        """Asignar permisos a un rol"""
        self.print_section(f"7. ROLES - Asignar Permisos a Rol (ID: {rol_id})")
        
        data = {
            "permiso_ids": permiso_ids
        }
        
        response = requests.post(
            f"{BASE_URL}/roles/{rol_id}/permisos",
            headers=self.get_headers(),
            json=data
        )
        
        if response.status_code == 200:
            rol = response.json()
            self.print_result("OK", f"Permisos asignados al rol: {rol['nombre']}")
            self.print_result("OK", f"Total de permisos: {len(rol['permisos'])}")
            return rol
        else:
            self.print_result("ERROR", f"Error al asignar permisos: {response.status_code}")
            self.print_result("ERROR", response.text)
            return None
    
    def test_actualizar_rol(self, rol_id: int):
        """Actualizar un rol"""
        self.print_section(f"8. ROLES - Actualizar Rol (ID: {rol_id})")
        
        update_data = {
            "nombre": "auditor_v2",
            "descripcion": "Rol para auditar actividades del sistema - Versión 2"
        }
        
        response = requests.put(
            f"{BASE_URL}/roles/{rol_id}",
            headers=self.get_headers(),
            json=update_data
        )
        
        if response.status_code == 200:
            rol = response.json()
            self.print_result("OK", f"Rol actualizado: {rol['nombre']}")
            self.print_result("OK", f"Nueva descripción: {rol['descripcion']}")
            return rol
        else:
            self.print_result("ERROR", f"Error al actualizar rol: {response.status_code}")
            self.print_result("ERROR", response.text)
            return None
    
    def test_eliminar_rol(self, rol_id: int):
        """Eliminar (soft delete) un rol"""
        self.print_section(f"9. ROLES - Eliminar Rol (ID: {rol_id})")
        
        response = requests.delete(
            f"{BASE_URL}/roles/{rol_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 204:
            self.print_result("OK", f"Rol eliminado exitosamente (soft delete)")
            return True
        else:
            self.print_result("ERROR", f"Error al eliminar rol: {response.status_code}")
            self.print_result("ERROR", response.text)
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("\n" + "🚀 " * 35)
        print("PRUEBAS DE FASE 2: ROLES Y PERMISOS DINÁMICOS")
        print("🚀 " * 35)
        
        # 1. Login
        if not self.login():
            return
        
        # 2. Listar roles
        roles = self.test_listar_roles()
        
        # 3. Obtener rol detallado
        if roles:
            self.test_obtener_rol_detallado(roles[0]['id'])
        
        # 4. Listar permisos
        permisos = self.test_listar_permisos()
        
        # 5. Obtener permiso específico
        if permisos:
            self.test_obtener_permiso(permisos[0]['id'])
        
        # 6. Crear nuevo rol
        nuevo_rol = self.test_crear_rol()
        
        # 7. Asignar permisos al nuevo rol
        if nuevo_rol and permisos:
            permiso_ids = [p['id'] for p in permisos[:5]]  # Asignar primeros 5 permisos
            self.test_asignar_permisos_a_rol(nuevo_rol['id'], permiso_ids)
        
        # 8. Actualizar rol
        if nuevo_rol:
            self.test_actualizar_rol(nuevo_rol['id'])
        
        # 9. Eliminar rol
        if nuevo_rol:
            self.test_eliminar_rol(nuevo_rol['id'])
        
        print("\n" + "✅ " * 35)
        print("PRUEBAS COMPLETADAS")
        print("✅ " * 35 + "\n")


if __name__ == "__main__":
    tester = TestFase2()
    tester.run_all_tests()
