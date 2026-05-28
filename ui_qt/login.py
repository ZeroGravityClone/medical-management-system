import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QMessageBox, QApplication
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from repositories.usuarios_repository import UsuariosRepository
from db.init_db import RUTA_DB

import ctypes
from PySide6.QtWidgets import QWidget


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema Médico - Acceso")
        self.resize(450, 600)
        self.setFixedSize(450, 600)

        # repo
        self.usuarios_repo = UsuariosRepository(RUTA_DB)

        # estado
        self.login_exitoso = False
        self.usuario_validado = ""
        self.rol_validado = ""

        # 🔥 MODO OSCURO GLOBAL
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: white;
                font-family: Segoe UI;
            }

            QFrame {
                background-color: #111827;
                border-radius: 15px;
                border: 1px solid #334155;
            }

            QLineEdit {
                background-color: #1f2937;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }

            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }

            QPushButton {
                background-color: #2563eb;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QLabel {
                color: #e5e7eb;
            }
        """)

        # layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # CONTENEDOR
        self.container = QFrame()
        self.layout_container = QVBoxLayout(self.container)
        self.layout_container.setSpacing(15)

        self.main_layout.addWidget(self.container)

        # ================= HEADER =================
        self.title = QLabel("GESTIÓN MÉDICA")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.layout_container.addWidget(self.title)

        self.subtitle = QLabel("Acceso al sistema")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.layout_container.addWidget(self.subtitle)

        # ================= USUARIO =================
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.layout_container.addWidget(self.txt_usuario)

        # ================= PASSWORD =================
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.layout_container.addWidget(self.txt_password)

        # ================= BOTÓN =================
        self.btn_login = QPushButton("INICIAR SESIÓN")
        self.btn_login.clicked.connect(self.validar_acceso)
        self.layout_container.addWidget(self.btn_login)

        # Enter login
        self.txt_password.returnPressed.connect(self.validar_acceso)

        # centrar ventana
        self.center()

    def showEvent(self, event):
        super().showEvent(event)
        self.set_dark_title_bar()    

    def set_dark_title_bar(self):
        hwnd = int(self.winId())
        value = ctypes.c_int(1)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            20,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )

    # ---------------- LOGIN ----------------
    def validar_acceso(self):
        user = self.txt_usuario.text().upper()
        password = self.txt_password.text()

        try:
            data = self.usuarios_repo.login(user, password)

            if not data:
                QMessageBox.warning(self, "Error", "Usuario o clave incorrectos")
                return

            if data["acceso"] == "DENEGADO":
                QMessageBox.critical(self, "Acceso", "Usuario sin permisos")
                return

            self.login_exitoso = True
            self.usuario_validado = data["usuario"]
            self.rol_validado = data["rol"]

            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------------- CENTRAR ----------------
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)