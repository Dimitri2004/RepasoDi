import sqlite3


def generar_db():
    conn = sqlite3.connect('tech_elite.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS reparaciones')
    # ID, Modelo, Cliente, Fecha_Compra, Version_SO, Num_Serie, Garantia
    cursor.execute('''CREATE TABLE reparaciones
                      (
                          id       INTEGER PRIMARY KEY,
                          modelo   TEXT,
                          cliente  TEXT,
                          f_compra TEXT,
                          so       TEXT,
                          serie    TEXT,
                          garantia INTEGER
                      )''')

    datos = [
        (1, 'iPhone 15 Pro', 'Lucía Mella', '2024-02-10', 'iOS 17', 'SN-9981', 1),
        (2, 'Laptop MSI Katana', 'Jorge Vales', '2023-05-20', 'Win 11', 'SN-4421', 0),
        (3, 'iPad Air', 'Marta Porto', '2023-11-12', 'iPadOS 17', 'SN-1102', 1),
        (4, 'Steam Deck', 'Brais Gil', '2024-01-05', 'SteamOS', 'SN-8873', 1),
        (5, 'Workstation Dell', 'Empresa X', '2022-08-30', 'Ubuntu 22', 'SN-0051', 0)
    ]

    cursor.executemany('INSERT INTO reparaciones VALUES (?,?,?,?,?,?,?)', datos)
    conn.commit()
    conn.close()
    print("✅ Base de datos 'tech_elite.db' generada correctamente.")


if __name__ == "__main__":
    generar_db()