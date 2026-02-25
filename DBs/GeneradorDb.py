import sqlite3

def generar_db_logistica():
    conn = sqlite3.connect('mensajeria.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS envios')
    # ID, Paquete, Destinatario, Fecha_Salida, Metodo_Envio, Tracking_ID, Asegurado
    cursor.execute('''CREATE TABLE envios(
                        id INTEGER PRIMARY KEY, 
                        paquete TEXT, 
                        destinatario TEXT, 
                        f_salida TEXT, 
                        metodo TEXT, 
                        tracking TEXT, 
                        asegurado INTEGER)''')

    datos = [
        (1, 'Caja Mediana', 'Sabela Gago', '2024-02-25', 'Aéreo', 'TRK-990', 1),
        (2, 'Sobre Documentos', 'Pepe López', '2024-02-25', 'Estándar', 'TRK-441', 0),
        (3, 'Palet Industrial', 'Empresa Galega', '2024-02-26', 'Marítimo', 'TRK-112', 1),
        (4, 'Pack Electrónica', 'Marta Rivas', '2024-02-27', 'Urgente', 'TRK-885', 1),
        (5, 'Caja Pequeña', 'Luis Fer', '2024-02-28', 'Estándar', 'TRK-003', 0)
    ]
    cursor.executemany('INSERT INTO envios VALUES (?,?,?,?,?,?,?)', datos)
    conn.commit()
    conn.close()
    print("✅ BD 'mensajeria.db' generada.")

generar_db_logistica()