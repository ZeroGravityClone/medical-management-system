from PySide6.QtWidgets import (
    QMainWindow, QMessageBox
)

from repositories.pacientes_repository import PacientesRepository
from repositories.usuarios_repository import UsuariosRepository
from repositories.catalogos_repository import CatalogosRepository
from ui_qt.views.registro_pacientes import RegistroPacientesDialog
from ui_qt.lista_pacientes_dialog import ListaPacientesDialog
from ui_qt.gestion_usuarios_dialog import GestionUsuariosDialog
from ui_qt.calculadora_dialog import CalculadoraDialog
from ui_qt.acerca_de_dialog import AcercaDeDialog
from ui_qt.asistente_ia_dialog import AsistenteIADialog

from db.init_db import RUTA_DB


class VentanaPrincipal(QMainWindow):
    def __init__(self, nombre_usuario, rol_usuario):
        super().__init__()

        # =======================
        # ESTADO USUARIO
        # =======================
        self.nombre_usuario = nombre_usuario
        self.rol_usuario = rol_usuario
        self.cerrar_sesion_flag = False

        # =======================
        # VENTANA
        # =======================
        self.setWindowTitle(
            f"USUARIO: {self.nombre_usuario} | PERFIL: {self.rol_usuario}"
        )
        self.resize(850, 600)
        self.center()

        # =======================
        # REPOSITORIOS
        # =======================
        self.pacientes_repo = PacientesRepository(RUTA_DB)
        self.usuarios_repo = UsuariosRepository(RUTA_DB)
        self.catalogos_repo = CatalogosRepository(RUTA_DB)

        # =======================
        # MENÚ PRINCIPAL
        # =======================
        self.crear_menu()

    # =========================================================
    # MENU BAR
    # =========================================================
    def crear_menu(self):
        menu_bar = self.menuBar()

        # ================= ARCHIVOS =================
        menu_archivos = menu_bar.addMenu("Archivos")

        menu_archivos.addAction(
            "Registro de Pacientes",
            self.abrir_registro_pacientes
        )

        menu_archivos.addAction(
            "Lista de Pacientes",
            self.abrir_proceso_datos
        )

        menu_archivos.addSeparator()

        menu_archivos.addAction(
            "Cerrar Sesión",
            self.cerrar_sesion
        )

        # ================= ADMIN =================
        if self.rol_usuario == "ADMIN":
            menu_admin = menu_bar.addMenu("Administrador")
            menu_admin.addAction(
                "Gestión de Usuarios",
                self.abrir_gestion_usuarios
            )

        # ================= HERRAMIENTAS =================
        menu_herr = menu_bar.addMenu("Herramientas")

        menu_herr.addAction(
            "Calculadora",
            self.abrir_calculadora
        )

        menu_herr.addAction(
            "🤖 Asistente IA (Groq)",
            self.abrir_asistente_ia
        )

        # ================= AYUDA =================
        menu_ayuda = menu_bar.addMenu("Ayuda")

        menu_ayuda.addAction(
            "Acerca de",
            self.abrir_acerca_de
        )

        # acción global extra
        menu_bar.addAction(
            "Cerrar Sesión",
            self.cerrar_sesion
        )

    # =========================================================
    # UTILIDAD CENTRAR
    # =========================================================
    def center(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    # =========================================================
    # CIERRE SESIÓN
    # =========================================================
    def cerrar_sesion(self):
        self.cerrar_sesion_flag = True
        self.close()

    # =========================
    # DUMMY METHODS (TEMPORAL)
    # =========================

    def abrir_registro_pacientes(self):
        dialog = RegistroPacientesDialog(
            self.pacientes_repo,
            self.catalogos_repo,
            self.rol_usuario
        )
        dialog.exec()

    def abrir_proceso_datos(self):

        dialog = ListaPacientesDialog(
            self.pacientes_repo
        )   

        dialog.exec()

    def abrir_gestion_usuarios(self):

        ventana = GestionUsuariosDialog(
            self.usuarios_repo,
            self.nombre_usuario
        )

        ventana.exec()

    def abrir_calculadora(self):

        dialog = CalculadoraDialog()

        dialog.exec()

    def abrir_asistente_ia(self):

        dialog = AsistenteIADialog()

        dialog.exec()

    def abrir_acerca_de(self):

        dialog = AcercaDeDialog()

        dialog.exec()

    def cerrar_sesion(self):
        self.cerrar_sesion_flag = True
        self.close()