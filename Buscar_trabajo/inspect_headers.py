from src.sheets_manager import conectar_sheets
import json

def inspect_headers():
    try:
        print("🔌 Conectando a Sheets...")
        hoja = conectar_sheets()
        
        print("📚 Leyendo encabezados y primera fila de datos...")
        # Leer filas 2 (encabezados) y 3 (primer dato)
        datos = hoja.get_values("A2:O3")
        
        if len(datos) > 0:
            print("\n--- Encabezados (Fila 2) ---")
            print(json.dumps(datos[0], indent=2, ensure_ascii=False))
        
        if len(datos) > 1:
            print("\n--- Primer Dato (Fila 3) ---")
            print(json.dumps(datos[1], indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_headers()
