from src.utils import cargar_texto_pdf
import os

def test_pdf_missing():
    print("🧪 Probando carga de PDF inexistente...")
    texto = cargar_texto_pdf("archivo_que_no_existe.pdf")
    if texto == "":
        print("✅ Prueba exitosa: Retornó cadena vacía como se esperaba.")
    else:
        print(f"❌ Prueba fallida: Retornó '{texto}'")

if __name__ == "__main__":
    test_pdf_missing()
