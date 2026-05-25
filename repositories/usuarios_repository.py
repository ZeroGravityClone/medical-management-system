import sqlite3

def login(db_path, usuario, clave):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT usuario, rol, acceso
        FROM usuarios
        WHERE usuario = ? AND clave = ?
    """, (usuario.upper(), clave))

    row = c.fetchone()
    conn.close()

    if not row:
        return None

    if row["acceso"] == "DENEGADO":
        return None

    return {
        "usuario": row["usuario"],
        "rol": row["rol"],
        "acceso": row["acceso"]
    }

def obtener_todos(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT usuario, rol, acceso FROM usuarios")
    data = c.fetchall()

    conn.close()
    return data


def crear_usuario(db_path, usuario, clave, rol, acceso):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        INSERT INTO usuarios (usuario, clave, rol, acceso)
        VALUES (?, ?, ?, ?)
    """, (usuario.upper(), clave, rol, acceso))

    conn.commit()
    conn.close()


def actualizar_usuario(db_path, usuario, clave, rol, acceso):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if clave:
        c.execute("""
            UPDATE usuarios
            SET clave=?, rol=?, acceso=?
            WHERE usuario=?
        """, (clave, rol, acceso, usuario))
    else:
        c.execute("""
            UPDATE usuarios
            SET rol=?, acceso=?
            WHERE usuario=?
        """, (rol, acceso, usuario))

    conn.commit()
    conn.close()


def eliminar_usuario(db_path, usuario):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DELETE FROM usuarios WHERE usuario=?", (usuario,))

    conn.commit()
    conn.close()