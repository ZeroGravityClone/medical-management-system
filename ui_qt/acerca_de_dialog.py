from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class AcercaDeDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Acerca de")
        self.setFixedSize(420, 320)

        self.center()

        self.build_ui()

    # ================= UI =================

    def build_ui(self):

        main = QVBoxLayout(self)

        # CARD
        card = QFrame()

        card.setStyleSheet("""

        QFrame{
            background:#111827;
            border-radius:12px;
            border:1px solid #334155;
        }

        QLabel{
            color:white;
        }

        """)

        layout = QVBoxLayout(card)

        # TITULO
        title = QLabel("Sistema de Gestión Médica")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        # VERSION
        version = QLabel("Versión 1.0 - Build 2026")
        version.setAlignment(Qt.AlignCenter)

        layout.addWidget(version)

        # separador visual
        sep = QLabel("────────────────────────")
        sep.setAlignment(Qt.AlignCenter)
        sep.setStyleSheet("color:#374151;")

        layout.addWidget(sep)

        # INFO
        info = QLabel(
            "Sistema desarrollado para la gestión de pacientes,\n"
            "control de usuarios y administración médica.\n\n"
            "Tecnologías:\n"
            "- Python\n"
            "- PySide6\n"
            "- SQLite\n"
        )

        info.setAlignment(Qt.AlignCenter)

        layout.addWidget(info)

        # AUTOR
        autor = QLabel("Desarrollado por: José Ochoa")
        autor.setAlignment(Qt.AlignCenter)

        autor.setStyleSheet("""
            font-size:14px;
            font-weight:bold;
            color:#60a5fa;
        """)

        layout.addWidget(autor)

        # FOOTER
        footer = QLabel("© 2026 - Todos los derechos reservados")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:#9ca3af; font-size:11px;")

        layout.addWidget(footer)

        # BOTON
        btn = QPushButton("Cerrar")

        btn.clicked.connect(self.close)

        btn.setStyleSheet("""
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

        layout.addWidget(btn)

        main.addWidget(card)

    # ================= CENTRAR =================

    def center(self):

        screen = self.screen().geometry()

        self.move(
            (screen.width()-self.width())//2,
            (screen.height()-self.height())//2
        )