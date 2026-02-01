"""
Script de migración completa de permisos

Este script:
1. Crea todos los permisos faltantes en la base de datos
2. Asigna TODOS los permisos al rol admin
3. Mantiene los permisos existentes intactos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import SessionLocal
from app.models.rol_permiso import Rol, Permiso
from sqlalchemy import func

# Lista completa de permisos que deben existir
PERMISOS_COMPLETOS = [
    # ========================================
    # USUARIOS
    # ========================================
    ("crear_usuario", "Crear nuevos usuarios", "usuarios"),
    ("editar_usuario", "Editar información de usuarios", "usuarios"),
    ("eliminar_usuario", "Eliminar usuarios", "usuarios"),
    ("ver_usuarios", "Ver lista de usuarios", "usuarios"),
    ("cambiar_rol_usuario", "Cambiar rol de un usuario", "usuarios"),
    
    # ========================================
    # ROLES Y PERMISOS
    # ========================================
    ("gestionar_roles", "Crear, editar y eliminar roles", "roles"),
    ("gestionar_permisos", "Crear, editar y eliminar permisos", "permisos"),
    
    # ========================================
    # CLIENTES
    # ========================================
    ("crear_cliente", "Crear nuevos clientes", "clientes"),
    ("editar_cliente", "Editar clientes existentes", "clientes"),
    ("eliminar_cliente", "Eliminar clientes", "clientes"),
    ("ver_clientes", "Ver lista de clientes", "clientes"),
    
    # ========================================
    # RUTAS
    # ========================================
    ("crear_ruta", "Crear nuevas rutas", "rutas"),
    ("editar_ruta", "Editar rutas existentes", "rutas"),
    ("eliminar_ruta", "Eliminar rutas", "rutas"),
    ("ver_rutas", "Ver lista de rutas", "rutas"),
    
    # ========================================
    # TRAMOS
    # ========================================
    ("crear_tramo", "Crear nuevos tramos", "tramos"),
    ("editar_tramo", "Editar tramos existentes", "tramos"),
    ("eliminar_tramo", "Eliminar tramos", "tramos"),
    ("ver_tramos", "Ver lista de tramos", "tramos"),
    
    # ========================================
    # TRAMO DETALLE
    # ========================================
    ("crear_tramo_detalle", "Crear detalles de tramos", "tramo_detalle"),
    ("editar_tramo_detalle", "Editar detalles de tramos", "tramo_detalle"),
    ("eliminar_tramo_detalle", "Eliminar detalles de tramos", "tramo_detalle"),
    ("ver_tramo_detalle", "Ver detalles de tramos", "tramo_detalle"),
    
    # ========================================
    # PEAJES
    # ========================================
    ("crear_peaje", "Crear nuevos peajes", "peajes"),
    ("editar_peaje", "Editar peajes existentes", "peajes"),
    ("eliminar_peaje", "Eliminar peajes", "peajes"),
    ("ver_peajes", "Ver lista de peajes", "peajes"),
    
    # ========================================
    # VEHÍCULOS
    # ========================================
    ("crear_vehiculo", "Crear nuevos vehículos", "vehiculos"),
    ("editar_vehiculo", "Editar vehículos existentes", "vehiculos"),
    ("eliminar_vehiculo", "Eliminar vehículos", "vehiculos"),
    ("ver_vehiculos", "Ver lista de vehículos", "vehiculos"),
    
    # ========================================
    # MARCAS DE VEHÍCULOS
    # ========================================
    ("crear_marca", "Crear nuevas marcas de vehículos", "marcas_vehiculos"),
    ("editar_marca", "Editar marcas de vehículos", "marcas_vehiculos"),
    ("eliminar_marca", "Eliminar marcas de vehículos", "marcas_vehiculos"),
    ("ver_marcas", "Ver lista de marcas de vehículos", "marcas_vehiculos"),
    
    # ========================================
    # CONFIGURACIÓN DE VEHÍCULOS
    # ========================================
    ("crear_configuracion_vehiculo", "Crear configuraciones de vehículos", "configuracion_vehiculos"),
    ("editar_configuracion_vehiculo", "Editar configuraciones de vehículos", "configuracion_vehiculos"),
    ("eliminar_configuracion_vehiculo", "Eliminar configuraciones de vehículos", "configuracion_vehiculos"),
    ("ver_configuracion_vehiculos", "Ver configuraciones de vehículos", "configuracion_vehiculos"),
    
    # ========================================
    # RENDIMIENTO
    # ========================================
    ("crear_rendimiento", "Crear configuraciones de rendimiento", "rendimiento"),
    ("editar_rendimiento", "Editar configuraciones de rendimiento", "rendimiento"),
    ("eliminar_rendimiento", "Eliminar configuraciones de rendimiento", "rendimiento"),
    ("ver_rendimiento", "Ver configuraciones de rendimiento", "rendimiento"),
    
    # ========================================
    # CONFIGURACIÓN Y REPORTES
    # ========================================
    ("editar_configuracion", "Editar configuración general del sistema", "configuracion"),
    ("ver_reportes", "Ver reportes y análisis", "reportes"),
]


def main():
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("🔧 MIGRACIÓN COMPLETA DE PERMISOS DEL SISTEMA")
        print("="*80 + "\n")
        
        # ========================================
        # PASO 1: Crear permisos faltantes
        # ========================================
        print("PASO 1: Creando permisos faltantes...")
        print("-" * 80)
        
        permisos_creados = 0
        permisos_existentes = 0
        nuevos_permisos = []
        
        for nombre, descripcion, categoria in PERMISOS_COMPLETOS:
            existente = db.query(Permiso).filter(
                func.lower(Permiso.nombre) == func.lower(nombre)
            ).first()
            
            if existente:
                permisos_existentes += 1
            else:
                permiso = Permiso(
                    nombre=nombre,
                    descripcion=descripcion,
                    categoria=categoria,
                    es_sistema=1,
                    activo=1
                )
                db.add(permiso)
                db.flush()
                nuevos_permisos.append(permiso)
                permisos_creados += 1
                print(f"  ✅ Permiso '{nombre}' creado (ID: {permiso.id}, categoría: {categoria})")
        
        db.commit()
        
        print(f"\n📊 Resumen:")
        print(f"   • Permisos ya existentes: {permisos_existentes}")
        print(f"   • Permisos creados: {permisos_creados}")
        print(f"   • Total permisos: {permisos_existentes + permisos_creados}")
        
        # ========================================
        # PASO 2: Asignar todos los permisos al admin
        # ========================================
        print("\n" + "="*80)
        print("PASO 2: Asignando permisos al rol Admin...")
        print("-" * 80)
        
        admin_rol = db.query(Rol).filter(Rol.nombre == "admin").first()
        
        if not admin_rol:
            print("❌ ERROR: No se encontró el rol 'admin'")
            return 1
        
        permisos_antes = len(admin_rol.permisos)
        
        # Obtener todos los permisos del sistema
        todos_permisos = db.query(Permiso).filter(Permiso.activo == 1).all()
        
        # Asignar todos los permisos al admin
        admin_rol.permisos = todos_permisos
        db.commit()
        
        permisos_despues = len(admin_rol.permisos)
        permisos_agregados = permisos_despues - permisos_antes
        
        print(f"  ✅ Admin actualizado:")
        print(f"     • Permisos antes: {permisos_antes}")
        print(f"     • Permisos después: {permisos_despues}")
        print(f"     • Permisos agregados: {permisos_agregados}")
        
        # ========================================
        # PASO 3: Mostrar permisos del admin por categoría
        # ========================================
        print("\n" + "="*80)
        print("PASO 3: Permisos del Admin por categoría")
        print("-" * 80)
        
        # Agrupar por categoría
        permisos_por_categoria = {}
        for p in admin_rol.permisos:
            cat = p.categoria or "sin_categoria"
            if cat not in permisos_por_categoria:
                permisos_por_categoria[cat] = []
            permisos_por_categoria[cat].append(p.nombre)
        
        categorias_ordenadas = sorted(permisos_por_categoria.keys())
        
        for cat in categorias_ordenadas:
            permisos = sorted(permisos_por_categoria[cat])
            print(f"\n  📁 {cat.upper()} ({len(permisos)} permisos):")
            for p in permisos:
                print(f"     • {p}")
        
        # ========================================
        # RESUMEN FINAL
        # ========================================
        print("\n\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA CON ÉXITO")
        print("="*80)
        print(f"\nNuevos permisos creados: {permisos_creados}")
        print(f"Permisos totales en sistema: {len(todos_permisos)}")
        print(f"Permisos asignados al Admin: {permisos_despues}")
        print(f"\nCategorías cubiertas: {len(categorias_ordenadas)}")
        print(f"Categorías: {', '.join(sorted([c.upper() for c in categorias_ordenadas]))}")
        
        print("\n" + "="*80)
        print("🎉 El rol Admin ahora tiene acceso completo a TODOS los recursos")
        print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
