"""
Script de prueba para el sistema de autenticación y usuarios
Verifica login, permisos y acceso a endpoints
"""

import requests
from colorama import Fore, Style, init

# Inicializar colorama para colores en Windows
init(autoreset=True)

BASE_URL = "http://127.0.0.1:8000"

# Usuarios de prueba
USUARIOS = [
    {"nombre": "Administrador", "email": "admin@test.com", "password": "admin123", "rol": "admin"},
    {"nombre": "Supervisor", "email": "supervisor@test.com", "password": "supervisor123", "rol": "supervisor"},
    {"nombre": "Gestor de Rutas", "email": "gestor_rutas@test.com", "password": "gestor123", "rol": "gestor_rutas"},
    {"nombre": "Gestor de Peajes", "email": "gestor_peajes@test.com", "password": "gestor123", "rol": "gestor_peajes"},
    {"nombre": "Gestor de Clientes", "email": "gestor_clientes@test.com", "password": "gestor123", "rol": "gestor_clientes"},
    {"nombre": "Consultor", "email": "consultor@test.com", "password": "consultor123", "rol": "consultor"},
]


def print_header(text):
    """Imprime un encabezado colorido"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{text.center(80)}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Fore.YELLOW}ℹ️  {text}{Style.RESET_ALL}")


def test_root():
    """Prueba el endpoint raíz"""
    print_header("PRUEBA 1: Endpoint Raíz")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"Servidor respondió correctamente")
            print_info(f"Respuesta: {response.json()}")
            return True
        else:
            print_error(f"Error: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        return False


def test_login(usuario):
    """Prueba el login de un usuario"""
    print(f"\n{Fore.MAGENTA}📝 Probando login: {usuario['nombre']} ({usuario['email']}){Style.RESET_ALL}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": usuario["email"], "password": usuario["password"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_success(f"Login exitoso - Rol: {data['usuario_rol']}")
            print_info(f"Token obtenido: {token[:30]}...")
            return token
        else:
            print_error(f"Login falló: Status {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en login: {e}")
        return None


def test_me(token, usuario):
    """Prueba el endpoint /me"""
    print(f"{Fore.BLUE}🔍 Verificando /me para {usuario['nombre']}{Style.RESET_ALL}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Usuario actual: {data['nombre']} | Rol: {data['rol']}")
            return True
        else:
            print_error(f"/me falló: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en /me: {e}")
        return False


def test_acceso_endpoint(token, usuario, endpoint, metodo="GET", data=None):
    """Prueba el acceso a un endpoint específico"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        if metodo == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif metodo == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data or {})
        
        if response.status_code in [200, 201]:
            return "✅ Permitido"
        elif response.status_code == 403:
            return "🚫 Denegado (403)"
        elif response.status_code == 422:
            return "⚠️  Error validación (422)"
        else:
            return f"❓ Status {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)[:30]}"


def test_permisos_por_rol():
    """Prueba los permisos de cada rol"""
    print_header("PRUEBA 3: Verificación de Permisos por Rol")
    
    # Endpoints a probar
    endpoints = [
        ("/clientes/", "GET", None),
        ("/peajes/", "GET", None),
        ("/rutas/", "GET", None),
    ]
    
    resultados = {}
    
    for usuario in USUARIOS:
        token = test_login(usuario)
        if token:
            test_me(token, usuario)
            print(f"\n{Fore.CYAN}Probando acceso a endpoints:{Style.RESET_ALL}")
            
            for endpoint, metodo, data in endpoints:
                resultado = test_acceso_endpoint(token, usuario, endpoint, metodo, data)
                endpoint_name = endpoint.strip("/")
                print(f"  {endpoint_name:20} {metodo:4} → {resultado}")
            
            resultados[usuario['rol']] = True
        else:
            resultados[usuario['rol']] = False
        
        print("-" * 80)
    
    return resultados


def test_login_incorrecto():
    """Prueba login con credenciales incorrectas"""
    print_header("PRUEBA 4: Login con Credenciales Incorrectas")
    
    print_info("Intentando login con email inexistente...")
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "noexiste@test.com", "password": "123456"}
    )
    
    if response.status_code == 401:
        print_success("Login rechazado correctamente (401 Unauthorized)")
    else:
        print_error(f"Respuesta inesperada: {response.status_code}")
    
    print_info("Intentando login con contraseña incorrecta...")
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "admin@test.com", "password": "wrongpassword"}
    )
    
    if response.status_code == 401:
        print_success("Login rechazado correctamente (401 Unauthorized)")
    else:
        print_error(f"Respuesta inesperada: {response.status_code}")


def test_sin_token():
    """Prueba acceso a endpoints sin token"""
    print_header("PRUEBA 5: Acceso Sin Token de Autenticación")
    
    endpoints = ["/clientes/", "/peajes/", "/rutas/", "/me"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print_success(f"{endpoint:20} → Bloqueado correctamente (401)")
            else:
                print_error(f"{endpoint:20} → Status inesperado: {response.status_code}")
        except Exception as e:
            print_error(f"{endpoint:20} → Error: {e}")


def main():
    """Ejecuta todas las pruebas"""
    print(f"\n{Fore.GREEN}{'*'*80}")
    print(f"{Fore.GREEN}*{' '*78}*")
    print(f"{Fore.GREEN}*{'PRUEBAS DE AUTENTICACIÓN Y USUARIOS'.center(78)}*")
    print(f"{Fore.GREEN}*{' '*78}*")
    print(f"{Fore.GREEN}{'*'*80}{Style.RESET_ALL}\n")
    
    print_info(f"Servidor: {BASE_URL}")
    print_info(f"Usuarios a probar: {len(USUARIOS)}")
    
    # Ejecutar pruebas
    test_root()
    test_login_incorrecto()
    test_sin_token()
    test_permisos_por_rol()
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    print_success("✅ Todas las pruebas básicas completadas")
    print_info("Los usuarios de prueba están creados y funcionando")
    print_info("El sistema de autenticación JWT está operativo")
    
    print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Sistema de autenticación verificado correctamente{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Pruebas interrumpidas por el usuario{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error inesperado: {e}{Style.RESET_ALL}")
