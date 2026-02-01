"""
Script para agregar permisos de TRAMOS faltantes y asignarlos al rol Admin
"""
from app.database.session import SessionLocal
from app.models.rol_permiso import Rol, Permiso
from sqlalchemy import func

def agregar_permisos_tramos():
    db = SessionLocal()
    try:
        print("\n🔍 PASO 1: Verificando permisos de tramos...")
        
        # Permisos de tramos que deben existir
        PERMISOS_TRAMOS = [
            ("crear_tramo", "Crear nuevos tramos", "tramos"),
            ("editar_tramo", "Editar tramos existentes", "tramos"),
            ("eliminar_tramo", "Eliminar tramos", "tramos"),
            ("ver_tramos", "Ver lista de tramos", "tramos"),
        ]
        
        permisos_creados = 0
        permisos_ids = []
        
        for nombre, descripcion, categoria in PERMISOS_TRAMOS:
            existente = db.query(Permiso).filter(
                func.lower(Permiso.nombre) == func.lower(nombre)
            ).first()
            
            if existente:
                print(f"  ✓ Permiso '{nombre}' ya existe (ID: {existente.id})")
                permisos_ids.append(existente.id)
            else:
                permiso = Permiso(
                    nombre=nombre,
                    descripcion=descripcion,
                    categoria=categoria,
                    es_sistema=1,
                    activo=1
                )
                db.add(permiso)
                db.flush()  # Para obtener el ID
                permisos_ids.append(permiso.id)
                print(f"  ✅ Permiso '{nombre}' creado (ID: {permiso.id})")
                permisos_creados += 1
        
        db.commit()
        print(f"\n📊 Total permisos de tramos creados: {permisos_creados}/4")
        
        # PASO 2: Asignar todos los permisos al rol Admin
        print("\n🔍 PASO 2: Verificando rol Admin...")
        
        admin_rol = db.query(Rol).filter(
            func.lower(Rol.nombre) == 'admin'
        ).first()
        
        if not admin_rol:
            print("  ❌ ERROR: No se encontró el rol 'admin'")
            return
        
        print(f"  ✓ Rol Admin encontrado (ID: {admin_rol.id})")
        print(f"  📋 Permisos actuales del admin: {len(admin_rol.permisos)}")
        
        # Obtener todos los permisos del sistema
        todos_los_permisos = db.query(Permiso).filter(
            Permiso.es_sistema == 1,
            Permiso.activo == 1
        ).all()
        
        print(f"  📋 Total permisos en el sistema: {len(todos_los_permisos)}")
        
        # Asignar TODOS los permisos al admin
        permisos_antes = len(admin_rol.permisos)
        admin_rol.permisos = todos_los_permisos
        db.commit()
        permisos_despues = len(admin_rol.permisos)
        
        print(f"\n✅ Admin actualizado:")
        print(f"   • Permisos antes: {permisos_antes}")
        print(f"   • Permisos después: {permisos_despues}")
        print(f"   • Permisos agregados: {permisos_despues - permisos_antes}")
        
        # Mostrar todos los permisos del admin
        print(f"\n📋 Lista completa de permisos del Admin:")
        permisos_por_categoria = {}
        for permiso in admin_rol.permisos:
            if permiso.categoria not in permisos_por_categoria:
                permisos_por_categoria[permiso.categoria] = []
            permisos_por_categoria[permiso.categoria].append(permiso.nombre)
        
        for categoria in sorted(permisos_por_categoria.keys()):
            print(f"\n   {categoria.upper()}:")
            for nombre in sorted(permisos_por_categoria[categoria]):
                print(f"     • {nombre}")
        
        print("\n✅ ¡Listo! El admin ahora tiene TODOS los permisos del sistema")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("🔧 AGREGAR PERMISOS DE TRAMOS Y ACTUALIZAR ADMIN")
    print("=" * 70)
    agregar_permisos_tramos()
    print("\n" + "=" * 70)
