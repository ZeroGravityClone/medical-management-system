from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QWidget
)

from PySide6.QtCore import Qt


class GestionUsuariosDialog(QDialog):

    def __init__(
        self,
        usuarios_repo,
        usuario_actual
    ):
        super().__init__()

        self.usuarios_repo = usuarios_repo
        self.usuario_actual = usuario_actual

        self.setWindowTitle(
            "Gestión de Permisos de Usuarios"
        )

        self.resize(700,450)

        self.center()

        self.build_ui()

        self.cargar_usuarios()

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        layout = QHBoxLayout(self)

        # ========= TABLA =========

        izquierda = QVBoxLayout()

        titulo = QLabel(
            "Usuarios Registrados"
        )

        izquierda.addWidget(titulo)

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(3)

        self.tabla.setHorizontalHeaderLabels([
            "Usuario",
            "Rol",
            "Acceso"
        ])

        self.tabla.doubleClicked.connect(
            self.cargar_datos_seleccion
        )

        izquierda.addWidget(
            self.tabla
        )

        # ========= FORM =========

        derecha = QVBoxLayout()

        derecha.addWidget(
            QLabel("Usuario")
        )

        self.txt_usuario = QLineEdit()

        derecha.addWidget(
            self.txt_usuario
        )

        derecha.addWidget(
            QLabel("Contraseña")
        )

        self.txt_password = QLineEdit()

        self.txt_password.setEchoMode(
            QLineEdit.Password
        )

        derecha.addWidget(
            self.txt_password
        )

        derecha.addWidget(
            QLabel("Rol")
        )

        self.cbo_rol = QComboBox()

        self.cbo_rol.addItems([
            "GUEST",
            "ADMIN"
        ])

        derecha.addWidget(
            self.cbo_rol
        )

        derecha.addWidget(
            QLabel("Acceso")
        )

        self.cbo_acceso = QComboBox()

        self.cbo_acceso.addItems([
            "PERMITIDO",
            "DENEGADO"
        ])

        derecha.addWidget(
            self.cbo_acceso
        )

        # botones

        self.btn_guardar = QPushButton(
            "Guardar / Actualizar"
        )

        self.btn_guardar.clicked.connect(
            self.guardar_usuario
        )

        derecha.addWidget(
            self.btn_guardar
        )

        self.btn_eliminar = QPushButton(
            "Eliminar Usuario"
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_usuario
        )

        derecha.addWidget(
            self.btn_eliminar
        )

        derecha.addStretch()

        layout.addLayout(
            izquierda,
            3
        )

        layout.addLayout(
            derecha,
            1
        )

        # tema oscuro

        self.setStyleSheet("""

        QDialog{
            background:#0f172a;
            color:white;
        }

        QLabel{
            color:white;
        }

        QLineEdit,QComboBox{
            background:#1f2937;
            color:white;
            border:1px solid #334155;
            border-radius:6px;
            padding:6px;
        }

        QPushButton{
            background:#2563eb;
            color:white;
            border-radius:6px;
            padding:8px;
            font-weight:bold;
        }

        QPushButton:hover{
            background:#1d4ed8;
        }

        QTableWidget{
            background:#1f2937;
            color:white;
            gridline-color:#334155;
        }

        QHeaderView::section{
            background:#111827;
            color:white;
            padding:5px;
        }

        """)

    # ==================================================
    # CARGAR TABLA
    # ==================================================

    def cargar_usuarios(self):

        rows = self.usuarios_repo.obtener_todos()

        self.tabla.setRowCount(
            len(rows)
        )

        for fila,row in enumerate(rows):

            for col,valor in enumerate(row):

                item = QTableWidgetItem(
                    str(valor)
                )

                self.tabla.setItem(
                    fila,
                    col,
                    item
                )

    # ==================================================
    # CARGAR DATOS TABLA
    # ==================================================

    def cargar_datos_seleccion(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            return

        self.txt_usuario.setText(
            self.tabla.item(fila,0).text()
        )

        self.txt_password.clear()

        self.cbo_rol.setCurrentText(
            self.tabla.item(fila,1).text()
        )

        self.cbo_acceso.setCurrentText(
            self.tabla.item(fila,2).text()
        )

    # ==================================================
    # GUARDAR
    # ==================================================

    def guardar_usuario(self):

        u = self.txt_usuario.text().strip().upper()

        p = self.txt_password.text().strip()

        rol = self.cbo_rol.currentText()

        acceso = self.cbo_acceso.currentText()

        if not u:

            QMessageBox.warning(
                self,
                "Atención",
                "Usuario vacío"
            )

            return

        # PROTECCIONES

        if u=="ADMIN":

            if acceso=="DENEGADO" or rol!="ADMIN":

                QMessageBox.critical(
                    self,
                    "Error",
                    "ADMIN no puede degradarse"
                )

                return

        if u==self.usuario_actual:

            if acceso=="DENEGADO" or rol!="ADMIN":

                QMessageBox.critical(
                    self,
                    "Error",
                    "No puedes quitarte permisos"
                )

                return

        try:

            existe = self.usuarios_repo.existe_usuario(u)

            if existe:

                self.usuarios_repo.actualizar_usuario(
                    u,
                    p,
                    rol,
                    acceso
                )

            else:

                if not p:

                    QMessageBox.warning(
                        self,
                        "Atención",
                        "Contraseña requerida"
                    )

                    return

                self.usuarios_repo.crear_usuario(
                    u,
                    p,
                    rol,
                    acceso
                )

            self.cargar_usuarios()

            QMessageBox.information(
                self,
                "OK",
                "Usuario guardado"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    # ==================================================
    # ELIMINAR
    # ==================================================

    def eliminar_usuario(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            return

        u = self.tabla.item(
            fila,
            0
        ).text()

        if u=="ADMIN":

            QMessageBox.critical(
                self,
                "Error",
                "ADMIN no puede eliminarse"
            )

            return

        if u==self.usuario_actual:

            QMessageBox.critical(
                self,
                "Error",
                "No puedes eliminarte"
            )

            return

        resp = QMessageBox.question(
            self,
            "Confirmar",
            f"Eliminar {u}?"
        )

        if resp != QMessageBox.Yes:
            return

        self.usuarios_repo.eliminar_usuario(
            u
        )

        self.cargar_usuarios()

    # ==================================================
    # CENTRAR
    # ==================================================

    def center(self):

        screen = self.screen().geometry()

        self.move(
            (screen.width()-self.width())//2,
            (screen.height()-self.height())//2
        )