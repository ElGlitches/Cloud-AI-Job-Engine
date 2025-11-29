import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from gspread_formatting import (
    DataValidationRule, BooleanCondition, set_data_validation_for_cell_range,
    format_cell_ranges, CellFormat, set_frozen
)
from .config import SCOPES, SHEET_NAME 
import time

ENCABEZADOS = [
    "Título", "Empresa", "Ubicación", "Modalidad", "Nivel", "Jornada", "URL",
    "Salario", "Estado", "Fecha de Registro", "Fecha Publicación", "Prioridad", "Descripción",
    "Match %", "Razón Match"
]

ESTADOS = ["Postulando", "Entrevista", "Rechazado", "Contratado", "Sin respuesta", "Descartado"]

def obtener_urls_existentes(sheet):
    """
    Obtiene un set con todas las URLs que ya están registradas en la hoja.
    Útil para filtrar antes de procesar.
    """
    try:
        data = sheet.get_all_values()
        urls = [row[6] for row in data[1:] if len(row) > 6 and row[6]]
        return set(urls)
    except Exception as e:
        print(f"Advertencia: No se pudieron cargar URLs existentes: {e}")
        return set()

def _aplicar_formato_y_validaciones(sheet):
    """Aplica el formato, filtro, congelación y validación de datos a la hoja."""
    
    set_frozen(sheet, rows=2)
    sheet.set_basic_filter()
    
    regla = DataValidationRule(BooleanCondition("ONE_OF_LIST", ESTADOS), showCustomUi=True)
    set_data_validation_for_cell_range(sheet, "I3:I10000", regla)
    
    format_cell_ranges(sheet, [("A2:M2", CellFormat(textFormat={"bold": True}))])
    print("Formato y validaciones aplicadas.")

def aplanar_y_normalizar(resultados_crudos):
    """
    Convierte la lista de resultados de las búsquedas en una única lista de diccionarios normalizados.
    """
    vacantes_normalizadas = []
    
    if resultados_crudos:
        print(f"DEBUG APLANAR: El primer resultado crudo es de tipo: {type(resultados_crudos[0])}")
    
    for item in resultados_crudos: 
        if item is None:
            continue
        
        if isinstance(item, list):
            vacantes_normalizadas.extend(item)
        elif isinstance(item, dict):
            vacantes_normalizadas.append(item)
        else:
            print(f"DEBUG APLANAR: Tipo de dato inesperado encontrado: {type(item)}")
            
    vacantes_limpias = []
    for vacante in vacantes_normalizadas:
        vacante['url'] = vacante.get('url', '') 
        vacante['descripcion'] = vacante.get('descripcion', '') 
        
        vacantes_limpias.append(vacante)

    print(f"DEBUG APLANAR: Vacantes normalizadas listas para deducción: {len(vacantes_limpias)}")
    
    return vacantes_limpias

def conectar_sheets():
    """Establece la conexión, abre/crea el archivo y la hoja de vacantes."""
    
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    cliente = gspread.authorize(creds)

    sh = None
    for _ in range(3):
        try:
            try:
                sh = cliente.open(SHEET_NAME)
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"No se encontró '{SHEET_NAME}', creando nuevo archivo en Drive...")
                sh = cliente.create(SHEET_NAME)
            break
        except Exception as e:
            if "503" in str(e):
                print("Google Sheets no disponible, reintentando...")
                time.sleep(3)
            else:
                raise
    else:
        raise RuntimeError("No se pudo conectar con Google Sheets después de varios intentos.")

    hojas = [ws.title for ws in sh.worksheets()]
    if "Vacantes" in hojas:
        return sh.worksheet("Vacantes")
    else:
        print("Creando hoja 'Vacantes' dentro del archivo...")
        return sh.add_worksheet("Vacantes", rows=200, cols=len(ENCABEZADOS))


def preparar_hoja(sheet):
    """
    Asegura que la hoja tenga los encabezados correctos y el formato base.
    """
    datos = sheet.get_all_values()
    
    if len(datos) < 2 or datos[1][:len(ENCABEZADOS)] != ENCABEZADOS:
        sheet.clear()
        print("Hoja limpiada. Insertando nuevos encabezados y formato.")
        sheet.update("A1", [[f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]])
        sheet.append_row(ENCABEZADOS)
        
        _aplicar_formato_y_validaciones(sheet)
    else:
        sheet.update("A1", [[f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]])
        _aplicar_formato_y_validaciones(sheet)


def actualizar_sheet(sheet, ofertas: list[dict]):
    """
    Añade nuevas vacantes a la hoja, anulando la deduplicación temporalmente 
    para forzar la inserción y depurar el campo URL.
    """
    
    existentes = obtener_urls_existentes(sheet)

    nuevas_filas = []

    for o in ofertas:
        url = o.get("url")

        if url and url in existentes:
             continue 

        nuevas_filas.append([
            o.get("titulo", ""),
            o.get("empresa", ""),
            o.get("ubicacion", ""),
            o.get("modalidad", ""),
            o.get("nivel", ""),
            o.get("jornada", ""),
            o.get("url", ""),
            o.get("salario", ""),
            "",
            o.get("fecha_busqueda", ""),
            o.get("fecha_publicacion", ""),
            o.get("prioridad", ""),
            o.get("descripcion", ""),
            o.get("match_percent", ""),
            o.get("match_reason", "")
        ])

    if nuevas_filas:
        sheet.append_rows(nuevas_filas)
        print(f"{len(nuevas_filas)} nuevas vacantes agregadas.")
    else:
        print("No hay nuevas vacantes para agregar.")


def registrar_actualizacion(sheet):
    """Actualiza la celda A1 con la fecha y hora actuales."""
    valor = f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    sheet.update("A1", [[valor]])
    print("Fecha de actualización registrada.")