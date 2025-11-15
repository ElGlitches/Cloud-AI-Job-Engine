# --- Importaciones ---
import requests
import json
from .config import URL_GETONBRD, MAX_VACANTES_POR_PALABRA
from .utils import fecha_actual, calc_prioridad
# --- Fin Importaciones ---

def _procesar_resultados_getonbrd(json_data: list, keyword: str):
    """Analiza la respuesta JSON de GetOnBrd y extrae las vacantes."""
    vacantes_procesadas = []
    
    for item in json_data[:MAX_VACANTES_POR_PALABRA]: 
        
        # 💡 Acceso a secciones principales del JSON
        attributes = item.get("attributes", {})
        links = item.get("links", {})
        
        # --- EXTRACCIÓN DE CAMPOS ANIDADOS ---
        
        # Empresa: Anidada en attributes -> company -> data -> name (asumiendo que 'company' está resuelta)
        # NOTA: Como la compañía es un link a otra API, nos basaremos solo en el ID por ahora 
        # y usaremos un valor por defecto si no se puede acceder al nombre.
        company_id = attributes.get("company", {}).get("data", {}).get("id", "No indicado")        
        # Ubicación: Puede ser una ciudad, región o país. Usamos el campo de país o la ciudad si está disponible.
        location_data = attributes.get("countries", [attributes.get("location_name")]) 
        location_str = ", ".join(loc for loc in location_data if loc) if location_data else "No indicado"
        remote_modality = attributes.get("remote_modality", "no_remote")

        seniority_type = attributes.get("seniority", {}).get("data", {}).get("type", "no_seniority")

        # Salario: Mapeo de mínimo y máximo a una sola cadena
        min_salary = attributes.get("min_salary")
        max_salary = attributes.get("max_salary")
        salario_str = f"${min_salary} - ${max_salary}" if min_salary or max_salary else "No informado"

        vacante_dict = {
            # --- CORRECCIONES CRÍTICAS DEL MAPEO ---
            "titulo": attributes.get("title", "No indicado"), 
            "empresa": f"ID:{company_id}", 
            "modalidad": remote_modality.replace('_', ' ').title(), 
            "nivel": seniority_type.replace("seniority", "").capitalize(),
            "url": links.get("public_url", ""), 
            "salario": salario_str,
            "jornada": attributes.get("jornada", "Full-time"), # (F)
            "descripcion": attributes.get("description", ""), # (M)
            "fecha_busqueda": fecha_actual(), 
            "fecha_publicacion": attributes.get("published_at", ""),
            "prioridad": calc_prioridad(attributes.get("remote")), # Pasa el booleano 'remote'
            "keyword_buscada": keyword
        }
        
        vacantes_procesadas.append(vacante_dict)
        
    return vacantes_procesadas

# ⚠️ Función principal (debe recibir el argumento 'keyword')
def buscar_vacantes_getonbrd(keyword: str): 
    """Realiza la solicitud API a GetOnBrd para una única palabra clave."""
    
    vacantes_raw = []
    url = URL_GETONBRD.format(requests.utils.quote(keyword)) # Codificar keyword para la URL
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        #print(json.dumps(data['data'][0], indent=2))
        
        if 'data' in data and isinstance(data['data'], list):
            vacantes_raw.extend(
                _procesar_resultados_getonbrd(data['data'], keyword)
            )
            
    except requests.exceptions.RequestException as e:
        # Lanza una excepción para que sea capturada por el ThreadPoolExecutor
        raise Exception(f"Error HTTP en GetOnBrd para '{keyword}': {e}") 
        
    return vacantes_raw