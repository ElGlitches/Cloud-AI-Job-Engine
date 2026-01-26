# Enterprise Cloud & Data Automation Toolkit (AI Job Search Engine) 🚀

**Un motor de búsqueda y análisis de mercado laboral potenciado por Inteligencia Artificial.**

Este proyecto no es solo un script; es una plataforma de ingeniería de datos diseñada para automatizar la búsqueda, filtrado y análisis de oportunidades laborales en múltiples portales (LinkedIn, GetOnBrd, etc.), utilizando modelos LLM (Gemini) para determinar el "match" real con el perfil del candidato.

## 🎯 Objetivo del Proyecto

Optimizar el proceso de búsqueda de empleo reduciendo el tiempo de revisión manual en un **90%**. El sistema orquesta:
1.  **Extracción de Datos:** Scraping ético y multi-hilo de ofertas en tiempo real.
2.  **Análisis Cognitivo:** Un agente de IA lee cada descripción, detecta stack tecnológico, seniority y salario, y lo compara con tu CV.
3.  **Reporting Automatizado:** Centralización de resultados en un Dashboard de Google Sheets con semáforos de prioridad.

## 🛠️ Capacidades Destacadas (Architecture)

*   **Smart Scrapers (Backend):** Motores de extracción resilientes para LinkedIn y GetOnBrd.
*   **AI Analysis Core:** Pipeline de procesamiento que utiliza `Gemini 2.0 Flash` para estructurar datos no estructurados (descripciones de empleo).
*   **Data Integrity:** Validaciones automáticas, deduplicación y manejo de errores (Tenacity).
*   **Cloud Integration:** Sincronización automática con Google Workspace API.

## 📁 Estructura del Proyecto

- `backend-services/`: Motor de búsqueda y orquestación de scrapers (`job_search_engine.py`).
- `ai-automations/`: Lógica de agentes inteligentes para análisis de CV y vacantes.
- `data-engineering/`: Pipelines ETL para transformación y carga en Sheets.
- `infrastructure/`: Configuración centralizada y manejo de credenciales.

## 🚀 Tecnologías Principales
Python 3.10+ | Google Gemini AI | Selenium/Playwright | Pandas | Google Sheets API | Docker Ready

