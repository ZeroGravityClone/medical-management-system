import sqlite3

class CatalogosRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def obtener_estados(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT nombre FROM estados")
            return [r[0] for r in cur.fetchall()]

    def obtener_consultas(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT descripcion FROM consultas")
            return [r[0] for r in cur.fetchall()]
    
    def obtener_municipios(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT descripcion, cod_muni FROM municipio")
            return cur.fetchall()
        
    def obtener_parroquias(self, cod_muni):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT descripcion, cod_parro
                FROM parroquia
                WHERE cod_muni = ?
            """, (cod_muni,))
            return cur.fetchall()
        
    def obtener_comunidades(self, cod_parro):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT descripcion, cod_com
                FROM comunidad
                WHERE cod_parro = ?
            """, (cod_parro,))
            return cur.fetchall()
        
    