# src/utils.py

from datetime import datetime
# Importamos calc_prioridad si usa otra utilidad interna, pero aquí solo necesita datetime

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