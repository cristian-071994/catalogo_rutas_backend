"""
Script para verificar que TODOS los endpoints tengan autenticación
"""
import sys
sys.path.append('.')
import os
from pathlib import Path

def verificar_seguridad_router(file_path):
    """Verifica que todas las funciones de endpoint tengan current_user"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las funciones de endpoint
    import re
    
    # Patrón para detectar endpoints
    pattern = r'@router\.(get|post|put|delete|patch)\([^)]*\)\s*\n\s*def\s+(\w+)\s*\((.*?)\):'
    
    endpoints = re.findall(pattern, content, re.DOTALL)
    
    resultados = []
    for method, func_name, params in endpoints:
        # Verificar si tiene current_user
        tiene_auth = 'current_user' in params
        resultados.append({
            'method': method.upper(),
            'function': func_name,
            'protected': tiene_auth,
            'params': params.replace('\n', ' ').strip()
        })
    
    return resultados

def main():
    routers_dir = Path('app/routers')
    
    # Archivos a verificar (excluir __init__.py y auth.py)
    archivos_router = [
        'rutas.py',
        'peajes.py',
        'tramos.py',
        'vehiculos.py',
        'marcas_vehiculos.py',
        'configuracion.py',
        'configuracion_vehiculos.py',
        'rendimiento_configuracion.py',
        'tramo_detalle.py',
        'clientes.py',
        'usuarios.py',
        'roles.py',
        'permisos.py'
    ]
    
    print("=" * 80)
    print("VERIFICACIÓN DE SEGURIDAD - ENDPOINTS PROTEGIDOS")
    print("=" * 80)
    
    total_endpoints = 0
    total_protegidos = 0
    total_sin_proteger = 0
    
    for archivo in archivos_router:
        file_path = routers_dir / archivo
        if not file_path.exists():
            continue
        
        print(f"\n📁 {archivo}")
        print("-" * 80)
        
        resultados = verificar_seguridad_router(file_path)
        
        for r in resultados:
            total_endpoints += 1
            
            if r['protected']:
                total_protegidos += 1
                print(f"  🔒 {r['method']:<6} {r['function']:<40} ✅ PROTEGIDO")
            else:
                total_sin_proteger += 1
                print(f"  🔓 {r['method']:<6} {r['function']:<40} ⚠️  SIN PROTECCIÓN")
    
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total endpoints:        {total_endpoints}")
    print(f"Protegidos:             {total_protegidos} ✅")
    print(f"Sin proteger:           {total_sin_proteger} ⚠️")
    
    if total_sin_proteger == 0:
        print("\n🎉 ¡EXCELENTE! TODOS los endpoints están protegidos")
        return 0
    else:
        print(f"\n⚠️  ATENCIÓN: Hay {total_sin_proteger} endpoints sin protección")
        return 1

if __name__ == "__main__":
    exit(main())
