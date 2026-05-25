import sqlite3

class PacientesRepository:

    def __init__(self, db_path):
        self.db_path = db_path

    def obtener_todos(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT cedula, apellidos, nombres, fecha_registro, telefono, consulta
            FROM pacientes
        """)
        data = cur.fetchall()
        conn.close()
        return data

    def buscar_por_cedula(self, cedula):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM pacientes WHERE cedula=?", (cedula,))
        row = cur.fetchone()
        conn.close()
        return row

    def insertar(self, valores):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pacientes (
                apellidos, nombres, cedula, fecha_nac, lugar_nac, sexo,
                municipio, parroquia, comunidad, direccion,
                condicion, telefono, consulta, fecha_registro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, valores)

        conn.commit()
        conn.close()

    def actualizar(self, id_, valores):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            UPDATE pacientes SET
                apellidos=?, nombres=?, cedula=?, fecha_nac=?, lugar_nac=?, sexo=?,
                municipio=?, parroquia=?, comunidad=?, direccion=?,
                condicion=?, telefono=?, consulta=?, fecha_registro=?
            WHERE id=?
        """, (*valores, id_))

        conn.commit()
        conn.close()

    def eliminar(self, id_):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM pacientes WHERE id=?", (id_,))
        conn.commit()
        conn.close()

    def existe_cedula(self, cedula):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pacientes WHERE cedula = ?", (cedula,))
        existe = cur.fetchone()

        conn.close()
        return existe is not None
    
    def existe_cedula_excluyendo_id(self, cedula, id_):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM pacientes
            WHERE cedula = ? AND id != ?
        """, (cedula, id_))

        existe = cur.fetchone()
        conn.close()

        return existe is not None

    def obtener_resumen(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT cedula, apellidos, nombres, fecha_registro, telefono, consulta
            FROM pacientes
        """)

        data = cur.fetchall()
        conn.close()
        return data


