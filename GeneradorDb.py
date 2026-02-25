import sqlite3


def crear_bases_datos():
    # --- BD EJERCICIO 3: COLEXIO ---
    conn_edu = sqlite3.connect('colexio.db')
    cursor_edu = conn_edu.cursor()
    cursor_edu.execute('DROP TABLE IF EXISTS alumnos')
    cursor_edu.execute('''CREATE TABLE alumnos
                          (
                              id    INTEGER PRIMARY KEY,
                              nome  TEXT,
                              nota1 REAL,
                              nota2 REAL,
                              nota3 REAL
                          )''')
    alumnos = [
        (1, 'Ana Silva', 8.5, 7.0, 9.0),
        (2, 'Brais Porto', 4.0, 3.5, 5.0),
        (3, 'Carla Meis', 2.0, 4.0, 3.0),
        (4, 'David Rivas', 9.5, 10.0, 9.0)
    ]
    cursor_edu.executemany('INSERT INTO alumnos VALUES (?,?,?,?,?)', alumnos)
    conn_edu.commit()
    conn_edu.close()

    # --- BD EJERCICIO 4: FLOTA ---
    conn_car = sqlite3.connect('flota.db')
    cursor_car = conn_car.cursor()
    cursor_car.execute('DROP TABLE IF EXISTS vehiculos')
    cursor_car.execute('''CREATE TABLE vehiculos
                          (
                              id         INTEGER PRIMARY KEY,
                              modelo     TEXT,
                              dispoñible INTEGER
                          )''')  # 1 = Si, 0 = No
    coches = [
        (1, 'Toyota Corolla', 1),
        (2, 'Seat Ibiza', 0),
        (3, 'Ford Focus', 1),
        (4, 'Tesla Model 3', 0),
        (5, 'Renault Clio', 1)
    ]
    cursor_car.executemany('INSERT INTO vehiculos VALUES (?,?,?)', coches)
    conn_car.commit()
    conn_car.close()

    print("✅ Bases de datos 'colexio.db' e 'flota.db' creadas con éxito.")


if __name__ == "__main__":
    crear_bases_datos()