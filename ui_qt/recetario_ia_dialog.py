# ui_qt/recetario_ia_dialog.py

import os
import platform
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox, QLineEdit, QFrame,
    QCompleter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import QThread, Qt

from services.recetario_worker import RecetarioIAWorker
from services.document_service import DocumentService


# =========================================================================
# DIÁLOGO DE BÚSQUEDA HISTÓRICA DE RECETAS
# =========================================================================
class HistorialRecetasDialog(QDialog):
    def __init__(self, parent=None, pacientes_repo=None):
        super().__init__(parent)
        self.pacientes_repo = pacientes_repo
        
        self.setWindowTitle("Historial de Recetas Emitidas")
        self.resize(650, 400)
        self.center()
        self.build_ui()
        self.cargar_completer()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Buscador Unificado
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.txt_buscar_paciente = QLineEdit()
        self.txt_buscar_paciente.setPlaceholderText("Buscar paciente por nombre o cédula para su historial...")
        
        self.btn_buscar = QPushButton("Buscar Historial")
        self.btn_buscar.setObjectName("BtnPrimary")
        self.btn_buscar.clicked.connect(self.buscar_historial)

        search_layout.addWidget(self.txt_buscar_paciente)
        search_layout.addWidget(self.btn_buscar)
        layout.addLayout(search_layout)

        # Tabla de Recetas
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Fecha Emisión", "Nombre del Archivo PDF"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.tabla.doubleClicked.connect(self.abrir_receta_seleccionada)
        layout.addWidget(self.tabla)

        # Botón cerrar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("BtnSecondary")
        btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)

        self.txt_buscar_paciente.returnPressed.connect(self.buscar_historial)

        self.setStyleSheet("""
            QDialog { background-color: #111218; }
            QLabel { color: #8a8fbc; font-weight: bold; }
            QLineEdit { background-color: #1e202f; color: #e2e4f0; border: 1px solid #2f3352; border-radius: 6px; padding: 6px; }
            QTableWidget { background-color: #141622; alternate-background-color: #1a1c2e; color: #e2e4f0; border: 1px solid #2f3352; gridline-color: #1e202f; border-radius: 6px; }
            QHeaderView::section { background-color: #111218; color: #8a8fbc; padding: 8px; border: none; border-bottom: 1px solid #2f3352; border-right: 1px solid #2f3352; font-weight: bold; }
            QTableWidget::item:selected { background-color: #2e355c; color: #ffffff; }
            QPushButton { font-weight: bold; border-radius: 6px; padding: 8px 16px; }
            QPushButton#BtnPrimary { background-color: #7078f4; color: #111218; border: 1px solid #7078f4; }
            QPushButton#BtnSecondary { background-color: #1d2035; color: #cbd5e1; border: 1px solid #2d3154; }
            QPushButton#BtnSecondary:hover { background-color: #262b49; border-color: #409eff; }
        """)

    def cargar_completer(self):
        # Completer inteligente con MatchContains
        lista = self.pacientes_repo.obtener_lista_autocompletado()
        self.completer = QCompleter(lista, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.txt_buscar_paciente.setCompleter(self.completer)

    def buscar_historial(self):
        texto = self.txt_buscar_paciente.text().strip()
        if not texto:
            return

        # Extraer la cédula si se usó el autocompletado
        cedula = texto
        if "(" in texto and ")" in texto:
            cedula = texto.split("(")[-1].split(")")[0]

        paciente = self.pacientes_repo.buscar_por_cedula(cedula)
        if not paciente:
            QMessageBox.warning(self, "Aviso", f"El paciente no está registrado en el sistema.")
            return

        self.recetas_filtradas = self.pacientes_repo.obtener_recetas_por_paciente(paciente["id"])
        self.tabla.setRowCount(len(self.recetas_filtradas))

        if len(self.recetas_filtradas) == 0:
            QMessageBox.information(self, "Información", f"El paciente {paciente['nombres']} {paciente['apellidos']} no tiene recetas emitidas aún.")
            return

        for fila, receta in enumerate(self.recetas_filtradas):
            item_fecha = QTableWidgetItem(receta["fecha_creacion"])
            item_fecha.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, 0, item_fecha)

            item_archivo = QTableWidgetItem(receta["nombre_archivo"])
            item_archivo.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, 1, item_archivo)

    def abrir_receta_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return

        ruta = self.recetas_filtradas[fila]["ruta_archivo"]
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo PDF:\n{str(e)}")

    def center(self):
        screen = self.screen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)


