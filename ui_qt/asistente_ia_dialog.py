# ui_qt/asistente_ia_dialog.py

import os
import httpx 
from dotenv import load_dotenv
from groq import Groq

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea, 
    QWidget, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject, QThread

# Cargar variables de entorno del archivo .env
load_dotenv()


# =========================
# WORKER (HILO SEGURO)
# =========================
class IAWorker(QObject):
    respuesta_lista = Signal(str)
    error_ocurrido = Signal(str)
    finished = Signal()

    def __init__(self, pregunta):
        super().__init__()
        self.pregunta = pregunta

    def run(self):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("No se encontró la clave de API (GROQ_API_KEY) en el entorno.")

            # Configuración de proxy
            proxy_url = os.getenv("PROXY_URL")
            if proxy_url:
                h_client = None
                try:
                    
                    h_client = httpx.Client(proxy=proxy_url)
                except TypeError:
                    try:
                        
                        h_client = httpx.Client(proxies=proxy_url)
                    except TypeError:
                        
                        os.environ["HTTP_PROXY"] = proxy_url
                        os.environ["HTTPS_PROXY"] = proxy_url
                        os.environ["ALL_PROXY"] = proxy_url
                        h_client = httpx.Client()
                
                client = Groq(api_key=api_key, http_client=h_client)
            else:
                client = Groq(api_key=api_key)

            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente médico profesional para un sistema de gestión. Responde claro, formal y ético."
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
            "Hola 👋 Soy tu asistente médico conectado a Groq de forma segura. ¿En qué puedo ayudarte?"
        )

        self.thread = None
        self.worker = None

    # ================= UI =================
    def build_ui(self):
        main = QVBoxLayout(self)

        self.chat_area = QVBoxLayout()
        self.chat_area.setAlignment(Qt.AlignTop) 

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
        QDialog { 
            background: #111218; 
        }

        QScrollArea {
            border: 1px solid #2f3352;
            border-radius: 8px;
            background: #181a23;
        }

        QWidget#chat_container {
            background: #181a23;
        }

        QLineEdit {
            background: #1e202f;
            color: #e2e4f0;
            border: 1px solid #2f3352;
            border-radius: 8px;
            padding: 10px;
        }

        QLineEdit:focus {
            border: 1px solid #7078f4;
        }

        QPushButton {
            background: #7078f4;
            color: #111218;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: bold;
        }

        QPushButton:hover {
            background: #5c63db;
        }
        
        QPushButton:disabled {
            background: #2f3352;
            color: #8a8fbc;
        }
        """)

    # ================= CHAT =================
    def add_message(self, role, text):
        label = QLabel()
        label.setWordWrap(True) 

        if role == "USER":
            label.setText(f"🧑 **Tú**:\n{text}")
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet("""
                background-color: #212433;
                color: #e2e4f0;
                padding: 12px;
                border-radius: 10px;
                margin: 5px 50px 5px 5px;
                border: 1px solid #2f3352;
            """)
        else:
            label.setText(f"🤖 **IA**:\n{text}")
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet("""
                background-color: #111218;
                color: #e2e4f0;
                padding: 12px;
                border-radius: 10px;
                margin: 5px 5px 5px 50px;
                border: 1px solid #3e4491;
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

        self.thread = QThread()
        self.worker = IAWorker(pregunta)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.respuesta_lista.connect(self.mostrar_respuesta)
        self.worker.error_ocurrido.connect(self.on_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def mostrar_respuesta(self, texto):
        self.add_message("IA", texto)
        self.btn.setEnabled(True)
        self.btn.setText("Enviar")

    def on_error(self, error_msg):
        QMessageBox.critical(self, "Error de IA", f"No se pudo procesar la solicitud:\n\n{error_msg}")
        self.btn.setEnabled(True)
        self.btn.setText("Enviar")

    def center(self):
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
