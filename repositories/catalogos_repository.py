# repositories/catalogos_repository.py

import sqlite3


class CatalogosRepository:

    def __init__(self, db_path):
        self.db_path = db_path

    def obtener_estados(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT nombre FROM estados ORDER BY nombre ASC")
        data = [row[0] for row in c.fetchall()]
        conn.close()
        return data

    def obtener_consultas(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT descripcion FROM consultas ORDER BY descripcion ASC")
        data = [row[0] for row in c.fetchall()]
        conn.close()
        return data

    # === NUEVO: Obtener Municipios filtrados por Estado ===
    def obtener_municipios_por_estado(self, estado_nombre):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT descripcion, cod_muni 
            FROM municipio 
            WHERE estado_nombre = ? 
            ORDER BY descripcion ASC
        """, (estado_nombre.upper(),))
        data = c.fetchall()
        conn.close()
        return data

    # === Obtener Parroquias filtradas por Municipio ===
    def obtener_parroquias_por_municipio(self, cod_muni):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT descripcion, cod_parro 
            FROM parroquia 
            WHERE cod_muni = ? 
            ORDER BY descripcion ASC
        """, (cod_muni,))
        data = c.fetchall()
        conn.close()
        return data

    # === Obtener Comunidades filtradas por Parroquia ===
    def obtener_comunidades_por_parroquia(self, cod_parro):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT descripcion 
            FROM comunidad 
            WHERE cod_parro = ? 
            ORDER BY descripcion ASC
        """, (cod_parro,))
        data = [row[0] for row in c.fetchall()]
        conn.close()
        return data
