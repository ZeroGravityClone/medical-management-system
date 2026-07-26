# ui_qt/views/registro_pacientes.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QHBoxLayout,
    QMessageBox, QDateEdit, QInputDialog, QFrame, QLabel, QWidget
)
from PySide6.QtCore import QDate, Qt

from services.document_service import DocumentService


# =========================================================================
# NUEVO: DIÁLOGO DE BÚSQUEDA PERSONALIZADO (Mismo formato que el formulario)
# =========================================================================
class BuscarPacienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Buscar Paciente")
        self.resize(360, 160)
        self.setFixedSize(360, 160) # Tamaño fijo compacto

        self.cedula_resultado = None

        self.center()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Seleccione nacionalidad e ingrese la cédula:"))

        # Fila de Cédula estructurada
        h_layout = QHBoxLayout()
        h_layout.setSpacing(6)

        self.cbo_nac = QComboBox()
        self.cbo_nac.addItems(["V", "E", "J"])
        self.cbo_nac.setFixedWidth(55)

        self.txt_num = QLineEdit()
        self.txt_num.setPlaceholderText("Ej: 12345678")
        # Enfocar campo numérico al abrir
        self.txt_num.setFocus() 

        h_layout.addWidget(self.cbo_nac)
        h_layout.addWidget(self.txt_num)
        layout.addLayout(h_layout)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("BtnSecondary")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setObjectName("BtnPrimary")
        self.btn_buscar.clicked.connect(self.aceptar)

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_buscar)
        layout.addLayout(btn_layout)

        # Trigger al presionar Enter en el teclado
        self.txt_num.returnPressed.connect(self.aceptar)

        # Estilo acoplado a Moonlight
        self.setStyleSheet("""
            QDialog {
                background-color: #111218;
            }

            QLabel {
                color: #8a8fbc;
                font-weight: bold;
            }

            QLineEdit, QComboBox {
                background-color: #1e202f;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                border-radius: 6px;
                padding: 6px;
            }

            QLineEdit:focus, QComboBox:focus {
                border-color: #7078f4;
            }

            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 16px;
            }

            QPushButton#BtnPrimary {
                background-color: #7078f4;
                color: #111218;
                border: 1px solid #7078f4;
            }

            QPushButton#BtnPrimary:hover {
                background-color: #5c63db;
            }

            QPushButton#BtnSecondary {
                background-color: #1d2035;
                color: #cbd5e1;
                border: 1px solid #2d3154;
            }

            QPushButton#BtnSecondary:hover {
                background-color: #262b49;
                border-color: #409eff;
            }
        """)

    def aceptar(self):
        num = self.txt_num.text().strip()
        if not num:
            QMessageBox.warning(self, "Atención", "Debe ingresar el número de cédula.")
            return
        
        nac = self.cbo_nac.currentText()
        # Formatear el resultado como lo espera el repositorio
        self.cedula_resultado = f"{nac}-{num}"
        self.accept()

    def center(self):
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )


