import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QComboBox, QLineEdit, QPushButton, \
    QTextEdit
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart  # Para el gráfico


class ExameNotas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xestión Académica")
        self.alumnos = self.obter_datos_db()

        maia = QGridLayout()

        # Combo (Cargamos el nombre: a[1])
        maia.addWidget(QLabel("Seleccionar alumno : "), 0, 0)
        self.cmbAlumno = QComboBox()
        self.cmbAlumno.addItems([a[1] for a in self.alumnos])
        self.cmbAlumno.currentIndexChanged.connect(self.cargar_alumno)  # .connect añadido
        maia.addWidget(self.cmbAlumno, 0, 1)

        # Notas
        maia.addWidget(QLabel("Nota 1:"), 1, 0)
        self.txtN1 = QLineEdit()
        maia.addWidget(self.txtN1, 1, 1)

        maia.addWidget(QLabel("Nota 2 :"), 2, 0)
        self.txtN2 = QLineEdit()
        maia.addWidget(self.txtN2, 2, 1)

        maia.addWidget(QLabel("Nota 3 :"), 3, 0)
        self.txtN3 = QLineEdit()
        maia.addWidget(self.txtN3, 3, 1)

        self.lblMedia = QLabel("Media: -")
        maia.addWidget(self.lblMedia, 4, 0)

        self.btnPDF = QPushButton("Generar PDF")
        self.btnPDF.clicked.connect(self.generar_datos)
        maia.addWidget(self.btnPDF, 4, 1)

        container = QWidget()
        container.setLayout(maia)
        self.setCentralWidget(container)

        if self.alumnos:
            self.cargar_alumno()

    def cargar_alumno(self):  # Nombre corregido
        idx = self.cmbAlumno.currentIndex()
        if idx != -1:
            alu = self.alumnos[idx]
            self.txtN1.setText(str(alu[2]))
            self.txtN2.setText(str(alu[3]))
            self.txtN3.setText(str(alu[4]))

            media = (alu[2] + alu[3] + alu[4]) / 3
            self.lblMedia.setText(f"Media : {media:.2f}")

    def obter_datos_db(self):
        try:
            conexion = sqlite3.connect('DBs/colexio.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nome, nota1, nota2, nota3 FROM alumnos")
            datos = cursor.fetchall()
            conexion.close()
            return [list(fila) for fila in datos]
        except sqlite3.Error as e:
            print(f"Error DB: {e}")
            return []

    def generar_datos(self):
        doc = SimpleDocTemplate("PDFs/Informe_Notas.pdf", pagesize=A4)
        guion = []
        estilos = getSampleStyleSheet()

        guion.append(Paragraph("Informe de Rendemento Académico", estilos['Title']))
        guion.append(Spacer(1, 20))

        # Cabecera corregida
        datos_data = [["Alumno", "Media"]]
        medias_para_grafico = []  # Guardaremos las medias para el gráfico posterior

        for a in self.alumnos:
            media = (a[2] + a[3] + a[4]) / 3
            datos_data.append([a[1], f"{media:.2f}"])
            medias_para_grafico.append(media)

        estilo_tabla = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'CENTER')
        ]

        for i, fila in enumerate(datos_data[1:], start=1):
            nota_media = float(fila[1])
            if nota_media < 5:
                estilo_tabla.append(('TEXTCOLOR', (1, i), (1, i), colors.red))
                estilo_tabla.append(('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'))  # Typo corregido
            else:
                estilo_tabla.append(('TEXTCOLOR', (1, i), (1, i), colors.blue))

        t = Table(datos_data)
        t.setStyle(TableStyle(estilo_tabla))
        guion.append(t)
        guion.append(Spacer(1, 30))

        # --- AÑADIDO: GRÁFICO DE BARRAS ---
        guion.append(Paragraph("Gráfico de Medias", estilos['Heading2']))
        d = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [medias_para_grafico]  # Debe ser una lista de listas
        bc.categoryAxis.categoryNames = [a[1] for a in self.alumnos]
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 10
        d.add(bc)
        guion.append(d)

        doc.build(guion)
        print("PDF CREADO")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExameNotas()
    window.show()
    sys.exit(app.exec())