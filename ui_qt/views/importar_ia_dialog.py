# ui_qt/views/importar_ia_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import QThread, Qt

from services.ai_parser_service import AIPatientParserWorker


class ImportarIADialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Asistente de Registro Inteligente IA")
        self.resize(600, 400)

        self.datos_extraidos = None

        self.center()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

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

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("BtnSecondary")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_analizar = QPushButton("Analizar con IA")
        self.btn_analizar.setObjectName("BtnPrimary")
        self.btn_analizar.clicked.connect(self.iniciar_analisis)

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_analizar)

        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #111218;
            }

            QLabel {
                color: #8a8fbc;
                font-size: 12px;
                font-weight: bold;
            }

            QTextEdit {
                background-color: #1e202f;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }

            QTextEdit:focus {
                border: 1px solid #7078f4;
            }

            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 18px;
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
            }
        """)

    def iniciar_analisis(self):
        texto = self.txt_notas.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Atención", "El cuadro de texto está vacío.")
            return

        self.btn_analizar.setEnabled(False)
        self.btn_analizar.setText("Procesando...")
        self.btn_cancelar.setEnabled(False)

        self.thread = QThread()
        self.worker = AIPatientParserWorker(texto)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.datos_parseados.connect(self.on_parseo_exitoso)
        self.worker.error_ocurrido.connect(self.on_parseo_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_parseo_exitoso(self, datos):
        self.datos_extraidos = datos
        self.accept()

    def on_parseo_error(self, mensaje_error):
        QMessageBox.critical(
            self, 
            "Error de Análisis", 
            f"El asistente de IA no pudo procesar la solicitud:\n\n{mensaje_error}"
        )
        self.btn_analizar.setEnabled(True)
        self.btn_analizar.setText("Analizar con IA")
        self.btn_cancelar.setEnabled(True)

    def center(self):
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