# =========================================================================
# DIÁLOGO PRINCIPAL DEL RECETARIO MÉDICO IA
# =========================================================================
class RecetarioIADialog(QDialog):
    def __init__(self, parent=None, pacientes_repo=None):
        super().__init__(parent)

        self.pacientes_repo = pacientes_repo
        self.doc_service = DocumentService(self.pacientes_repo)

        self.setWindowTitle("Generador Inteligente de Recetarios IA")
        self.resize(700, 520)

        self.center()
        self.build_ui()
        self.cargar_completer_pacientes()

    # ================= INTERFAZ VISUAL MOONLIGHT =================
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Cabecera
        header_layout = QHBoxLayout()
        titulo = QLabel("Generador de Recetas e Indicaciones IA")
        titulo.setObjectName("DialogTitle")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #52a9ff;")
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        self.btn_historial = QPushButton("🔍 Ver Historial")
        self.btn_historial.setObjectName("BtnSecondary")
        self.btn_historial.clicked.connect(self.abrir_historial_recetas)
        header_layout.addWidget(self.btn_historial)
        layout.addLayout(header_layout)

        # --- BUSCADOR INTELIGENTE UNIFICADO ---
        layout.addWidget(QLabel("Búsqueda Rápida de Paciente por Nombre o Cédula:"))
        self.txt_buscar_paciente = QLineEdit()
        self.txt_buscar_paciente.setPlaceholderText("Escriba para buscar... (Ej: Juan Perez o 12345678)")
        layout.addWidget(self.txt_buscar_paciente)

        # --- PANEL DE DATOS DE LECTURA (Binds automáticos) ---
        card_paciente = QFrame()
        card_paciente.setObjectName("CardContainer")
        layout_card = QHBoxLayout(card_paciente)
        layout_card.setContentsMargins(12, 12, 12, 12)
        layout_card.setSpacing(10)

        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Cédula (Carga automática)")
        self.txt_cedula.setReadOnly(True)
        self.txt_cedula.setObjectName("ReadOnlyInput")
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre Completo (Carga automática)")
        self.txt_nombre.setReadOnly(True)
        self.txt_nombre.setObjectName("ReadOnlyInput")

        layout_card.addWidget(QLabel("Cédula:"))
        layout_card.addWidget(self.txt_cedula)
        layout_card.addWidget(QLabel("Paciente:"))
        layout_card.addWidget(self.txt_nombre)
        layout.addWidget(card_paciente)

        # --- TEXTAREA DE INDICACIONES ---
        layout.addWidget(QLabel("Escriba las indicaciones médicas o un comando rápido de simulación:"))
        
        self.txt_notas = QTextEdit()
        self.txt_notas.setPlaceholderText(
            "Escriba las indicaciones del tratamiento...\n\n"
            "💡 Tips de comandos rápidos de simulación:\n"
            "• 'inventa una receta'\n"
            "• 'genera una receta de prueba para amigdalitis'\n"
            "• 'crea una receta aleatoria para hipertensión'"
        )
        layout.addWidget(self.txt_notas)

        # --- CONTROL DE BOTONES ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancelar = QPushButton("Cerrar")
        self.btn_cancelar.setObjectName("BtnSecondary")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_generar = QPushButton("✨ Generar Receta PDF")
        self.btn_generar.setObjectName("BtnPrimary")
        self.btn_generar.setEnabled(False) # Bloqueado por seguridad hasta validar paciente
        self.btn_generar.clicked.connect(self.procesar_receta)

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_generar)

        layout.addLayout(btn_layout)

        # Conexiones reactivas
        self.txt_buscar_paciente.textChanged.connect(self.on_busqueda_paciente_changed)
        self.txt_notas.textChanged.connect(self.validar_requisitos_generacion)

        self.setStyleSheet("""
            QDialog { background-color: #111218; }
            QFrame#CardContainer { background-color: #181a23; border: 1px solid #2f3352; border-radius: 8px; }
            QLabel { color: #8a8fbc; font-weight: bold; }
            QLineEdit, QTextEdit { background-color: #1e202f; color: #e2e4f0; border: 1px solid #2f3352; border-radius: 6px; padding: 8px; }
            QLineEdit:focus, QTextEdit:focus { border-color: #7078f4; }
            QLineEdit#ReadOnlyInput { background-color: #141622; color: #64748b; border: 1px solid #1e202f; }
            QPushButton { font-weight: bold; border-radius: 6px; padding: 10px 20px; min-width: 120px; }
            QPushButton#BtnPrimary { background-color: #7078f4; color: #111218; border: 1px solid #7078f4; }
            QPushButton#BtnPrimary:hover { background-color: #5c63db; }
            QPushButton#BtnPrimary:disabled { background-color: #141622; color: #475569; border: 1px solid #1e202f; }
            QPushButton#BtnSecondary { background-color: #1d2035; color: #cbd5e1; border: 1px solid #2d3154; }
            QPushButton#BtnSecondary:hover { background-color: #262b49; border-color: #409eff; }
        """)

    # ================= CONTEXTO Y COMPLETER INTERACTIVO =================
    def cargar_completer_pacientes(self):
        """Carga la lista unificada en el Completer con MatchContains."""
        lista_pacientes = self.pacientes_repo.obtener_lista_autocompletado()
        self.completer = QCompleter(lista_pacientes, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.txt_buscar_paciente.setCompleter(self.completer)

    def on_busqueda_paciente_changed(self, text):
        """Reactivo: al cambiar el texto de búsqueda, extrae la cédula y rellena los campos."""
        texto = text.strip()
        cedula = texto

        if "(" in texto and ")" in texto:
            cedula = texto.split("(")[-1].split(")")[0]

        # Consultar si existe en la base de datos de manera tolerante al guion
        paciente = self.pacientes_repo.buscar_por_cedula(cedula)
        if paciente:
            self.txt_cedula.setText(paciente["cedula"])
            self.txt_nombre.setText(f"{paciente['nombres']} {paciente['apellidos']}")
        else:
            self.txt_cedula.clear()
            self.txt_nombre.clear()

        self.validar_requisitos_generacion()

    def validar_requisitos_generacion(self):
        """Valida que la receta esté asociada a un paciente real o sea simulación."""
        notas = self.txt_notas.toPlainText().strip().lower()
        cedula_activa = self.txt_cedula.text().strip()

        # Permitir simulación académica
        es_simulacion = any(x in notas for x in ["inventa", "aleatoria", "prueba", "test"])
        if es_simulacion and len(notas) > 3:
            self.btn_generar.setEnabled(True)
            return

        # Requiere existencia de cédula activa y notas para habilitar
        if self.pacientes_repo.existe_cedula(cedula_activa) and len(notas) > 5:
            self.btn_generar.setEnabled(True)
        else:
            self.btn_generar.setEnabled(False)

    # ================= CONTROLADOR ASÍNCRONO =================
    def procesar_receta(self):
        notas = self.txt_notas.toPlainText().strip()
        nombre = self.txt_nombre.text().strip()
        cedula = self.txt_cedula.text().strip()

        self.btn_generar.setEnabled(False)
        self.btn_generar.setText("Analizando...")
        self.btn_cancelar.setEnabled(False)

        self.thread = QThread()
        self.worker = RecetarioIAWorker(notas, nombre, cedula)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.receta_lista.connect(self.compilar_pdf)
        self.worker.error_ocurrido.connect(self.on_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def compilar_pdf(self, receta_json):
        try:
            # Invocar al Orquestador Único de Documentos
            ruta_pdf = self.doc_service.registrar_receta_medica(receta_json)
            
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Receta generada y registrada con éxito.\n\nEl archivo se abrirá automáticamente."
            )
            self.abrir_archivo_pdf(ruta_pdf)
            
        except Exception as e:
            QMessageBox.critical(self, "Error PDF", f"No se pudo compilar o asentar el recetario:\n{str(e)}")
            
        finally:
            self.btn_generar.setEnabled(True)
            self.btn_generar.setText("✨ Generar Receta PDF")
            self.btn_cancelar.setEnabled(True)

    def on_error(self, error_msg):
        QMessageBox.critical(self, "Error de IA", f"No se pudo procesar la receta médica:\n\n{error_msg}")
        self.btn_generar.setEnabled(True)
        self.btn_generar.setText("✨ Generar Receta PDF")
        self.btn_cancelar.setEnabled(True)

    def abrir_historial_recetas(self):
        dialog = HistorialRecetasDialog(self, self.pacientes_repo)
        dialog.exec()

    def abrir_archivo_pdf(self, ruta):
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
        except Exception as e:
            print(f"No se pudo abrir el visor de PDF: {e}")

    def center(self):
        screen = self.screen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
