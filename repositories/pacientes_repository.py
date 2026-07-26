# repositories/pacientes_repository.py

import sqlite3
from datetime import datetime


class PacientesRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    # === Registro de persistencia de documentos ===
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

    # === Obtener todas las cédulas registradas para el Completer ===
    def obtener_todas_cedulas(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT cedula FROM pacientes ORDER BY cedula ASC")
        cedulas = [row[0] for row in c.fetchall()]
        conn.close()
        return cedulas

    # === NUEVO: Lista unificada de Autocompletado (Nombre + Cédula) ===
    def obtener_lista_autocompletado(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT nombres, apellidos, cedula FROM pacientes ORDER BY nombres ASC")
        rows = c.fetchall()
        conn.close()
        # Formato: "Nombres Apellidos (V-12345678)"
        return [f"{r['nombres']} {r['apellidos']} ({r['cedula']})" for r in rows]

    # === Obtener historial de recetas registradas de un paciente ===
    def obtener_recetas_por_paciente(self, patient_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT id, nombre_archivo, ruta_archivo, fecha_creacion 
            FROM documents 
            WHERE patient_id = ? AND tipo_documento = 'RECETA_MEDICA'
            ORDER BY fecha_creacion DESC
        """, (patient_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

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

    # === BUSCAR REFACTORIZADO (Soporta búsquedas con o sin prefijo) ===
    def buscar_por_cedula(self, cedula):
        cedula_clean = cedula.strip().upper()
        
        # Si el usuario no escribió el guion (ej: '12345678'), buscamos usando comodín '%'
        if "-" not in cedula_clean:
            query_param = f"%-{cedula_clean}" # Coincide con 'V-12345678', 'E-12345678', etc.
            sql = "SELECT * FROM pacientes WHERE cedula LIKE ?"
        else:
            query_param = cedula_clean
            sql = "SELECT * FROM pacientes WHERE cedula = ?"

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(sql, (query_param,))
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

    # === EXISTE REFACTORIZADO (Soporta comprobación con o sin prefijo) ===
    def existe_cedula(self, cedula):
        cedula_clean = cedula.strip().upper()
        
        if "-" not in cedula_clean:
            query_param = f"%-{cedula_clean}"
            sql = "SELECT 1 FROM pacientes WHERE cedula LIKE ?"
        else:
            query_param = cedula_clean
            sql = "SELECT 1 FROM pacientes WHERE cedula = ?"

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(sql, (query_param,))
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
