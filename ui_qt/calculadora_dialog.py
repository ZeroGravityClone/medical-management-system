from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt


class CalculadoraDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculadora")
        self.setFixedSize(300, 400)

        self.center()

        self.build_ui()

    # ================= UI =================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # pantalla
        self.pantalla = QLineEdit()

        self.pantalla.setAlignment(
            Qt.AlignRight
        )

        self.pantalla.setReadOnly(False)

        self.pantalla.setStyleSheet("""

        QLineEdit{
            font-size:28px;
            font-weight:bold;
            padding:10px;
            background:#1f2937;
            color:white;
            border:1px solid #334155;
            border-radius:8px;
        }

        """)

        layout.addWidget(self.pantalla)

        # grid botones
        grid = QGridLayout()

        botones = [
            ('7',0,0),('8',0,1),('9',0,2),('/',0,3),
            ('4',1,0),('5',1,1),('6',1,2),('*',1,3),
            ('1',2,0),('2',2,1),('3',2,2),('-',2,3),
            ('C',3,0),('0',3,1),('=',3,2),('+',3,3),
        ]

        for txt,f,c in botones:

            btn = QPushButton(txt)

            btn.clicked.connect(
                lambda _, t=txt: self.click(t)
            )

            btn.setStyleSheet(self.style_btn(txt))

            grid.addWidget(btn,f,c)

        layout.addLayout(grid)

    # ================= LOGICA =================

    def click(self, t):

        if t == "C":
            self.pantalla.clear()
            return

        if t == "=":

            try:
                res = eval(
                    self.pantalla.text()
                )

                self.pantalla.setText(
                    str(res)
                )

            except:

                self.pantalla.setText(
                    "Error"
                )

            return

        self.pantalla.setText(
            self.pantalla.text() + t
        )

    # ================= ESTILO BOTONES =================

    def style_btn(self, t):

        if t == "C":

            return """
            QPushButton{
                background:#dc3545;
                color:white;
                font-size:18px;
                border-radius:6px;
                padding:10px;
            }
            QPushButton:hover{
                background:#c82333;
            }
            """

        if t == "=":

            return """
            QPushButton{
                background:#28a745;
                color:white;
                font-size:18px;
                border-radius:6px;
                padding:10px;
            }
            QPushButton:hover{
                background:#218838;
            }
            """

        if t in ["/","*","-","+"]:

            return """
            QPushButton{
                background:#1f4a75;
                color:white;
                font-size:18px;
                border-radius:6px;
                padding:10px;
            }
            QPushButton:hover{
                background:#153350;
            }
            """

        return """
        QPushButton{
            background:#3a7ebf;
            color:white;
            font-size:18px;
            border-radius:6px;
            padding:10px;
        }
        QPushButton:hover{
            background:#285a8a;
        }
        """

    # ================= CENTRAR =================

    def center(self):

        screen = self.screen().geometry()

        self.move(
            (screen.width()-self.width())//2,
            (screen.height()-self.height())//2
        )