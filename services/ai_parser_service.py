# services/ai_parser_service.py

import os
import json
from dotenv import load_dotenv
from groq import Groq

from PySide6.QtCore import QObject, Signal

# Cargar variables de entorno del archivo .env
load_dotenv()


class AIPatientParserWorker(QObject):
    datos_parseados = Signal(dict)
    error_ocurrido = Signal(str)
    finished = Signal()

    def __init__(self, texto_usuario):
        super().__init__()
        self.texto_usuario = texto_usuario

    def run(self):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("No se encontró la clave de API (GROQ_API_KEY) en el entorno.")

            client = Groq(api_key=api_key)

            # Prompt del sistema diseñado para parsear o INVENTAR datos coherentes con tu DB
            prompt_sistema = """
            Eres un asistente médico experto en transcripción de datos clínicos.
            Tu tarea es analizar el texto proporcionado por el usuario y extraer la información en un objeto JSON estricto.

            ========================================================================
            REGLA DE GENERACIÓN ALEATORIA (DUMMY DATA):
            Si el usuario te pide "datos aleatorios", "inventar un paciente", "test", "prueba", "rellena todo" o cualquier variante de simulación:
            Debes INVENTAR un paciente venezolano realista (apellidos, nombres, cédula, teléfono, dirección, etc.).
            
            Para garantizar la INTEGRIDAD REFERENCIAL con la base de datos SQLite, debes elegir obligatoriamente una de las siguientes combinaciones geográficas exactas (elige una al azar):
            
            Opción A:
            - "lugar_nacimiento": "LARA", "municipio": "IRIBARREN", "parroquia": "CATEDRAL", "comunidad": "CENTRO"
            
            Opción B:
            - "lugar_nacimiento": "DISTRITO CAPITAL", "municipio": "LIBERTADOR", "parroquia": "EL VALLE", "comunidad": "LONGARAY"
            
            Opción C:
            - "lugar_nacimiento": "MIRANDA", "municipio": "CHACAO", "parroquia": "CHACAO", "comunidad": "ALTAMIRA"
            
            Opción D:
            - "lugar_nacimiento": "CARABOBO", "municipio": "VALENCIA", "parroquia": "SAN JOSÉ", "comunidad": "EL VIÑEDO"
            
            No inventes combinaciones geográficas fuera de estas 4 opciones bajo ninguna circunstancia cuando generes datos de prueba.
            ========================================================================

            Esquema JSON obligatorio a retornar:
            {
              "nombres": "Nombres del paciente",
              "apellidos": "Apellidos del paciente",
              "nacionalidad": "V" o "E" o "J" (Por defecto 'V'),
              "cedula_numero": "Solo dígitos de la cédula",
              "fecha_nacimiento": "YYYY-MM-DD",
              "sexo": "Masculino" o "Femenino",
              "telefono": "Número telefónico",
              "lugar_nacimiento": "Estado de nacimiento (EN MAYÚSCULAS)",
              "municipio": "Municipio (EN MAYÚSCULAS)",
              "parroquia": "Parroquia (EN MAYÚSCULAS)",
              "comunidad": "Comunidad (EN MAYÚSCULAS)",
              "direccion": "Dirección detallada de habitación",
              "condicion": "Estable" o "Grave" o "Observación" (Por defecto 'Estable'),
              "consulta": "Medicina General" o "Emergencia de Adultos" o "Consulta de Control" o "Pediatría" o "Cardiología" o "Ginecología y Obstetricia" o "Traumatología"
            }

            Reglas de Parseo de Texto Libre (Cuando el usuario SÍ provee datos reales):
            1. Mapea los datos según el esquema.
            2. Si no se menciona un campo, devuélvelo como string vacío "".
            3. Si solo se menciona la edad (ej: 28 años), calcula el año de nacimiento asumiendo que el año actual es 2026.
            4. Retorna ÚNICAMENTE el objeto JSON. Sin explicaciones ni formato markdown.
            """

            # Llamada a Groq utilizando el modo JSON nativo (response_format)
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b", # Usando tu nuevo modelo de alto rendimiento
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": self.texto_usuario}
                ],
                temperature=0.4, # Subimos levemente la temperatura para permitir mejor creatividad en datos aleatorios
                response_format={"type": "json_object"}
            )

            raw_response = completion.choices[0].message.content
            datos = json.loads(raw_response)

            self.datos_parseados.emit(datos)

        except Exception as e:
            self.error_ocurrido.emit(str(e))
        
        finally:
            self.finished.emit()
