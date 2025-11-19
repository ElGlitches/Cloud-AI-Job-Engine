import sys
import os
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock config and environment
import src.config
src.config.URL_GETONBRD = "mock_url"
src.config.MAX_VACANTES_POR_PALABRA = 10
os.environ["GEMINI_API_KEY"] = "mock_key"

# Mock genai client to avoid real API calls during unit test
from src import analizador_vacantes
analizador_vacantes.client = MagicMock()
analizador_vacantes.client.models.generate_content.return_value.text = """
```json
{
    "empresa": "TechCorp",
    "ubicacion": "Remoto",
    "modalidad": "Remoto",
    "nivel": "Senior",
    "jornada": "Full-time",
    "salario": "$3000 - $4000",
    "seniority_score": 90,
    "top_skills": ["Python", "AWS", "Docker"],
    "match_percent": 85,
    "match_reason": "Buen perfil técnico, falta experiencia en Kubernetes."
}
```
"""

from src.analizador_vacantes import analizar_vacante

def test_fit_score():
    print("🧪 Testing Fit Score logic...")
    
    # Call the function (which now uses the mock client)
    result_json = analizar_vacante("Descripción de prueba", "Título de prueba")
    
    # Parse the result (it returns a string)
    import json
    data = json.loads(result_json)
    
    # Verify new fields
    assert "match_percent" in data, "Missing match_percent"
    assert data["match_percent"] == 85, f"Incorrect match_percent: {data['match_percent']}"
    print(f"✅ Match Percent: {data['match_percent']}")
    
    assert "match_reason" in data, "Missing match_reason"
    assert data["match_reason"] == "Buen perfil técnico, falta experiencia en Kubernetes.", "Incorrect match_reason"
    print(f"✅ Match Reason: {data['match_reason']}")
    
    print("\n🎉 Fit Score logic verified!")

if __name__ == "__main__":
    test_fit_score()
