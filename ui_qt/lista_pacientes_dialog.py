# ui_qt/lista_pacientes_dialog.py

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMenu,
    QApplication
)
from PySide6.QtCore import Qt


class ListaPacientesDialog(QDialog):
    def __init__(self, pacientes_repo):
        super().__init__()

        self.pacientes_repo = pacientes_repo

        self.setWindowTitle("Listado de Pacientes")
        self.resize(900, 520) # Ajustado sutilmente para acomodar la tabla con mayor aire

        self.center()
        self.build_ui()
        self.cargar_datos()

    # ================= UI REFACTORIZADA =================
    def build_ui(self):
        # Layout Principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # TÍTULO ESTILO MOONLIGHT
        titulo = QLabel("Listado de Pacientes")
        titulo.setObjectName("DialogTitle")
        titulo.setAlignment(Qt.AlignLeft) # Alineado a la izquierda para armonizar con el Dashboard
        layout.addWidget(titulo)

        columnas = [
            "Cédula",
            "Apellidos",
            "Nombres",
            "Fecha Registro",
            "Teléfono",
            "Consulta"
        ]

        # TABLA DE PACIENTES
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)

        # Ocultar numeración lateral de filas para limpiar la interfaz
        self.tabla.verticalHeader().setVisible(False)

        # Alternancia de color de fila para facilitar lectura visual rápida
        self.tabla.setAlternatingRowColors(True)

        # Configuración de estiramiento y redimensionado de columnas
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Selección de fila completa
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)

        # Menú contextual de copiado rápido
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.menu_copiar)

        layout.addWidget(self.tabla)

        # BARRA DE ACCIÓN INFERIOR (BOTÓN ALINEADO A LA DERECHA)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch() # Empuja el botón "Cerrar" a la derecha

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedWidth(120) # Ancho estándar premium
        btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

        # HOJA DE ESTILOS DE LA TABLA (MOONLIGHT COMPATIBLE)
        self.setStyleSheet("""
            QDialog {
                background-color: #111218;
            }

            QLabel#DialogTitle {
                font-size: 18px;
                font-weight: bold;
                color: #52a9ff; /* Celeste Moonlight */
                padding-bottom: 4px;
            }

            /* Estilo Avanzado para la Tabla */
            QTableWidget {
                background-color: #141622;
                alternate-background-color: #1a1c2e; /* Fila alterna sutil */
                color: #e2e4f0;
                border: 1px solid #2f3352;
                gridline-color: #1e202f; /* División de retícula fina */
                border-radius: 8px;
            }

            /* Estilo para las Cabeceras */
            QHeaderView::section {
                background-color: #111218;
                color: #8a8fbc; /* Azul grisáceo de Moonlight */
                padding: 10px;
                border: none;
                border-bottom: 1px solid #2f3352;
                border-right: 1px solid #2f3352;
                font-weight: bold;
                font-size: 12px;
            }

            /* Item seleccionado (Color de énfasis Moonlight suave) */
            QTableWidget::item:selected {
                background-color: #2e355c;
                color: #ffffff;
            }

            /* Estilo del Botón inferior */
            QPushButton {
                background-color: #1d2035;
                color: #e2e8f0;
                border: 1px solid #2d3154;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #262b49;
                border-color: #409eff;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #151829;
            }

            /* Menú Contextual (Clic derecho sobre tabla) */
            QMenu {
                background-color: #141622;
                color: #cbd5e1;
                border: 1px solid #2f3352;
                border-radius: 6px;
                padding: 4px;
            }

            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #7078f4; /* Púrpura Moonlight */
                color: #111218;
                font-weight: bold;
            }
        """)

    # ================= CARGAR DATOS (LÓGICA INTACTA) =================
    def cargar_datos(self):
        try:
            rows = self.pacientes_repo.obtener_resumen()

            self.tabla.setRowCount(len(rows))

            for fila, datos in enumerate(rows):
                for columna, valor in enumerate(datos):
                    item = QTableWidgetItem(str(valor))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla.setItem(fila, columna, item)

        except Exception as e:
            print("ERROR:", e)

    # ================= MENU COPIAR (LÓGICA INTACTA) =================
    def menu_copiar(self, pos):
        item = self.tabla.itemAt(pos)

        if not item:
            return

        fila = item.row()
        columna = item.column()
        valor = item.text()

        # solo cédula o teléfono
        if columna in (0, 4):
            valor = "".join(c for c in valor if c.isdigit())

        menu = QMenu()
        accion = menu.addAction(f"Copiar: {valor}")
        seleccion = menu.exec(self.tabla.mapToGlobal(pos))

        if seleccion == accion:
            clipboard = QApplication.clipboard()
            clipboard.setText(valor)

    # ================= CENTRAR =================
    def center(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)