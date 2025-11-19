from datetime import datetime

# --- 1. Configuración de Google Sheets ---
SHEET_NAME = "Vacantes_Automatizadas" 

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

PALABRAS_CLAVE = [
    # --- TUS FORTALEZAS (Lo que vende tu CV hoy) ---
    "Python",             # Tu lenguaje principal
    "Ingeniero de Datos", # Tu perfil actual (DataStage, ETL)
    "ETL",                # Específico para tu experiencia en Banca
    "Automatización",     # Tu mayor logro (Reducción 40% tiempo)
    "SQL",                # Base de todo tu trabajo
    
    # --- TU PROYECCIÓN TÉCNICA (Sin ser "Jefe") ---
    "DevOps",             # Por tu exp con Ansible/CI/CD (Mejor que "Arquitecto")
    "SRE",                # Por tu exp en Monitoreo/Estabilidad (Muy bien pagado)
    "Backend",            # Tu base general
    "AWS",                # Tu nube más fuerte
    
    # --- OPCIONALES / FILTROS ---
   # "Remoto"              # Si es prioridad
   # "hírido"
]

MAX_VACANTES_POR_PALABRA = 20 # Límite para cada keyword/portal

# 🌐 URLs Base para Scraping (Usar {} para formato de string)
URL_GETONBRD = "https://www.getonbrd.com/api/v0/search/jobs?query={}&expand=[\"company\",\"location_cities\",\"seniority\",\"modality\"]"
# URL_LINKEDIN = "..." 
# URL_COMPUTRABAJO = "..." 

