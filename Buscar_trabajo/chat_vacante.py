import os
import sys
import glob
import time
import json
from src.asesor import iniciar_chat, generar_pack_postulacion
from src.sheets_manager import conectar_sheets
from src.analizador_vacantes import analizar_vacante

def obtener_vacantes_pendientes(sheet):
    """Obtiene vacantes con Match % = 'Pendiente' o vacío."""
    # Usamos get_all_values para evitar error de "duplicate headers" si hay columnas vacías
    todas_las_filas = sheet.get_all_values()
    
    # La fila 1 es metadata ("Última actualización..."), la fila 2 son los HEADERS
    if len(todas_las_filas) < 3:
        return []
        
    headers = todas_las_filas[1]
    data = []
    
    # Mapeo manual (Datos desde fila 3 en adelante)
    for i, row in enumerate(todas_las_filas[2:]):
        item = {}
        for j, h in enumerate(headers):
            if h and j < len(row): # Solo columnas con nombre
                item[h] = row[j]
        
        # Agregar índice real (i + 3 porque row 1 metadata, row 2 headers, i0 based)
        item["_row_idx"] = i + 3
        data.append(item)
    
    pendientes = []
    
    for row in data:
        start_date = row.get("Fecha de Registro", "")
        # Filtrado simple: Si no tiene Match % calculado o dice Pendiente
        match_val = str(row.get("Match %", "")).strip()
        
        # Lógica: Si es Pendiente, vacio, o 0.
        if match_val in ["Pendiente", "", "0"]:
            pendientes.append(row)
            
    # Ordenar las últimas primero
    return pendientes[::-1]

def procesar_vacante_seleccionada(vacante, sheet):
    """
    1. Analiza la vacante con IA
    2. Genera Pack
    3. Actualiza Sheet
    4. Retorna contexto para chat
    """
    print(f"\n🧠 Analizando a fondo: {vacante.get('Título')} @ {vacante.get('Empresa')}...")
    
    # 1. Análisis Técnico
    analisis_json = analizar_vacante(vacante.get("URL", ""), vacante.get("Título", ""))
    
    # Parsear para actualizar sheet
    try:
        data_analisis = json.loads(analisis_json)
        match_pct = data_analisis.get("match_percent", 0)
        
        # 2. Generar Pack (Carta, Tips)
        print("📝 Redactando estrategia de postulación...")
        pack_content = generar_pack_postulacion({
            "titulo": vacante.get("Título"),
            "empresa": vacante.get("Empresa"),
            "descripcion": "Revisar link para detalle", # El asesor ya tiene el contexto del análisis
            "url": vacante.get("URL"),
            "analisis_previo": analisis_json
        })
        
        # Guardar en archivo
        dir_reco = os.path.join(os.path.dirname(__file__), "recomendaciones")
        os.makedirs(dir_reco, exist_ok=True)
        filename = f"{vacante.get('Empresa')}_{vacante.get('Título')}.md".replace("/", "-").strip()
        filepath = os.path.join(dir_reco, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(pack_content)
            
        print(f"✅ Pack guardado en: recomendaciones/{filename}")
        
        # 3. Actualizar Sheet (Opcional, si queremos guardar el resultado)
        # Nota: Escribir en una celda específica requiere coordenadas.
        # Por simplicidad ahora, solo mostramos el resultado.
        print(f"🎯 Match IA calculado: {match_pct}%")
        
        return pack_content
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return None

def main():
    print("\n👔 ASESOR DE VACANTES 'A DEMANDA' 👔")
    print("---------------------------------------")
    print("Conectando con tu base de vacantes...")
    
    try:
        sheet = conectar_sheets()
        vacantes = obtener_vacantes_pendientes(sheet)
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return

    if not vacantes:
        print("✅ No hay vacantes pendientes de análisis (Match = Pendiente).")
        return

    print(f"\nSe encontraron {len(vacantes)} vacantes pre-filtradas por Keywords:")
    
    # Mostrar menú (Top 10 para no saturar)
    top_n = vacantes[:10]
    for i, v in enumerate(top_n):
        print(f"[{i+1}] {v.get('Título')} - {v.get('Empresa')} (📍 {v.get('Ubicación')})")

    # Selección
    try:
        sel = int(input("\nElige vacante a analizar (0 para salir): "))
        if sel == 0: return
        target_vacante = top_n[sel-1]
    except (ValueError, IndexError):
        print("Selección inválida.")
        return

    # Procesar
    contexto = procesar_vacante_seleccionada(target_vacante, sheet)
    
    if contexto:
        # Iniciar Chat
        print("\n💬 Iniciando Chat con el Asesor...")
        chat_session = iniciar_chat(contexto)
        
        print(f"\n🤖 Asesor: He estudiado la vacante de {target_vacante.get('Empresa')}. ¿Preparamos la entrevista o revisamos la carta?")
        
        while True:
            user_input = input("\n👤 Tú: ")
            if user_input.lower() in ["salir", "exit"]: break
            try:
                resp = chat_session.send_message(user_input)
                print(f"\n🤖 Asesor: {resp.text}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
