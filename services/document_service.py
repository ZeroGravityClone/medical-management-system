# services/document_service.py

import os
from datetime import datetime
from services.pdf_generator import generar_planilla_paciente, generar_receta_medica


class DocumentService:
    def __init__(self, pacientes_repo, base_dir="boveda_digital"):
        self.pacientes_repo = pacientes_repo
        self.base_dir = base_dir

    def registrar_planilla_registro(self, datos_paciente: dict) -> str:
        """Determina rutas físicas, genera el PDF de registro en su subcarpeta y asienta en DB."""
        cedula = datos_paciente.get("cedula")
        paciente = self.pacientes_repo.buscar_por_cedula(cedula)
        
        if not paciente:
            raise ValueError(f"No se encontró el paciente con cédula {cedula} para generar planilla.")

        patient_id = paciente["id"]
        
        # Subcarpeta: boveda_digital/paciente_{id}/registro/
        folder_planilla = os.path.join(self.base_dir, f"paciente_{patient_id}", "registro")
        if not os.path.exists(folder_planilla):
            os.makedirs(folder_planilla)

        nombre_archivo = f"planilla_registro_{patient_id}.pdf"
        ruta_archivo = os.path.abspath(os.path.join(folder_planilla, nombre_archivo))

        # Compilar físicamente el PDF
        generar_planilla_paciente(datos_paciente, ruta_archivo)

        # Persistencia en la tabla de documentos
        self.pacientes_repo.registrar_documento(
            patient_id=patient_id,
            tipo_documento="PLANILLA_REGISTRO",
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo
        )

        return ruta_archivo

    def registrar_receta_medica(self, receta_json: dict) -> str:
        """Genera la receta en la subcarpeta del paciente (Requiere registro obligatorio)."""
        cedula = receta_json.get("paciente", {}).get("cedula")
        paciente = self.pacientes_repo.buscar_por_cedula(cedula) if cedula else None

        # RESTRICCIÓN DE SEGURIDAD EXIGIDA
        if not paciente:
            raise ValueError("Restricción de Seguridad: El paciente debe estar registrado previamente en el sistema para generar su recetario.")

        patient_id = paciente["id"]
        
        # Subcarpeta: boveda_digital/paciente_{id}/recetas/
        folder_recetas = os.path.join(self.base_dir, f"paciente_{patient_id}", "recetas")
        if not os.path.exists(folder_recetas):
            os.makedirs(folder_recetas)

        fecha_hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"receta_{fecha_hoy}.pdf"
        ruta_archivo = os.path.abspath(os.path.join(folder_recetas, nombre_archivo))

        # Compilar físicamente el PDF de receta médica
        generar_receta_medica(receta_json, ruta_archivo)

        # Persistencia en DB
        self.pacientes_repo.registrar_documento(
            patient_id=patient_id,
            tipo_documento="RECETA_MEDICA",
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo
        )

        return ruta_archivo
