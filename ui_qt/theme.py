from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


def apply_dark_theme(app):
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(15, 23, 42))
    dark_palette.setColor(QPalette.WindowText, Qt.white)

    dark_palette.setColor(QPalette.Base, QColor(17, 24, 39))
    dark_palette.setColor(QPalette.AlternateBase, QColor(31, 41, 55))

    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)

    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(37, 99, 235))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)

    dark_palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #0f172a;
        }

        QMenuBar {
            background-color: #111827;
            color: white;
        }

        QMenuBar::item:selected {
            background-color: #1f2937;
        }

        QMenu {
            background-color: #111827;
            color: white;
        }

        QMenu::item:selected {
            background-color: #2563eb;
        }
    """)