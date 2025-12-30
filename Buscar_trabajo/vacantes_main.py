import os
import sys
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.getonbrd import buscar_vacantes_getonbrd
from src.linkedin_jobs import buscar_vacantes_linkedin
from src.sheets_manager import aplanar_y_normalizar, conectar_sheets, preparar_hoja, actualizar_sheet, registrar_actualizacion, obtener_urls_existentes
from src.analizador_vacantes import analizar_vacante
from src.asesor import generar_pack_postulacion
from src.config import PALABRAS_CLAVE


PORTALES_ACTIVOS = [
    ("GetOnBrd", buscar_vacantes_getonbrd),
    ("LinkedIn", buscar_vacantes_linkedin),
    # ("Computrabajo", buscar_vacantes_computrabajo),
]


def recoleccion_de_vacantes() -> List[Dict[str, Any]]:
    """
    Recolecta vacantes usando concurrencia anidada (por portal y por keyword).
    """
    resultados_raw = []

    tareas_con_keywords = []
    for portal_nombre, portal_func in PORTALES_ACTIVOS:
        for keyword in PALABRAS_CLAVE:
            tareas_con_keywords.append((portal_nombre, portal_func, keyword))

    print(f"-> Iniciando {len(tareas_con_keywords)} búsquedas en paralelo...")

    with ThreadPoolExecutor(max_workers=10) as executor:

        future_to_task = {
            executor.submit(portal_func, keyword): (portal_nombre, keyword)
            for portal_nombre, portal_func, keyword in tareas_con_keywords
        }

        for future in as_completed(future_to_task):
            portal_nombre, keyword = future_to_task[future]

            try:
                vacantes_encontradas = future.result()
                if vacantes_encontradas:
                    resultados_raw.extend(vacantes_encontradas)

            except Exception as e:
                print(f"ERROR: Falló la búsqueda en {portal_nombre} para '{keyword}'. Razón: {e}")

    return resultados_raw

