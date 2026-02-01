"""
Script de auditoría completa de permisos del sistema

Este script:
1. Identifica TODOS los permisos que se requieren en los routers
2. Verifica cuáles existen en la base de datos
3. Muestra las discrepancias
4. Lista todos los permisos del rol admin
"""

import sys
import os
import re

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import SessionLocal
from app.models.rol_permiso import Rol, Permiso

# ========================================
# PASO 1: PERMISOS REQUERIDOS EN CÓDIGO
# ========================================

PERMISOS_EN_ROUTERS = {
    # Configuración
    "editar_configuracion": "configuracion",
    
    # Configuración de vehículos
    "crear_configuracion_vehiculo": "configuracion_vehiculos",
    "editar_configuracion_vehiculo": "configuracion_vehiculos",
    "eliminar_configuracion_vehiculo": "configuracion_vehiculos",
    
    # Marcas de vehículos
    "crear_marca": "marcas_vehiculos",
    "editar_marca": "marcas_vehiculos",
    "eliminar_marca": "marcas_vehiculos",
    
    # Peajes
    "crear_peaje": "peajes",
    "editar_peaje": "peajes",
    "eliminar_peaje": "peajes",
    
    # Rendimiento
    "crear_rendimiento": "rendimiento",
    "editar_rendimiento": "rendimiento",
    "eliminar_rendimiento": "rendimiento",
    
    # Rutas
    "crear_ruta": "rutas",
    "editar_ruta": "rutas",
    "eliminar_ruta": "rutas",
    
    # Tramos
    "crear_tramo": "tramos",
    "editar_tramo": "tramos",
    
    # Tramo Detalle
    "crear_tramo_detalle": "tramo_detalle",
    "editar_tramo_detalle": "tramo_detalle",
    "eliminar_tramo_detalle": "tramo_detalle",
    
    # Vehículos
    "crear_vehiculo": "vehiculos",
    "editar_vehiculo": "vehiculos",
    "eliminar_vehiculo": "vehiculos",
}


