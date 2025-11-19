def test_overwrite_logic():
    print("🧪 Testing Overwrite Protection Logic...")

    # 1. Scenario: API has data, AI tries to overwrite
    vacante = {
        "empresa": "Banco de Chile", # ✅ Good data
        "ubicacion": "Santiago",
        "modalidad": "Híbrido"
    }
    
    analisis_data = {
        "empresa": "Empresa Genérica IA", # ❌ Should be ignored
        "ubicacion": "Cualquier lugar",
        "modalidad": "Remoto",
        "match_percent": 95,
        "match_reason": "Buena experiencia"
    }
    
    # Logic from vacantes_main.py
    campos_a_actualizar = ["empresa", "ubicacion", "modalidad"]
    valores_nulos = ["", "No indicado", "No Determinado", "N/A", "No informado", "None"]

    for campo in campos_a_actualizar:
        valor_actual = vacante.get(campo, "")
        valor_ia = analisis_data.get(campo, "")
        
        if str(valor_actual) in valores_nulos and valor_ia:
            vacante[campo] = valor_ia
            
    # Always update these
    vacante["match_percent"] = analisis_data.get("match_percent", 0)
    vacante["match_reason"] = analisis_data.get("match_reason", "Sin motivo")

    # Assertions
    assert vacante["empresa"] == "Banco de Chile", f"Error: Company overwritten! Got {vacante['empresa']}"
    assert vacante["match_percent"] == 95, "Error: Match percent not updated"
    print("✅ Scenario 1 Passed: API data protected.")

    # 2. Scenario: API has NO data, AI fills it
    vacante_empty = {
        "empresa": "No informado", # ❌ Bad data
        "ubicacion": "",
    }
    
    for campo in campos_a_actualizar:
        valor_actual = vacante_empty.get(campo, "")
        valor_ia = analisis_data.get(campo, "")
        
        if str(valor_actual) in valores_nulos and valor_ia:
            vacante_empty[campo] = valor_ia
            
    assert vacante_empty["empresa"] == "Empresa Genérica IA", "Error: AI did not fill missing company"
    print("✅ Scenario 2 Passed: AI filled missing data.")

if __name__ == "__main__":
    test_overwrite_logic()
