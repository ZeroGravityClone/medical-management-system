from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMenu
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMenu


class ListaPacientesDialog(QDialog):
    def __init__(self, pacientes_repo):
        super().__init__()

        self.pacientes_repo = pacientes_repo

        self.setWindowTitle("Listado de Pacientes")
        self.resize(900, 500)

        self.center()
        self.build_ui()
        self.cargar_datos()

    # ================= UI =================
    def build_ui(self):

        layout = QVBoxLayout(self)

        titulo = QLabel("Listado de Pacientes")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:white;
        """)

        layout.addWidget(titulo)

        columnas = [
            "Cédula",
            "Apellidos",
            "Nombres",
            "Fecha Registro",
            "Teléfono",
            "Consulta"
        ]

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.tabla.customContextMenuRequested.connect(
            self.menu_copiar
        )

        layout.addWidget(self.tabla)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)

        layout.addWidget(btn_cerrar)

        # ========= tema oscuro =========

        self.setStyleSheet("""
        QDialog{
            background-color:#0f172a;
            color:white;
        }

        QLabel{
            color:white;
        }

        QTableWidget{
            background-color:#1f2937;
            color:white;
            border:1px solid #334155;
            gridline-color:#334155;
        }

        QHeaderView::section{
            background-color:#111827;
            color:white;
            padding:6px;
            border:1px solid #334155;
            font-weight:bold;
        }

        QTableWidget::item:selected{
            background:#2563eb;
        }

        QPushButton{
            background-color:#2563eb;
            color:white;
            padding:8px;
            border-radius:6px;
            font-weight:bold;
        }

        QPushButton:hover{
            background:#1d4ed8;
        }

        QMenu{
            background:#111827;
            color:white;
        }

        QMenu::item:selected{
            background:#2563eb;
        }
        """)

    # ================= CARGAR DATOS =================
    def cargar_datos(self):

        try:

            rows = self.pacientes_repo.obtener_resumen()

            self.tabla.setRowCount(len(rows))

            for fila, datos in enumerate(rows):

                for columna, valor in enumerate(datos):

                    item = QTableWidgetItem(
                        str(valor)
                    )

                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                    self.tabla.setItem(
                        fila,
                        columna,
                        item
                    )

        except Exception as e:
            print("ERROR:", e)

    # ================= MENU COPIAR =================
    def menu_copiar(self, pos):

        item = self.tabla.itemAt(pos)

        if not item:
            return

        fila = item.row()
        columna = item.column()

        valor = item.text()

        # solo cédula o teléfono
        if columna in (0,4):

            valor = "".join(
                c for c in valor
                if c.isdigit()
            )

        menu = QMenu()

        accion = menu.addAction(
            f"Copiar: {valor}"
        )

        seleccion = menu.exec(
            self.tabla.mapToGlobal(pos)
        )

        if seleccion == accion:

            clipboard = QApplication.clipboard()

            clipboard.setText(valor)

    # ================= CENTRAR =================
    def center(self):

        screen = self.screen().geometry()

        x = (screen.width()-self.width())//2
        y = (screen.height()-self.height())//2

        self.move(x,y)