def main():
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("🔍 AUDITORÍA COMPLETA DE PERMISOS DEL SISTEMA")
        print("="*80 + "\n")
        
        # ========================================
        # PASO 1: Listar permisos en código
        # ========================================
        print("📋 PASO 1: Permisos requeridos en los routers")
        print("-" * 80)
        print(f"Total de permisos encontrados en código: {len(PERMISOS_EN_ROUTERS)}")
        
        categorias = {}
        for permiso, categoria in PERMISOS_EN_ROUTERS.items():
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(permiso)
        
        for categoria in sorted(categorias.keys()):
            print(f"\n  📁 {categoria.upper()}:")
            for permiso in sorted(categorias[categoria]):
                print(f"     • {permiso}")
        
        # ========================================
        # PASO 2: Permisos en base de datos
        # ========================================
        print("\n\n" + "="*80)
        print("💾 PASO 2: Permisos en la base de datos")
        print("="*80)
        
        permisos_bd = db.query(Permiso).all()
        print(f"Total de permisos en BD: {len(permisos_bd)}")
        
        permisos_bd_por_categoria = {}
        permisos_bd_dict = {}
        
        for p in permisos_bd:
            categoria = p.categoria or "sin_categoria"
            if categoria not in permisos_bd_por_categoria:
                permisos_bd_por_categoria[categoria] = []
            permisos_bd_por_categoria[categoria].append(p.nombre)
            permisos_bd_dict[p.nombre] = p
        
        for categoria in sorted(permisos_bd_por_categoria.keys()):
            print(f"\n  📁 {categoria.upper()}:")
            for permiso in sorted(permisos_bd_por_categoria[categoria]):
                print(f"     • {permiso}")
        
        # ========================================
        # PASO 3: Comparación y discrepancias
        # ========================================
        print("\n\n" + "="*80)
        print("⚠️  PASO 3: ANÁLISIS DE DISCREPANCIAS")
        print("="*80)
        
        permisos_faltantes = []
        permisos_extra = []
        
        # Permisos que están en código pero NO en BD
        for permiso in PERMISOS_EN_ROUTERS.keys():
            if permiso not in permisos_bd_dict:
                permisos_faltantes.append(permiso)
        
        # Permisos que están en BD pero NO en código
        for permiso in permisos_bd_dict.keys():
            if permiso not in PERMISOS_EN_ROUTERS:
                permisos_extra.append(permiso)
        
        if permisos_faltantes:
            print(f"\n❌ PERMISOS FALTANTES EN BD ({len(permisos_faltantes)}):")
            print("   Estos se requieren en código pero NO existen en la base de datos:")
            for p in sorted(permisos_faltantes):
                categoria = PERMISOS_EN_ROUTERS.get(p, "desconocida")
                print(f"     • {p} (categoría: {categoria})")
        else:
            print("\n✅ Todos los permisos requeridos existen en BD")
        
        if permisos_extra:
            print(f"\n📌 PERMISOS ADICIONALES EN BD ({len(permisos_extra)}):")
            print("   Estos están en BD pero NO se usan actualmente en los routers:")
            for p in sorted(permisos_extra):
                categoria = permisos_bd_dict[p].categoria
                print(f"     • {p} (categoría: {categoria})")
        
        # ========================================
        # PASO 4: Permisos del rol Admin
        # ========================================
        print("\n\n" + "="*80)
        print("👤 PASO 4: PERMISOS DEL ROL ADMIN")
        print("="*80)
        
        admin_rol = db.query(Rol).filter(Rol.nombre == "admin").first()
        
        if admin_rol:
            permisos_admin = admin_rol.permisos
            print(f"\nRol: {admin_rol.nombre}")
            print(f"Total permisos asignados: {len(permisos_admin)}")
            print(f"Total permisos en sistema: {len(permisos_bd)}")
            
            # Agrupar por categoría
            permisos_admin_por_categoria = {}
            for p in permisos_admin:
                cat = p.categoria or "sin_categoria"
                if cat not in permisos_admin_por_categoria:
                    permisos_admin_por_categoria[cat] = []
                permisos_admin_por_categoria[cat].append(p.nombre)
            
            print("\nPermisos por categoría:")
            for cat in sorted(permisos_admin_por_categoria.keys()):
                permisos = sorted(permisos_admin_por_categoria[cat])
                print(f"\n  📁 {cat.upper()} ({len(permisos)}):")
                for p in permisos:
                    print(f"     • {p}")
            
            # Ver qué permisos le faltan al admin
            permisos_admin_nombres = {p.nombre for p in permisos_admin}
            permisos_faltantes_admin = []
            
            for p in permisos_bd:
                if p.nombre not in permisos_admin_nombres:
                    permisos_faltantes_admin.append(p)
            
            if permisos_faltantes_admin:
                print(f"\n⚠️  PERMISOS QUE FALTAN AL ADMIN ({len(permisos_faltantes_admin)}):")
                for p in permisos_faltantes_admin:
                    print(f"     • {p.nombre} ({p.categoria})")
            else:
                print("\n✅ El admin tiene TODOS los permisos del sistema")
        else:
            print("\n❌ ERROR: No se encontró el rol 'admin'")
        
        # ========================================
        # RESUMEN FINAL
        # ========================================
        print("\n\n" + "="*80)
        print("📊 RESUMEN EJECUTIVO")
        print("="*80)
        print(f"\n✓ Permisos requeridos en código:    {len(PERMISOS_EN_ROUTERS)}")
        print(f"✓ Permisos existentes en BD:        {len(permisos_bd)}")
        print(f"❌ Permisos faltantes en BD:         {len(permisos_faltantes)}")
        print(f"📌 Permisos extra en BD:             {len(permisos_extra)}")
        
        if admin_rol:
            print(f"\n👤 Permisos del Admin:               {len(permisos_admin)}/{len(permisos_bd)}")
            if permisos_faltantes_admin:
                print(f"⚠️  Permisos faltantes al Admin:     {len(permisos_faltantes_admin)}")
        
        print("\n" + "="*80)
        
        if permisos_faltantes or (admin_rol and permisos_faltantes_admin):
            print("\n⚠️  ACCIÓN REQUERIDA:")
            print("   Se encontraron discrepancias. Ejecute el script de migración.")
            return 1
        else:
            print("\n✅ TODO CORRECTO: Sistema de permisos en orden")
            return 0
        
    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
