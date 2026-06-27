# ui_qt/gestion_usuarios_dialog.py

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QFrame,
    QHeaderView
)
from PySide6.QtCore import Qt


class GestionUsuariosDialog(QDialog):

    def __init__(self, usuarios_repo, usuario_actual):
        super().__init__()

        self.usuarios_repo = usuarios_repo
        self.usuario_actual = usuario_actual

        self.setWindowTitle("Gestión de Permisos de Usuarios")
        self.resize(780, 480) # Dimensiones optimizadas para distribución lateral

        self.center()
        self.build_ui()
        self.cargar_usuarios()

    # ==================================================
    # UI REFACTORIZADA
    # ==================================================
    def build_ui(self):
        # Layout Principal Horizontal (Split)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ==================================================
        # PANEL IZQUIERDO: LISTADO (TABLA DE USUARIOS)
        # ==================================================
        izquierda = QVBoxLayout()
        izquierda.setSpacing(10)

        titulo_tabla = QLabel("Usuarios Registrados")
        titulo_tabla.setObjectName("SubTitleLabel")
        izquierda.addWidget(titulo_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Usuario", "Rol", "Acceso"])
        
        # Ocultar numeración lateral y activar diseño moderno
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Estirar columnas proporcionalmente
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Conexión original de carga de datos al hacer doble clic
        self.tabla.doubleClicked.connect(self.cargar_datos_seleccion)

        izquierda.addWidget(self.tabla)
        layout.addLayout(izquierda, stretch=3)

        # ==================================================
        # PANEL DERECHO: FORMULARIO DE ACCESOS (CARD)
        # ==================================================
        derecha_container = QVBoxLayout()
        
        # Tarjeta de Formulario estilo Moonlight
        self.card_form = QFrame()
        self.card_form.setObjectName("CardForm")
        
        layout_card = QVBoxLayout(self.card_form)
        layout_card.setContentsMargins(16, 16, 16, 16)
        layout_card.setSpacing(12)

        lbl_tit_card = QLabel("Configurar Acceso")
        lbl_tit_card.setObjectName("CardTitle")
        layout_card.addWidget(lbl_tit_card)

        # Formulario interno alineado
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("ID de usuario")
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Nueva contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)

        self.cbo_rol = QComboBox()
        self.cbo_rol.addItems(["GUEST", "ADMIN"])

        self.cbo_acceso = QComboBox()
        self.cbo_acceso.addItems(["PERMITIDO", "DENEGADO"])

        form_layout.addRow("Usuario:", self.txt_usuario)
        form_layout.addRow("Clave:", self.txt_password)
        form_layout.addRow("Rol:", self.cbo_rol)
        form_layout.addRow("Acceso:", self.cbo_acceso)

        layout_card.addLayout(form_layout)

        # Separación sutil antes de los botones dentro de la tarjeta
        layout_card.addSpacing(6)

        # Botones CRUD con pesos visuales semánticos
        self.btn_guardar = QPushButton("Guardar / Actualizar")
        self.btn_guardar.setObjectName("BtnPrimary") # Acción principal de guardado (Violeta)
        self.btn_guardar.clicked.connect(self.guardar_usuario)
        layout_card.addWidget(self.btn_guardar)

        self.btn_eliminar = QPushButton("Eliminar Usuario")
        self.btn_eliminar.setObjectName("BtnDanger") # Advertencia destructiva (Borde rojo)
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)
        layout_card.addWidget(self.btn_eliminar)

        derecha_container.addWidget(self.card_form)
        derecha_container.addStretch() # Mantiene la tarjeta compacta arriba

        layout.addLayout(derecha_container, stretch=2)

        # HOJA DE ESTILOS PERSONALIZADA (MOONLIGHT COMPATIBLE)
        self.setStyleSheet("""
            QDialog {
                background-color: #111218;
            }

            QLabel#SubTitleLabel {
                font-size: 15px;
                font-weight: bold;
                color: #52a9ff; /* Celeste Moonlight */
            }

            QFrame#CardForm {
                background-color: #181a23;
                border: 1px solid #2f3352;
                border-radius: 8px;
            }

            QLabel {
                color: #8a8fbc;
                font-weight: 500;
            }

            QLabel#CardTitle {
                color: #52a9ff;
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid #2f3352;
                padding-bottom: 6px;
                margin-bottom: 4px;
            }

            QLineEdit, QComboBox {
                background-color: #1e202f;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                border-radius: 6px;
                padding: 6px 10px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #7078f4;
                background-color: #212433;
            }

            /* Estilo para la Tabla de Usuarios */
            QTableWidget {
                background-color: #141622;
                alternate-background-color: #1a1c2e;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                gridline-color: #1e202f;
                border-radius: 8px;
            }

            QHeaderView::section {
                background-color: #111218;
                color: #8a8fbc;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #2f3352;
                border-right: 1px solid #2f3352;
                font-weight: bold;
                font-size: 11px;
            }

            QTableWidget::item:selected {
                background-color: #2e355c;
                color: #ffffff;
            }

            /* Botones CRUD */
            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 20px;
            }

            QPushButton#BtnPrimary {
                background-color: #7078f4;
                color: #111218;
                border: 1px solid #7078f4;
            }

            QPushButton#BtnPrimary:hover {
                background-color: #5c63db;
                border-color: #5c63db;
            }

            QPushButton#BtnDanger {
                background-color: transparent;
                color: #ef4444;
                border: 1px solid #2d1717;
            }

            QPushButton#BtnDanger:hover {
                background-color: #ef4444;
                color: #111218;
                border-color: #ef4444;
            }
        """)

    # ==================================================
    # CARGAR TABLA (LÓGICA DE NEGOCIO INTACTA)
    # ==================================================
    def cargar_usuarios(self):
        rows = self.usuarios_repo.obtener_todos()
        self.tabla.setRowCount(len(rows))

        for fila, row in enumerate(rows):
            for col, valor in enumerate(row):
                item = QTableWidgetItem(str(valor))
                self.tabla.setItem(fila, col, item)

    # ==================================================
    # CARGAR DATOS TABLA (LÓGICA DE NEGOCIO INTACTA)
    # ==================================================
    def cargar_datos_seleccion(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return

        self.txt_usuario.setText(self.tabla.item(fila, 0).text())
        self.txt_password.clear()
        self.cbo_rol.setCurrentText(self.tabla.item(fila, 1).text())
        self.cbo_acceso.setCurrentText(self.tabla.item(fila, 2).text())

    # ==================================================
    # GUARDAR (LÓGICA DE SEGURIDAD INTACTA)
    # ==================================================
    def guardar_usuario(self):
        u = self.txt_usuario.text().strip().upper()
        p = self.txt_password.text().strip()
        rol = self.cbo_rol.currentText()
        acceso = self.cbo_acceso.currentText()

        if not u:
            QMessageBox.warning(self, "Atención", "Usuario vacío")
            return

        # PROTECCIONES DE SEGURIDAD ORIGINALES
        if u == "ADMIN":
            if acceso == "DENEGADO" or rol != "ADMIN":
                QMessageBox.critical(self, "Error", "ADMIN no puede degradarse")
                return

        if u == self.usuario_actual:
            if acceso == "DENEGADO" or rol != "ADMIN":
                QMessageBox.critical(self, "Error", "No puedes quitarte permisos")
                return

        try:
            existe = self.usuarios_repo.existe_usuario(u)

            if existe:
                self.usuarios_repo.actualizar_usuario(u, p, rol, acceso)
            else:
                if not p:
                    QMessageBox.warning(self, "Atención", "Contraseña requerida")
                    return
                self.usuarios_repo.crear_usuario(u, p, rol, acceso)

            self.cargar_usuarios()
            QMessageBox.information(self, "OK", "Usuario guardado")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ==================================================
    # ELIMINAR (LÓGICA DE SEGURIDAD INTACTA)
    # ==================================================
    def eliminar_usuario(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return

        u = self.tabla.item(fila, 0).text()

        # PROTECCIONES DE SEGURIDAD ORIGINALES
        if u == "ADMIN":
            QMessageBox.critical(self, "Error", "ADMIN no puede eliminarse")
            return

        if u == self.usuario_actual:
            QMessageBox.critical(self, "Error", "No puedes eliminarte")
            return

        resp = QMessageBox.question(self, "Confirmar", f"Eliminar {u}?")
        if resp != QMessageBox.Yes:
            return

        self.usuarios_repo.eliminar_usuario(u)
        self.cargar_usuarios()

    # ==================================================
    # CENTRAR
    # ==================================================
    def center(self):
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
