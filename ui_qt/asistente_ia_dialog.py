import json
import ssl
import urllib.request
import urllib.error
from groq import Groq
from PySide6.QtCore import QObject, Signal

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton,
    QScrollArea, QWidget, QLabel
)
from PySide6.QtCore import Qt, Signal, QObject, QThread


# =========================
# WORKER (HILO SEGURO)
# =========================
class IAWorker(QObject):

    respuesta_lista = Signal(str)
    finished = Signal()

    def __init__(self, pregunta):
        super().__init__()
        self.pregunta = pregunta

    def run(self):
        
        try:
            #API DE IA

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente médico profesional. Responde claro y ético."
                    },
                    {
                        "role": "user",
                        "content": self.pregunta
                    }
                ],
                temperature=0.7,
                max_tokens=512
            )

            texto = completion.choices[0].message.content

        except Exception as e:
            texto = f"Error IA: {str(e)}"

        self.respuesta_lista.emit(texto)
        self.finished.emit()


# =========================
# DIALOG
# =========================
class AsistenteIADialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asistente Médico IA (Groq)")
        self.resize(700, 600)

        self.center()
        self.build_ui()

        self.add_message(
            "IA",
            "Hola 👋 Soy tu asistente médico conectado a Groq. ¿En qué puedo ayudarte?"
        )

        self.thread = None
        self.worker = None

    # ================= UI =================

    def build_ui(self):

        main = QVBoxLayout(self)

        self.chat_area = QVBoxLayout()

        self.chat_container = QWidget()
        self.chat_container.setLayout(self.chat_area)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.chat_container)

        main.addWidget(self.scroll)

        bottom = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Escribe tu consulta...")
        self.input.returnPressed.connect(self.enviar)

        self.btn = QPushButton("Enviar")
        self.btn.clicked.connect(self.enviar)

        bottom.addWidget(self.input)
        bottom.addWidget(self.btn)

        main.addLayout(bottom)

        self.setStyleSheet("""
        QDialog{ background:#0f172a; }

        QLineEdit{
            background:#1f2937;
            color:white;
            border:1px solid #334155;
            border-radius:8px;
            padding:8px;
        }

        QPushButton{
            background:#2563eb;
            color:white;
            padding:8px;
            border-radius:8px;
            font-weight:bold;
        }

        QPushButton:hover{
            background:#1d4ed8;
        }
        """)

    # ================= CHAT =================

    def add_message(self, role, text):

        label = QLabel()

        if role == "USER":
            label.setText(f"🧑 Tú:\n{text}")
            label.setAlignment(Qt.AlignRight)
            label.setStyleSheet("""
                background:#1e293b;
                color:white;
                padding:10px;
                border-radius:10px;
                margin:5px;
            """)
        else:
            label.setText(f"🤖 IA:\n{text}")
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet("""
                background:#111827;
                color:#e5e7eb;
                padding:10px;
                border-radius:10px;
                margin:5px;
            """)

        self.chat_area.addWidget(label)

        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

    # ================= ENVIAR =================

    def enviar(self):

        pregunta = self.input.text().strip()
        if not pregunta:
            return

        self.add_message("USER", pregunta)
        self.input.clear()

        self.btn.setEnabled(False)
        self.btn.setText("Pensando...")

        # THREAD
        self.thread = QThread()
        self.worker = IAWorker(pregunta)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.respuesta_lista.connect(self.mostrar_respuesta)
        self.worker.finished.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    # ================= RESPUESTA UI (SEGURO) =================

    def mostrar_respuesta(self, texto):

        self.add_message("IA", texto)

        self.btn.setEnabled(True)
        self.btn.setText("Enviar")

    # ================= CENTRAR =================

    def center(self):

        screen = self.screen().geometry()

        self.move(
            (screen.width()-self.width())//2,
            (screen.height()-self.height())//2
        )