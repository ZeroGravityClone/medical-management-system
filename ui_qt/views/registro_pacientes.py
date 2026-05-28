from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QHBoxLayout,
    QMessageBox, QDateEdit, QInputDialog
)
from PySide6.QtCore import QDate


class RegistroPacientesDialog(QDialog):
    def __init__(self, pacientes_repo, catalogos_repo, rol_usuario):
        super().__init__()

        self.pacientes_repo = pacientes_repo
        self.catalogos_repo = catalogos_repo
        self.rol_usuario = rol_usuario

        self.paciente_actual_id = None

        self.setWindowTitle("Registro de Pacientes")
        self.resize(900, 500)

        self.build_ui()
        self.cargar_catalogos()
        self.center()

    # ---------------- UI ----------------
    def build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # FECHA
        self.txt_fecha = QLineEdit()
        self.txt_fecha.setText(QDate.currentDate().toString("dd/MM/yyyy"))
        self.txt_fecha.setReadOnly(True)
        form.addRow("Fecha Registro:", self.txt_fecha)

        # APELLIDOS / NOMBRES
        self.txt_apellidos = QLineEdit()
        self.txt_nombres = QLineEdit()

        form.addRow("Apellidos:", self.txt_apellidos)
        form.addRow("Nombres:", self.txt_nombres)

        # CEDULA
        self.cbo_nac = QComboBox()
        self.cbo_nac.addItems(["V", "E", "J"])
        self.txt_cedula = QLineEdit()

        cedula_layout = QHBoxLayout()
        cedula_layout.addWidget(self.cbo_nac)
        cedula_layout.addWidget(self.txt_cedula)

        form.addRow("Cédula:", cedula_layout)

        # NACIMIENTO
        self.date_nac = QDateEdit()
        self.date_nac.setCalendarPopup(True)
        self.date_nac.setDate(QDate(2000, 1, 1))
        form.addRow("Fecha Nac:", self.date_nac)

        # LUGAR / SEXO
        self.cbo_lugar = QComboBox()
        self.cbo_sexo = QComboBox()
        self.cbo_sexo.addItems(["Masculino", "Femenino"])

        form.addRow("Lugar Nac:", self.cbo_lugar)
        form.addRow("Sexo:", self.cbo_sexo)

        # UBICACION
        self.cbo_muni = QComboBox()
        self.cbo_parro = QComboBox()
        self.cbo_comu = QComboBox()

        form.addRow("Municipio:", self.cbo_muni)
        form.addRow("Parroquia:", self.cbo_parro)
        form.addRow("Comunidad:", self.cbo_comu)

        # DIRECCION
        self.txt_direccion = QTextEdit()
        self.txt_direccion.setFixedHeight(60)
        form.addRow("Dirección:", self.txt_direccion)

        # CONTACTO
        self.txt_tel = QLineEdit()

        self.cbo_condicion = QComboBox()
        self.cbo_condicion.addItems(["Estable", "Grave", "Observación"])

        self.cbo_consulta = QComboBox()

        form.addRow("Teléfono:", self.txt_tel)
        form.addRow("Condición:", self.cbo_condicion)
        form.addRow("Consulta:", self.cbo_consulta)

        layout.addLayout(form)

        # BOTONES
        btn_layout = QHBoxLayout()

        self.btn_buscar = QPushButton("Buscar")
        self.btn_guardar = QPushButton("Guardar")
        self.btn_modificar = QPushButton("Modificar")
        self.btn_eliminar = QPushButton("Eliminar")

        self.btn_buscar.clicked.connect(self.buscar)
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_eliminar.clicked.connect(self.eliminar)

        btn_layout.addWidget(self.btn_buscar)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_modificar)
        btn_layout.addWidget(self.btn_eliminar)

        layout.addLayout(btn_layout)

        # permisos
        if self.rol_usuario != "ADMIN":
            self.btn_modificar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)

        # DARK MODE
        self.setStyleSheet("""
        QDialog {
            background-color: #0f172a;
            color: white;
            font-family: Segoe UI;
        }

        QLabel {
            color: #e5e7eb;
        }

        QLineEdit, QTextEdit, QDateEdit, QComboBox {
            background-color: #1f2937;
            color: white;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px;
        }

        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
            border: 1px solid #3b82f6;
        }

        QPushButton {
            background-color: #2563eb;
            color: white;
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1d4ed8;
        }

        QPushButton:disabled {
            background-color: #374151;
            color: #9ca3af;
        }
        """)

    # ---------------- CATALOGOS ----------------
    def cargar_catalogos(self):
        self.cbo_lugar.addItems(self.catalogos_repo.obtener_estados())
        self.cbo_consulta.addItems(self.catalogos_repo.obtener_consultas())

        municipios = self.catalogos_repo.obtener_municipios()
        self.munis_dict = {m[0]: m[1] for m in municipios}
        self.cbo_muni.addItems(self.munis_dict.keys())

    # ---------------- CRUD ----------------
    def guardar(self):
        try:
            cedula = f"{self.cbo_nac.currentText()}-{self.txt_cedula.text()}"

            if self.pacientes_repo.existe_cedula(cedula):
                QMessageBox.warning(self, "Duplicado", "Ya existe la cédula")
                return

            valores = (
                self.txt_apellidos.text(),
                self.txt_nombres.text(),
                cedula,
                self.date_nac.date().toString("yyyy-MM-dd"),
                self.cbo_lugar.currentText(),
                self.cbo_sexo.currentText(),
                self.cbo_muni.currentText(),
                self.cbo_parro.currentText(),
                self.cbo_comu.currentText(),
                self.txt_direccion.toPlainText(),
                self.cbo_condicion.currentText(),
                self.txt_tel.text(),
                self.cbo_consulta.currentText(),
                QDate.currentDate().toString("yyyy-MM-dd")
            )

            self.pacientes_repo.insertar(valores)

            QMessageBox.information(self, "OK", "Paciente guardado")
            self.limpiar()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def buscar(self):
        cedula, ok = QInputDialog.getText(self, "Buscar", "Cédula:")
        if not ok or not cedula:
            return

        paciente = self.pacientes_repo.buscar_por_cedula(cedula)

        if not paciente:
            QMessageBox.warning(self, "Error", "No encontrado")
            return

        self.paciente_actual_id = paciente["id"]

        self.txt_apellidos.setText(paciente["apellidos"] or "")
        self.txt_nombres.setText(paciente["nombres"] or "")
        self.txt_tel.setText(paciente["telefono"] or "")
        self.txt_direccion.setPlainText(paciente["direccion"] or "")

        ced = paciente["cedula"].split("-")
        self.cbo_nac.setCurrentText(ced[0])
        self.txt_cedula.setText(ced[1])

        QMessageBox.information(self, "OK", "Paciente cargado")

    def modificar(self):
        if self.rol_usuario != "ADMIN":
            return

        if not self.paciente_actual_id:
            QMessageBox.warning(self, "Error", "Seleccione un paciente")
            return

        cedula = f"{self.cbo_nac.currentText()}-{self.txt_cedula.text()}"

        valores = (
            self.txt_apellidos.text(),
            self.txt_nombres.text(),
            cedula,
            self.date_nac.date().toString("yyyy-MM-dd"),
            self.cbo_lugar.currentText(),
            self.cbo_sexo.currentText(),
            self.cbo_muni.currentText(),
            self.cbo_parro.currentText(),
            self.cbo_comu.currentText(),
            self.txt_direccion.toPlainText(),
            self.cbo_condicion.currentText(),
            self.txt_tel.text(),
            self.cbo_consulta.currentText(),
            QDate.currentDate().toString("yyyy-MM-dd")
        )

        self.pacientes_repo.actualizar(self.paciente_actual_id, valores)

        QMessageBox.information(self, "OK", "Paciente actualizado")

    def eliminar(self):
        if self.rol_usuario != "ADMIN":
            return

        if not self.paciente_actual_id:
            QMessageBox.warning(self, "Error", "No hay paciente cargado")
            return

        self.pacientes_repo.eliminar(self.paciente_actual_id)

        QMessageBox.information(self, "OK", "Paciente eliminado")
        self.limpiar()

    # ---------------- UTIL ----------------
    def limpiar(self):
        self.paciente_actual_id = None
        self.txt_apellidos.clear()
        self.txt_nombres.clear()
        self.txt_cedula.clear()
        self.txt_tel.clear()
        self.txt_direccion.clear()

    def center(self):
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )