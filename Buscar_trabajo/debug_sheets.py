from src.sheets_manager import conectar_sheets
import json

def debug_sheet():
    try:
        print("🔌 Conectando a Sheets...")
        hoja = conectar_sheets()
        
        print("📚 Leyendo valores...")
        # Leer las primeras 5 filas (incluyendo encabezados)
        datos = hoja.get_values("A1:O5")
        
        for i, row in enumerate(datos):
            print(f"\n--- Fila {i+1} ---")
            print(json.dumps(row, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_sheet()
