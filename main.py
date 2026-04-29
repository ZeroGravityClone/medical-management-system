import urllib.request
import json
import threading
import ssl
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from PIL import Image, ImageTk
import traceback
from tkcalendar import DateEntry
from datetime import date, datetime
import os
import sys

# ==============================================================================
# GESTIÓN DE RUTAS PARA PYINSTALLER (EJECUTABLE)
# ==============================================================================
def obtener_rutas():
    """ Devuelve (ruta_para_bd, ruta_para_assets) """
    if getattr(sys, 'frozen', False):
        ruta_bd = os.path.dirname(sys.executable) 
        ruta_assets = sys._MEIPASS 
    else:
        ruta_bd = os.path.dirname(os.path.abspath(__file__))
        ruta_assets = ruta_bd
    return ruta_bd, ruta_assets

RUTA_BASE_DB, RUTA_ASSETS = obtener_rutas()

# ==============================================================================
# FILTRO PARA SILENCIAR ERRORES FANTASMAS DE CUSTOMTKINTER
# ==============================================================================
def silenciar_errores_tk(exc, val, tb):
    mensaje_error = str(val)
    if "invalid command name" in mensaje_error and ("check_dpi_scaling" in mensaje_error or "update" in mensaje_error):
        pass 
    else:
        traceback.print_exception(exc, val, tb)

tk.Tk.report_callback_exception = silenciar_errores_tk

# ==============================================================================
# CONFIGURACIÓN GLOBAL Y CREACIÓN DE BASE DE DATOS LOCAL
# ==============================================================================
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")

