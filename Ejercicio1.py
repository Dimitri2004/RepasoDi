import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit)
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4


class ExameGamer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exame DI - Gamer Store")

        # 1. Cargar datos desde la DB
        self.videoxogos = self.obter_datos_db()

        maia = QGridLayout()

        # Widgets
        maia.addWidget(QLabel("Seleccionar Juego: "), 0, 0)
        self.cmbXogos = QComboBox()
        # El nombre del juego es x[1] en tu SELECT (id es 0, nombre es 1)
        self.cmbXogos.addItems([x[1] for x in self.videoxogos])
        self.cmbXogos.currentIndexChanged.connect(self.cargar_datos)
        maia.addWidget(self.cmbXogos, 0, 1)

        maia.addWidget(QLabel("Género/Nombre :"), 1, 0)  # En tu SQL el 1 es el nombre
        self.txtNombre = QLineEdit()
        maia.addWidget(self.txtNombre, 1, 1)

        maia.addWidget(QLabel("Stock :"), 2, 0)  # En tu SQL el 2 es stock
        self.txtStock = QLineEdit()
        maia.addWidget(self.txtStock, 2, 1)

        maia.addWidget(QLabel("Prezo (€) :"), 3, 0)  # En tu SQL el 3 es precio
        self.txtPrezo = QLineEdit()
        maia.addWidget(self.txtPrezo, 3, 1)

        # Botones
        self.btnActualizar = QPushButton("Actualizar Datos Localmente")
        self.btnActualizar.clicked.connect(self.actualizar_datos)
        maia.addWidget(self.btnActualizar, 4, 0)

        self.btnPDF = QPushButton("Generar PDF")
        self.btnPDF.clicked.connect(self.generar_pdf)
        maia.addWidget(self.btnPDF, 4, 1)

        self.txtArea = QTextEdit()
        self.txtArea.setReadOnly(True)
        maia.addWidget(self.txtArea, 5, 0, 1, 2)

        container = QWidget()
        container.setLayout(maia)
        self.setCentralWidget(container)

        if self.videoxogos:
            self.cargar_datos()

    def cargar_datos(self):
        idx = self.cmbXogos.currentIndex()
        if idx != -1:
            datos = self.videoxogos[idx]
            # Mapeo según tu SELECT id(0), nombre(1), stock(2), precio(3)
            self.txtNombre.setText(str(datos[1]))
            self.txtStock.setText(str(datos[2]))
            self.txtPrezo.setText(str(datos[3]))

    def actualizar_datos(self):
        idx = self.cmbXogos.currentIndex()
        if idx != -1:
            self.videoxogos[idx][1] = self.txtNombre.text()
            self.videoxogos[idx][2] = self.txtStock.text()
            self.videoxogos[idx][3] = self.txtPrezo.text()  # Corregido índice 3
            self.txtArea.append(f"Actualizado en memoria: {self.videoxogos[idx][1]}")

    def generar_pdf(self):
        doc = SimpleDocTemplate("PDFs/Informe_Ventas.pdf", pagesize=A4)
        guion = []
        estilos = getSampleStyleSheet()

        guion.append(Paragraph("Informe de Ventas Gamer Store", estilos['Title']))
        guion.append(Spacer(1, 20))

        # Tabla Corregida (Fila de cabecera única)
        datos_taboa = [["ID", "Nombre", "Stock", "Precio"]]
        for x in self.videoxogos:
            datos_taboa.append(x)

        t = Table(datos_taboa)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # GRID para toda la tabla
        ]))
        guion.append(t)
        guion.append(Spacer(1, 40))

        # Gráfico Corregido
        d = Drawing(400, 200)  # Añadir dimensiones al Drawing
        pie = Pie()
        pie.x = 150
        pie.y = 10
        pie.width = 150
        pie.height = 150
        # Corregido x[30] por x[2] (Stock/Ventas)
        pie.data = [float(x[2]) for x in self.videoxogos]
        pie.labels = [x[1] for x in self.videoxogos]
        d.add(pie)
        guion.append(d)

        doc.build(guion)
        self.txtArea.append("PDF Generado correctamente.")

    def obter_datos_db(self):
        try:
            conexion = sqlite3.connect('DBs/tienda.db')
            cursor = conexion.cursor()
            # OJO: Aquí el orden es 0:id, 1:nombre, 2:stock, 3:precio
            cursor.execute("SELECT id, nombre, stock, precio FROM productos")
            datos = cursor.fetchall()
            conexion.close()
            return [list(fila) for fila in datos]
        except sqlite3.Error as e:
            self.txtArea.append(f"Error DB: {e}")
            return []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExameGamer()
    window.show()
    sys.exit(app.exec())