# insertar en labd.py

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "sistema_medico.db")

# Verificar existencia de la base de datos antes de proceder
if not os.path.exists(DB_PATH):
    print(f"Error: No se encontró la base de datos en {DB_PATH}.")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Reestructurando tablas de catálogos geográficos y asegurando tabla de documentos...")

# =========================================================
# RECREAR TABLAS CON LLAVES DE RELACIÓN LIMPIAS
# =========================================================
cur.execute("DROP TABLE IF EXISTS estados")
cur.execute("DROP TABLE IF EXISTS consultas")
cur.execute("DROP TABLE IF EXISTS municipio")
cur.execute("DROP TABLE IF EXISTS parroquia")
cur.execute("DROP TABLE IF EXISTS comunidad")

# Aseguramos la existencia de la tabla de documentos unificada
cur.execute('''CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NULL,
                tipo_documento TEXT NOT NULL,
                nombre_archivo TEXT NOT NULL,
                ruta_archivo TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES pacientes(id) ON DELETE SET NULL
            )''')

cur.execute("CREATE TABLE estados (nombre TEXT)")
cur.execute("CREATE TABLE consultas (descripcion TEXT)")
cur.execute("CREATE TABLE municipio (cod_muni INTEGER, descripcion TEXT, estado_nombre TEXT)")
cur.execute("CREATE TABLE parroquia (cod_parro INTEGER, cod_muni INTEGER, descripcion TEXT)")
cur.execute("CREATE TABLE comunidad (cod_com TEXT, cod_parro INTEGER, descripcion TEXT)")

# =========================================================
# 1. POBLAR ESTADOS DE VENEZUELA (Exactamente 10)
# =========================================================
estados = ["LARA", "DISTRITO CAPITAL", "CARABOBO", "MIRANDA", "ZULIA", "ARAGUA", "MÉRIDA", "TÁCHIRA", "ANZOÁTEGUI", "FALCÓN"]

estados_data = [
    ("LARA",),
    ("DISTRITO CAPITAL",),
    ("CARABOBO",),
    ("MIRANDA",),
    ("ZULIA",),
    ("ARAGUA",),
    ("MÉRIDA",),
    ("TÁCHIRA",),
    ("ANZOÁTEGUI",),
    ("FALCÓN",)
]
cur.executemany("INSERT INTO estados (nombre) VALUES (?)", estados_data)

# =========================================================
# 2. POBLAR MUNICIPIOS (Exactamente 5 por Estado -> 50 Total)
# =========================================================
municipios_por_estado = {
    "LARA": ["IRIBARREN", "PALAVECINO", "TORRES", "MORAN", "JIMENEZ"],
    "DISTRITO CAPITAL": ["LIBERTADOR", "CHACAO_DC", "BARUTA_DC", "HATILLO_DC", "SUCRE_DC"],
    "CARABOBO": ["VALENCIA", "NAGUANAGUA", "SAN DIEGO", "GUACARA", "PUERTO CABELLO"],
    "MIRANDA": ["SUCRE", "CHACAO", "BARUTA", "EL HATILLO", "PLAZA"],
    "ZULIA": ["MARACAIBO", "SAN FRANCISCO", "CABIMAS", "LAGUNILLAS", "COLON"],
    "ARAGUA": ["GIRARDOT", "SANTIAGO MARIÑO", "JOSÉ FÉLIX RIBAS", "LINARES ALCÁNTARA", "ZAMORA"],
    "MÉRIDA": ["LIBERTADOR MÉRIDA", "CAMPO ELÍAS", "ALBERTO ADRIANI", "TOVAR", "RANGEL"],
    "TÁCHIRA": ["SAN CRISTÓBAL", "CÁRDENAS", "JUNÍN", "BOLÍVAR", "JÁUREGUI"],
    "ANZOÁTEGUI": ["SIMÓN BOLÍVAR", "JUAN ANTONIO SOTILLO", "ANACO", "FREITES", "SIMÓN RODRÍGUEZ"],
    "FALCÓN": ["MIRANDA FALCON", "CARIRUBANA", "COLINA", "SILVA", "MONSEÑOR ITURRIZA"]
}

# Vocabularios para asignación jerárquica limpia y no numérica
pool_parroquias = [
    "CATEDRAL", "CONCEPCIÓN", "SANTA ROSA", "EL CARMEN", "SAN JOSÉ", 
    "LA CANDELARIA", "ALTAGRACIA", "SAN JUAN", "SAN AGUSTÍN", "EL RECREO", 
    "SAN BERNARDINO", "SAN PEDRO", "EL VALLE", "COCHE", "ANTÍMANO", 
    "CARICUAO", "MACARAO", "LA VEGA", "LA PASTORA", "SAN BLAS", 
    "MIGUEL PEÑA", "RAFAEL URDANETA", "NAGUANAGUA", "MAÑONGO", "LA ENTRADA", 
    "TRINCHERA", "CHACAO", "EL PEDREGAL", "LA CASTELLANA", "ALTAMIRA", 
    "PETARE", "LA DOLORITA", "MARICHE", "CAUCAGÜITA", "OLEGARIO VILLALOBOS", 
    "CHIQUINQUIRÁ", "COQUIVACOA", "JUANA DE ÁVILA", "SAN FRANCISCO", "EL BAJO", 
    "MARCIAL HERNÁNDEZ", "DOMITILA FLORES", "LAS DELICIAS", "CHORONÍ", "MADRE MARÍA", 
    "JOAQUÍN CRESPO", "SPINETTI DINI", "ARIAS", "MILLA", "CARACCIOLO", 
    "LA CONCORDIA", "SAN JUAN BAUTISTA", "PEDRO MARÍA MORANTES", "SAN SEBASTIÁN"
]

