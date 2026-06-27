# ui_qt/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from repositories.pacientes_repository import PacientesRepository
from repositories.usuarios_repository import UsuariosRepository
from repositories.catalogos_repository import CatalogosRepository

from ui_qt.views.registro_pacientes import RegistroPacientesDialog
from ui_qt.lista_pacientes_dialog import ListaPacientesDialog
from ui_qt.gestion_usuarios_dialog import GestionUsuariosDialog
from ui_qt.calculadora_dialog import CalculadoraDialog
from ui_qt.acerca_de_dialog import AcercaDeDialog
from ui_qt.asistente_ia_dialog import AsistenteIADialog
from ui_qt.recetario_ia_dialog import RecetarioIADialog # <-- NUEVO IMPORT

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
        # CONFIGURACIÓN VENTANA
        # =======================
        self.setWindowTitle("Sistema de Gestión Médica")
        self.resize(1100, 550) # Mantenemos estrictamente tu medida optimizada de pantalla
        self.center()

        # =======================
        # REPOSITORIOS
        # =======================
        self.pacientes_repo = PacientesRepository(RUTA_DB)
        self.usuarios_repo = UsuariosRepository(RUTA_DB)
        self.catalogos_repo = CatalogosRepository(RUTA_DB)

        # =======================
        # DISEÑO DE INTERFAZ (MOONLIGHT)
        # =======================
        self.inicializar_ui()

    def inicializar_ui(self):
        # Widget Central Contenedor
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)

        # Layout Horizontal Principal (Sidebar | Contenido Derecho)
        self.layout_principal = QHBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # 1. SIDEBAR (Navegación Izquierda)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        
        self.layout_sidebar = QVBoxLayout(self.sidebar)
        self.layout_sidebar.setContentsMargins(16, 24, 16, 24)
        self.layout_sidebar.setSpacing(8)

        self.construir_sidebar()
        self.layout_principal.addWidget(self.sidebar)

        # 2. CONTENEDOR DERECHO (Topbar + Área de Trabajo)
        self.contenedor_derecho = QWidget()
        self.layout_derecho = QVBoxLayout(self.contenedor_derecho)
        self.layout_derecho.setContentsMargins(0, 0, 0, 0)
        self.layout_derecho.setSpacing(0)

        # Topbar
        self.topbar = QFrame()
        self.topbar.setObjectName("Topbar")
        self.topbar.setFixedHeight(60)
        
        self.layout_topbar = QHBoxLayout(self.topbar)
        self.layout_topbar.setContentsMargins(32, 0, 32, 0)
        self.layout_topbar.setAlignment(Qt.AlignVCenter)

        self.construir_topbar()
        self.layout_derecho.addWidget(self.topbar)

        # Área de Trabajo (Dashboard / Contenido Central)
        self.area_trabajo = QFrame()
        self.area_trabajo.setObjectName("AreaTrabajo")
        
        self.layout_trabajo = QVBoxLayout(self.area_trabajo)
        self.layout_trabajo.setContentsMargins(32, 32, 32, 32)
        self.layout_trabajo.setSpacing(16)

        self.construir_dashboard()
        self.layout_derecho.addWidget(self.area_trabajo)

        self.layout_principal.addWidget(self.contenedor_derecho)

    def construir_sidebar(self):
        # Header del Sidebar
        self.lbl_logo = QLabel("MENÚ PRINCIPAL")
        self.lbl_logo.setObjectName("SidebarTitle")
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        self.layout_sidebar.addWidget(self.lbl_logo)
        
        # Línea divisoria limpia
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setObjectName("SidebarDivider")
        self.layout_sidebar.addWidget(linea)

        self.layout_sidebar.addSpacing(8)

        # Botones de Navegación
        self.btn_registro = QPushButton("Registro de Pacientes")
        self.btn_registro.setObjectName("SidebarButton")
        self.btn_registro.clicked.connect(self.abrir_registro_pacientes)
        self.layout_sidebar.addWidget(self.btn_registro)

        self.btn_lista = QPushButton("Lista de Pacientes")
        self.btn_lista.setObjectName("SidebarButton")
        self.btn_lista.clicked.connect(self.abrir_proceso_datos)
        self.layout_sidebar.addWidget(self.btn_lista)

        # NUEVO BOTÓN: Recetario Inteligente (IA)
        self.btn_recetario = QPushButton("Recetario Inteligente (IA)")
        self.btn_recetario.setObjectName("SidebarButton")
        self.btn_recetario.clicked.connect(self.abrir_recetario_ia)
        self.layout_sidebar.addWidget(self.btn_recetario)

        self.btn_calculadora = QPushButton("Calculadora Médica")
        self.btn_calculadora.setObjectName("SidebarButton")
        self.btn_calculadora.clicked.connect(self.abrir_calculadora)
        self.layout_sidebar.addWidget(self.btn_calculadora)

        self.btn_ia = QPushButton("Asistente IA (Groq)")
        self.btn_ia.setObjectName("SidebarButton")
        self.btn_ia.clicked.connect(self.abrir_asistente_ia)
        self.layout_sidebar.addWidget(self.btn_ia)

        # Sección de Administrador (Condicional)
        if self.rol_usuario == "ADMIN":
            self.lbl_admin = QLabel("ADMINISTRACIÓN")
            self.lbl_admin.setObjectName("SidebarSectionLabel")
            self.layout_sidebar.addWidget(self.lbl_admin)

            self.btn_usuarios = QPushButton("Gestión de Usuarios")
            self.btn_usuarios.setObjectName("SidebarButton")
            self.btn_usuarios.clicked.connect(self.abrir_gestion_usuarios)
            self.layout_sidebar.addWidget(self.btn_usuarios)

        # Espaciador expansivo
        self.layout_sidebar.addStretch()

        # Botón de Información
        self.btn_info = QPushButton("Acerca de")
        self.btn_info.setObjectName("SidebarButton")
        self.btn_info.clicked.connect(self.abrir_acerca_de)
        self.layout_sidebar.addWidget(self.btn_info)

        # Botón Cerrar Sesión
        self.btn_logout = QPushButton("Cerrar Sesión")
        self.btn_logout.setObjectName("SidebarLogoutButton")
        self.btn_logout.clicked.connect(self.cerrar_sesion)
        self.layout_sidebar.addWidget(self.btn_logout)

    def construir_topbar(self):
        # Título de la pantalla activa
        self.lbl_pantalla = QLabel("PANEL DE CONTROL")
        self.lbl_pantalla.setObjectName("TopbarTitle")
        
        # Información de sesión
        self.lbl_sesion = QLabel(f"Usuario: {self.nombre_usuario}   |   Rol: {self.rol_usuario}")
        self.lbl_sesion.setObjectName("TopbarSession")

        self.layout_topbar.addWidget(self.lbl_pantalla)
        self.layout_topbar.addStretch()
        self.layout_topbar.addWidget(self.lbl_sesion)

    def construir_dashboard(self):
        # Dashboard de bienvenida
        self.lbl_welcome = QLabel(f"Bienvenido al Sistema Médico, {self.nombre_usuario}")
        self.lbl_welcome.setObjectName("DashboardTitle")
        self.layout_trabajo.addWidget(self.lbl_welcome)

        self.lbl_desc = QLabel("Seleccione una opción del menú de la izquierda para comenzar a trabajar.")
        self.lbl_desc.setObjectName("DashboardSub")
        self.layout_trabajo.addWidget(self.lbl_desc)

        # Tarjeta contenedora (Card)
        self.card_info = QFrame()
        self.card_info.setObjectName("Card")
        
        layout_card = QVBoxLayout(self.card_info)
        layout_card.setContentsMargins(24, 24, 24, 24)
        layout_card.setSpacing(12)

        lbl_card_title = QLabel("Resumen de Funciones")
        lbl_card_title.setObjectName("CardTitle")
        layout_card.addWidget(lbl_card_title)

        lbl_card_body = QLabel(
            "• El registro de pacientes se almacena localmente mediante base de datos SQLite relacional.\n"
            "• Las consultas de IA están conectadas de manera asíncrona mediante la API segura de Groq utilizando QThreads.\n"
            "• Utilice el menú de administración para el control, alta y modificación de accesos en el sistema."
        )
        lbl_card_body.setObjectName("CardBody")
        layout_card.addWidget(lbl_card_body)

        self.layout_trabajo.addWidget(self.card_info)
        self.layout_trabajo.addStretch()

    def center(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def cerrar_sesion(self):
        self.cerrar_sesion_flag = True
        self.close()

    # =========================
    # ACCIONES DEL CONTROLADOR
    # =========================
    def abrir_registro_pacientes(self):
        dialog = RegistroPacientesDialog(
            self.pacientes_repo,
            self.catalogos_repo,
            self.rol_usuario
        )
        dialog.exec()

    def abrir_proceso_datos(self):
        dialog = ListaPacientesDialog(self.pacientes_repo)   
        dialog.exec()

    def abrir_recetario_ia(self):
        """Lanza el diálogo del recetario pasando el repositorio de pacientes de la ventana principal."""
        dialog = RecetarioIADialog(self, self.pacientes_repo)  # <-- Se pasa self.pacientes_repo
        dialog.exec()

    def abrir_gestion_usuarios(self):
        ventana = GestionUsuariosDialog(self.usuarios_repo, self.nombre_usuario)
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
