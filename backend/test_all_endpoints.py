#!/usr/bin/env python3
"""
Script de Testing Automatizado - Catalogo Rutas Backend
Prueba todos los endpoints en orden lógico
"""

import requests
import json
from decimal import Decimal

BASE_URL = "http://127.0.0.1:8000"

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Diccionario para guardar IDs
ids = {}

def log_test(name, method, endpoint, status_code):
    """Registrar resultado del test"""
    if 200 <= status_code < 300:
        print(f"{GREEN}✓ {BOLD}{method}{RESET}{GREEN} {endpoint} ({status_code}){RESET}")
    else:
        print(f"{RED}✗ {BOLD}{method}{RESET}{RED} {endpoint} ({status_code}){RESET}")

def test_configuracion():
    """1. Pruebas de Configuración General"""
    print(f"\n{BLUE}{BOLD}=== 1. CONFIGURACIÓN GENERAL ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/configuracion/",
        json={"clave": "precio_galon", "valor": "12000", "descripcion": "Precio por galón"}
    )
    if response.status_code == 201:
        ids['config'] = response.json()['id']
        log_test("POST Configuración", "POST", "/configuracion/", response.status_code)
    else:
        print(f"{YELLOW}Info: Configuración ya existe{RESET}")
        # Obtener el ID existente
        get_resp = requests.get(f"{BASE_URL}/configuracion/")
        if get_resp.status_code == 200:
            configs = get_resp.json()
            if configs:
                ids['config'] = configs[0]['id']
    
    # GET all
    response = requests.get(f"{BASE_URL}/configuracion/")
    log_test("GET Configuraciones", "GET", "/configuracion/", response.status_code)
    
    # GET by id
    if 'config' in ids:
        response = requests.get(f"{BASE_URL}/configuracion/{ids['config']}")
        log_test("GET Configuración by ID", "GET", f"/configuracion/{ids['config']}", response.status_code)

def test_clientes():
    """2. Pruebas de Clientes"""
    print(f"\n{BLUE}{BOLD}=== 2. CLIENTES ==={RESET}")
    
    # POST
    response = requests.post(f"{BASE_URL}/clientes/", json={"nombre": "Cliente Test A"})
    if response.status_code == 201:
        ids['cliente1'] = response.json()['id']
        log_test("POST Cliente 1", "POST", "/clientes/", response.status_code)
    
    # POST Cliente 2
    response = requests.post(f"{BASE_URL}/clientes/", json={"nombre": "Cliente Test B"})
    if response.status_code == 201:
        ids['cliente2'] = response.json()['id']
        log_test("POST Cliente 2", "POST", "/clientes/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/clientes/")
    log_test("GET Clientes", "GET", "/clientes/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/clientes/{ids['cliente1']}")
    log_test("GET Cliente by ID", "GET", f"/clientes/{ids['cliente1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/clientes/{ids['cliente1']}",
        json={"nombre": "Cliente Test A Actualizado"}
    )
    log_test("PUT Cliente", "PUT", f"/clientes/{ids['cliente1']}", response.status_code)

def test_tramos():
    """3. Pruebas de Tramos"""
    print(f"\n{BLUE}{BOLD}=== 3. TRAMOS ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/tramos/",
        json={"origen": "Mediacanoa", "destino": "Buenaventura"}
    )
    if response.status_code == 201:
        ids['tramo1'] = response.json()['id']
        log_test("POST Tramo 1", "POST", "/tramos/", response.status_code)
    
    # POST Tramo 2
    response = requests.post(
        f"{BASE_URL}/tramos/",
        json={"origen": "Buenaventura", "destino": "Cali"}
    )
    if response.status_code == 201:
        ids['tramo2'] = response.json()['id']
        log_test("POST Tramo 2", "POST", "/tramos/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/tramos/")
    log_test("GET Tramos", "GET", "/tramos/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/tramos/{ids['tramo1']}")
    log_test("GET Tramo by ID", "GET", f"/tramos/{ids['tramo1']}", response.status_code)