# =========================================================================
# CLASE PRINCIPAL DE REGISTRO
# =========================================================================
class RegistroPacientesDialog(QDialog):
    def __init__(self, pacientes_repo, catalogos_repo, rol_usuario):
        super().__init__()

        self.pacientes_repo = pacientes_repo
        self.catalogos_repo = catalogos_repo
        self.rol_usuario = rol_usuario

        # Instanciar el orquestador central de documentos
        self.doc_service = DocumentService(self.pacientes_repo)

        self.paciente_actual_id = None

        self.setWindowTitle("Registro de Pacientes")
        self.resize(920, 560)
        self.setMinimumSize(920, 560)

        self.build_ui()
        self.cargar_catalogos()
        self.center()

    # ---------------- UI REFACTORIZADA ----------------
    def build_ui(self):
        # Layout Principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Contenedor del Formulario (Layout Horizontal para dos columnas)
        form_container_layout = QHBoxLayout()
        form_container_layout.setSpacing(16)

        # =========================================================
        # COLUMNA IZQUIERDA (Datos Personales + Información Médica)
        # =========================================================
        col_izquierda = QVBoxLayout()
        col_izquierda.setSpacing(16)

        # --- CARD 1: DATOS PERSONALES ---
        card_personales = QFrame()
        card_personales.setObjectName("CardForm")
        layout_personales = QVBoxLayout(card_personales)
        layout_personales.setContentsMargins(16, 16, 16, 16)
        layout_personales.setSpacing(10)

        lbl_tit_personales = QLabel("Datos Personales")
        lbl_tit_personales.setObjectName("CardFormTitle")
        layout_personales.addWidget(lbl_tit_personales)

        form_personales = QFormLayout()
        form_personales.setSpacing(8)
        form_personales.setLabelAlignment(Qt.AlignRight)

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Apellidos del paciente")
        self.txt_nombres = QLineEdit()
        self.txt_nombres.setPlaceholderText("Nombres del paciente")

        self.cbo_nac = QComboBox()
        self.cbo_nac.addItems(["V", "E", "J"])
        self.cbo_nac.setFixedWidth(55)
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Número de documento")

        cedula_layout = QHBoxLayout()
        cedula_layout.setSpacing(6)
        cedula_layout.addWidget(self.cbo_nac)
        cedula_layout.addWidget(self.txt_cedula)

        self.date_nac = QDateEdit()
        self.date_nac.setCalendarPopup(True)
        self.date_nac.setDate(QDate(2000, 1, 1))

        self.cbo_sexo = QComboBox()
        self.cbo_sexo.addItems(["Masculino", "Femenino"])

        form_personales.addRow("Apellidos:", self.txt_apellidos)
        form_personales.addRow("Nombres:", self.txt_nombres)
        form_personales.addRow("Cédula:", cedula_layout)
        form_personales.addRow("Fecha Nac:", self.date_nac)
        form_personales.addRow("Sexo:", self.cbo_sexo)

        layout_personales.addLayout(form_personales)
        col_izquierda.addWidget(card_personales)

        # --- CARD 2: INFORMACIÓN MÉDICA ---
        card_medica = QFrame()
        card_medica.setObjectName("CardForm")
        layout_medica = QVBoxLayout(card_medica)
        layout_medica.setContentsMargins(16, 16, 16, 16)
        layout_medica.setSpacing(10)

        lbl_tit_medica = QLabel("Información de Consulta")
        lbl_tit_medica.setObjectName("CardFormTitle")
        layout_medica.addWidget(lbl_tit_medica)

        form_medica = QFormLayout()
        form_medica.setSpacing(8)
        form_medica.setLabelAlignment(Qt.AlignRight)

        self.txt_fecha = QLineEdit()
        self.txt_fecha.setText(QDate.currentDate().toString("dd/MM/yyyy"))
        self.txt_fecha.setReadOnly(True)
        self.txt_fecha.setObjectName("ReadOnlyInput")

        self.cbo_condicion = QComboBox()
        self.cbo_condicion.addItems(["Estable", "Grave", "Observación"])

        self.cbo_consulta = QComboBox()

        form_medica.addRow("Fecha Registro:", self.txt_fecha)
        form_medica.addRow("Condición:", self.cbo_condicion)
        form_medica.addRow("Consulta:", self.cbo_consulta)

        layout_medica.addLayout(form_medica)
        col_izquierda.addWidget(card_medica)

        form_container_layout.addLayout(col_izquierda, stretch=1)

        # =========================================================
        # COLUMNA DERECHA (Contacto, Ubicación y Dirección)
        # =========================================================
        col_derecha = QVBoxLayout()
        col_derecha.setSpacing(16)

        # --- CARD 3: UBICACIÓN Y CONTACTO ---
        card_ubicacion = QFrame()
        card_ubicacion.setObjectName("CardForm")
        layout_ubicacion = QVBoxLayout(card_ubicacion)
        layout_ubicacion.setContentsMargins(16, 16, 16, 16)
        layout_ubicacion.setSpacing(10)

        lbl_tit_ubicacion = QLabel("Ubicación y Contacto")
        lbl_tit_ubicacion.setObjectName("CardFormTitle")
        layout_ubicacion.addWidget(lbl_tit_ubicacion)

        form_ubicacion = QFormLayout()
        form_ubicacion.setSpacing(8)
        form_ubicacion.setLabelAlignment(Qt.AlignRight)

        self.txt_tel = QLineEdit()
        self.txt_tel.setPlaceholderText("Número telefónico")

        self.cbo_lugar = QComboBox()
        self.cbo_muni = QComboBox()
        self.cbo_parro = QComboBox()
        self.cbo_comu = QComboBox()

        self.txt_direccion = QTextEdit()
        self.txt_direccion.setFixedHeight(85)
        self.txt_direccion.setPlaceholderText("Dirección detallada de habitación...")

        form_ubicacion.addRow("Teléfono:", self.txt_tel)
        form_ubicacion.addRow("Estado/Lugar:", self.cbo_lugar)
        form_ubicacion.addRow("Municipio:", self.cbo_muni)
        form_ubicacion.addRow("Parroquia:", self.cbo_parro)
        form_ubicacion.addRow("Comunidad:", self.cbo_comu)
        form_ubicacion.addRow("Dirección:", self.txt_direccion)

        layout_ubicacion.addLayout(form_ubicacion)
        col_derecha.addWidget(card_ubicacion)

        form_container_layout.addLayout(col_derecha, stretch=1)
        main_layout.addLayout(form_container_layout)

        # =========================================================
        # BOTONES DE ACCIÓN (CRUD + AUTOMATIZACIÓN IA)
        # =========================================================
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setObjectName("BtnSecondary")
        
        self.btn_guardar = QPushButton("Guardar Paciente")
        self.btn_guardar.setObjectName("BtnPrimary")
        
        self.btn_modificar = QPushButton("Modificar")
        self.btn_modificar.setObjectName("BtnSecondary")
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setObjectName("BtnDanger")

        self.btn_ia_importar = QPushButton("✨ Llenar con IA")
        self.btn_ia_importar.setObjectName("BtnIA")

        btn_layout.addWidget(self.btn_buscar)
        btn_layout.addWidget(self.btn_ia_importar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_modificar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_guardar)

        main_layout.addLayout(btn_layout)

        # Conexiones
        self.btn_buscar.clicked.connect(self.buscar)
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_ia_importar.clicked.connect(self.importar_ia)

        # Permisos
        if self.rol_usuario != "ADMIN":
            self.btn_modificar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)
            self.btn_ia_importar.setEnabled(False)

        # HOJA DE ESTILOS DEL DIÁLOGO (MOONLIGHT COMPATIBLE)
        self.setStyleSheet("""
            QDialog {
                background-color: #111218;
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

            QLabel#CardFormTitle {
                color: #52a9ff;
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid #2f3352;
                padding-bottom: 6px;
                margin-bottom: 4px;
            }

            QLineEdit, QTextEdit, QDateEdit, QComboBox {
                background-color: #1e202f;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                border-radius: 6px;
                padding: 6px 10px;
            }

            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #7078f4;
                background-color: #212433;
            }

            QLineEdit#ReadOnlyInput {
                background-color: #141622;
                color: #64748b;
                border: 1px solid #1e202f;
            }

            /* Botones CRUD */
            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 100px;
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

            QPushButton#BtnSecondary {
                background-color: #1d2035;
                color: #cbd5e1;
                border: 1px solid #2d3154;
            }

            QPushButton#BtnSecondary:hover {
                background-color: #262b49;
                border-color: #409eff;
                color: #ffffff;
            }

            QPushButton#BtnIA {
                background-color: #121424;
                color: #52a9ff;
                border: 1px solid #2f3352;
            }

            QPushButton#BtnIA:hover {
                background-color: #1a1e36;
                border-color: #52a9ff;
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

            QPushButton:disabled {
                background-color: #141622;
                color: #475569;
                border: 1px solid #1e202f;
            }
        """)

    # ---------------- MÉTODOS: IMPORTADOR IA ----------------
    def importar_ia(self):
        from ui_qt.views.importar_ia_dialog import ImportarIADialog

        dialog = ImportarIADialog(self)
        if dialog.exec() == ImportarIADialog.Accepted:
            datos = dialog.datos_extraidos
            if datos:
                self.autollenar_formulario(datos)

    def autollenar_formulario(self, datos):
        try:
            # 1. Datos Personales
            self.txt_nombres.setText(datos.get("nombres", ""))
            self.txt_apellidos.setText(datos.get("apellidos", ""))
            
            nacionalidad = datos.get("nacionalidad", "V").upper()
            if nacionalidad in ["V", "E", "J"]:
                self.cbo_nac.setCurrentText(nacionalidad)
                
            self.txt_cedula.setText(datos.get("cedula_numero", ""))
            
            # Fecha de nacimiento
            fecha_str = datos.get("fecha_nacimiento", "")
            if fecha_str:
                qdate = QDate.fromString(fecha_str, "yyyy-MM-dd")
                if qdate.isValid():
                    self.date_nac.setDate(qdate)
                    
            self.cbo_sexo.setCurrentText(datos.get("sexo", "Masculino"))
            
            # 2. Contacto y Ubicación
            self.txt_tel.setText(datos.get("telefono", ""))
            
            lugar_nac = datos.get("lugar_nacimiento", "").upper()
            self.cbo_lugar.setCurrentText(lugar_nac)
            
            muni_nombre = datos.get("municipio", "").upper()
            self.cbo_muni.setCurrentText(muni_nombre)
            
            parro_nombre = datos.get("parroquia", "").upper()
            self.cbo_parro.setCurrentText(parro_nombre)
            
            comu_nombre = datos.get("comunidad", "").upper()
            self.cbo_comu.setCurrentText(comu_nombre)
            
            self.txt_direccion.setPlainText(datos.get("direccion", ""))
            
            # 3. Datos Médicos
            condicion = datos.get("condicion", "Estable")
            self.cbo_condicion.setCurrentText(condicion)
            
            self.cbo_consulta.setCurrentText(datos.get("consulta", ""))
            
            QMessageBox.information(
                self, 
                "Asistente IA", 
                "Campos rellenados con éxito.\n\n"
                "Por favor, verifique los datos antes de guardar."
            )
            
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Aviso", 
                f"Ocurrió un detalle al escribir algunos campos:\n{str(e)}"
            )

    # ---------------- CATALOGOS EN CASCADA REACTIVA (4 NIVELES) ----------------
    def cargar_catalogos(self):
        self.cbo_lugar.clear()
        self.cbo_lugar.addItems(self.catalogos_repo.obtener_estados())
        self.cbo_consulta.clear()
        self.cbo_consulta.addItems(self.catalogos_repo.obtener_consultas())

        self.cbo_lugar.currentTextChanged.connect(self.actualizar_municipios)
        self.cbo_muni.currentTextChanged.connect(self.actualizar_parroquias)
        self.cbo_parro.currentTextChanged.connect(self.actualizar_comunidades)

        self.actualizar_municipios(self.cbo_lugar.currentText())

    def actualizar_municipios(self, estado_nombre):
        self.cbo_muni.blockSignals(True)
        self.cbo_parro.blockSignals(True)
        self.cbo_comu.blockSignals(True)

        self.cbo_muni.clear()
        self.cbo_parro.clear()
        self.cbo_comu.clear()

        self.cbo_muni.blockSignals(False)
        self.cbo_parro.blockSignals(False)
        self.cbo_comu.blockSignals(False)

        if not estado_nombre:
            return

        municipios = self.catalogos_repo.obtener_municipios_por_estado(estado_nombre)
        self.munis_dict = {m[0].upper(): m[1] for m in municipios}
        
        self.cbo_muni.addItems(self.munis_dict.keys())
        self.actualizar_parroquias(self.cbo_muni.currentText())

    def actualizar_parroquias(self, nombre_muni):
        self.cbo_parro.blockSignals(True)
        self.cbo_comu.blockSignals(True)

        self.cbo_parro.clear()
        self.cbo_comu.clear()

        self.cbo_parro.blockSignals(False)
        self.cbo_comu.blockSignals(False)

        cod_muni = self.munis_dict.get(nombre_muni.upper())
        if not cod_muni:
            return

        parroquias = self.catalogos_repo.obtener_parroquias_por_municipio(cod_muni)
        self.parros_dict = {p[0].upper(): p[1] for p in parroquias}
        
        self.cbo_parro.addItems(self.parros_dict.keys())
        self.actualizar_comunidades(self.cbo_parro.currentText())

    def actualizar_comunidades(self, nombre_parro):
        self.cbo_comu.clear()

        cod_parro = self.parros_dict.get(nombre_parro.upper())
        if not cod_parro:
            return

        comunidades = self.catalogos_repo.obtener_comunidades_por_parroquia(cod_parro)
        self.cbo_comu.addItems(comunidades)

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

            # 1. Inserción pura en la base de datos SQLite mediante repositorio
            self.pacientes_repo.insertar(valores)

            # 2. Compilar diccionario de datos del paciente
            datos_paciente = {
                "apellidos": self.txt_apellidos.text(),
                "nombres": self.txt_nombres.text(),
                "cedula": cedula,
                "fecha_nac": self.date_nac.date().toString("yyyy-MM-dd"),
                "lugar_nac": self.cbo_lugar.currentText(),
                "sexo": self.cbo_sexo.currentText(),
                "municipio": self.cbo_muni.currentText(),
                "parroquia": self.cbo_parro.currentText(),
                "comunidad": self.cbo_comu.currentText(),
                "direccion": self.txt_direccion.toPlainText(),
                "condicion": self.cbo_condicion.currentText(),
                "telefono": self.txt_tel.text(),
                "consulta": self.cbo_consulta.currentText(),
                "fecha_registro": QDate.currentDate().toString("yyyy-MM-dd")
            }

            # 3. Invocar al Orquestador Central de Documentos de forma segura
            try:
                ruta_pdf = self.doc_service.registrar_planilla_registro(datos_paciente)
                
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"Paciente guardado en base de datos con éxito.\n\n"
                    f"Planilla PDF generada y registrada en:\n{ruta_pdf}"
                )
            except Exception as doc_error:
                QMessageBox.warning(
                    self, 
                    "Aviso", 
                    f"Paciente guardado en la base de datos, pero la planilla PDF no pudo ser orquestada:\n{str(doc_error)}"
                )

            self.limpiar()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === BUSCAR REFACTORIZADO A MODAL PERSONALIZADO ===
    def buscar(self):
        # Lanza el nuevo diálogo de búsqueda estructurado
        dialog = BuscarPacienteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            cedula = dialog.cedula_resultado
            if not cedula:
                return

            paciente = self.pacientes_repo.buscar_por_cedula(cedula)

            if not paciente:
                QMessageBox.warning(self, "Error", f"No se encontró ningún paciente con la cédula: {cedula}")
                return

            self.paciente_actual_id = paciente["id"]

            self.txt_apellidos.setText(paciente["apellidos"] or "")
            self.txt_nombres.setText(paciente["nombres"] or "")
            self.txt_tel.setText(paciente["telefono"] or "")
            self.txt_direccion.setPlainText(paciente["direccion"] or "")

            ced = paciente["cedula"].split("-")
            self.cbo_nac.setCurrentText(ced[0])
            self.txt_cedula.setText(ced[1])

            # Propagar cascada geográfica según los datos cargados del paciente
            self.cbo_lugar.setCurrentText(paciente["lugar_nac"] or "")
            self.cbo_muni.setCurrentText(paciente["municipio"] or "")
            self.cbo_parro.setCurrentText(paciente["parroquia"] or "")
            self.cbo_comu.setCurrentText(paciente["comunidad"] or "")

            self.cbo_condicion.setCurrentText(paciente["condicion"] or "Estable")
            self.cbo_consulta.setCurrentText(paciente["consulta"] or "")

            QMessageBox.information(
                self, 
                "Éxito", 
                f"Paciente {paciente['nombres']} {paciente['apellidos']} cargado con éxito."
            )

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