def inicializar_bd():
    ruta_db = os.path.join(RUTA_BASE_DB, "sistema_medico.db")
    conn = sqlite3.connect(ruta_db)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE, clave TEXT,
                    rol TEXT DEFAULT 'GUEST', acceso TEXT DEFAULT 'PERMITIDO'
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apellidos TEXT, nombres TEXT, cedula TEXT UNIQUE,
                    fecha_nac TEXT, lugar_nac TEXT, sexo TEXT,
                    municipio TEXT, parroquia TEXT, comunidad TEXT,
                    direccion TEXT, condicion TEXT, telefono TEXT,
                    consulta TEXT, fecha_registro TEXT
                )''')

    c.execute('CREATE TABLE IF NOT EXISTS estados (nombre TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS municipio (cod_muni INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS parroquia (cod_parro INTEGER, cod_muni INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS comunidad (cod_com INTEGER, cod_parro INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS consultas (descripcion TEXT)')

    c.execute("SELECT count(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (usuario, clave, rol, acceso) VALUES ('ADMIN', '1234', 'ADMIN', 'PERMITIDO')")

    conn.commit()
    conn.close()

inicializar_bd()

# ==============================================================================
# CLASE 1: PANTALLA DE LOGIN
# ==============================================================================

class PantallaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema Médico - Acceso")
        self.geometry("450x600") 
        self.resizable(False, False)
        
        ctk.set_appearance_mode("Light") 
        self.configure(fg_color="#EBF2F7") 

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

        self.login_exitoso = False
        self.usuario_validado = ""
        self.rol_validado = ""
        self.conexion_login = self.conectar_bd()

        # --- DISEÑO DE LA INTERFAZ ---

        self.main_container = ctk.CTkFrame(
            self, 
            fg_color="white", 
            corner_radius=15, 
            border_width=2, 
            border_color="#B0C4DE"
        )
        self.main_container.pack(padx=20, pady=20, fill="both", expand=True)

        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="#F8FAFC", height=180, corner_radius=15)
        self.header_frame.pack(fill="x", padx=2, pady=2)
        self.header_frame.pack_propagate(False)

        ruta_script = os.path.dirname(__file__)
        ruta_logo = os.path.join(ruta_script, "logo.png")

        if os.path.exists(ruta_logo):
            try:
                img_pil = Image.open(ruta_logo)
                
                self.logo_image = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(110, 110))
                self.lbl_logo = ctk.CTkLabel(self.header_frame, image=self.logo_image, text="")
                self.lbl_logo.pack(pady=(15, 0))
            except Exception:
                self.lbl_logo = ctk.CTkLabel(self.header_frame, text="🏥", font=("Arial", 50))
                self.lbl_logo.pack(pady=(15, 0))
        else:
        
            self.lbl_logo = ctk.CTkLabel(self.header_frame, text="🏥", font=("Arial", 50))
            self.lbl_logo.pack(pady=(15, 0))

        self.lbl_titulo = ctk.CTkLabel(
            self.header_frame, 
            text="GESTIÓN MÉDICA", 
            text_color="#1E3A8A", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        )
        self.lbl_titulo.pack()

        
        self.linea = ctk.CTkFrame(self.main_container, fg_color="#D1D5DB", height=1)
        self.linea.pack(fill="x", padx=40, pady=20)

        
        self.form_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=40)

        # Usuario
        self.lbl_user = ctk.CTkLabel(
            self.form_frame, 
            text="USUARIO", 
            text_color="#4B5563", 
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_user.pack(anchor="w")
        
        self.txt_usuario = ctk.CTkEntry(
            self.form_frame, 
            width=320, 
            height=45, 
            placeholder_text="Nombre de usuario",
            fg_color="#F9FAFB",
            border_color="#ABB8C3",
            text_color="black"
        )
        self.txt_usuario.pack(pady=(5, 20))
        self.txt_usuario.focus()

        # Contraseña
        self.lbl_pass = ctk.CTkLabel(
            self.form_frame, 
            text="CONTRASEÑA", 
            text_color="#4B5563", 
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_pass.pack(anchor="w")
        
        self.txt_password = ctk.CTkEntry(
            self.form_frame, 
            show="*", 
            width=320, 
            height=45, 
            placeholder_text="••••••••",
            fg_color="#F9FAFB",
            border_color="#ABB8C3",
            text_color="black"
        )
        self.txt_password.pack(pady=(5, 30))

        
        self.btn_ingresar = ctk.CTkButton(
            self.form_frame, 
            text="INICIAR SESIÓN", 
            command=self.validar_acceso, 
            width=320, 
            height=50,
            corner_radius=8,
            fg_color="#2563EB", 
            hover_color="#1D4ED8",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        self.btn_ingresar.pack()

        
        self.lbl_footer = ctk.CTkLabel(
            self.main_container, 
            text="Servicio Comunitario 2026", 
            text_color="#9CA3AF", 
            font=("Segoe UI", 10)
        )
        self.lbl_footer.pack(side="bottom", pady=15)

        self.bind('<Return>', lambda event: self.validar_acceso())


    def conectar_bd(self):
        try:
            ruta_db = os.path.join(RUTA_BASE_DB, "sistema_medico.db")
            conn = sqlite3.connect(ruta_db)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as err:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{err}")
            self.destroy()
            return None

    def validar_acceso(self):
        usuario_ingresado = self.txt_usuario.get().upper()
        password = self.txt_password.get()
        try:
            cursor = self.conexion_login.cursor()
            sql = "SELECT * FROM usuarios WHERE usuario = ? AND clave = ?"
            cursor.execute(sql, (usuario_ingresado, password))
            user_data = cursor.fetchone()
            
            if user_data:
                if user_data['acceso'] == 'DENEGADO':
                    messagebox.showerror("Acceso Denegado", "Tu cuenta no tiene permisos para acceder.")
                    return

                self.conexion_login.close()
                self.login_exitoso = True
                self.usuario_validado = user_data['usuario']
                self.rol_validado = user_data['rol']
                self.withdraw()  
                self.quit()      
            else:
                messagebox.showerror("Error", "Usuario o clave incorrectos")
                self.txt_password.delete(0, tk.END)
        except sqlite3.Error as err:
            messagebox.showerror("Error SQL", str(err))

# ==============================================================================
# CLASE 2: VENTANA PRINCIPAL
# ==============================================================================
class VentanaPrincipal(ctk.CTk):
    def __init__(self, nombre_usuario, rol_usuario):
        super().__init__()
        
        self.nombre_usuario = nombre_usuario 
        self.rol_usuario = rol_usuario
        self.cerrar_sesion_flag = False 
        
        self.title(f"---> USUARIO: {self.nombre_usuario} | PERFIL: {self.rol_usuario}")
        self.geometry("850x600")
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (850 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

        self.ruta_db = os.path.join(RUTA_BASE_DB, "sistema_medico.db")

        try:
            ruta_img = os.path.join(RUTA_ASSETS, "fondo_medico.png")
            img_original = Image.open(ruta_img)
            self.fondo_ctk = ctk.CTkImage(light_image=img_original, dark_image=img_original, size=(850, 600))
            label_fondo = ctk.CTkLabel(self, image=self.fondo_ctk, text="")
            label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        except: pass

        # ==============================================================================
        # MENU SUPERIOR DINÁMICO
        # ==============================================================================
        barra_menus = tk.Menu(self)
        self.config(menu=barra_menus)
        
        menu_archivos = tk.Menu(barra_menus, tearoff=0)
        menu_archivos.add_command(label="Registro de Pacientes", command=self.abrir_registro_pacientes)
        menu_archivos.add_command(label="Lista de Pacientes", command=self.abrir_proceso_datos)
        menu_archivos.add_separator()
        menu_archivos.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        barra_menus.add_cascade(label="Archivos", menu=menu_archivos)
        
        if self.rol_usuario == "ADMIN":
            menu_admin = tk.Menu(barra_menus, tearoff=0)
            menu_admin.add_command(label="Gestión de Usuarios", command=self.abrir_gestion_usuarios)
            barra_menus.add_cascade(label="Administrador", menu=menu_admin)
        
        menu_herr = tk.Menu(barra_menus, tearoff=0)
        menu_herr.add_command(label="Calculadora", command=self.abrir_calculadora)
        menu_herr.add_command(label="🤖 Asistente IA (Groq)", command=self.abrir_asistente_ia)
        
        barra_menus.add_cascade(label="Herramientas", menu=menu_herr)

        menu_ayuda = tk.Menu(barra_menus, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self.abrir_acerca_de)
        barra_menus.add_cascade(label="Ayuda", menu=menu_ayuda)
        
        barra_menus.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)

    def cerrar_sesion(self):
        self.cerrar_sesion_flag = True
        self.quit()

    # ==============================================================================
    # MÓDULOS DEL SISTEMA
    # ==============================================================================
    
    def abrir_registro_pacientes(self):
        ventana_pac = ctk.CTkToplevel(self)
        ventana_pac.title("Registro de Pacientes")
        ventana_pac.geometry("880x470") 
        ventana_pac.transient(self)
        ventana_pac.grab_set()
        
        ventana_pac.update_idletasks()
        x = (ventana_pac.winfo_screenwidth() // 2) - (880 // 2)
        y = (ventana_pac.winfo_screenheight() // 2) - (470 // 2)
        ventana_pac.geometry(f"+{x}+{y}")

        ventana_pac.paciente_actual_id = None

        def validar_solo_numeros(texto_ingresado):
            return texto_ingresado == "" or texto_ingresado.isdigit()
        validacion_numeros = (ventana_pac.register(validar_solo_numeros), '%P')

        main_frame = ctk.CTkFrame(ventana_pac, fg_color="#f9f9f9", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        frame_ident = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_ident.pack(fill="x", padx=20, pady=(5, 5))
        
        ctk.CTkLabel(frame_ident, text="Fecha de Registro:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=(5, 5))
        txt_fecha_reg = ctk.CTkEntry(frame_ident, width=100)
        txt_fecha_reg.grid(row=0, column=1, padx=5)
        txt_fecha_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        txt_fecha_reg.configure(state="readonly")

        group_pers = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc", fg_color="white")
        group_pers.pack(fill="x", padx=15, pady=(10, 5)) 
        ctk.CTkLabel(group_pers, text=" Datos Personales ", fg_color="white", text_color="#1a5276", font=("Arial", 12, "bold")).place(x=15, y=5)

        inner_pers = ctk.CTkFrame(group_pers, fg_color="transparent")
        inner_pers.pack(padx=15, pady=(25, 10), fill="x")
        
        ctk.CTkLabel(inner_pers, text="Apellidos:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        txt_apellidos = ctk.CTkEntry(inner_pers, width=180)
        txt_apellidos.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(inner_pers, text="Nombres:").grid(row=0, column=2, sticky="e", padx=5)
        txt_nombres = ctk.CTkEntry(inner_pers, width=180)
        txt_nombres.grid(row=0, column=3, padx=5)
        
        ctk.CTkLabel(inner_pers, text="Cédula:").grid(row=0, column=4, sticky="e", padx=5)
        frame_cedula = ctk.CTkFrame(inner_pers, fg_color="transparent")
        frame_cedula.grid(row=0, column=5, sticky="w", padx=5)
        cbo_nac = ctk.CTkComboBox(frame_cedula, values=["V", "E", "J"], width=55, state="readonly")
        cbo_nac.pack(side="left", padx=(0, 5))
        cbo_nac.set("V")
        txt_cedula = ctk.CTkEntry(frame_cedula, width=100, validate="key", validatecommand=validacion_numeros)
        txt_cedula.pack(side="left")

        ctk.CTkLabel(inner_pers, text="Fecha Nac.:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        cal_fecha_nac = DateEntry(inner_pers, width=15, background='#3a7ebf', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', year=2000)
        cal_fecha_nac.grid(row=1, column=1, sticky="w", padx=5)

        ctk.CTkLabel(inner_pers, text="Edad:").grid(row=1, column=2, sticky="e", padx=5)
        frame_edad = ctk.CTkFrame(inner_pers, fg_color="transparent")
        frame_edad.grid(row=1, column=3, sticky="w", columnspan=2)
        txt_edad = ctk.CTkEntry(frame_edad, width=50)
        txt_edad.pack(side="left", padx=5)
        txt_edad.configure(state="readonly")
        
        def actualizar_edad(event=None):
            try:
                fecha_nac = cal_fecha_nac.get_date()
                hoy = date.today()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                txt_edad.configure(state="normal")
                txt_edad.delete(0, tk.END)
                txt_edad.insert(0, str(edad))
                txt_edad.configure(state="readonly")
            except: pass

        cal_fecha_nac.bind("<<DateEntrySelected>>", actualizar_edad)
        actualizar_edad()

        ctk.CTkLabel(frame_edad, text="Lugar Nac:").pack(side="left", padx=5)
        cbo_lugar = ctk.CTkComboBox(frame_edad, width=110, state="readonly")
        cbo_lugar.pack(side="left", padx=5)

        ctk.CTkLabel(inner_pers, text="Sexo:").grid(row=1, column=5, sticky="w", padx=5)
        cbo_sexo = ctk.CTkComboBox(inner_pers, values=["Masculino", "Femenino"], width=110, state="readonly")
        cbo_sexo.grid(row=1, column=5, sticky="e", padx=5)

        group_ubi = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc", fg_color="white")
        group_ubi.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(group_ubi, text=" Ubicación Geográfica ", fg_color="white", text_color="#1a5276", font=("Arial", 12, "bold")).place(x=15, y=5)

        inner_ubi = ctk.CTkFrame(group_ubi, fg_color="transparent")
        inner_ubi.pack(padx=15, pady=(25, 10), fill="x")
        
        ctk.CTkLabel(inner_ubi, text="Municipio:").grid(row=0, column=0, sticky="e", padx=5)
        c_m = ctk.CTkComboBox(inner_ubi, width=170, state="readonly")
        c_m.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(inner_ubi, text="Parroquia:").grid(row=0, column=2, sticky="e", padx=5)
        c_p = ctk.CTkComboBox(inner_ubi, width=170, state="readonly")
        c_p.grid(row=0, column=3, padx=5)
        
        ctk.CTkLabel(inner_ubi, text="Comunidad:").grid(row=0, column=4, sticky="e", padx=5)
        c_c = ctk.CTkComboBox(inner_ubi, width=150, state="readonly")
        c_c.grid(row=0, column=5, padx=5)
        
        ctk.CTkLabel(inner_ubi, text="Dirección:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        txt_direccion = ctk.CTkTextbox(inner_ubi, width=650, height=35, border_width=1, border_color="#cccccc")
        txt_direccion.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky="w")

        group_otros = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc", fg_color="white")
        group_otros.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(group_otros, text=" Información Médica y Contacto ", fg_color="white", text_color="#1a5276", font=("Arial", 12, "bold")).place(x=15, y=5)

        inner_otros = ctk.CTkFrame(group_otros, fg_color="transparent")
        inner_otros.pack(padx=15, pady=(25, 10), fill="x") 
        
        ctk.CTkLabel(inner_otros, text="Condición:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        cbo_condicion = ctk.CTkComboBox(inner_otros, values=["Estable", "Grave", "Observación"], width=150, state="readonly")
        cbo_condicion.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(inner_otros, text="Teléfono:").grid(row=0, column=2, sticky="e", padx=5)
        txt_telefono = ctk.CTkEntry(inner_otros, width=150, validate="key", validatecommand=validacion_numeros)
        txt_telefono.grid(row=0, column=3, padx=5)
        
        ctk.CTkLabel(inner_otros, text="Consulta:").grid(row=0, column=4, sticky="e", padx=5)
        c_consulta = ctk.CTkComboBox(inner_otros, width=150, state="readonly")
        c_consulta.grid(row=0, column=5, padx=5)

        self.dict_m = {}; self.dict_p = {}; self.dict_c = {}
        def cargar_comu(choice=None):
            parro = c_p.get()
            if parro in self.dict_p:
                c_c.set('')
                self.cursor_p.execute("SELECT descripcion, cod_com FROM comunidad WHERE cod_parro = ?", (self.dict_p[parro],))
                self.dict_c.clear()
                for d, c in self.cursor_p.fetchall(): self.dict_c[d] = c
                lista_comunidades = list(self.dict_c.keys())
                c_c.configure(values=lista_comunidades)
                if lista_comunidades: c_c.set(lista_comunidades[0])
                else: c_c.set("Sin registros")
            else:
                c_c.configure(values=[]); c_c.set('')

        def cargar_parro(choice=None):
            muni = c_m.get()
            if muni in self.dict_m:
                c_p.set(''); c_c.set(''); c_c.configure(values=[])
                self.cursor_p.execute("SELECT descripcion, cod_parro FROM parroquia WHERE cod_muni = ?", (self.dict_m[muni],))
                self.dict_p.clear()
                for d, c in self.cursor_p.fetchall(): self.dict_p[d] = c
                lista_parroquias = list(self.dict_p.keys())
                c_p.configure(values=lista_parroquias)
                if lista_parroquias:
                    c_p.set(lista_parroquias[0]); cargar_comu()
                else:
                    c_p.set("Sin registros"); c_c.configure(values=[]); c_c.set("Sin registros")

        try:
            self.conn_p = sqlite3.connect(self.ruta_db)
            self.cursor_p = self.conn_p.cursor()
            
            self.cursor_p.execute("SELECT nombre FROM estados")
            lista_estados = [row[0] for row in self.cursor_p.fetchall()]
            if lista_estados:
                cbo_lugar.configure(values=lista_estados)
                cbo_lugar.set(lista_estados[0])
            else:
                cbo_lugar.configure(values=["Sin registros"]); cbo_lugar.set("Sin registros")
                
            self.cursor_p.execute("SELECT descripcion FROM consultas") 
            lista_consultas = [row[0] for row in self.cursor_p.fetchall()]
            if lista_consultas:
                c_consulta.configure(values=lista_consultas)
                c_consulta.set(lista_consultas[0])
            else:
                c_consulta.configure(values=["General"]); c_consulta.set("General")
                
            c_m.configure(command=cargar_parro)
            c_p.configure(command=cargar_comu)
            
            self.cursor_p.execute("SELECT descripcion, cod_muni FROM municipio")
            for d, c in self.cursor_p.fetchall(): self.dict_m[d] = c
            
            muni_values = list(self.dict_m.keys())
            if muni_values:
                c_m.configure(values=muni_values)
                c_m.set(muni_values[0])
                cargar_parro() 
        except Exception as e:
            pass

        def cargar_bd():
            dialogo_busqueda = ctk.CTkToplevel(ventana_pac)
            dialogo_busqueda.title("Buscar Paciente")
            dialogo_busqueda.geometry("350x180")
            dialogo_busqueda.transient(ventana_pac)
            dialogo_busqueda.grab_set() 
            
            dialogo_busqueda.update_idletasks()
            xb = (dialogo_busqueda.winfo_screenwidth() // 2) - (350 // 2)
            yb = (dialogo_busqueda.winfo_screenheight() // 2) - (180 // 2)
            dialogo_busqueda.geometry(f"+{xb}+{yb}")

            validacion_busq_numeros = (dialogo_busqueda.register(validar_solo_numeros), '%P')
            ctk.CTkLabel(dialogo_busqueda, text="Ingrese la Cédula a buscar:", font=("Arial", 14, "bold")).pack(pady=(20, 10))

            frame_input = ctk.CTkFrame(dialogo_busqueda, fg_color="transparent")
            frame_input.pack(pady=5)
            cbo_busq_tipo = ctk.CTkComboBox(frame_input, values=["V", "E", "J"], width=60, state="readonly")
            cbo_busq_tipo.pack(side="left", padx=5)
            cbo_busq_tipo.set("V")

            txt_busq_num = ctk.CTkEntry(frame_input, width=150, validate="key", validatecommand=validacion_busq_numeros)
            txt_busq_num.pack(side="left", padx=5)
            txt_busq_num.focus()

            def ejecutar_busqueda(event=None):
                num_ingresado = txt_busq_num.get().strip()
                if not num_ingresado: return
                
                ced_busc = f"{cbo_busq_tipo.get()}-{num_ingresado}"
                dialogo_busqueda.destroy() 
                
                try:
                    conn = sqlite3.connect(self.ruta_db)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM pacientes WHERE cedula = ?", (ced_busc,))
                    paciente = cursor.fetchone()
                    conn.close()
                    
                    if paciente:
                        ventana_pac.paciente_actual_id = paciente['id']
                        fecha_reg = paciente['fecha_registro']
                        txt_fecha_reg.configure(state="normal")
                        txt_fecha_reg.delete(0, tk.END)
                        if fecha_reg and "-" in fecha_reg:
                            try: txt_fecha_reg.insert(0, datetime.strptime(fecha_reg, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            except: txt_fecha_reg.insert(0, str(fecha_reg))
                        else: txt_fecha_reg.insert(0, str(fecha_reg))
                        txt_fecha_reg.configure(state="readonly")
                        
                        txt_apellidos.delete(0, tk.END); txt_apellidos.insert(0, paciente['apellidos'] or "")
                        txt_nombres.delete(0, tk.END); txt_nombres.insert(0, paciente['nombres'] or "")
                        
                        ced_full = paciente['cedula'] or ""
                        if "-" in ced_full:
                            nac, num = ced_full.split("-", 1)
                            cbo_nac.set(nac)
                            txt_cedula.delete(0, tk.END); txt_cedula.insert(0, num)
                        else:
                            txt_cedula.delete(0, tk.END); txt_cedula.insert(0, ced_full)
                            
                        if paciente['fecha_nac']:
                            try: cal_fecha_nac.set_date(datetime.strptime(paciente['fecha_nac'], "%Y-%m-%d").date())
                            except: pass

                        if paciente['lugar_nac']: cbo_lugar.set(paciente['lugar_nac'])
                        if paciente['sexo']: cbo_sexo.set(paciente['sexo'])
                        if paciente['condicion']: cbo_condicion.set(paciente['condicion'])
                        if paciente['consulta']: c_consulta.set(paciente['consulta'])
                        
                        txt_telefono.delete(0, tk.END); txt_telefono.insert(0, paciente['telefono'] or "")
                        txt_direccion.delete("0.0", tk.END); txt_direccion.insert("0.0", paciente['direccion'] or "")
                        
                        if paciente['municipio']: c_m.set(paciente['municipio']); cargar_parro()
                        if paciente['parroquia']: c_p.set(paciente['parroquia']); cargar_comu()
                        if paciente['comunidad']: c_c.set(paciente['comunidad'])
                        
                        actualizar_edad()
                        
                        
                        nom_resumen = paciente['nombres'] or ""
                        ape_resumen = paciente['apellidos'] or ""
                        ced_resumen = paciente['cedula'] or ""
                        edad_resumen = txt_edad.get() or "N/A"
                        
                        mensaje_exito = (
                            f"¡Paciente cargado exitosamente!\n\n"
                            f"Datos del Paciente:\n"
                            f"----------------------------------------\n"
                            f"👤 Nombres: {nom_resumen}\n"
                            f"👥 Apellidos: {ape_resumen}\n"
                            f"🪪 Cédula: {ced_resumen}\n"
                            f"🎂 Edad: {edad_resumen} años\n"
                            f"----------------------------------------"
                        )
                        messagebox.showinfo("Carga Exitosa", mensaje_exito)
                        # ---------------------------------------------------
                    else:
                        messagebox.showwarning("No encontrado", "Paciente no registrado.")
                except Exception as e: pass

            btn_buscar = ctk.CTkButton(dialogo_busqueda, text="Buscar", command=ejecutar_busqueda, width=120)
            btn_buscar.pack(pady=15)
            dialogo_busqueda.bind('<Return>', ejecutar_busqueda)

        def guardar_bd():
            if not txt_apellidos.get() or not txt_nombres.get() or not txt_cedula.get():
                messagebox.showwarning("Faltan Datos", "Complete Nombres, Apellidos y Cédula.")
                return
            try:
                fecha_reg_sqlite = datetime.strptime(txt_fecha_reg.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
                fecha_nac_sqlite = cal_fecha_nac.get_date().strftime("%Y-%m-%d")
                cedula_completa = f"{cbo_nac.get()}-{txt_cedula.get()}"
                direccion_texto = txt_direccion.get("0.0", tk.END).strip()

                conn = sqlite3.connect(self.ruta_db)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula_completa,))
                if cursor.fetchone():
                    messagebox.showwarning("Duplicado", "La cédula ya está registrada.")
                    conn.close(); return 
                
                sql = """INSERT INTO pacientes 
                         (apellidos, nombres, cedula, fecha_nac, lugar_nac, sexo, 
                          municipio, parroquia, comunidad, direccion, condicion, telefono, consulta, fecha_registro) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                valores = (txt_apellidos.get(), txt_nombres.get(), cedula_completa, fecha_nac_sqlite, cbo_lugar.get(), cbo_sexo.get(),
                           c_m.get(), c_p.get(), c_c.get(), direccion_texto, cbo_condicion.get(), txt_telefono.get(), c_consulta.get(), fecha_reg_sqlite)
                cursor.execute(sql, valores)
                conn.commit(); conn.close()
                messagebox.showinfo("Éxito", "Guardado exitosamente.")
                ventana_pac.paciente_actual_id = None
                txt_apellidos.delete(0, tk.END); txt_nombres.delete(0, tk.END); txt_cedula.delete(0, tk.END)
                txt_telefono.delete(0, tk.END); txt_direccion.delete("0.0", tk.END)
            except Exception as e: pass

        def modificar_bd():
            if self.rol_usuario != "ADMIN": return
            if not ventana_pac.paciente_actual_id: return
            try:
                fecha_reg_sqlite = datetime.strptime(txt_fecha_reg.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
                fecha_nac_sqlite = cal_fecha_nac.get_date().strftime("%Y-%m-%d")
                cedula_completa = f"{cbo_nac.get()}-{txt_cedula.get()}"
                direccion_texto = txt_direccion.get("0.0", tk.END).strip()
                conn = sqlite3.connect(self.ruta_db)
                cursor = conn.cursor()
                sql = """UPDATE pacientes SET 
                         apellidos=?, nombres=?, cedula=?, fecha_nac=?, lugar_nac=?, sexo=?, 
                         municipio=?, parroquia=?, comunidad=?, direccion=?, condicion=?, telefono=?, consulta=?, fecha_registro=?
                         WHERE id=?"""
                valores = (txt_apellidos.get(), txt_nombres.get(), cedula_completa, fecha_nac_sqlite, cbo_lugar.get(), cbo_sexo.get(),
                           c_m.get(), c_p.get(), c_c.get(), direccion_texto, cbo_condicion.get(), txt_telefono.get(), c_consulta.get(), fecha_reg_sqlite,
                           ventana_pac.paciente_actual_id)
                cursor.execute(sql, valores)
                conn.commit(); conn.close()
                messagebox.showinfo("Éxito", "Registro modificado.")
            except Exception as e: pass

        def eliminar_bd():
            if self.rol_usuario != "ADMIN": return
            if not ventana_pac.paciente_actual_id: return
            resp = messagebox.askyesno("Confirmar", "¿Eliminar paciente?")
            if not resp: return
            try:
                conn = sqlite3.connect(self.ruta_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pacientes WHERE id=?", (ventana_pac.paciente_actual_id,))
                conn.commit(); conn.close()
                messagebox.showinfo("Éxito", "Eliminado.")
                ventana_pac.paciente_actual_id = None
                txt_apellidos.delete(0, tk.END); txt_nombres.delete(0, tk.END); txt_cedula.delete(0, tk.END)
                txt_telefono.delete(0, tk.END); txt_direccion.delete("0.0", tk.END)
            except Exception as e: pass

        frame_botones = ctk.CTkFrame(ventana_pac, fg_color="transparent")
        frame_botones.pack(pady=15)
        btn_cargar = ctk.CTkButton(frame_botones, text="Buscar Paciente", fg_color="#17a2b8", hover_color="#138496", font=("Arial", 12, "bold"), command=cargar_bd)
        btn_cargar.pack(side="left", padx=10)
        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar Nuevo", fg_color="#28a745", hover_color="#218838", font=("Arial", 12, "bold"), command=guardar_bd)
        btn_guardar.pack(side="left", padx=10)
        btn_modificar = ctk.CTkButton(frame_botones, text="Modificar", fg_color="#ffc107", hover_color="#e0a800", text_color="black", font=("Arial", 12, "bold"), command=modificar_bd)
        if self.rol_usuario != "ADMIN": btn_modificar.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
        btn_modificar.pack(side="left", padx=10)
        btn_eliminar = ctk.CTkButton(frame_botones, text="Eliminar", fg_color="#dc3545", hover_color="#c82333", font=("Arial", 12, "bold"), command=eliminar_bd)
        if self.rol_usuario != "ADMIN": btn_eliminar.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
        btn_eliminar.pack(side="left", padx=10)

    
    def abrir_proceso_datos(self):
        ventana_proc = ctk.CTkToplevel(self)
        ventana_proc.title("Listado de Pacientes")
        ventana_proc.geometry("900x500")
        ventana_proc.transient(self); ventana_proc.grab_set()
        ventana_proc.update_idletasks()
        x = (ventana_proc.winfo_screenwidth() // 2) - (900 // 2)
        y = (ventana_proc.winfo_screenheight() // 2) - (500 // 2)
        ventana_proc.geometry(f"+{x}+{y}")

        ctk.CTkLabel(ventana_proc, text="Listado de Pacientes", font=("Arial", 16, "bold")).pack(pady=15)
        
        frame_t = ctk.CTkFrame(ventana_proc, corner_radius=0)
        frame_t.pack(pady=10, padx=20, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", rowheight=25)
        style.map('Treeview', background=[('selected', '#3a7ebf')])

        cols = ("cedula", "apellidos", "nombres", "fecha_registro", "telefono", "consulta")
        tabla = ttk.Treeview(frame_t, columns=cols, show="headings")
        
        anchos = {"cedula": 100, "apellidos": 150, "nombres": 150, "fecha_registro": 110, "telefono": 110, "consulta": 120}
        for c in cols: 
            tabla.heading(c, text=c.replace("_", " ").title())
            tabla.column(c, width=anchos[c], anchor="center")
            
        tabla.tag_configure('impar', background="#e8f4f8") 
        tabla.tag_configure('par', background="#ffffff")   
        
        scroll = ctk.CTkScrollbar(frame_t, command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        menu_copiar = tk.Menu(ventana_proc, tearoff=0)

        def copiar_al_portapapeles(texto):
            ventana_proc.clipboard_clear()
            ventana_proc.clipboard_append(texto)

        def al_click_derecho(event):
            region = tabla.identify_region(event.x, event.y)
            if region == "cell":
                fila = tabla.identify_row(event.y)
                columna = tabla.identify_column(event.x)
                tabla.selection_set(fila) 
                
                col_idx = int(columna.replace('#', '')) - 1
                valores = tabla.item(fila, "values")
                
                if valores and 0 <= col_idx < len(valores):
                    valor_celda = str(valores[col_idx])
                    
                    if col_idx in (0, 4):
                        valor_celda = "".join(c for c in valor_celda if c.isdigit())
                        
                    menu_copiar.delete(0, tk.END)
                    menu_copiar.add_command(
                        label=f"Copiar: {valor_celda}", 
                        command=lambda v=valor_celda: copiar_al_portapapeles(v)
                    )
                    menu_copiar.post(event.x_root, event.y_root)

        tabla.bind("<Button-3>", al_click_derecho)

        try:
            conn = sqlite3.connect(self.ruta_db)
            cursor = conn.cursor()
            cursor.execute("SELECT cedula, apellidos, nombres, fecha_registro, telefono, consulta FROM pacientes")
            contador = 0
            for r in cursor.fetchall(): 
                if contador % 2 == 0: tabla.insert("", tk.END, values=tuple(r), tags=('par',))
                else: tabla.insert("", tk.END, values=tuple(r), tags=('impar',))
                contador += 1
            conn.close()
        except: pass
        
        ctk.CTkButton(ventana_proc, text="Cerrar", command=ventana_proc.destroy, width=150).pack(pady=15)

    def abrir_gestion_usuarios(self):
        vent_usu = ctk.CTkToplevel(self)
        vent_usu.title("Gestión de Permisos de Usuarios")
        vent_usu.geometry("680x420")
        vent_usu.transient(self)
        vent_usu.grab_set()
        
        vent_usu.update_idletasks()
        xu = (vent_usu.winfo_screenwidth() // 2) - (680 // 2)
        yu = (vent_usu.winfo_screenheight() // 2) - (420 // 2)
        vent_usu.geometry(f"+{xu}+{yu}")

        frame_lista = ctk.CTkFrame(vent_usu)
        frame_lista.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame_lista, text="Usuarios Registrados", font=("Arial", 14, "bold")).pack(pady=5)
        
        tabla_usu = ttk.Treeview(frame_lista, columns=("usuario", "rol", "acceso"), show="headings")
        tabla_usu.heading("usuario", text="Usuario"); tabla_usu.heading("rol", text="Rol"); tabla_usu.heading("acceso", text="Acceso")
        tabla_usu.column("usuario", width=120); tabla_usu.column("rol", width=80); tabla_usu.column("acceso", width=80)
        tabla_usu.pack(fill="both", expand=True, padx=5, pady=5)

        def cargar_usuarios():
            tabla_usu.delete(*tabla_usu.get_children())
            try:
                conn = sqlite3.connect(self.ruta_db)
                c = conn.cursor()
                c.execute("SELECT usuario, rol, acceso FROM usuarios")
                for r in c.fetchall(): tabla_usu.insert("", tk.END, values=tuple(r))
                conn.close()
            except: pass
        cargar_usuarios()

        frame_form = ctk.CTkFrame(vent_usu, width=250)
        frame_form.pack(side="right", fill="y", padx=10, pady=10)
        ctk.CTkLabel(frame_form, text="Configurar Usuario", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(frame_form, text="Usuario:").pack()
        txt_u = ctk.CTkEntry(frame_form, width=180); txt_u.pack(pady=2)
        ctk.CTkLabel(frame_form, text="Contraseña:").pack()
        txt_p = ctk.CTkEntry(frame_form, show="*", width=180); txt_p.pack(pady=2)
        ctk.CTkLabel(frame_form, text="Nivel de Rol:").pack(pady=(10, 0))
        cbo_rol = ctk.CTkComboBox(frame_form, values=["GUEST", "ADMIN"], width=180, state="readonly"); cbo_rol.set("GUEST"); cbo_rol.pack(pady=2)
        ctk.CTkLabel(frame_form, text="Estado de Acceso:").pack(pady=(10, 0))
        cbo_acceso = ctk.CTkComboBox(frame_form, values=["PERMITIDO", "DENEGADO"], width=180, state="readonly"); cbo_acceso.set("DENEGADO"); cbo_acceso.pack(pady=2)

        def guardar_usuario():
            u = txt_u.get().strip().upper()
            p = txt_p.get().strip()
            rol = cbo_rol.get()
            acc = cbo_acceso.get()
            
            if not u: 
                messagebox.showwarning("Atención", "El campo Usuario no puede estar vacío.", parent=vent_usu)
                return
            
            # --- PROTECCIONES ---
            if u == "ADMIN" and (acc == "DENEGADO" or rol != "ADMIN"):
                messagebox.showerror("Acción Denegada", "No se puede degradar ni denegar el acceso al usuario principal ADMIN.", parent=vent_usu)
                return

            if u == self.nombre_usuario and (acc == "DENEGADO" or rol != "ADMIN"): 
                messagebox.showerror("Acción Denegada", "No puedes denegar tu propio acceso ni quitarte el rol de ADMIN mientras estás en sesión.", parent=vent_usu)
                return

            try:
                conn = sqlite3.connect(self.ruta_db)
                c = conn.cursor()
                c.execute("SELECT usuario FROM usuarios WHERE usuario = ?", (u,))
                existe = c.fetchone()

                if existe: 
                    
                    if p: 
                        c.execute("UPDATE usuarios SET clave=?, rol=?, acceso=? WHERE usuario=?", (p, rol, acc, u))
                    else: 
                        c.execute("UPDATE usuarios SET rol=?, acceso=? WHERE usuario=?", (rol, acc, u))
                    accion_msg = "actualizado"
                else: 
                    
                    if not p: 
                        messagebox.showwarning("Atención", "Debe asignar una contraseña para el nuevo usuario.", parent=vent_usu)
                        conn.close()
                        return
                    c.execute("INSERT INTO usuarios (usuario, clave, rol, acceso) VALUES (?, ?, ?, ?)", (u, p, rol, acc))
                    accion_msg = "registrado"
                
                conn.commit(); conn.close()
                txt_u.delete(0, tk.END); txt_p.delete(0, tk.END)
                cargar_usuarios()
                
                
                messagebox.showinfo("Éxito", f"Usuario '{u}' {accion_msg} correctamente con acceso {acc}.", parent=vent_usu)

            except Exception as e: 
                messagebox.showerror("Error", f"Ocurrió un error en la base de datos:\n{e}", parent=vent_usu)

        def cargar_datos_seleccion():
            sel = tabla_usu.selection()
            if not sel: return
            item = tabla_usu.item(sel[0])["values"]
            txt_u.delete(0, tk.END); txt_u.insert(0, item[0])
            txt_p.delete(0, tk.END); cbo_rol.set(item[1]); cbo_acceso.set(item[2])
        
        tabla_usu.bind("<Double-1>", lambda e: cargar_datos_seleccion())

        def eliminar_usuario():
            sel = tabla_usu.selection()
            if not sel: 
                messagebox.showwarning("Atención", "Seleccione un usuario de la tabla para eliminar.", parent=vent_usu)
                return
            
            u = tabla_usu.item(sel[0])["values"][0]
            
            
            if u == "ADMIN": 
                messagebox.showerror("Error Crítico", "El usuario principal 'ADMIN' no puede ser eliminado del sistema.", parent=vent_usu)
                return
                
            if u == self.nombre_usuario: 
                messagebox.showerror("Acción Denegada", "No puedes eliminar tu propia cuenta mientras estás en sesión.", parent=vent_usu)
                return

            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro que desea eliminar permanentemente al usuario '{u}'?", parent=vent_usu):
                try:
                    conn = sqlite3.connect(self.ruta_db)
                    c = conn.cursor()
                    c.execute("DELETE FROM usuarios WHERE usuario = ?", (u,))
                    conn.commit(); conn.close(); 
                    cargar_usuarios()
                    txt_u.delete(0, tk.END); txt_p.delete(0, tk.END)
                    
                    
                    messagebox.showinfo("Eliminado", f"El usuario '{u}' ha sido eliminado exitosamente.", parent=vent_usu)
                except Exception as e: 
                    messagebox.showerror("Error", f"Ocurrió un error al intentar eliminar:\n{e}", parent=vent_usu)

        ctk.CTkButton(frame_form, text="Guardar / Actualizar", command=guardar_usuario, fg_color="#28a745", hover_color="#218838", height=35).pack(pady=(20, 5))
        ctk.CTkButton(frame_form, text="Eliminar Usuario", command=eliminar_usuario, fg_color="#dc3545", hover_color="#c82333").pack(pady=5)

    def abrir_calculadora(self):
        vent_calc = ctk.CTkToplevel(self)
        vent_calc.title("Calculadora")
        vent_calc.geometry("300x400")
        vent_calc.transient(self)
        vent_calc.resizable(False, False)
        vent_calc.update_idletasks()
        xc = (vent_calc.winfo_screenwidth() // 2) - (300 // 2)
        yc = (vent_calc.winfo_screenheight() // 2) - (400 // 2)
        vent_calc.geometry(f"+{xc}+{yc}")

        pantalla = ctk.CTkEntry(vent_calc, font=("Arial", 28, "bold"), justify="right")
        pantalla.pack(fill="x", padx=10, pady=15, ipady=15)
        frame_teclas = ctk.CTkFrame(vent_calc, fg_color="transparent")
        frame_teclas.pack(fill="both", expand=True, padx=10, pady=5)

        def presionar(tecla):
            if tecla == "C": pantalla.delete(0, tk.END)
            elif tecla == "=":
                try: res = eval(pantalla.get()); pantalla.delete(0, tk.END); pantalla.insert(0, str(res))
                except: pantalla.delete(0, tk.END); pantalla.insert(0, "Error")
            else: pantalla.insert(tk.END, tecla)

        teclas = [('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3),
                  ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3),
                  ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
                  ('C', 3, 0), ('0', 3, 1), ('=', 3, 2), ('+', 3, 3)]

        for i in range(4): frame_teclas.grid_columnconfigure(i, weight=1); frame_teclas.grid_rowconfigure(i, weight=1)
        for (texto, f, c) in teclas:
            color = "#3a7ebf" if texto not in ["C", "=", "/", "*", "-", "+"] else "#1f4a75"
            hover = "#285a8a" if texto not in ["C", "=", "/", "*", "-", "+"] else "#153350"
            if texto == "C": color, hover = "#dc3545", "#c82333"
            elif texto == "=": color, hover = "#28a745", "#218838"
            btn = ctk.CTkButton(frame_teclas, text=texto, font=("Arial", 20, "bold"), fg_color=color, hover_color=hover, command=lambda t=texto: presionar(t))
            btn.grid(row=f, column=c, padx=3, pady=3, sticky="nsew")

    def abrir_acerca_de(self):
        vent_acerca = ctk.CTkToplevel(self)
        vent_acerca.title("Acerca de")
        vent_acerca.geometry("350x250")
        vent_acerca.transient(self)
        vent_acerca.resizable(False, False)
        
        vent_acerca.update_idletasks()
        x = (vent_acerca.winfo_screenwidth() // 2) - (350 // 2)
        y = (vent_acerca.winfo_screenheight() // 2) - (250 // 2)
        vent_acerca.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(vent_acerca, text="Sistema de Gestión Médico", font=("Arial", 18, "bold")).pack(pady=(25, 5))
        ctk.CTkLabel(vent_acerca, text="Versión 1.0 (Portable)", font=("Arial", 12)).pack(pady=0)
        
        ctk.CTkLabel(vent_acerca, text="Creado y desarrollado por:", font=("Arial", 12)).pack(pady=(20, 0))
        
        ctk.CTkLabel(vent_acerca, text="[José Ochoa]", font=("Arial", 16, "bold"), text_color="#1a5276").pack(pady=(0, 20))
        
        ctk.CTkLabel(vent_acerca, text="Todos los derechos reservados © 2026", font=("Arial", 10)).pack(pady=5)
        
        ctk.CTkButton(vent_acerca, text="Cerrar", command=vent_acerca.destroy, width=120).pack(pady=(5, 10))


    # ==============================================================================
    # Asistente de IA Groq (Chatbot)
    # ==============================================================================


    def abrir_asistente_ia(self):
        
        vent_ia = ctk.CTkToplevel(self)
        vent_ia.title("Asistente Médico IA (Groq)")
        vent_ia.geometry("650x550")
        vent_ia.transient(self)
        
        
        vent_ia.update_idletasks()
        x = (vent_ia.winfo_screenwidth() // 2) - (650 // 2)
        y = (vent_ia.winfo_screenheight() // 2) - (550 // 2)
        vent_ia.geometry(f"+{x}+{y}")

        ctk.CTkLabel(vent_ia, text="Asistente de IA - Groq", font=("Arial", 16, "bold")).pack(pady=10)
        
        chat_historial = ctk.CTkTextbox(vent_ia, width=600, height=400, state="normal", wrap="word")
        chat_historial.pack(padx=20, pady=5)
        chat_historial.insert(tk.END, "🤖 IA: ¡Hola! Soy el asistente médico. Conectado vía Groq. ¿En qué puedo ayudarte?\n\n")
        chat_historial.configure(state="disabled")

        frame_input = ctk.CTkFrame(vent_ia)
        frame_input.pack(fill="x", padx=20, pady=10)

        txt_mensaje = ctk.CTkEntry(frame_input, width=490, placeholder_text="Escribe tu consulta...")
        txt_mensaje.pack(side="left", padx=(0, 10))

        def consultar_ia():
            pregunta = txt_mensaje.get().strip()
            if not pregunta: return

            chat_historial.configure(state="normal")
            chat_historial.insert(tk.END, f"👤 Tú: {pregunta}\n\n")
            chat_historial.configure(state="disabled")
            chat_historial.see(tk.END)
            txt_mensaje.delete(0, tk.END)
            btn_enviar.configure(state="disabled", text="Pensando...")

            def peticion_internet():
                API_KEY = "GROQ_API_KEY" 
                
                URL = "https://api.groq.com/openai/v1/chat/completions"
                
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Eres un asistente médico profesional para un consultorio en Venezuela. Responde de forma clara y ética."
                        },
                        {"role": "user", "content": pregunta}
                    ],
                    "temperature": 0.7
                }
                
                try:
                    import ssl
                    
                    contexto_ssl = ssl._create_unverified_context()
                    
                    datos_envio = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(URL, data=datos_envio, method="POST")
                    
                    
                    req.add_header('Content-Type', 'application/json')
                    req.add_header('Authorization', f'Bearer {API_KEY}')
                    
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')

                    with urllib.request.urlopen(req, context=contexto_ssl, timeout=20) as response:
                        res_json = json.loads(response.read().decode('utf-8'))
                        
                        
                        texto_ia = res_json['choices'][0]['message']['content']
                        
                except urllib.error.HTTPError as e:
                    
                    error_body = e.read().decode('utf-8')
                    texto_ia = f"❌ Error de Groq ({e.code}): {error_body}"
                except Exception as e:
                    texto_ia = f"❌ Error inesperado: {str(e)}"

                def actualizar_ui():
                    chat_historial.configure(state="normal")
                    chat_historial.insert(tk.END, f"🤖 IA: {texto_ia}\n\n")
                    chat_historial.configure(state="disabled")
                    chat_historial.see(tk.END)
                    btn_enviar.configure(state="normal", text="Enviar")

                vent_ia.after(0, actualizar_ui)

                

            threading.Thread(target=peticion_internet).start()

        btn_enviar = ctk.CTkButton(frame_input, text="Enviar", width=100, command=consultar_ia)
        btn_enviar.pack(side="right")
        vent_ia.bind('<Return>', lambda e: consultar_ia())


# ==============================================================================
# ARRANQUE
# ==============================================================================
def abrir_sistema_principal(usuario, rol):
    app_main = VentanaPrincipal(usuario, rol)
    app_main.mainloop()
    volver = getattr(app_main, 'cerrar_sesion_flag', False)
    try: app_main.destroy()
    except: pass
    return volver

if __name__ == "__main__":
    while True:
        app_log = PantallaLogin()
        app_log.mainloop() 
        if app_log.login_exitoso:
            usuario = app_log.usuario_validado
            rol = app_log.rol_validado
            app_log.destroy() 
            if not abrir_sistema_principal(usuario, rol):
                break
        else:
            break