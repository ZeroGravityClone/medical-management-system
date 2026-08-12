
# Sistema de Gestión Médica Inteligente

Este proyecto es un sistema de gestión médica desarrollado de forma nativa en **PySide6 (Qt6)** utilizando **SQLite** como motor de persistencia relacional. Diseñado específicamente para optimizar la velocidad de registro clínico, el sistema integra automatización asistida por Inteligencia Artificial (NLP con Groq), generación desatendida de documentos PDF e ingeniería de red privada (SD-WAN) para evadir restricciones de geolocalización.

---

## 🚀 Características Principales

*   **Interfaz Moonlight Qt:** Diseño de interfaz unificado, reactivo y de alta definición (dark theme) con un sistema de navegación basado en Sidebar y Topbar adaptado para un rendimiento óptimo en Linux/Crouton.
*   **Automatización Asistida por IA (Groq):**
    *   **Llenado Inteligente de Datos:** Permite al operador ingresar información en lenguaje natural para que el modelo `llama-3.1-8b-instant` estructure la información de registro clínico de forma asíncrona mediante hilos `QThread`.
    *   **Generador de Recetarios e Indicaciones:** Transcribe e interpreta indicaciones informales del médico a una estructura JSON que es compilada físicamente en un PDF.
    *   **Simulación Académica:** Soporta comandos rápidos de prueba (ej: `"inventa un paciente"`, `"receta de prueba"`) con datos de prueba realistas para demostraciones.
*   **Generación de Documentos (ReportLab):** Compilación y exportación automatizada de planillas oficiales de registro e indicaciones en formato PDF, almacenadas de forma organizada en la bóveda digital.
*   **Base de Datos y Consistencia Territorial:**
    *   Base de datos relacional SQLite con una retícula geográfica estricta de 4 niveles de cascada reactiva: **Estado ➔ Municipio ➔ Parroquia ➔ Comunidad** (600 registros geográficos libres de duplicados y huérfanos).
    *   Auto-completado unificado (`QCompleter`) en búsquedas por nombre o cédula con tolerancia a formatos (soporte para búsquedas con o sin guion de nacionalidad).
*   **Control de Accesos por Roles (RBAC):** Privilegios diferenciados para perfiles **ADMIN** y **GUEST** con medidas de protección de seguridad interna.
*   **Bypass de Geolocalización (SD-WAN):** Enrutamiento seguro y privado de peticiones de IA por medio de un túnel **ZeroTier** configurado como proxy privado sobre un servidor remoto, evitando bloqueos por IP geográfica.

---

## 📁 Estructura de la Arquitectura

El proyecto está organizado bajo una estructura modular que separa las responsabilidades de datos, lógica y presentación:

