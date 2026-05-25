import sqlite3

def login_user(db_path, usuario, clave):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT usuario, rol, acceso FROM usuarios WHERE usuario=? AND clave=?",
        (usuario.upper(), clave)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    usuario_db, rol, acceso = user

    if acceso == "DENEGADO":
        return None

    return {
        "usuario": usuario_db,
        "rol": rol,
        "acceso": acceso
    }