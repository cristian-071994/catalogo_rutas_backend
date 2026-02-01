import sqlite3

conn = sqlite3.connect('catalogo_rutas.db')
cursor = conn.cursor()

# Ver si hay peajes con nombre SAN PEDRO
cursor.execute("SELECT id, nombre, nombre_peaje FROM peajes WHERE nombre LIKE '%SAN PEDRO%'")
rows = cursor.fetchall()

print(f"Peajes con 'SAN PEDRO' en nombre: {len(rows)}")
for row in rows:
    print(f"  ID={row[0]}, nombre='{row[1]}', nombre_peaje='{row[2]}'")

# Ver la estructura de la tabla
print("\n--- Estructura de tabla peajes ---")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='peajes'")
print(cursor.fetchone()[0])

conn.close()
