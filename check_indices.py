import sqlite3

conn = sqlite3.connect('catalogo_rutas.db')
cursor = conn.cursor()

# Ver índices
print("=== ÍNDICES EN PEAJES ===")
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='peajes'")
for row in cursor.fetchall():
    print(f"\nÍndice: {row[0]}")
    print(f"SQL: {row[1]}")

# Ver si hay peajes existentes
print("\n\n=== PEAJES EXISTENTES ===")
cursor.execute("SELECT id, nombre, nombre_peaje FROM peajes LIMIT 10")
for row in cursor.fetchall():
    print(f"ID={row[0]}, nombre='{row[1]}', nombre_peaje='{row[2]}'")

conn.close()
