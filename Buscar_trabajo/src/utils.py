from datetime import datetime
from pypdf import PdfReader
# Importamos calc_prioridad si usa otra utilidad interna, pero aquí solo necesita datetime

def cargar_texto_pdf(ruta_pdf: str) -> str:
    """
    Lee el texto de un archivo PDF.
    Retorna el texto extraído o una cadena vacía si hay error.
    """
    try:
        reader = PdfReader(ruta_pdf)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() + "\n"
        return texto.strip()
    except Exception as e:
        print(f"⚠️ Error al leer PDF ({ruta_pdf}): {e}")
        return ""

def fecha_actual():
    """Devuelve la fecha actual en formato YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")

def normalizar_texto(texto):
    """Limpia texto de None o espacios extra"""
    if not texto:
        return ""
    return str(texto).strip()

def calc_prioridad(modalidad):
    """Asigna prioridad según modalidad u otras reglas"""
    
    # 💡 CORRECCIÓN: Convierte el valor a cadena antes de usar .lower()
    # Además, si es booleano, nos basaremos en el valor True/False directamente.
    
    if modalidad is True: # Si recibimos el booleano True (es remoto)
        return "Alta"
    if modalidad is False: # Si recibimos el booleano False (no es remoto)
        return "Baja"
        
    # Si es una cadena (comportamiento original, ej: "remoto", "híbrido")
    modalidad_str = str(modalidad or "").lower()
    
    if "remoto" in modalidad_str:
        return "Alta"
    elif "híbrido" in modalidad_str:
        return "Media"
    return "Baja"

def clean_json_response(text: str) -> str:
    """
    Limpia la respuesta de la IA para extraer solo el JSON válido.
    Elimina bloques de código markdown (```json ... ```).
    """
    if not text:
        return ""
    
    # Eliminar envoltorios de markdown
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    return cleaned.strip()