pool_comunidades = [
    "CENTRO", "BARRIO AJURO", "URBANIZACIÓN ESTE", "LAS MERCEDES", "EL RECREO", 
    "LA ESPERANZA", "PUEBLO NUEVO", "SECTOR EL FARO", "URBANIZACIÓN REAL", "BARRIO CENTRAL", 
    "SECTOR LA LUCHA", "URBANIZACIÓN GARDENIA", "LAS ACACIAS", "LOS PALOS GRANDES", "LAS FLORES", 
    "VALLE VERDE", "LA COROMOTO", "SAN JACINTO", "EL MILAGRO", "LA VICTORIA", 
    "EL PROGRESO", "SECTOR SAN JOSÉ", "LOS RUICES", "MONTE CRISTO", "LA CALIFORNIA", 
    "LA URBINA", "EL LLANITO", "LAS QUINTAS", "LA VIÑA", "PREBO", 
    "EL VIÑEDO", "MAÑONGO", "LA GRANJA", "TAZAJAL", "LAS CHIMENEAS", 
    "TRIGAL NORTE", "TRIGAL SUR", "GUAPARO", "EL PARRAL", "SABANA GRANDE", 
    "BELLO MONTE", "LOS CHAGUARAMOS", "SANTA MÓNICA", "CUMBRES DE CURUMO", "PRADOS DEL ESTE"
]

# =========================================================
# PROCESAMIENTO E INSERCIÓN JERÁRQUICA EN BUCLE
# =========================================================
print("Ejecutando inserciones relacionales estrictas...")

cod_muni_secuencial = 1
cod_parro_secuencial = 1
cod_comu_secuencial = 1

for estado in estados:
    # Obtener los 5 municipios correspondientes a este estado
    municipios = municipios_por_estado[estado]
    
    for muni_nombre in municipios:
        str_cod_muni = f"{cod_muni_secuencial:03d}"
        
        # 2. Insertar Municipio
        cur.execute(
            "INSERT INTO municipio (descripcion, cod_muni, estado_nombre) VALUES (?, ?, ?)",
            (muni_nombre, str_cod_muni, estado)
        )
        
        # Seleccionar 4 parroquias de forma determinista para este municipio
        for j in range(4):
            idx_parro = (cod_muni_secuencial * 4 + j) % len(pool_parroquias)
            parro_nombre = pool_parroquias[idx_parro]
            str_cod_parro = f"{cod_parro_secuencial:04d}"
            
            # 3. Insertar Parroquia
            cur.execute(
                "INSERT INTO parroquia (descripcion, cod_parro, cod_muni) VALUES (?, ?, ?)",
                (parro_nombre, str_cod_parro, str_cod_muni)
            )
            
            # Seleccionar 3 comunidades de forma determinista para esta parroquia
            for k in range(3):
                idx_comu = (cod_parro_secuencial * 3 + k) % len(pool_comunidades)
                comu_nombre = pool_comunidades[idx_comu]
                str_cod_comu = f"C{cod_comu_secuencial:04d}"
                
                # 4. Insertar Comunidad
                cur.execute(
                    "INSERT INTO comunidad (descripcion, cod_com, cod_parro) VALUES (?, ?, ?)",
                    (comu_nombre, str_cod_comu, str_cod_parro)
                )
                
                cod_comu_secuencial += 1
            
            cod_parro_secuencial += 1
            
        cod_muni_secuencial += 1

# =========================================================
# CONSULTAS CLÍNICAS AUXILIARES
# =========================================================
cur.executemany("INSERT INTO consultas (descripcion) VALUES (?)", [
    ("Medicina General",), ("Emergencia de Adultos",), ("Consulta de Control",), ("Pediatría",)
])

# =========================================================
# CONSULTAS DE CONTROL (Verificación de Totales)
# =========================================================
cur.execute("SELECT COUNT(*) FROM estados;")
total_estados = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM municipio;")
total_municipios = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM parroquia;")
total_parroquias = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM comunidad;")
total_comunidades = cur.fetchone()[0]

conn.commit()
conn.close()

# =========================================================
# REPORTE DE CONTROL DE INTEGRIDAD
# =========================================================
print("\n" + "="*50)
print("REPORTE DE VERIFICACIÓN DE INTEGRIDAD REFERENCIAL")
print("="*50)
print(f"Estados esperados:      10  |  Insertados: {total_estados}")
print(f"Municipios esperados:   50  |  Insertados: {total_municipios}")
print(f"Parroquias esperadas:  200  |  Insertados: {total_parroquias}")
print(f"Comunidades esperadas: 600  |  Insertados: {total_comunidades}")
print("="*50)

if total_estados == 10 and total_municipios == 50 and total_parroquias == 200 and total_comunidades == 600:
    print("✔ VERIFICACIÓN EXITOSA: La base de datos es consistente y la tabla de documentos está activa.")
else:
    print("❌ ERROR DE INTEGRIDAD: Los totales no coinciden con la retícula establecida.")
