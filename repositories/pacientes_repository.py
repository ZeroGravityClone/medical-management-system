# repositories/pacientes_repository.py

import sqlite3
from datetime import datetime


class PacientesRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    # === NUEVO: Registro de persistencia de documentos ===
    def registrar_documento(self, patient_id, tipo_documento, nombre_archivo, ruta_archivo):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            INSERT INTO documents (patient_id, tipo_documento, nombre_archivo, ruta_archivo, fecha_creacion)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, tipo_documento, nombre_archivo, ruta_archivo, fecha_creacion))
        conn.commit()
        conn.close()

    def insertar(self, valores):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO pacientes (
                apellidos, nombres, cedula, fecha_nac, lugar_nac, sexo,
                municipio, parroquia, comunidad, direccion, condicion,
                telefono, consulta, fecha_registro
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, valores)
        conn.commit()
        conn.close()

    def buscar_por_cedula(self, cedula):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM pacientes WHERE cedula = ?", (cedula.upper(),))
        row = c.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    def actualizar(self, paciente_id, valores):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE pacientes
            SET apellidos=?, nombres=?, cedula=?, fecha_nac=?, lugar_nac=?, sexo=?,
                municipio=?, parroquia=?, comunidad=?, direccion=?, condicion=?,
                telefono=?, consulta=?, fecha_registro=?
            WHERE id = ?
        """, valores + (paciente_id,))
        conn.commit()
        conn.close()

    def eliminar(self, paciente_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        conn.commit()
        conn.close()

    def existe_cedula(self, cedula):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT 1 FROM pacientes WHERE cedula = ?", (cedula.upper(),))
        row = c.fetchone()
        conn.close()
        return row is not None

    def obtener_resumen(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT cedula, apellidos, nombres, fecha_registro, telefono, consulta FROM pacientes")
        rows = c.fetchall()
        conn.close()
        return rows
