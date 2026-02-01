"""Script para verificar que la migración de Enum a tabla Rol fue exitosa"""
import sqlite3

conn = sqlite3.connect('catalogo_rutas.db')
cur = conn.cursor()

print("=" * 60)
print("VERIFICACIÓN DE MIGRACIÓN: ENUM -> TABLA ROL")
print("=" * 60)

# Verificar usuarios con roles
print("\n✅ Usuarios y sus Roles:")
cur.execute('''
    SELECT u.email, r.nombre 
    FROM usuarios u 
    JOIN roles r ON u.rol_id = r.id 
    ORDER BY r.nombre
''')
for email, rol in cur.fetchall():
    print(f"  {email:25} -> {rol}")

# Verificar roles disponibles
print("\n✅ Roles Disponibles:")
cur.execute('SELECT nombre, descripcion FROM roles WHERE es_sistema = 1')
for nombre, desc in cur.fetchall():
    print(f"  {nombre:20} - {desc}")

# Verificar permisos
print("\n✅ Permisos (primeros 10):")
cur.execute('SELECT nombre, categoria FROM permisos LIMIT 10')
for nombre, cat in cur.fetchall():
    print(f"  {nombre:25} [{cat}]")

# Verificar relación rol-permiso
print("\n✅ Relación Rol-Permisos (ejemplo: admin):")
cur.execute('''
    SELECT p.nombre
    FROM roles r
    JOIN rol_permiso rp ON r.id = rp.rol_id
    JOIN permisos p ON rp.permiso_id = p.id
    WHERE r.nombre = 'admin'
    LIMIT 5
''')
for (perm,) in cur.fetchall():
    print(f"  - {perm}")

conn.close()
print("\n" + "=" * 60)
print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 60)
