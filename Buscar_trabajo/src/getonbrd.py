# --- Importaciones ---
import requests
import json
from .config import URL_GETONBRD, MAX_VACANTES_POR_PALABRA
from .utils import fecha_actual, calc_prioridad
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# --- Fin Importaciones ---

# --- Constante de Límite ---
LIMITE_ANTIGUEDAD_DIAS = 60 # Máximo 2 meses

def _procesar_resultados_getonbrd(json_data: list, keyword: str):
    """
    Analiza la respuesta JSON de GetOnBrd, aplica el filtro de antigüedad, 
    y extrae las vacantes con el mapeo corregido.
    """
    vacantes_procesadas = []
    
    # 1. CALCULAR FECHA LÍMITE
    fecha_limite = datetime.now() - timedelta(days=LIMITE_ANTIGUEDAD_DIAS)
    
    for item in json_data[:MAX_VACANTES_POR_PALABRA]: 
  
        # 💡 Acceso a secciones principales del JSON
        attributes = item.get("attributes", {})
        links = item.get("links", {})
        timestamp_publicacion = attributes.get("published_at")

        # ⚠️ FILTRO DE ANTIGÜEDAD (Si es demasiado viejo, lo saltamos)
        if timestamp_publicacion:
            fecha_publicacion = datetime.fromtimestamp(timestamp_publicacion)
            
            if fecha_publicacion < fecha_limite:
                continue # Omitir y pasar a la siguiente vacante
        # 💡 LÓGICA DE EXTRACCIÓN (Usando 'expand')
        
        # 1. EMPRESA
        company_data = attributes.get("company", {}).get("data", {})
        if company_data:
             empresa_candidata = company_data.get("attributes", {}).get("name", "No indicado")
        else:
             # Fallback al ID si falla la expansión
             parts = item_id.split('-')
             empresa_candidata = parts[-3] if len(parts) >= 3 else "No indicado"

        # 2. UBICACIÓN
        cities_data = attributes.get("location_cities", {}).get("data", [])
        regions_data = attributes.get("location_regions", {}).get("data", [])
        
        ubicacion_str = "No indicado"
        if cities_data:
            nombres_ciudades = [c.get("attributes", {}).get("name") for c in cities_data]
            nombres_ciudades = [n for n in nombres_ciudades if n] 
            ubicacion_str = ", ".join(nombres_ciudades) if nombres_ciudades else "No indicado"
        elif regions_data:
            nombres_regiones = [r.get("attributes", {}).get("name") for r in regions_data]
            nombres_regiones = [n for n in nombres_regiones if n] 
            ubicacion_str = ", ".join(nombres_regiones) if nombres_regiones else "No indicado"
        else:
            ubicacion_str = "Remoto" if attributes.get("remote") else "No indicado"

        # 3. NIVEL (Seniority)
        seniority_data = attributes.get("seniority", {}).get("data", {})
        if seniority_data:
            nivel_str = seniority_data.get("attributes", {}).get("name", "No indicado")
        else:
            nivel_str = "No indicado"
         # --- 3. CORRECCIÓN DE FECHA DE PUBLICACIÓN Y DESCRIPCIÓN ---
        
        # Fecha de Publicación: Se envía como un timestamp Unix (número grande).
        timestamp_publicacion = attributes.get("published_at")
        
        # Descripción: Contiene etiquetas HTML que deben eliminarse.
        descripcion_html = attributes.get("description", "")
        descripcion_limpia = BeautifulSoup(descripcion_html, 'html.parser').get_text(separator=' ', strip=True)

        # Salario: Mapeo de mínimo y máximo a una sola cadena
        min_salary = attributes.get("min_salary")
        max_salary = attributes.get("max_salary")
        salario_str = f"${min_salary} - ${max_salary}" if min_salary or max_salary else "No informado"

        vacante_dict = {
            # --- CAMPOS FÁCILES Y CRÍTICOS ---
            "titulo": attributes.get("title", "No indicado"), 
            "url": links.get("public_url", ""), 
            "descripcion": descripcion_limpia,
            
            # --- DATOS CRUDOS ADICIONALES ---
            "fecha_publicacion": fecha_publicacion.strftime("%Y-%m-%d"), # ✅ FECHA FORMATEADA
            
            # --- CAMPOS QUE LA IA DEBE LLENAR (VACÍOS POR DEFECTO) ---
            "empresa": empresa_candidata, # ✅ CAMPO MAPEADO
            "ubicacion": ubicacion_str,   # ✅ CAMPO MAPEADO
            "modalidad": "Remoto" if attributes.get("remote") else "Presencial", # ✅ CAMPO MAPEADO
            "nivel": nivel_str,           # ✅ CAMPO MAPEADO
            "jornada": attributes.get("modality", {}).get("data", {}).get("attributes", {}).get("name", "No indicado"), # ✅ JORNADA REAL (Full time, etc.)
            "salario": salario_str,       # ✅ CAMPO MAPEADO
            
            # --- CAMPOS AUXILIARES ---
            "fecha_busqueda": fecha_actual(),
            "prioridad": calc_prioridad(attributes.get("remote")), # ✅ PRIORIDAD CALCULADA
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