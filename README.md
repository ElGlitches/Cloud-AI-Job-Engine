# Enterprise Cloud & Data Automation Toolkit (AI Job Search Engine) 🚀

**Un motor de búsqueda y análisis de mercado laboral potenciado por Inteligencia Artificial.**

Este proyecto no es solo un script; es una plataforma de ingeniería de datos diseñada para automatizar la búsqueda, filtrado y análisis de oportunidades laborales en múltiples portales (LinkedIn, GetOnBrd, etc.), utilizando modelos LLM (Gemini) para determinar el "match" real con el perfil del candidato.

## 🎯 Objetivo del Proyecto

Optimizar el proceso de búsqueda de empleo reduciendo el tiempo de revisión manual en un **90%**. El sistema orquesta:
1.  **Extracción de Datos:** Scraping ético y multi-hilo de ofertas en tiempo real.
2.  **Análisis Cognitivo:** Un agente de IA lee cada descripción, detecta stack tecnológico, seniority y salario, y lo compara con tu CV.
3.  **Reporting Automatizado:** Centralización de resultados en un Dashboard de Google Sheets con semáforos de prioridad.
4.  **Generación de Estrategia:** Creación automática de cartas de presentación y análisis de brechas para cada vacante relevante.

## 🛠️ Capacidades Destacadas (Architecture)

*   **Smart Scrapers (Backend):** Motores de extracción resilientes para LinkedIn y GetOnBrd.
*   **AI Analysis Core:** Pipeline de procesamiento que utiliza `Gemini 2.0 Flash` para estructurar datos no estructurados (descripciones de empleo).
*   **Zero-Touch Automation:** Sistema de ejecución desatendida vía Cron para búsquedas diarias automáticas.
*   **Data Integrity:** Validaciones automáticas, deduplicación y manejo de errores (Tenacity).
*   **Cloud Integration:** Sincronización automática con Google Workspace API.

## ⚙️ Configuración e Instalación

### 1. Prerrequisitos
- **Python 3.10** o superior.
- Una cuenta de **Google Cloud Platform** (para API de Sheets).
- Una API Key de **Google Gemini** (AI Studio).

### 2. Instalación de Dependencias
```bash
# 1. Clonar repositorio
git clone <url-del-repo>
cd Cloud-AI-Job-Engine

# 2. Crear entorno virtual (Recomendado)
python3 -m venv venv
source venv/bin/activate

# 3. Instalar librerías
pip install -r requirements.txt

# 4. Instalar navegadores para scraping
playwright install chromium
```

### 3. Configuración de Credenciales
El sistema requiere dos archivos clave en la raíz del proyecto para funcionar:

1.  **`.env`**: Variables de entorno para la IA.
    ```bash
    GEMINI_API_KEY="tu_api_key_aqui"
    ```

2.  **`credentials.json`**: Credencial de servicio de Google Cloud para acceder a Sheets.
    - *Debe tener permisos de edición sobre la hoja de cálculo definida en `config.py`.*

## 💻 Uso y Ejecución

### 1. Ejecución Manual Interactiva
Para una búsqueda guiada con opciones de menú:
```bash
python3 backend-services/job_search_engine.py
```

### 2. Ejecución Automatizada (Silent Mode)
Para ejecutar el proceso completo sin intervención usuario (ideal para scripts de fondo):
```bash
python3 backend-services/automate_search.py
```

### 3. Programación Diaria (Cron)
El sistema incluye un wrapper script para ejecución programada.
- **Script:** `backend-services/run_daily_job.sh`
- **Logs:** Se generan en `job_search.log` en la raíz del proyecto.
- **Configuración:** Programado para ejecutarse diariamente a las 09:00 AM.

## 📁 Estructura del Proyecto

- `backend-services/`: Motor de búsqueda central, scripts de automatización y orquestación.
- `ai-automations/`: Lógica de agentes inteligentes para análisis de CV y vacantes.
- `data-engineering/`: Pipelines ETL para transformación y carga en Sheets.
- `infrastructure/`: Configuración centralizada y manejo de credenciales.

## 🚀 Tecnologías Principales
Python 3.10+ | Google Gemini AI | Selenium/Playwright | Pandas | Google Sheets API | Docker Ready
