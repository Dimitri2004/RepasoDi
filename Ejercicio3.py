import sys
import sqlite3
from traceback import print_tb

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QComboBox, QLineEdit, QPushButton, \
    QTextEdit
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart  # Para el gráfico


class ExamenFlota(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xestión de Flota")
        self.coches = self.obtener_datos_db()


        maia=QGridLayout()
        self.cmbCoches=QComboBox()
        self.cmbCoches.addItems([a[1] for a in self.coches])
        self.cmbCoches.currentIndexChanged.connect(self.cargar_coches)
        self.txtEstado=QLineEdit()
        self.btnPDF=QPushButton("Generar PDF")
        self.btnPDF.clicked.connect(self.generar_pdf)

        maia.addWidget(QLabel("Vehiculos : "),0,0)
        maia.addWidget(self.cmbCoches,0,1)
        maia.addWidget(QLabel("Estado actual : "),1,0)
        maia.addWidget(self.txtEstado,1,1)
        maia.addWidget(self.btnPDF,2,0,1,2)

        container = QWidget()
        container.setLayout(maia)
        self.setCentralWidget(container)

        if self.coches:
            self.cargar_coches()
    def cargar_coches(self):
        idx=self.cmbCoches.currentIndex()
        if idx != -1:
            coch=self.coches[idx]
            estado="Libre" if coch[2] == 1 else "Alquilado"
            self.txtEstado.setText(estado)

    def generar_pdf(self):
        try:
            doc = SimpleDocTemplate("Informe_flota.pdf", pagesize=A4)
            guion = []
            estilos = getSampleStyleSheet()

            guion.append(Paragraph("Estados de Flota", estilos['Title']))
            guion.append(Spacer(1, 20))

            # CORRECCIÓN 1: La cabecera en una sola lista para que sea una fila
            datos_tabla = [["Modelo", "Estado"]]
            libres = 0
            ocupados = 0

            for c in self.coches:
                estado = "Libre" if c[2] == 1 else "Alquilado"
                datos_tabla.append([c[1], estado])

                if c[2] == 1:
                    libres += 1
                else:
                    ocupados += 1

            # CORRECCIÓN 2: Usar datos_tabla, NO guion
            t = Table(datos_tabla)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            guion.append(t)
            guion.append(Spacer(1, 40))

            guion.append(Paragraph("Disponibilidad", estilos['Heading2']))

            d = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 120
            pie.height = 120
            pie.data = [libres, ocupados]
            pie.labels = ['Libres', 'Ocupados']
            pie.slices[0].fillColor = colors.green
            pie.slices[1].fillColor = colors.red

            d.add(pie)
            guion.append(d)

            doc.build(guion)
            print("PDF Creado")
        except Exception as e:
            print(f"Error al generar PDF: {e}")


    def obtener_datos_db(self):
        try:
            conexion = sqlite3.connect('flota.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT id, modelo, dispoñible FROM vehiculos")
            datos = cursor.fetchall()
            conexion.close()
            return [list(fila) for fila in datos]
        except sqlite3.Error as e:
            print(f"Erro DB: {e}")
            return []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExamenFlota()
    window.show()
    sys.exit(app.exec())
