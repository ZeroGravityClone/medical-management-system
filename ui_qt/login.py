# ui_qt/login.py

import os
import ctypes
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QMessageBox, QApplication
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from repositories.usuarios_repository import UsuariosRepository
from db.init_db import RUTA_DB


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema Médico - Acceso")
        self.resize(450, 600)
        self.setFixedSize(450, 600)

        # Forzar a Qt a pintar los fondos de la hoja de estilos en este QWidget (Crucial para Linux/Crouton)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Repo de usuarios
        self.usuarios_repo = UsuariosRepository(RUTA_DB)

        # Estado de sesión
        self.login_exitoso = False
        self.usuario_validado = ""
        self.rol_validado = ""

        self.build_ui()
        self.center()

    # ================= UI REFACTORIZADA (MOONLIGHT CARD) =================
    def build_ui(self):
        # Layout Principal de la ventana (Centra la tarjeta)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Centramos todo de manera horizontal y vertical
        main_layout.addStretch()

        h_center_layout = QHBoxLayout()
        h_center_layout.addStretch()

        # --- TARJETA CENTRAL DE LOGIN (Moonlight Card) ---
        self.card_login = QFrame()
        self.card_login.setObjectName("CardLogin")
        self.card_login.setFixedSize(360, 440) # Dimensiones perfectas de escala
        
        # Layout interno de la tarjeta
        layout_card = QVBoxLayout(self.card_login)
        layout_card.setContentsMargins(32, 32, 32, 32) # Padding interno generoso
        layout_card.setSpacing(14)

        # 1. ICONO / LOGO CLÍNICO
        self.lbl_logo_icon = QLabel("🏥")
        self.lbl_logo_icon.setAlignment(Qt.AlignCenter)
        self.lbl_logo_icon.setStyleSheet("font-size: 32px; background: transparent;")
        layout_card.addWidget(self.lbl_logo_icon)

        # 2. TÍTULOS
        self.title = QLabel("GESTIÓN MÉDICA")
        self.title.setObjectName("Title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout_card.addWidget(self.title)

        self.subtitle = QLabel("Acceso al sistema")
        self.subtitle.setObjectName("Subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout_card.addWidget(self.subtitle)

        # Espaciador interno sutil
        layout_card.addSpacing(8)

        # 3. INPUT DE USUARIO
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        layout_card.addWidget(self.txt_usuario)

        # 4. INPUT DE CONTRASEÑA
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)
        layout_card.addWidget(self.txt_password)

        # Espaciador interno antes del botón
        layout_card.addSpacing(6)

        # 5. BOTÓN DE INICIO DE SESIÓN
        self.btn_login = QPushButton("INICIAR SESIÓN")
        self.btn_login.setObjectName("BtnLogin")
        layout_card.addWidget(self.btn_login)

        h_center_layout.addWidget(self.card_login)
        h_center_layout.addStretch()
        
        main_layout.addLayout(h_center_layout)
        main_layout.addStretch()

        # Conexiones de Eventos
        self.btn_login.clicked.connect(self.validar_acceso)
        self.txt_password.returnPressed.connect(self.validar_acceso)

        # HOJA DE ESTILOS UNIFICADA MOONLIGHT
        self.setStyleSheet("""
            QWidget {
                background-color: #111218; /* Fondo oscuro profundo */
                font-family: "Segoe UI", "DejaVu Sans", sans-serif;
            }

            /* Estilo para la Tarjeta de Login */
            QFrame#CardLogin {
                background-color: #181a23;
                border: 1px solid #2f3352;
                border-radius: 12px;
            }

            QLabel#Title {
                color: #52a9ff; /* Celeste Moonlight */
                background-color: transparent;
            }

            QLabel#Subtitle {
                color: #8a8fbc; /* Gris violeta */
                background-color: transparent;
            }

            QLineEdit {
                background-color: #1e202f;
                color: #e2e4f0;
                border: 1px solid #2f3352;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #7078f4;
                background-color: #212433;
            }

            /* Botón de Inicio de Sesión */
            QPushButton#BtnLogin {
                background-color: #7078f4;
                color: #111218;
                border: 1px solid #7078f4;
                border-radius: 6px;
                padding: 11px;
                font-weight: bold;
                font-size: 13px;
            }

            QPushButton#BtnLogin:hover {
                background-color: #5c63db;
                border-color: #5c63db;
            }

            QPushButton#BtnLogin:pressed {
                background-color: #494fad;
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)
        self.set_dark_title_bar()    

    def set_dark_title_bar(self):
        if os.name == 'nt':
            try:
                hwnd = int(self.winId())
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    20,
                    ctypes.byref(value),
                    ctypes.sizeof(value)
                )
            except Exception as e:
                print(f"No se pudo aplicar barra de título oscura: {e}")

    # ---------------- LÓGICA DE VALIDACIÓN (INTACTA) ----------------
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

    def center(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
