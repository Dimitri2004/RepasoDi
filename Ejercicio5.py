import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget,
                             QLabel, QComboBox, QLineEdit, QCheckBox, QSlider,
                             QGroupBox, QVBoxLayout, QPushButton)
from PyQt6.QtCore import Qt  # Para configurar la orientación del Slider
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class ConcesionarioSlider(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Concesionarios Manolo - Selector Dinámico")
        self.registros = self.conectar_db()

        maia = QGridLayout()

        # --- DATOS DE LA DB (Combo y Edits) ---
        self.cmbModelos = QComboBox()
        self.cmbModelos.addItems([m[1] for m in self.registros])
        self.cmbModelos.currentIndexChanged.connect(self.cargar_datos)
        maia.addWidget(QLabel("Vehículo:"), 0, 0)
        maia.addWidget(self.cmbModelos, 0, 1)

        self.txtProp = QLineEdit();
        self.txtProp.setReadOnly(True)
        maia.addWidget(QLabel("Propietario:"), 1, 0)
        maia.addWidget(self.txtProp, 1, 1)

        # --- QSLIDER (Barra de Desplazamiento para el Seguro) ---
        self.grupo_seguro = QGroupBox("Nivel de Cobertura de Seguro")
        lay_s = QVBoxLayout()

        # Creamos el Slider horizontal
        self.sldSeguro = QSlider(Qt.Orientation.Horizontal)
        self.sldSeguro.setMinimum(0)
        self.sldSeguro.setMaximum(2)
        self.sldSeguro.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sldSeguro.setTickInterval(1)
        self.sldSeguro.valueChanged.connect(self.actualizar_texto_slider)

        self.lblInfoSlider = QLabel("Nivel: Básico (200€)")

        lay_s.addWidget(self.sldSeguro)
        lay_s.addWidget(self.lblInfoSlider)
        self.grupo_seguro.setLayout(lay_s)
        maia.addWidget(self.grupo_seguro, 2, 0, 1, 2)

        # --- CHECKBOXES ---
        self.chkLimpieza = QCheckBox("Limpieza (+30€)")
        self.chkCombustible = QCheckBox("Depósito Lleno (+80€)")
        self.chkLimpieza.stateChanged.connect(self.calcular_precio)
        self.chkCombustible.stateChanged.connect(self.calcular_precio)
        maia.addWidget(self.chkLimpieza, 3, 0)
        maia.addWidget(self.chkCombustible, 3, 1)


        # --- TOTAL ---
        self.lblTotal = QLabel("TOTAL: 200.00 €")
        self.lblTotal.setStyleSheet("font-size: 15pt; font-weight: bold; color: blue;")
        maia.addWidget(self.lblTotal, 4, 0, 1, 2)

        self.btnPDF = QPushButton("PDF")
        maia.addWidget(self.btnPDF, 5, 1)
        self.btnPDF.clicked.connect(self.generar_pdf)


        container = QWidget()
        container.setLayout(maia)
        self.setCentralWidget(container)
        self.cargar_datos()

    def conectar_db(self):
        # Usamos la BD que generamos antes
        try:
            conn = sqlite3.connect('DBs/concesionario.db')
            res = conn.execute("SELECT * FROM vehiculos").fetchall()
            conn.close()
            return res
        except:
            return []

    def cargar_datos(self):
        idx = self.cmbModelos.currentIndex()
        if idx != -1:
            self.txtProp.setText(self.registros[idx][2])
            self.calcular_precio()

    def actualizar_texto_slider(self):
        # Cambiamos el texto según la posición de la barra
        niveles = ["Básico (200€)", "Intermedio (350€)", "Premium (600€)"]
        self.lblInfoSlider.setText(f"Nivel: {niveles[self.sldSeguro.value()]}")
        self.calcular_precio()

    def calcular_precio(self):
        # Precios según posición del Slider: 0->200, 1->350, 2->600
        precios_base = [200, 350, 600]
        total = precios_base[self.sldSeguro.value()]

        if self.chkLimpieza.isChecked(): total += 30
        if self.chkCombustible.isChecked(): total += 80

        self.lblTotal.setText(f"TOTAL: {total:.2f} €")
        return total

    def generar_pdf(self):
        try:
            doc = SimpleDocTemplate("PDFs/Orzamento_Slider.pdf", pagesize=A4)
            guion = []
            estilos = getSampleStyleSheet()

            # 1. Título y Datos del Vehículo
            guion.append(Paragraph("Informe de Configuración de Vehículo", estilos['Title']))
            guion.append(Spacer(1, 20))

            idx = self.cmbModelos.currentIndex()
            modelo = self.cmbModelos.currentText()
            propietario = self.txtProp.text()

            # 2. Tabla de Resumen
            total_final = self.calcular_precio()
            datos_t = [
                ["Concepto", "Detalle"],
                ["Vehículo", modelo],
                ["Propietario", propietario],
                ["Total Orzamento", f"{total_final:.2f} €"]
            ]

            tabla = Table(datos_t, colWidths=[120, 250])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.cadetblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
            ]))
            guion.append(tabla)
            guion.append(Spacer(1, 30))

            # 3. Representación del Slider (Nivel de Cobertura)
            guion.append(Paragraph("Nivel de Cobertura Seleccionado:", estilos['Heading2']))
            guion.append(Spacer(1, 10))

            # Creamos un dibujo para la barra de nivel
            d = Drawing(400, 100)
            barra = HorizontalBarChart()
            barra.x = 20
            barra.y = 20
            barra.height = 50
            barra.width = 350

            # El valor del Slider es 0, 1 o 2. Lo mostramos como progreso.
            valor_slider = self.sldSeguro.value()
            barra.data = [[valor_slider + 1]]  # Sumamos 1 para que no sea 0 en el gráfico

            barra.valueAxis.valueMin = 0
            barra.valueAxis.valueMax = 3  # El máximo nivel + 1
            barra.valueAxis.labels.fontName = 'Helvetica'

            # Etiquetas de los niveles
            barra.categoryAxis.categoryNames = ['Nivel de Seguro']

            # Color dinámico: más verde cuanto más alto sea el nivel
            cores = [colors.orange, colors.yellowgreen, colors.darkgreen]
            barra.bars[0].fillColor = cores[valor_slider]

            d.add(barra)
            guion.append(d)

            # Texto explicativo debajo de la barra
            niveis_texto = ["Básico (Mínimo legal)", "Intermedio (Lúas e Roubo)", "Premium (Todo Risco)"]
            guion.append(Paragraph(f"<b>Selección:</b> {niveis_texto[valor_slider]}", estilos['Normal']))

            doc.build(guion)
            print("✅ PDF con barra de nivel generado con éxito.")

        except Exception as e:
            print(f"Erro ao xerar o PDF: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConcesionarioSlider()
    window.show()
    sys.exit(app.exec())