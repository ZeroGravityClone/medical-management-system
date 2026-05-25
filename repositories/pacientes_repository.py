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


# ==============================================================================
# Modulos CRUD
# ==============================================================================


def existe_cedula(self, cedula):
    conn = sqlite3.connect(self.db_path)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pacientes WHERE cedula = ?", (cedula,))
    existe = cur.fetchone()

    conn.close()
    return existe is not None


def insertar(self, data):
    conn = sqlite3.connect(self.db_path)
    cur = conn.cursor()

    sql = """
    INSERT INTO pacientes
    (apellidos, nombres, cedula, fecha_nac, lugar_nac, sexo,
    municipio, parroquia, comunidad, direccion,
    condicion, telefono, consulta, fecha_registro)

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cur.execute(sql, data)

    conn.commit()
    conn.close()


def buscar_por_cedula(self, cedula):
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM pacientes WHERE cedula = ?", (cedula,))
    row = cur.fetchone()
    conn.close()
    return row