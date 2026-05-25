import sqlite3
import os

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
    c.execute('CREATE TABLE IF NOT EXISTS municipio (cod_muni INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS parroquia (cod_parro INTEGER, cod_muni INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS comunidad (cod_com INTEGER, cod_parro INTEGER, descripcion TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS consultas (descripcion TEXT)')

    c.execute("SELECT count(*) FROM usuarios")

    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO usuarios (usuario, clave, rol, acceso)
            VALUES ('ADMIN','1234','ADMIN','PERMITIDO')
        """)

    conn.commit()
    conn.close()