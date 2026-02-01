"""
Script para agregar los permisos faltantes de recursos
"""
import sys
sys.path.append('.')

from app.database.session import SessionLocal
from app.models.rol_permiso import Permiso, Rol

def agregar_permisos():
    db = SessionLocal()
    
    # Permisos a agregar
    nuevos_permisos = [
        # Tramos
        {"nombre": "crear_tramo", "descripcion": "Crear tramos", "categoria": "tramos"},
        {"nombre": "editar_tramo", "descripcion": "Editar tramos", "categoria": "tramos"},
        {"nombre": "eliminar_tramo", "descripcion": "Eliminar tramos", "categoria": "tramos"},
        {"nombre": "ver_tramos", "descripcion": "Ver tramos", "categoria": "tramos"},
        
        # Marcas
        {"nombre": "crear_marca", "descripcion": "Crear marcas de vehículos", "categoria": "marcas"},
        {"nombre": "editar_marca", "descripcion": "Editar marcas de vehículos", "categoria": "marcas"},
        {"nombre": "eliminar_marca", "descripcion": "Eliminar marcas de vehículos", "categoria": "marcas"},
        {"nombre": "ver_marcas", "descripcion": "Ver marcas de vehículos", "categoria": "marcas"},
        
        # Configuración de Vehículos
        {"nombre": "crear_configuracion_vehiculo", "descripcion": "Crear configuraciones de vehículos", "categoria": "configuracion_vehiculos"},
        {"nombre": "editar_configuracion_vehiculo", "descripcion": "Editar configuraciones de vehículos", "categoria": "configuracion_vehiculos"},
        {"nombre": "eliminar_configuracion_vehiculo", "descripcion": "Eliminar configuraciones de vehículos", "categoria": "configuracion_vehiculos"},
        {"nombre": "ver_configuracion_vehiculos", "descripcion": "Ver configuraciones de vehículos", "categoria": "configuracion_vehiculos"},
        
        # Rendimientos
        {"nombre": "crear_rendimiento", "descripcion": "Crear rendimientos", "categoria": "rendimientos"},
        {"nombre": "editar_rendimiento", "descripcion": "Editar rendimientos", "categoria": "rendimientos"},
        {"nombre": "eliminar_rendimiento", "descripcion": "Eliminar rendimientos", "categoria": "rendimientos"},
        {"nombre": "ver_rendimientos", "descripcion": "Ver rendimientos", "categoria": "rendimientos"},
        
        # Tramo Detalles
        {"nombre": "crear_tramo_detalle", "descripcion": "Crear detalles de tramos", "categoria": "tramo_detalles"},
        {"nombre": "editar_tramo_detalle", "descripcion": "Editar detalles de tramos", "categoria": "tramo_detalles"},
        {"nombre": "eliminar_tramo_detalle", "descripcion": "Eliminar detalles de tramos", "categoria": "tramo_detalles"},
        {"nombre": "ver_tramo_detalles", "descripcion": "Ver detalles de tramos", "categoria": "tramo_detalles"},
    ]
    
    # Crear permisos
    creados = 0
    for p_data in nuevos_permisos:
        existente = db.query(Permiso).filter(Permiso.nombre == p_data["nombre"]).first()
        if not existente:
            permiso = Permiso(**p_data)
            db.add(permiso)
            creados += 1
            print(f"✅ Creado: {p_data['nombre']}")
        else:
            print(f"⚠️  Ya existe: {p_data['nombre']}")
    
    db.commit()
    print(f"\n✅ Total permisos creados: {creados}")
    
    # Asignar permisos al rol admin
    admin_rol = db.query(Rol).filter(Rol.nombre == "admin").first()
    if admin_rol:
        # Obtener todos los permisos
        todos_permisos = db.query(Permiso).all()
        admin_rol.permisos = todos_permisos
        db.commit()
        print(f"✅ Asignados {len(todos_permisos)} permisos al rol 'admin'")
    
    # Asignar permisos de rutas al rol gestor_rutas
    gestor_rutas = db.query(Rol).filter(Rol.nombre == "gestor_rutas").first()
    if gestor_rutas:
        permisos_rutas = db.query(Permiso).filter(
            Permiso.categoria.in_(['rutas', 'tramos', 'tramo_detalles', 'peajes'])
        ).all()
        gestor_rutas.permisos = list(set(gestor_rutas.permisos + permisos_rutas))
        db.commit()
        print(f"✅ Asignados permisos de rutas a 'gestor_rutas'")
    
    db.close()

if __name__ == "__main__":
    agregar_permisos()
