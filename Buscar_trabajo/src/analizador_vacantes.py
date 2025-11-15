# src/analizador_vacantes.py (Versión Gemini)

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
def analizar_vacante(desc: str) -> str:
    """
    Analiza una descripción de vacante usando la API de Gemini.
    Incluye lógica de reintento con espera gradual.
    """
    
    # 1. Validación de Entrada
    if not desc or len(desc) < 20:
        return "Descripción demasiado corta para analizar."

    # 2. Ingeniería de Prompt
    prompt = (
        "Eres un analista de datos experto en mercado laboral. Tu tarea es analizar "
        "una descripción de trabajo y estructurar el resumen."
        "Necesitas identificar 3 elementos clave de la vacante, siguiendo este formato JSON estrictamente: "
        
        "{ "
        "  \"seniority\": [SENIORITY], "
        "  \"skills\": [SKILL_1, SKILL_2, SKILL_3], "
        "  \"resumen\": [BREVE_RESUMEN]"
        "}"
        
        "\n\nInstrucciones Clave:"
        "1. **Seniority:** Determina el nivel. Si no es claro, usa 'Mid'. Opciones: Junior, Mid, Senior, Lead."
        "2. **Skills:** Lista los 3 requisitos técnicos más frecuentes y MÁS importantes. Usa nombres cortos (ej., 'AWS', 'Python', 'Terraform')."
        "3. **Resumen:** Crea un resumen de la función en 15 palabras o menos."
        f"\n\nDESCRIPCIÓN DE LA VACANTE: {desc}"
    )

    # 3. Llamada a la API de Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[prompt]
    )
    
    # 4. Devolver resultado
    return response.text

