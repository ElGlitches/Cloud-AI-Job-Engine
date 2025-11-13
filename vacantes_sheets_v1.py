import requests
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN ---
PALABRAS_CLAVE = ["python", "data", "automatización", "etl"]
URL_API = "https://www.getonbrd.com/api/v0/search/jobs?query={}"
SHEET_NAME = "vacantes"

# --- AUTENTICACIÓN GOOGLE ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
CREDENCIALES = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
cliente = gspread.authorize(CREDENCIALES)
sheet = cliente.open(SHEET_NAME).sheet1

# --- FUNCIÓN BUSCAR VACANTES ---

def buscar_vacantes():
    ofertas = []
    for palabra in PALABRAS_CLAVE:
        response = requests.get(URL_API.format(palabra))
        if response.status_code == 200:
            data = response.json().get("data", [])
            for item in data:
                attrs = item.get("attributes", {})
                
                # Aseguramos que todos los valores sean strings simples
                titulo = str(attrs.get("title", "")).strip()
                empresa = str(attrs.get("company", {}).get("name", "")).strip()
                ubicacion = str(attrs.get("country_name", "")).strip()
                modalidad = str(attrs.get("modality", "")) if isinstance(attrs.get("modality"), str) else "N/A"
                url = "https://www.getonbrd.com" + str(attrs.get("permalink", ""))

                ofertas.append([titulo, empresa, ubicacion, modalidad, url])
    return ofertas



# def buscar_vacantes():
#     ofertas = []
#     for palabra in PALABRAS_CLAVE:
#         response = requests.get(URL_API.format(palabra))
#         if response.status_code == 200:
#             data = response.json().get("data", [])
#             for item in data:
#                 attrs = item.get("attributes", {})
#                 ofertas.append([
#                     attrs.get("title"),
#                     attrs.get("company", {}).get("name"),
#                     attrs.get("country_name"),
#                     attrs.get("modality"),
#                     "https://www.getonbrd.com" + attrs.get("permalink", "")
#                 ])
#     return ofertas

# --- ACTUALIZAR SHEETS ---
def actualizar_sheet(ofertas):
    registros_actuales = [fila[4] for fila in sheet.get_all_values()[1:]]  # URLs existentes
    nuevas = [o for o in ofertas if o[4] not in registros_actuales]

    if nuevas:
        sheet.append_rows(nuevas)
        print(f"✅ {len(nuevas)} nuevas vacantes agregadas a Google Sheets.")
    else:
        print("🔄 No hay nuevas vacantes para agregar.")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("Buscando vacantes...")
    resultados = buscar_vacantes()
    actualizar_sheet(resultados)
