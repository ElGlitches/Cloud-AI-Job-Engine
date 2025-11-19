# 🤖 Buscador de Vacantes con IA (Gemini)

Este proyecto automatiza la búsqueda de empleo en portales como **GetOnBrd** (y extensible a otros), analiza las vacantes utilizando **Google Gemini AI**, y las organiza en un **Google Sheet**.

Además, cuenta con un sistema de **"Fit Score"** que compara tu perfil profesional real con cada vacante para decirte qué tan buen match eres y por qué.

## 🚀 Características

- **Scraping Automático**: Busca vacantes por palabras clave (Python, AWS, etc.).
- **Filtrado Inteligente**:
    - Detecta vacantes ya procesadas para no gastar créditos de IA.
    - Filtra por antigüedad (ej: vacantes de hace más de 2 meses).
- **Análisis con IA (Gemini)**:
    - Extrae datos clave: Empresa, Salario, Stack Tecnológico.
    - **Fit Score**: Calcula un % de coincidencia con TU perfil.
    - **Feedback**: Te dice *por qué* haces match (o por qué no).
- **Google Sheets**: Guarda todo en una hoja de cálculo formateada y validada.

## 🛠️ Requisitos

- Python 3.9+
- Una cuenta de Google Cloud (para la API de Sheets).
- Una API Key de Google Gemini.

## 📦 Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone <tu-repo>
    cd Buscar_trabajo
    ```

2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Credenciales**:
    - **Google Sheets**: Coloca tu archivo `credentials.json` (Service Account) en la raíz.
    - **Gemini API**: Crea un archivo `.env` en la raíz con tu clave:
        ```env
        GEMINI_API_KEY=tu_api_key_aqui
        ```

4.  **Configurar tu Perfil**:
    - Renombra el archivo de ejemplo:
        ```bash
        mv src/perfil.py.example src/perfil.py
        ```
    - Edita `src/perfil.py` y pega tu CV o resumen de habilidades. **¡Esto es clave para que el Fit Score funcione!**

## ▶️ Uso

Simplemente ejecuta el script principal:

```bash
python vacantes_main.py
```

El script:
1.  Conectará a Google Sheets.
2.  Buscará vacantes nuevas.
3.  Las analizará con Gemini.
4.  Guardará los resultados en la hoja "Vacantes_Automatizadas".

## 📂 Estructura del Proyecto

- `vacantes_main.py`: Orquestador principal.
- `src/`:
    - `getonbrd.py`: Lógica de scraping para GetOnBrd.
    - `analizador_vacantes.py`: Conexión con Gemini e ingeniería de prompts.
    - `sheets_manager.py`: Manejo de Google Sheets (lectura/escritura/formato).
    - `perfil.py`: Tu información profesional (Ignorado por git).
    - `utils.py`: Utilidades generales.

## 🛡️ Privacidad

El archivo `src/perfil.py` contiene tus datos personales y está añadido a `.gitignore` para evitar que se suba accidentalmente a un repositorio público.
