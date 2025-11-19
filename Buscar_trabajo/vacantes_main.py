# vacantes_main.py

# --- 1. Importaciones ---
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Asegura que Python encuentre los módulos en la carpeta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importa las funciones de los módulos
from src.getonbrd import buscar_vacantes_getonbrd
# from src.linkedin_jobs import buscar_vacantes_linkedin
# from src.computrabajo import buscar_vacantes_computrabajo

# Importa el resto de tus utilidades
from src.sheets_manager import aplanar_y_normalizar, conectar_sheets, preparar_hoja, actualizar_sheet, registrar_actualizacion, obtener_urls_existentes
from src.analizador_vacantes import analizar_vacante
from src.config import PALABRAS_CLAVE


# Definición de las funciones de búsqueda activas
PORTALES_ACTIVOS = [
    ("GetOnBrd", buscar_vacantes_getonbrd),
    # ("LinkedIn", buscar_vacantes_linkedin),
    # ("Computrabajo", buscar_vacantes_computrabajo),
]


# --- 2. Funciones Lógicas ---

def recoleccion_de_vacantes() -> List[Dict[str, Any]]:
    """
    Recolecta vacantes usando concurrencia anidada (por portal y por keyword).
    """
    resultados_raw = []

    # 1. Crear todas las tareas (combinaciones de portal + keyword)
    tareas_con_keywords = []
    for portal_nombre, portal_func in PORTALES_ACTIVOS:
        for keyword in PALABRAS_CLAVE:
            # Tarea: (Nombre, Función, Keyword)
            tareas_con_keywords.append((portal_nombre, portal_func, keyword))

    print(f"-> Iniciando {len(tareas_con_keywords)} búsquedas en paralelo...")

    # 2. Ejecución Concurrente
    with ThreadPoolExecutor(max_workers=10) as executor:

        # ⚠️ CORRECCIÓN 1: Mapear la tarea al ejecutor. La clave es el objeto Future, el valor es (portal, keyword)
        future_to_task = {
            executor.submit(portal_func, keyword): (portal_nombre, keyword)
            for portal_nombre, portal_func, keyword in tareas_con_keywords
        }

        # 3. Recolección de resultados a medida que terminan
        for future in as_completed(future_to_task):
            portal_nombre, keyword = future_to_task[future] # ⚠️ CORRECCIÓN 2: Obtener el nombre de la tarea

            try:
                # El resultado aquí es la lista de vacantes devuelta por el scraper
                vacantes_encontradas = future.result()
                if vacantes_encontradas:
                    resultados_raw.extend(vacantes_encontradas)
                    # print(f"✅ Búsqueda exitosa en {portal_nombre} para '{keyword}'.")

            except Exception as e:
                # Capturar errores sin detener el script
                print(f"⚠️ ERROR: Falló la búsqueda en {portal_nombre} para '{keyword}'. Razón: {e}")

    return resultados_raw

