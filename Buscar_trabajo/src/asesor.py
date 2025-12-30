import os
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .utils import clean_json_response
from .perfil import get_candidate_prompt

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))




@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(APIError))
)
def generar_pack_postulacion(vacante: dict) -> str:
    """
    Genera un pack de postulación (Carta, Entrevista, Tips) para una vacante
    usando el CV del usuario.
    Retorna un string con formato Markdown.
    """
    titulo = vacante.get("titulo", "Puesto IT")
    empresa = vacante.get("empresa", "Empresa Confidencial")
    desc = vacante.get("descripcion", "")
    url = vacante.get("url", "No especificada")
    url = vacante.get("url", "No especificada")
    
    perfil_prompt = get_candidate_prompt()

    prompt = (
        f"Actúa como mi Headhunter Personal de Élite. No quiero consejos genéricos de chatbot. Quiero estrategia pura para ganar este puesto.\n\n"
        f"--- DATOS DE LA VACANTE ---\n"
        f"Empresa: {empresa}\n"
        f"Rol: {titulo}\n"
        f"Link: {url}\n"
        f"Descripción: {desc}\n\n"
        f"{perfil_prompt}\n"
        f"--- MENTALIDAD ---\n"
        f"Analiza esto como si tuvieras 'insider info'. Busca qué es lo que REALMENTE le duele a esta empresa (escalabilidad, deuda técnica, falta de liderazgo) basándote en la descripción.\n\n"
        f"--- ENTREGABLES ---\n"
        f"Genera un documento Markdown estratégico:\n\n"
        f"# [{titulo} en {empresa}]({url})\n\n"
        f"## 1. Diagnóstico Estratégico (The Hook)\n"
        f"- 🎯 **¿Qué les duele?**: Identifica el problema real (no lo obvio).\n"
        f"- 🔑 **Mi Llave Maestra**: ¿Qué experiencia exacta de mi CV resuelve ese dolor? (Cita proyectos míos específicos).\n"
        f"- ⚠️ **Red Flag / Gap**: ¿Qué excusa usarán para descartarme y cómo la desarmamos antes de la entrevista?\n\n"
        f"## 2. Cold Email de Alto Impacto (Para el Hiring Manager)\n"
        f"- Asunto: Corto, relevante y no clickbait.\n"
        f"- Cuerpo: 3 párrafos cortos. Párrafo 1: Contexto (vi tu búsqueda). Párrafo 2: Prueba social/Técnica (hice X, Y, Z). Párrafo 3: Call to Action (CTA) suave.\n"
        f"- Tono: Profesional pero conversacional, senior.\n\n"
        f"## 3. Preparación de Entrevista (Modo Hardcore)\n"
        f"- ❓ **Pregunta Trampa**: Esa pregunta difícil que seguro harán.\n"
        f"- ⭐ **Respuesta Ganadora**: Cómo responderla usando la técnica STAR con mis datos.\n"
        f"- 🗣️ **Pregunta 'Reverse Uno'**: Una pregunta tan buena que yo deba hacerles a ellos para que digan 'wow'.\n\n"
        f"## 4. Estrategia Salarial y Dudas\n"
        f"- Basado en el seniority pedido y skills, ¿tengo apalancamiento para negociar fuerte? (Sí/No y por qué).\n"
        f"- Sección interactiva: Pregúntame si hay algo ambiguo (ej: tech stack no claro) para que averigüemos antes de enviar.\n"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generando pack de postulación: {str(e)}"

def iniciar_chat(contexto_inicial: str):
    """
    Inicia una sesión de chat interactiva con el Asesor.
    Retorna el objeto chat.
    """
    try:
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=[
                genai.types.Content(
                    role="user",
                    parts=[genai.types.Part.from_text(
                        text=f"Hola. Este es el contexto de la vacante y mi perfil:\n{contexto_inicial}\n\n"
                        "A partir de ahora, responde como mi Asesor de Carrera. Sé breve y útil."
                    )]
                ),
                genai.types.Content(
                    role="model",
                    parts=[genai.types.Part.from_text(
                        text="Entendido. Soy tu Asesor de Carrera Senior. ¿En qué te puedo ayudar sobre esta vacante?"
                    )]
                )
            ]
        )
        return chat
    except Exception as e:
        print(f"Error iniciando chat: {e}")
        return None
