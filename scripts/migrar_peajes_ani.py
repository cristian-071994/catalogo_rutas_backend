import sqlite3

DB_PATH = "catalogo_rutas.db"

NUEVAS_COLUMNAS = [
    ("id_peaje_api", "VARCHAR(20)"),
    ("categoria_tarifa", "VARCHAR(10)"),
    ("fecha_ultima_tarifa", "DATETIME"),
]


def columna_existe(cursor, nombre_columna: str) -> bool:
    cursor.execute("PRAGMA table_info(peajes)")
    return any(row[1] == nombre_columna for row in cursor.fetchall())


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cambios = 0
    for nombre, tipo in NUEVAS_COLUMNAS:
        if not columna_existe(cursor, nombre):
            cursor.execute(f"ALTER TABLE peajes ADD COLUMN {nombre} {tipo}")
            cambios += 1

    conn.commit()
    conn.close()

    if cambios:
        print(f"✅ Migración ANI aplicada. Columnas agregadas: {cambios}")
    else:
        print("ℹ️ No se aplicaron cambios (columnas ya existían).")


if __name__ == "__main__":
    main()
