# main.py
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

# Importaciones de tu estructura
from db.init_db import inicializar_bd
from ui_qt.login import LoginWindow
from ui_qt.main_window import VentanaPrincipal

def cargar_estilo_moonlight(app: QApplication):
    """Carga de manera limpia el archivo QSS para la estética oscura."""
    ruta_estilo = os.path.join(os.path.dirname(__file__), "ui_qt", "styles.qss")
    archivo = QFile(ruta_estilo)
    if archivo.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(archivo)
        app.setStyleSheet(stream.readAll())
        archivo.close()
    else:
        print("Aviso: No se encontró ui_qt/styles.qss. Usando estilo por defecto.")

def abrir_sistema_principal(app: QApplication, usuario: str, rol: str) -> bool:
    """Instancia, muestra la ventana principal y espera a su cierre."""
    app_main = VentanaPrincipal(usuario, rol)
    app_main.show()
    
    # Iniciamos el bucle de eventos para la ventana principal
    app.exec()
    
    # Al cerrarse, verificamos si se solicitó cerrar sesión
    volver_a_login = getattr(app_main, 'cerrar_sesion_flag', False)
    app_main.deleteLater() 
    return volver_a_login

if __name__ == "__main__":
    # 1. Inicializar base de datos
    inicializar_bd()
    
    # 2. Inicializar la aplicación Qt
    app = QApplication(sys.argv)
    
    # 3. Cargar estilos
    cargar_estilo_moonlight(app)
    
    # 4. Flujo de control de sesiones
    while True:
        app_log = LoginWindow()
        app_log.show()
        
        # El bucle se detiene aquí mientras el Login esté abierto
        app.exec() 
        
        # Al cerrarse el login, el bucle anterior termina y evaluamos el éxito:
        if getattr(app_log, 'login_exitoso', False):
            usuario = getattr(app_log, 'usuario_validado', "")
            rol = getattr(app_log, 'rol_validado', "")
            
            app_log.deleteLater()
            
            # Abrimos la principal. Si no se solicita re-login, rompemos el ciclo y salimos.
            if not abrir_sistema_principal(app, usuario, rol):
                break
        else:
            # Si el usuario simplemente cerró la ventana de login, liberamos memoria y salimos
            app_log.deleteLater()
            break
            
    sys.exit(0)