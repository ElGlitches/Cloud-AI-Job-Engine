from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type
)
from google import genai
from google.genai.errors import APIError # Para capturar errores 
from dotenv import load_dotenv # Para cargar la clave API desde .env
import os 
import time
from .utils import clean_json_response # Importar función de limpieza
from .perfil import PERFIL_USUARIO # 👈 Importar perfil del usuario

# ⚠️ CARGA EXPLÍCITA DEL ARCHIVO .env
load_dotenv() 

# Inicializa el cliente de Gemini. Lee la clave API del entorno.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 

# -------------------------------------------------------------
# 🤖 LÓGICA DE REINTENTO Y LLAMADA A LA API
# -------------------------------------------------------------

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60), 
    stop=stop_after_attempt(5), 
    # Reintentar SOLO si ocurre un error de API (Rate Limit, etc.)
    retry=(retry_if_exception_type(APIError)) 
)
def analizar_vacante(desc: str, titulo:str) -> str:
    """
    Analiza una descripción de vacante usando la API de Gemini.
    Incluye lógica de reintento con espera gradual.
    """
    
    # 1. Validación de Entrada
    if not desc or len(desc) < 20:
        return "Descripción demasiado corta para analizar."

    # 1. Ingeniería de Prompt y Definición de Tarea
    prompt = (
        "Eres un experto en reclutamiento IT. Tu tarea es analizar la siguiente vacante "
        "y compararla con el perfil del candidato proporcionado.\n"
        
        f"\n👤 PERFIL DEL CANDIDATO:\n{PERFIL_USUARIO}\n"
        
        f"\n📄 VACANTE A ANALIZAR:\n"
        f"TÍTULO: {titulo}\n"
        f"DESCRIPCIÓN: {desc}\n"
        
        "\nInstrucciones:"
        "\n1. Extrae los datos clave de la vacante."
        "\n2. Calcula un 'match_percent' (0-100) basado en qué tan bien encaja el perfil con la vacante."
        "\n3. Genera una 'match_reason' breve (max 15 palabras) explicando el puntaje."
        "\n4. Devuelve todo en JSON estricto."
    )
    
    # 2. Definición del Esquema JSON (Schema)
    # ¡IMPORTANTE! Este esquema debe coincidir con TUS ENCABEZADOS de Sheets (A:M)
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

    # 3. Llamada a la API de Gemini (Usando JSON Schema)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[prompt],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema # Pasamos el esquema para una salida estricta
        )
    )
    
    # 4. Devolver resultado limpio
    return clean_json_response(response.text)