def procesar_vacantes(resultados_raw: List[Dict[str, Any]], urls_existentes: set = set()) -> List[Dict[str, Any]]:
    """
    Normaliza, aplica la deduplicación, y realiza el análisis CONCURRENTE (IA).
    """

    vacantes_normalizadas = aplanar_y_normalizar(resultados_raw)

    vacantes_unicas = {}
    vacantes_sin_url = []
    vacantes_descartadas = 0

    from src.utils import es_vacante_valida # Importación tardía para evitar ciclos si fuera necesario, o mover arriba

    for vacante in vacantes_normalizadas:
        # 0. FILTRO PREVIO (Exclusión/Inclusión)
        if not es_vacante_valida(vacante.get("titulo"), vacante.get("descripcion")):
            vacantes_descartadas += 1
            continue

        url = vacante.get("url")
        if url and url.strip():
            vacantes_unicas[url] = vacante
        else:
            vacantes_sin_url.append(vacante)
            
    print(f"🧹 Vacantes descartadas por filtro de palabras: {vacantes_descartadas}")

    vacantes_finales = list(vacantes_unicas.values()) + vacantes_sin_url

    print(f"Vacantes ÚNICAS y procesadas: {len(vacantes_finales)}")

    vacantes_a_analizar = []
    for v in vacantes_finales:
        if v.get("url") not in urls_existentes:
            vacantes_a_analizar.append(v)
        else:
            pass
            
    print(f"Filtrado: {len(vacantes_finales) - len(vacantes_a_analizar)} vacantes ya existían. Nuevas a analizar: {len(vacantes_a_analizar)}")

    if not vacantes_a_analizar:
        print("No hay vacantes nuevas para analizar.")
        return []

    # --- NUEVA LÓGICA: FILTRADO RÁPIDO (SIN IA) ---
    print(f"⚡ Filtrando {len(vacantes_a_analizar)} vacantes por palabras clave (Modo Rápido)...")
    
    # Palabras clave extra para validar relevancia (puedes añadir más aquí o leer del config)
    KEYWORDS_RELEVANTES = set([item.lower() for item in PALABRAS_CLAVE])
    
    vacantes_filtradas = []

    for vacante in vacantes_a_analizar:
        texto_completo = (vacante.get("titulo", "") + " " + vacante.get("descripcion", "")).lower()
        
        # Scoring simple
        score = 0
        matches = []
        for kw in KEYWORDS_RELEVANTES:
            if kw in texto_completo:
                score += 1
                matches.append(kw)
        
        # Umbral: Al menos 1 palabra clave fuerte
        if score > 0:
            vacante["match_percent"] = "Pendiente" # Se calculará en Chat Asesor
            vacante["match_reason"] = f"Keywords: {', '.join(matches[:3])}"
            vacante["seniority_estimado"] = "N/A"
            vacante["top_skills"] = ", ".join(matches)
            vacantes_filtradas.append(vacante)
        else:
             print(f"🗑️ Descartando vacante irrelevante: {vacante.get('titulo')}")
             # continue implícito al no hacer append
    
    # Actualizar la lista original para que el resto del script use solo las filtradas
    vacantes_a_analizar = vacantes_filtradas

    # --- FASE 2: GENERACIÓN DE PACK DE POSTULACIÓN (Asesor) ---
    print("\n🧠 Generando Packs de Postulación para candidatos fuertes (Match >= 70%)...")
    
    # Crear carpeta si no existe
    dir_recomendaciones = os.path.join(os.path.dirname(__file__), "recomendaciones")
    os.makedirs(dir_recomendaciones, exist_ok=True)

    for v in vacantes_a_analizar:
        match_pct = v.get("match_percent", 0)
        
        # Filtrar solo los buenos matches para no gastar tokens
        if isinstance(match_pct, (int, float)) and match_pct >= 70:
            empresa = v.get("empresa", "Empresa").replace("/", "-").strip()
            titulo = v.get("titulo", "Rol").replace("/", "-").strip()
            filename = f"{empresa}_{titulo}.md"
            filepath = os.path.join(dir_recomendaciones, filename)

            # Evitar regenerar si ya existe (opcional, pero ahorra dinero)
            if not os.path.exists(filepath):
                print(f"   ✨ Generando estrategia para: {v.get('titulo')} en {v.get('empresa')} ({match_pct}%)")
                try:
                    pack_content = generar_pack_postulacion(v)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(pack_content)
                except Exception as e:
                    print(f"   ⚠️ Error generando pack para {titulo}: {e}")
            else:
                print(f"   ✅ Pack ya existe: {filename}")

    return vacantes_a_analizar


if __name__ == "__main__":
    F_NAME = "vacantes_main.py"
    print(f"[{F_NAME}]: Iniciando proceso de búsqueda de vacantes...")

    try:
        print("\nConectando a Google Sheets para obtener historial...")
        hoja = conectar_sheets()
        preparar_hoja(hoja)
        urls_existentes = obtener_urls_existentes(hoja)
        print(f"{len(urls_existentes)} vacantes ya registradas en la base de datos.")
    except Exception as e:
        print(f"Error al conectar con Sheets al inicio: {e}")
        urls_existentes = set()
        hoja = None

    resultados_crudos = recoleccion_de_vacantes()
    print(f"\n{len(resultados_crudos)} vacantes encontradas. Procesando...")

    vacantes_finales = procesar_vacantes(resultados_crudos, urls_existentes)

    if vacantes_finales:
        try:
            print("\nIniciando guardado en Google Sheets...")
            
            if not hoja:
                hoja = conectar_sheets()
                preparar_hoja(hoja)

            actualizar_sheet(hoja, vacantes_finales)
            registrar_actualizacion(hoja)

        except Exception as e:
            print(f"ERROR CRÍTICO al interactuar con Google Sheets: {e}")
    else:
        print("\nNo hay nada nuevo que guardar.")

    print("\nProceso finalizado.")