def test_tramo_detalle():
    """4. Pruebas de Tramo Detalle"""
    print(f"\n{BLUE}{BOLD}=== 4. TRAMO DETALLE ==={RESET}")
    
    # POST - VACIO PLANO
    response = requests.post(
        f"{BASE_URL}/tramo-detalle/",
        json={
            "tramo_id": ids['tramo1'],
            "tipo_carga": "VACIO",
            "tipo_terreno": "PLANO",
            "kilometros": 150.5
        }
    )
    if response.status_code == 201:
        ids['detalle1'] = response.json()['id']
        log_test("POST Detalle VACIO+PLANO", "POST", "/tramo-detalle/", response.status_code)
    
    # POST - CARGADO PLANO
    response = requests.post(
        f"{BASE_URL}/tramo-detalle/",
        json={
            "tramo_id": ids['tramo1'],
            "tipo_carga": "CARGADO",
            "tipo_terreno": "PLANO",
            "kilometros": 150.5
        }
    )
    if response.status_code == 201:
        ids['detalle2'] = response.json()['id']
        log_test("POST Detalle CARGADO+PLANO", "POST", "/tramo-detalle/", response.status_code)
    
    # GET by tramo
    response = requests.get(f"{BASE_URL}/tramo-detalle/tramo/{ids['tramo1']}")
    log_test("GET Detalles by Tramo", "GET", f"/tramo-detalle/tramo/{ids['tramo1']}", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/tramo-detalle/{ids['detalle1']}")
    log_test("GET Detalle by ID", "GET", f"/tramo-detalle/{ids['detalle1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/tramo-detalle/{ids['detalle1']}",
        json={"kilometros": 160.0}
    )
    log_test("PUT Detalle", "PUT", f"/tramo-detalle/{ids['detalle1']}", response.status_code)

def test_peajes():
    """5. Pruebas de Peajes"""
    print(f"\n{BLUE}{BOLD}=== 5. PEAJES ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/peajes/",
        json={"nombre": "Peaje Buenaventura", "costo": 25000.00}
    )
    if response.status_code == 201:
        ids['peaje1'] = response.json()['id']
        log_test("POST Peaje 1", "POST", "/peajes/", response.status_code)
    
    # POST Peaje 2
    response = requests.post(
        f"{BASE_URL}/peajes/",
        json={"nombre": "Peaje Cali", "costo": 15000.00}
    )
    if response.status_code == 201:
        ids['peaje2'] = response.json()['id']
        log_test("POST Peaje 2", "POST", "/peajes/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/peajes/")
    log_test("GET Peajes", "GET", "/peajes/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/peajes/{ids['peaje1']}")
    log_test("GET Peaje by ID", "GET", f"/peajes/{ids['peaje1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/peajes/{ids['peaje1']}",
        json={"costo": 27000.00}
    )
    log_test("PUT Peaje", "PUT", f"/peajes/{ids['peaje1']}", response.status_code)

def test_marcas_vehiculos():
    """6. Pruebas de Marcas de Vehículos"""
    print(f"\n{BLUE}{BOLD}=== 6. MARCAS DE VEHÍCULOS ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/marcas-vehiculos/",
        json={"nombre": "Chevrolet"}
    )
    if response.status_code == 201:
        ids['marca1'] = response.json()['id']
        log_test("POST Marca", "POST", "/marcas-vehiculos/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/marcas-vehiculos/")
    log_test("GET Marcas", "GET", "/marcas-vehiculos/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/marcas-vehiculos/{ids['marca1']}")
    log_test("GET Marca by ID", "GET", f"/marcas-vehiculos/{ids['marca1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/marcas-vehiculos/{ids['marca1']}",
        json={"nombre": "Chevrolet Actualizada"}
    )
    log_test("PUT Marca", "PUT", f"/marcas-vehiculos/{ids['marca1']}", response.status_code)

def test_configuracion_vehiculos():
    """7. Pruebas de Configuración de Vehículos"""
    print(f"\n{BLUE}{BOLD}=== 7. CONFIGURACIÓN DE VEHÍCULOS ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/configuracion-vehiculos/",
        json={"marca_id": ids['marca1'], "modelo": 2020}
    )
    if response.status_code == 201:
        ids['config_vehiculo1'] = response.json()['id']
        log_test("POST Config Vehículo", "POST", "/configuracion-vehiculos/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/configuracion-vehiculos/")
    log_test("GET Configuraciones", "GET", "/configuracion-vehiculos/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/configuracion-vehiculos/{ids['config_vehiculo1']}")
    log_test("GET Config by ID", "GET", f"/configuracion-vehiculos/{ids['config_vehiculo1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/configuracion-vehiculos/{ids['config_vehiculo1']}",
        json={"modelo": 2021}
    )
    log_test("PUT Config", "PUT", f"/configuracion-vehiculos/{ids['config_vehiculo1']}", response.status_code)

def test_rendimiento_configuracion():
    """8. Pruebas de Rendimiento de Configuración"""
    print(f"\n{BLUE}{BOLD}=== 8. RENDIMIENTO DE CONFIGURACIÓN ==={RESET}")
    
    # POST - VACIO PLANO
    response = requests.post(
        f"{BASE_URL}/rendimiento-configuracion/",
        json={
            "configuracion_id": ids['config_vehiculo1'],
            "tipo_carga": "VACIO",
            "tipo_terreno": "PLANO",
            "rendimiento_km_galon": 12.5
        }
    )
    if response.status_code == 201:
        ids['rendimiento1'] = response.json()['id']
        log_test("POST Rendimiento VACIO+PLANO", "POST", "/rendimiento-configuracion/", response.status_code)
    
    # POST - CARGADO PLANO
    response = requests.post(
        f"{BASE_URL}/rendimiento-configuracion/",
        json={
            "configuracion_id": ids['config_vehiculo1'],
            "tipo_carga": "CARGADO",
            "tipo_terreno": "PLANO",
            "rendimiento_km_galon": 8.5
        }
    )
    if response.status_code == 201:
        ids['rendimiento2'] = response.json()['id']
        log_test("POST Rendimiento CARGADO+PLANO", "POST", "/rendimiento-configuracion/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/rendimiento-configuracion/")
    log_test("GET Rendimientos", "GET", "/rendimiento-configuracion/", response.status_code)
    
    # GET by config
    response = requests.get(f"{BASE_URL}/rendimiento-configuracion/configuracion/{ids['config_vehiculo1']}")
    log_test("GET Rendimientos by Config", "GET", f"/rendimiento-configuracion/configuracion/{ids['config_vehiculo1']}", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/rendimiento-configuracion/{ids['rendimiento1']}")
    log_test("GET Rendimiento by ID", "GET", f"/rendimiento-configuracion/{ids['rendimiento1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/rendimiento-configuracion/{ids['rendimiento1']}",
        json={"rendimiento_km_galon": 13.0}
    )
    log_test("PUT Rendimiento", "PUT", f"/rendimiento-configuracion/{ids['rendimiento1']}", response.status_code)

def test_vehiculos():
    """9. Pruebas de Vehículos"""
    print(f"\n{BLUE}{BOLD}=== 9. VEHÍCULOS ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/vehiculos/",
        json={"placa": "ABC123", "configuracion_id": ids['config_vehiculo1']}
    )
    if response.status_code == 201:
        ids['vehiculo1'] = response.json()['id']
        log_test("POST Vehículo", "POST", "/vehiculos/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/vehiculos/")
    log_test("GET Vehículos", "GET", "/vehiculos/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/vehiculos/{ids['vehiculo1']}")
    log_test("GET Vehículo by ID", "GET", f"/vehiculos/{ids['vehiculo1']}", response.status_code)
    
    # PUT
    response = requests.put(
        f"{BASE_URL}/vehiculos/{ids['vehiculo1']}",
        json={"placa": "ABC124"}
    )
    log_test("PUT Vehículo", "PUT", f"/vehiculos/{ids['vehiculo1']}", response.status_code)

def test_rutas():
    """10. Pruebas de Rutas (Lo más importante)"""
    print(f"\n{BLUE}{BOLD}=== 10. RUTAS ==={RESET}")
    
    # POST
    response = requests.post(
        f"{BASE_URL}/rutas/",
        json={
            "cliente_id": ids['cliente1'],
            "nombre": "Ruta Test Mediacanoa-Buenaventura",
            "descripcion": "Ruta de prueba"
        }
    )
    if response.status_code == 201:
        ids['ruta1'] = response.json()['id']
        log_test("POST Ruta", "POST", "/rutas/", response.status_code)
    
    # GET all
    response = requests.get(f"{BASE_URL}/rutas/")
    log_test("GET Rutas", "GET", "/rutas/", response.status_code)
    
    # GET by id
    response = requests.get(f"{BASE_URL}/rutas/{ids['ruta1']}")
    log_test("GET Ruta by ID", "GET", f"/rutas/{ids['ruta1']}", response.status_code)
    
    # GET by cliente
    response = requests.get(f"{BASE_URL}/rutas/cliente/{ids['cliente1']}")
    log_test("GET Rutas by Cliente", "GET", f"/rutas/cliente/{ids['cliente1']}", response.status_code)
    
    # POST tramo a ruta
    response = requests.post(
        f"{BASE_URL}/rutas/{ids['ruta1']}/tramos/{ids['tramo1']}",
        json={"orden": 1}
    )
    if response.status_code == 201:
        ids['tramo_ruta1'] = response.json()['id']
        log_test("POST Agregar Tramo a Ruta", "POST", f"/rutas/{ids['ruta1']}/tramos/{ids['tramo1']}", response.status_code)
    
    # POST peaje IDA
    response = requests.post(
        f"{BASE_URL}/rutas/{ids['ruta1']}/peajes/{ids['peaje1']}",
        json={"direccion": "IDA", "orden": 1}
    )
    if response.status_code == 201:
        ids['ruta_peaje_ida'] = response.json()['id']
        log_test("POST Agregar Peaje IDA", "POST", f"/rutas/{ids['ruta1']}/peajes/{ids['peaje1']}", response.status_code)
    
    # POST peaje REGRESO (mismo peaje)
    response = requests.post(
        f"{BASE_URL}/rutas/{ids['ruta1']}/peajes/{ids['peaje1']}",
        json={"direccion": "REGRESO", "orden": 2}
    )
    if response.status_code == 201:
        ids['ruta_peaje_regreso'] = response.json()['id']
        log_test("POST Agregar Peaje REGRESO", "POST", f"/rutas/{ids['ruta1']}/peajes/{ids['peaje1']} (REGRESO)", response.status_code)
    
    # GET resumen (IMPORTANTE)
    response = requests.get(f"{BASE_URL}/rutas/{ids['ruta1']}/resumen?configuracion_id={ids['config_vehiculo1']}")
    if response.status_code == 200:
        log_test("GET Resumen Ruta", "GET", f"/rutas/{ids['ruta1']}/resumen", response.status_code)
        resumen = response.json()
        print(f"{YELLOW}  Desglose de costo:{RESET}")
        print(f"    - Km totales: {resumen['km_totales']} km")
        print(f"    - Galones: {resumen['galones_combustible']}")
        print(f"    - Costo combustible: ${resumen['costo_combustible']}")
        print(f"    - Costo peajes: ${resumen['costo_peajes_total']}")
        print(f"    - COSTO TOTAL: ${resumen['costo_total']}")
    else:
        log_test("GET Resumen Ruta", "GET", f"/rutas/{ids['ruta1']}/resumen", response.status_code)
    
    # PUT ruta
    response = requests.put(
        f"{BASE_URL}/rutas/{ids['ruta1']}",
        json={"nombre": "Ruta Test Actualizada"}
    )
    log_test("PUT Ruta", "PUT", f"/rutas/{ids['ruta1']}", response.status_code)

def test_soft_deletes():
    """11. Pruebas de Soft Delete"""
    print(f"\n{BLUE}{BOLD}=== 11. SOFT DELETES ==={RESET}")
    
    # DELETE detalle
    response = requests.delete(f"{BASE_URL}/tramo-detalle/{ids['detalle2']}")
    log_test("DELETE TramoDetalle", "DELETE", f"/tramo-detalle/{ids['detalle2']}", response.status_code)
    
    # Verificar que quedó inactivo
    response = requests.get(f"{BASE_URL}/tramo-detalle/{ids['detalle2']}")
    if response.status_code == 200:
        detalle = response.json()
        if detalle['estado'] == 'inactivo':
            print(f"{GREEN}  ✓ TramoDetalle marcado como inactivo{RESET}")
    
    # DELETE peaje de ruta
    response = requests.delete(f"{BASE_URL}/rutas/{ids['ruta1']}/peajes/{ids['ruta_peaje_regreso']}")
    log_test("DELETE Peaje de Ruta", "DELETE", f"/rutas/{ids['ruta1']}/peajes/{ids['ruta_peaje_regreso']}", response.status_code)
    
    # DELETE tramo de ruta
    response = requests.delete(f"{BASE_URL}/rutas/{ids['ruta1']}/tramos/{ids['tramo_ruta1']}")
    log_test("DELETE Tramo de Ruta", "DELETE", f"/rutas/{ids['ruta1']}/tramos/{ids['tramo_ruta1']}", response.status_code)
    
    # DELETE ruta
    response = requests.delete(f"{BASE_URL}/rutas/{ids['ruta1']}")
    log_test("DELETE Ruta", "DELETE", f"/rutas/{ids['ruta1']}", response.status_code)
    
    # Verificar que quedó inactivo
    response = requests.get(f"{BASE_URL}/rutas/{ids['ruta1']}")
    if response.status_code == 200:
        ruta = response.json()
        if ruta['estado'] == 'inactivo':
            print(f"{GREEN}  ✓ Ruta marcada como inactivo{RESET}")
    
    # DELETE peaje
    response = requests.delete(f"{BASE_URL}/peajes/{ids['peaje2']}")
    log_test("DELETE Peaje", "DELETE", f"/peajes/{ids['peaje2']}", response.status_code)
    
    # DELETE cliente
    response = requests.delete(f"{BASE_URL}/clientes/{ids['cliente2']}")
    log_test("DELETE Cliente", "DELETE", f"/clientes/{ids['cliente2']}", response.status_code)

def main():
    """Ejecutar todos los tests"""
    print(f"\n{BOLD}{BLUE}╔════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{BLUE}║   TESTING AUTOMATIZADO - CATALOGO RUTAS BACKEND       ║{RESET}")
    print(f"{BOLD}{BLUE}╚════════════════════════════════════════════════════════╝{RESET}\n")
    
    try:
        test_configuracion()
        test_clientes()
        test_tramos()
        test_tramo_detalle()
        test_peajes()
        test_marcas_vehiculos()
        test_configuracion_vehiculos()
        test_rendimiento_configuracion()
        test_vehiculos()
        test_rutas()
        test_soft_deletes()
        
        print(f"\n{BOLD}{GREEN}╔════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{GREEN}║   TESTING COMPLETADO CON ÉXITO                       ║{RESET}")
        print(f"{BOLD}{GREEN}╚════════════════════════════════════════════════════════╝{RESET}\n")
        
    except Exception as e:
        print(f"\n{RED}{BOLD}ERROR:{RESET}{RED} {str(e)}{RESET}\n")

if __name__ == "__main__":
    main()
