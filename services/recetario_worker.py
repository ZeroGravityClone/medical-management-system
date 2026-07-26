# services/recetario_worker.py

import os
import json
import httpx 
from dotenv import load_dotenv
from groq import Groq

from PySide6.QtCore import QObject, Signal

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)


class RecetarioIAWorker(QObject):
    receta_lista = Signal(dict)
    error_ocurrido = Signal(str)
    finished = Signal()

    def __init__(self, texto_indicaciones, nombre_paciente="", cedula_paciente=""):
        super().__init__()
        self.texto_indicaciones = texto_indicaciones
        self.nombre_paciente = nombre_paciente
        self.cedula_paciente = cedula_paciente

    def run(self):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("No se encontró la clave de API (GROQ_API_KEY) en el entorno.")

            # Configuración de proxy
            proxy_url = os.getenv("PROXY_URL")
            if proxy_url:
                print(f"\n[DEBUG IA] Conectando a Groq a través de Proxy local: {proxy_url}")
                h_client = None
                try:
                    h_client = httpx.Client(proxy=proxy_url)
                except TypeError:
                    try:
                        h_client = httpx.Client(proxies=proxy_url)
                    except TypeError:
                        os.environ["HTTP_PROXY"] = proxy_url
                        os.environ["HTTPS_PROXY"] = proxy_url
                        os.environ["ALL_PROXY"] = proxy_url
                        h_client = httpx.Client()
                
                client = Groq(api_key=api_key, http_client=h_client)
            else:
                print("\n[DEBUG IA] Conectando a Groq de forma DIRECTA (Sin Proxy)")
                client = Groq(api_key=api_key)

            # Prompt enriquecido con reglas de simulación clínica
            prompt_sistema = """
            Eres un asistente farmacológico experto. Tu tarea es analizar las indicaciones del usuario y estructurarlas en un JSON de receta médica oficial.

            ========================================================================
            REGLA DE GENERACIÓN ALEATORIA (SIMULACIÓN CLÍNICA):
            Si el usuario te escribe "inventa una receta", "receta aleatoria", "prueba", "test", "simular receta" o variantes:
            Debes INVENTAR un caso médico completamente ficticio pero clínicamente coherente y realista para una patología común (por ejemplo: Hipertensión, Diabetes Tipo 2, Amigdalitis, Lumbalgia o Gripe común).
            
            1. Si no se proporcionaron nombre ni cédula del paciente, invéntalos con formato venezolano realista (ej. 'V-15882119' y 'Carlos Mendoza').
            2. Prescribe de 1 a 3 fármacos que guarden estricta relación y coherencia con la patología seleccionada.
            3. Redacta de 2 a 3 indicaciones generales (reposo, dieta, hidratación) y de 2 a 3 advertencias de seguridad específicas.
            ========================================================================

            Esquema JSON estricto a retornar:
            {
              "paciente": {
                "nombre": "Nombre del paciente (Usa el provisto por el sistema o invéntalo si es simulación)",
                "cedula": "Cédula del paciente (Usa la provista por el sistema o invéntala si es simulación)"
              },
              "receta": {
                "medicamentos": [
                  {
                    "nombre": "Nombre comercial o genérico estandarizado del medicamento",
                    "dosis": "Dosis exacta (ej: 500mg, 1 tableta, 5ml)",
                    "frecuencia": "Frecuencia de administración (ej: cada 8 horas, cada 12 horas, una vez al día)",
                    "duracion": "Duración total del tratamiento (ej: por 5 días, por 7 días)"
                  }
                ],
                "indicaciones_generales": [
                  "Recomendación no farmacológica (ej: reposo absoluto por 3 días)",
                  "Recomendación no farmacológica (ej: tomar abundante líquido)"
                ],
                "advertencias": [
                  "No automedicarse.",
                  "Seguir control médico.",
                  "Suspender el tratamiento en caso de presentar reacciones adversas y consultar a su médico."
                ]
              },
              "diagnostico_resumido": "Diagnóstico abreviado o síntoma principal (ej: Amigdalitis aguda, Hipertensión arterial)",
              "fecha_emision": "Fecha de hoy en formato DD/MM/YYYY"
            }

            Reglas Críticas:
            1. No inventes compuestos químicos extraños. Escribe nombres comerciales o genéricos estables y conocidos.
            2. Devuelve ÚNICAMENTE el objeto JSON sin introducciones ni formato markdown.
            """

            user_content = f"Paciente: {self.nombre_paciente}, Cédula: {self.cedula_paciente}.\nIndicaciones: {self.texto_indicaciones}"

            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            raw_response = completion.choices[0].message.content
            receta_json = json.loads(raw_response)

            self.receta_lista.emit(receta_json)

        except Exception as e:
            self.error_ocurrido.emit(str(e))
        
        finally:
            self.finished.emit()
