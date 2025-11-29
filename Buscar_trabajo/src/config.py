from datetime import datetime

SHEET_NAME = "Vacantes_Automatizadas" 

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

PALABRAS_CLAVE = [
    "Python",
    "Ingeniero de Datos",
    "ETL",
    "Automatización",
    "SQL",
    "DevOps",
    "SRE",
    "Backend",
    "AWS",
]

MAX_VACANTES_POR_PALABRA = 20

URL_GETONBRD = "https://www.getonbrd.com/api/v0/search/jobs?query={}&expand=[\"company\",\"location_cities\",\"seniority\",\"modality\"]"

RUTA_CV = "cv.pdf" 

