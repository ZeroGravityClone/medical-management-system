# services/document_service.py

import os
from datetime import datetime
from services.pdf_generator import generar_planilla_paciente, generar_receta_medica


class DocumentService:
    def __init__(self, pacientes_repo, base_dir="boveda_digital"):
        self.pacientes_repo = pacientes_repo
        self.base_dir = base_dir

    def registrar_planilla_registro(self, datos_paciente: dict) -> str:
        """Determina rutas físicas, genera el PDF de registro y asienta persistencia."""
        cedula = datos_paciente.get("cedula")
        paciente = self.pacientes_repo.buscar_por_cedula(cedula)
        
        if not paciente:
            raise ValueError(f"No se encontró el paciente con cédula {cedula} para generar planilla.")

        # La base de datos es la fuente de verdad (Rutas por ID)
        patient_id = paciente["id"]
        
        folder_paciente = os.path.join(self.base_dir, f"paciente_{patient_id}")
        if not os.path.exists(folder_paciente):
            os.makedirs(folder_paciente)

        nombre_archivo = f"planilla_registro_{patient_id}.pdf"
        ruta_archivo = os.path.abspath(os.path.join(folder_paciente, nombre_archivo))

        # Compilar físicamente el PDF
        generar_planilla_paciente(datos_paciente, ruta_archivo)

        # Persistencia en la tabla de documentos unificada
        self.pacientes_repo.registrar_documento(
            patient_id=patient_id,
            tipo_documento="PLANILLA_REGISTRO",
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo
        )

        return ruta_archivo

    def registrar_receta_medica(self, receta_json: dict) -> str:
        """Determina rutas físicas, genera la receta y asienta persistencia (Admite Pacientes Externos NULL)."""
        cedula = receta_json.get("paciente", {}).get("cedula")
        
        # Intentamos obtener el ID del paciente si está registrado
        paciente = self.pacientes_repo.buscar_por_cedula(cedula) if cedula else None
        patient_id = paciente["id"] if paciente else None

        # Resolver ruta física
        if patient_id:
            folder = os.path.join(self.base_dir, f"paciente_{patient_id}")
        else:
            folder = os.path.join(self.base_dir, "externos")

        if not os.path.exists(folder):
            os.makedirs(folder)

        fecha_hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"receta_{fecha_hoy}.pdf"
        ruta_archivo = os.path.abspath(os.path.join(folder, nombre_archivo))

        # Compilar físicamente el PDF de receta médica
        generar_receta_medica(receta_json, ruta_archivo)

        # Persistencia (Admite patient_id = None si es externo)
        self.pacientes_repo.registrar_documento(
            patient_id=patient_id,
            tipo_documento="RECETA_MEDICA",
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo
        )

        return ruta_archivo