```text
medical-management-system/
│
├── assets/                     # Recursos estáticos (logos, fondos)
│
├── db/
│   ├── init_db.py              # Inicializador físico de base de datos y esquema
│   └── sistema_medico.db       # Archivo de base de datos SQLite activo
│
├── repositories/
│   ├── pacientes_repository.py  # CRUD y consultas de pacientes y documentos en SQLite
│   └── catalogos_repository.py  # Consultas indexadas y cascadas de geografía
│
├── services/
│   ├── ai_parser_service.py    # Servicio asíncrono de NLP para registro
│   ├── recetario_worker.py     # Servicio asíncrono de NLP para recetario médico
│   ├── pdf_generator.py        # Motor gráfico ReportLab (Planillas y Recetas)
│   └── document_service.py     # Orquestador unificado de almacenamiento y persistencia de PDF
│
├── ui_qt/
│   ├── views/
│   │   ├── registro_pacientes.py  # Formulario modular en dos columnas
│   │   └── importar_ia_dialog.py  # Diálogo de entrada de texto libre para IA
│   ├── main_window.py          # Ventana principal del Dashboard (Sidebar/Topbar)
│   ├── recetario_ia_dialog.py  # Panel de recetario y buscador de historial clínico
│   ├── asistente_ia_dialog.py  # Diálogo de chat asistencial general
│   └── styles.qss              # Hoja de estilos global unificada de Moonlight Qt
│
├── boveda_digital/             # Directorio de almacenamiento físico de PDFs por paciente (auto-generado)
├── insertar en labd.py         # Script de depuración e inserción geográfica relacional
├── requirements.txt            # Dependencias del proyecto
└── main.py                     # Punto de entrada de la aplicación (Event Loop principal)


---

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.9+
*   **GUI Framework:** PySide6 (Qt 6)
*   **Database:** SQLite 3
*   **IA API:** Groq SDK (Llama 3.1 8B / gpt-oss-20b)
*   **PDF Compiler:** ReportLab 4.x
*   **HTTP/Proxy Client:** HTTPX
*   **Red Virtual:** ZeroTier One

---

## 🔧 Guía de Instalación y Configuración Paso a Paso

### 1. Clonar el repositorio y acceder a la rama de arquitectura
```bash
git clone https://github.com/ZeroGravityClone/medical-management-system.git
cd medical-management-system
git checkout refactor-architecture
```

### 2. Configurar el entorno virtual de Python
Crea y activa el entorno de desarrollo correspondiente para aislar las librerías:

*   **En Linux (Debian 11 / Crouton):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
*   **En Windows 10 (Desarrollo local):**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```

### 3. Instalar dependencias optimizadas
Instala las librerías requeridas. En entornos Linux estables como Debian 11, se fija la versión `PySide6==6.4.3` para garantizar la compatibilidad con la biblioteca de sistema `glibc`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🛡️ Configuración del Bypass Geográfico de IA (Opcional)

Si ejecutas la aplicación desde una región geográficamente restringida por Groq (como Venezuela) y tienes un túnel **ZeroTier** activo conectado a tu **Shadow PC (Windows)**, puedes configurar tu propio nodo proxy privado de alta velocidad para redirigir las peticiones de la IA.

### Paso A: Levantar el servidor Proxy en tu Shadow PC (Windows)
1.  Abre una terminal (`PowerShell` o `cmd`) en tu Shadow PC e instala el servidor proxy ligero:
    ```powershell
    pip install proxy.py
    ```
2.  Inicia el servidor para que escuche en todas las interfaces a través del puerto `8899`:
    ```powershell
    proxy --hostname 0.0.0.0 --port 8899
    ```
3.  Identifica la IP IPv4 asignada a tu adaptador de red de **ZeroTier** en el Shadow PC (ejemplo: `10.147.15.22`).

### Paso B: Configurar las variables en la Chromebook (Debian)
Crea un archivo llamado **`.env`** en la raíz de tu proyecto e ingresa tu API Key de Groq y la ruta de red de tu proxy de ZeroTier:

```env
# Clave de API de Groq
GROQ_API_KEY=tu_gsk_de_groq_aqui

# Proxy de ZeroTier apuntando a tu Shadow PC (Comenta o elimina esta línea si no requieres proxy)
PROXY_URL=http://10.147.15.22:8899
```

---

## 💾 Inicialización de la Base de Datos y Ejecución

### 1. Poblar la base de datos relacional
Para limpiar registros antiguos e inyectar el catálogo territorial de Venezuela de 600 registros de forma jerárquica y coherente, ejecuta el script unificado de semillas:

```bash
python "insertar en labd.py"
```

### 2. Ejecutar la aplicación
Arranca la aplicación iniciando el ciclo de eventos principal de PySide6:

```bash
python main.py
```

---

## 🔑 Credenciales por Defecto del Sistema

Para el inicio de sesión inicial en la interfaz de acceso de Moonlight:

*   **Usuario:** `ADMIN`
*   **Contraseña:** `1234`
*   **Rol:** `ADMIN`
```
```
