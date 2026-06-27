# db/init_db.py

import sqlite3
import os

RUTA_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sistema_medico.db"
)

def inicializar_bd():
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_base, "sistema_medico.db")

    conn = sqlite3.connect(ruta_db)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE,
                    clave TEXT,
                    rol TEXT DEFAULT 'GUEST',
                    acceso TEXT DEFAULT 'PERMITIDO'
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apellidos TEXT,
                    nombres TEXT,
                    cedula TEXT UNIQUE,
                    fecha_nac TEXT,
                    lugar_nac TEXT,
                    sexo TEXT,
                    municipio TEXT,
                    parroquia TEXT,
                    comunidad TEXT,
                    direccion TEXT,
                    condicion TEXT,
                    telefono TEXT,
                    consulta TEXT,
                    fecha_registro TEXT
                )''')

    c.execute('CREATE TABLE IF NOT EXISTS estados (nombre TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS municipio (cod_muni INTEGER, descripcion TEXT, estado_nombre TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS parroquia (cod_parro INTEGER, cod_muni INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS comunidad (cod_com TEXT, cod_parro INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS consultas (descripcion TEXT)')

    # === NUEVA TABLA DE DOCUMENTOS UNIFICADA ===
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NULL,
                    tipo_documento TEXT NOT NULL,
                    nombre_archivo TEXT NOT NULL,
                    ruta_archivo TEXT NOT NULL,
                    fecha_creacion TEXT NOT NULL,
                    FOREIGN KEY (patient_id) REFERENCES pacientes(id) ON DELETE SET NULL
                )''')

    c.execute("SELECT count(*) FROM usuarios")

    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO usuarios (usuario, clave, rol, acceso)
            VALUES ('ADMIN','1234','ADMIN','PERMITIDO')
        """)

    conn.commit()
    conn.close()
