import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock config values needed for import
import src.config
src.config.URL_GETONBRD = "mock_url"
src.config.MAX_VACANTES_POR_PALABRA = 10

from src.getonbrd import _procesar_resultados_getonbrd

def test_mapping():
    print("🧪 Testing GetOnBrd mapping logic...")
    
    # Mock JSON response from GetOnBrd
    mock_data = [
        {
            "id": "desarrollador-backend-python-empresa-fantasma-santiago-12345",
            "attributes": {
                "title": "Desarrollador Backend Python",
                "published_at": int(datetime.now().timestamp()), # Current timestamp
                "description": "<p>Descripción con <b>HTML</b></p>",
                "min_salary": 2000,
                "max_salary": 3000,
                "remote": True,
                "functions": "Desarrollo de API",
                "seniority": {
                    "data": {
                        "id": "senior",
                        "type": "seniority",
                        "attributes": {"name": "Senior"}
                    }
                },
                "location_cities": {
                    "data": [{"id": "santiago", "type": "city"}]
                }
            },
            "links": {
                "public_url": "https://www.getonbrd.com/jobs/..."
            }
        }
    ]
    
    # Run processing
    results = _procesar_resultados_getonbrd(mock_data, "python")
    
    if not results:
        print("❌ No results returned")
        return

    vacante = results[0]
    
    # Verify Date Format
    expected_date = datetime.now().strftime("%Y-%m-%d")
    assert vacante["fecha_publicacion"] == expected_date, f"Date mismatch: {vacante['fecha_publicacion']} != {expected_date}"
    print(f"✅ Date Formatted Correctly: {vacante['fecha_publicacion']}")
    
    # Verify Mapped Fields
    assert vacante["empresa"] == "fantasma", f"Company mismatch: {vacante['empresa']}"
    print(f"✅ Company Mapped: {vacante['empresa']}")
    
    assert vacante["ubicacion"] == "Ciudad Principal", f"Location mismatch: {vacante['ubicacion']}"
    print(f"✅ Location Mapped: {vacante['ubicacion']}")
    
    assert vacante["salario"] == "$2000 - $3000", f"Salary mismatch: {vacante['salario']}"
    print(f"✅ Salary Mapped: {vacante['salario']}")
    
    assert vacante["modalidad"] == "Remoto", f"Modalidad mismatch: {vacante['modalidad']}"
    print(f"✅ Modalidad Mapped: {vacante['modalidad']}")
    
    print("\n🎉 All mapping tests passed!")

if __name__ == "__main__":
    test_mapping()