def procesar_vacantes(resultados_raw: List[Dict[str, Any]], urls_existentes: set = set()) -> List[Dict[str, Any]]:
    """
    Normaliza, aplica la deduplicación, y realiza el análisis CONCURRENTE (IA).
    """

    # 1. Normalización y Aplanamiento
    vacantes_normalizadas = aplanar_y_normalizar(resultados_raw)

    vacantes_unicas = {}
    vacantes_sin_url = []

    # 2. DEDUPLICACIÓN y FILTRADO
    for vacante in vacantes_normalizadas:
        url = vacante.get("url")
        if url and url.strip():
            vacantes_unicas[url] = vacante
        else:
            # Retener vacantes sin URL para depuración
            vacantes_sin_url.append(vacante)

    vacantes_finales = list(vacantes_unicas.values()) + vacantes_sin_url

    print(f"✅ Vacantes ÚNICAS y procesadas: {len(vacantes_finales)}")

    # --- 2.5 FILTRADO DE YA EXISTENTES ---
    vacantes_a_analizar = []
    for v in vacantes_finales:
        if v.get("url") not in urls_existentes:
            vacantes_a_analizar.append(v)
        else:
            # Opcional: Imprimir si es muy verboso
            pass
            
    print(f"📉 Filtrado: {len(vacantes_finales) - len(vacantes_a_analizar)} vacantes ya existían. Nuevas a analizar: {len(vacantes_a_analizar)}")

    if not vacantes_a_analizar:
        print("✨ No hay vacantes nuevas para analizar.")
        return []

    # --- 3. ANÁLISIS CONCURRENTE (IA) ---
    print(f"-> Iniciando Análisis CONCURRENTE de {len(vacantes_a_analizar)} vacantes nuevas...")
    
    # max_workers=1: Procesamiento secuencial para evitar Rate Limiting
    with ThreadPoolExecutor(max_workers=1) as executor:

        futures = {
            executor.submit(
                analizar_vacante, 
                v.get("descripcion", ""), # Argumento 1: descripción
                v.get("titulo", "")       # Argumento 2: título
            ): v
            for v in vacantes_a_analizar
        }

        for future in as_completed(futures):
            vacante = futures[future]

            try:
                analisis_json_str = future.result(timeout=120)
                analisis_data = json.loads(analisis_json_str) # CONVERTIR JSON DE IA

                # 💡 LLENAR LOS CAMPOS DE LA VACANTE CON DATOS DE LA IA (SOLO SI FALTAN)
                campos_a_actualizar = ["empresa", "ubicacion", "modalidad", "nivel", "jornada", "salario"]
                valores_nulos = ["", "No indicado", "No Determinado", "N/A", "No informado", "None"]

                for campo in campos_a_actualizar:
                    valor_actual = vacante.get(campo, "")
                    valor_ia = analisis_data.get(campo, "")
                    
                    # Solo sobrescribir si el valor actual es "malo" y la IA trae algo
                    if str(valor_actual) in valores_nulos and valor_ia:
                        vacante[campo] = valor_ia

                # Campos de análisis estructurado (SIEMPRE ACTUALIZAR)
                vacante["seniority_estimado"] = analisis_data.get("nivel", "N/A") 
                vacante["fit_score"] = analisis_data.get("seniority_score", 0) 
                vacante["top_skills"] = ", ".join(analisis_data.get("top_skills", []))
                vacante["match_percent"] = analisis_data.get("match_percent", 0) # 👈 NUEVO
                vacante["match_reason"] = analisis_data.get("match_reason", "Sin motivo") # 👈 NUEVO

                # Guardar el JSON completo para auditoría o campos extra
                vacante["analisis"] = analisis_json_str
    
            except Exception as e:
                # Captura fallos persistentes de la API o errores de JSON parsing
                vacante["analisis"] = f"ERROR_IA: {e.__class__.__name__} - Revise .env o prompt"
                # 🛡️ Valores por defecto para evitar celdas vacías
                vacante["match_percent"] = 0
                vacante["match_reason"] = "Error en análisis IA"
                vacante["seniority_estimado"] = "No Determinado"
                vacante["top_skills"] = ""
                
    return vacantes_a_analizar


# --- 4. Ejecución principal ---
if __name__ == "__main__":
    F_NAME = "vacantes_main.py"
    print(f"[{F_NAME}]: Iniciando proceso de búsqueda de vacantes...")

    # 0. Preparar conexión y obtener historial (¡ANTES DE TODO!)
    try:
        print("\n🔌 Conectando a Google Sheets para obtener historial...")
        hoja = conectar_sheets()
        preparar_hoja(hoja)
        urls_existentes = obtener_urls_existentes(hoja)
        print(f"📚 {len(urls_existentes)} vacantes ya registradas en la base de datos.")
    except Exception as e:
        print(f"⚠️ Error al conectar con Sheets al inicio: {e}")
        urls_existentes = set()
        hoja = None # Se reintentará conectar al final si falló aquí

    # 1. Recolección de vacantes (¡En paralelo!)
    resultados_crudos = recoleccion_de_vacantes()
    print(f"\n✅ {len(resultados_crudos)} vacantes encontradas. Procesando...")

    # 2. Normalización, Deduplicación y Análisis (Pasando historial)
    vacantes_finales = procesar_vacantes(resultados_crudos, urls_existentes)

    # 3. Guardado en Google Sheets
    if vacantes_finales:
        try:
            print("\n💾 Iniciando guardado en Google Sheets...")
            
            if not hoja: # Si falló al inicio, reconectar
                hoja = conectar_sheets()
                preparar_hoja(hoja)

            # Pasar la lista final de vacantes
            actualizar_sheet(hoja, vacantes_finales)
            registrar_actualizacion(hoja)

        except Exception as e:
            print(f"❌ ERROR CRÍTICO al interactuar con Google Sheets: {e}")
    else:
        print("\n😴 No hay nada nuevo que guardar.")

    print("\nProceso finalizado.")