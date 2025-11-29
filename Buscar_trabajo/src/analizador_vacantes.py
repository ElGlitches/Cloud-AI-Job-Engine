from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type
)
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv
import os 
import time
from .utils import clean_json_response, cargar_texto_pdf
from .config import RUTA_CV

load_dotenv() 

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60), 
    stop=stop_after_attempt(5), 
    retry=(retry_if_exception_type(APIError)) 
)
def analizar_vacante(desc: str, titulo:str) -> str:
    """
    Analiza una descripción de vacante usando la API de Gemini.
    Incluye lógica de reintento con espera gradual.
    """
    
    if not desc or len(desc) < 20:
        return "Descripción demasiado corta para analizar."

    perfil_texto = cargar_texto_pdf(RUTA_CV)
    if not perfil_texto:
        perfil_texto = "No se encontró CV. Asumir perfil genérico de Desarrollador Python/Data."

    prompt = (
        "Eres un experto en reclutamiento IT. Tu tarea es analizar la siguiente vacante "
        "y compararla con el perfil del candidato proporcionado.\n"
        
        f"\nPERFIL DEL CANDIDATO:\n{perfil_texto}\n"
        
        f"\nVACANTE A ANALIZAR:\n"
        f"TÍTULO: {titulo}\n"
        f"DESCRIPCIÓN: {desc}\n"
        
        "\nInstrucciones:"
        "\n1. Extrae los datos clave de la vacante."
        "\n2. Calcula un 'match_percent' (0-100) siguiendo estas reglas:"
        "\n   - 90-100: Coincidencia perfecta (Python + ETL/Data + Cloud/AWS/GCP)."
        "\n   - 70-89: Buen match (Python o Backend fuerte, pero falta alguna tec específica)."
        "\n   - 40-69: Match parcial (Tecnologías relacionadas como SQL/Java/DevOps, pero no es el foco principal)."
        "\n   - 0-39: No compatible (Frontend puro, .NET, Mobile, o stack totalmente diferente)."
        "\n3. Genera una 'match_reason' breve (max 15 palabras) explicando el puntaje (ej: 'Stack Python/AWS ideal', 'Falta experiencia en React')."
        "\n4. Devuelve todo en JSON estricto."
    )
    
    schema = {
        "type": "object",
        "properties": {
            "empresa": {"type": "string", "description": "Nombre de la empresa."},
            "ubicacion": {"type": "string", "description": "Ciudad, País o 'Remoto'."},
            "modalidad": {"type": "string", "description": "Ej: 'Remoto', 'Híbrido', 'Presencial'."},
            "nivel": {"type": "string", "description": "Ej: 'Junior', 'Mid', 'Senior', 'Lead'."},
            "jornada": {"type": "string", "description": "Ej: 'Full-time', 'Part-time'."},
            "salario": {"type": "string", "description": "Rango salarial estimado (ej: $2000 - $3000) o 'No informado'."},
            "seniority_score": {"type": "integer", "description": "Puntuación de 1 a 100 de adecuación al perfil de automatización/backend."},
            "top_skills": {"type": "array", "items": {"type": "string"}, "description": "Lista de 3 requisitos técnicos clave."},
            "match_percent": {"type": "integer", "description": "Porcentaje de coincidencia (0-100) con el perfil del usuario."},
            "match_reason": {"type": "string", "description": "Explicación muy breve del match (ej: 'Falta experiencia en AWS')."},
        },
        "required": ["empresa", "ubicacion", "nivel", "salario", "top_skills", "match_percent", "match_reason"]
    }

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[prompt],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema
        )
    )
    
    return clean_json_response(response.text)

