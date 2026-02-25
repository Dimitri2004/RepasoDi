import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget,
                             QLabel, QComboBox, QLineEdit, QCheckBox, QRadioButton,
                             QGroupBox, QVBoxLayout, QPushButton)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

class TechFixElite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tech-Fix Elite Management")
        self.registros = self.conectar_db()

        #Maia que guarda los datos
        maia = QGridLayout()
        self.cmb=QComboBox()
        self.cmb.addItems([r[1] for r in self.registros])
        self.cmb.currentIndexChanged.connect(self.actualizar_datos)

        maia.addWidget(QLabel("Selleccionar Dispositivo :"),0,0)
        maia.addWidget(self.cmb,0,1)

        self.txtCliente=QLineEdit()
        self.txtCliente.setReadOnly(True)
        self.txtSo=QLineEdit()
        self.txtSo.setReadOnly(True)
        self.txtSerie=QLineEdit()
        self.txtSerie.setReadOnly(True)
        self.chkGarantia=QCheckBox("Garantia Activada")
        self.chkGarantia.setEnabled(False)

        maia.addWidget(QLabel("Cliente :"),1,0)
        maia.addWidget(self.txtCliente,1,1)
        maia.addWidget(QLabel("SO : "),2,0)
        maia.addWidget(self.txtSo,2,1)
        maia.addWidget(QLabel("Serie :"),3,0)
        maia.addWidget(self.txtSerie,3,1)
        maia.addWidget(self.chkGarantia,4,1)

        self.grupo=QGroupBox("Prioridade de Traballo")
        lay_r=QVBoxLayout()
        self.radEstandar=QRadioButton("Estandar (0€)")
        self.radUrgente=QRadioButton("Urgente (0€)")
        self.radEstandar.setChecked(True)
        lay_r.addWidget(self.radEstandar)
        lay_r.addWidget(self.radUrgente)
        self.grupo.setLayout(lay_r)
        maia.addWidget(self.grupo,5,0,1,2)

        self.chkBackup=QCheckBox("Copia de seguridad (+15€)")
        self.chkLimpieza=QCheckBox("Limpieza Qímica (+20€)")
        maia.addWidget(self.chkBackup,6,0)
        maia.addWidget(self.chkLimpieza,6,1)

        self.lblTotal=QLabel("TOTAL : 0.00 €")
        self.lblTotal.setStyleSheet("font-size: 18px; color: darkred; font-weight: bold;")
        maia.addWidget(self.lblTotal,7,0)

        self.btnPDF=QPushButton("PDF")
        maia.addWidget(self.btnPDF,7,1)

        self.radEstandar.toggled.connect(self.calcular_precio)
        self.radUrgente.toggled.connect(self.calcular_precio)
        self.chkBackup.stateChanged.connect(self.calcular_precio)
        self.chkLimpieza.stateChanged.connect(self.calcular_precio)
        self.btnPDF.clicked.connect(self.generar_pdf)

        container = QWidget()
        container.setLayout(maia)
        self.setCentralWidget(container)
        self.actualizar_datos()

    def conectar_db(self):
        try:
            conexion = sqlite3.connect('tech_elite.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT id, modelo, cliente,f_compra,so, serie,garantia FROM reparaciones")
            datos = cursor.fetchall()
            conexion.close()
            return [list(fila) for fila in datos]
        except sqlite3.Error as e:
            print(f"Erro DB: {e}")
            return []

    def actualizar_datos(self):
        idx = self.cmb.currentIndex()
        if idx != -1:
            d = self.registros[idx]
            self.txtCliente.setText(d[2])
            self.txtSo.setText(d[4])
            self.txtSerie.setText(d[5])
            # Marcamos garantía si el valor en la BD es 1
            self.chkGarantia.setChecked(True if d[6] == 1 else False)
            self.calcular_precio()  # Recalcular precio al cambiar de dispositivo

    def calcular_precio(self):
        # Coste Prioridad
        coste_prioridad = 40 if self.radUrgente.isChecked() else 0

        # Coste Extras
        coste_extras = 0
        if self.chkBackup.isChecked(): coste_extras += 15
        if self.chkLimpieza.isChecked(): coste_extras += 20

        total = coste_prioridad + coste_extras

        # Aplicar descuento si hay garantía (50%)
        if self.chkGarantia.isChecked():
            total = total * 0.5

        self.lblTotal.setText(f"TOTAL : {total:.2f} €")
        return total, coste_prioridad, coste_extras

    def generar_pdf(self):
        doc = SimpleDocTemplate("Factura_Elite.pdf", pagesize=A4)
        guion = []
        estilos = getSampleStyleSheet()

        guion.append(Paragraph("ORDE DE TRABALLO", estilos['Title']))
        guion.append(Spacer(1, 20))

        # Obtener datos actuales
        total, c_prioridad, c_extras = self.calcular_precio()
        idx = self.cmb.currentIndex()
        d = self.registros[idx]

        # Tabla de Datos
        datos_tabla = [
            ["CAMPO", "INFORMACIÓN"],
            ["Cliente", d[2]],
            ["Dispositivo", d[1]],
            ["Nº Serie", d[5]],
            ["Sistema Operativo", d[4]],
            ["Garantía", "SI (50% Dto)" if d[6] == 1 else "NON"],
            ["TOTAL FACTURA", f"{total:.2f} €"]
        ]

        t = Table(datos_tabla, colWidths=[150, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('SIZE', (0, -1), (-1, -1), 12),
        ]))
        guion.append(t)
        guion.append(Spacer(1, 30))

        # --- GRÁFICO DE TARTA ---
        guion.append(Paragraph("Desglose de Custos (Sen Descontos)", estilos['Heading2']))

        # Solo dibujamos si hay algún coste para evitar errores de Drawing
        if (c_prioridad + c_extras) > 0:
            d_canvas = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 120
            pie.height = 120
            pie.data = [c_prioridad, c_extras]
            pie.labels = ['Prioridade', 'Extras']

            # Colores bonitos
            pie.slices[0].fillColor = colors.red
            pie.slices[1].fillColor = colors.green

            d_canvas.add(pie)
            guion.append(d_canvas)
        else:
            guion.append(Paragraph("Non hai custos adicionais para mostrar no gráfico.", estilos['Normal']))

        doc.build(guion)
        print("PDF Elite xerado con éxito.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TechFixElite()
    window.show()
    sys.exit(app.exec())