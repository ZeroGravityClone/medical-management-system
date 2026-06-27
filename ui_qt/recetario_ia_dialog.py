# ui_qt/recetario_ia_dialog.py

import os
import platform
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox, QLineEdit, QFrame
)
from PySide6.QtCore import QThread, Qt

from services.recetario_worker import RecetarioIAWorker
from services.document_service import DocumentService


class RecetarioIADialog(QDialog):
    def __init__(self, parent=None, pacientes_repo=None):
        super().__init__(parent)

        self.pacientes_repo = pacientes_repo
        self.doc_service = DocumentService(self.pacientes_repo)

        self.setWindowTitle("Generador Inteligente de Recetarios IA")
        self.resize(700, 520)

        self.center()
        self.build_ui()

    # ================= INTERFAZ VISUAL MOONLIGHT =================
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Cabecera
        titulo = QLabel("Generador de Recetas e Indicaciones IA")
        titulo.setObjectName("DialogTitle")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #52a9ff;")
        layout.addWidget(titulo)

        # --- PANEL DE DATOS DEL PACIENTE ---
        card_paciente = QFrame()
        card_paciente.setObjectName("CardContainer")
        layout_card = QHBoxLayout(card_paciente)
        layout_card.setContentsMargins(12, 12, 12, 12)
        layout_card.setSpacing(10)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre del Paciente (Opcional)")
        
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Cédula de Identidad (Opcional)")

        layout_card.addWidget(QLabel("Paciente:"))
        layout_card.addWidget(self.txt_nombre)
        layout_card.addWidget(QLabel("Cédula:"))
        layout_card.addWidget(self.txt_cedula)
        layout.addWidget(card_paciente)

        # --- TEXTAREA DE INDICACIONES ---
        layout.addWidget(QLabel("Escriba las indicaciones médicas o un comando rápido de simulación:"))
        
        self.txt_notas = QTextEdit()
        self.txt_notas.setPlaceholderText(
            "Escriba las indicaciones del tratamiento...\n\n"
            "💡 TIP DE DEFENSA - Comandos rápidos de simulación:\n"
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
        self.btn_generar.clicked.connect(self.procesar_receta)

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_generar)

        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #111218;
            }

            QFrame#CardContainer {
                background-color: #181a23;
                border: 1px solid #2f3352;
                border-radius: 8px;
            }

            QLabel {
                color: #8a8fbc;
                font-weight: bold;
            }

            QLineEdit, QTextEdit {
                background-color: #1e202f;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                border-radius: 6px;
                padding: 8px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border-color: #7078f4;
            }

            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 20px;
                min-width: 120px;
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

    # ================= CONTROLADOR ASÍNCRONO =================
    def procesar_receta(self):
        notas = self.txt_notas.toPlainText().strip()
        if not notas:
            QMessageBox.warning(self, "Atención", "El cuadro de indicaciones está vacío.")
            return

        self.btn_generar.setEnabled(False)
        self.btn_generar.setText("Analizando dosis...")
        self.btn_cancelar.setEnabled(False)

        nombre = self.txt_nombre.text().strip()
        cedula = self.txt_cedula.text().strip()

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
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
