"""Pruebas funcionales del clasificador visual (imagenes).

Avance de Proyecto 2 - MBIA2602.
Carga el modelo ya entrenado (imagenes/resultados/modelo_imagenes.pt) y lo
prueba contra una muestra fija de imagenes del split 'test' generado por
generar_dataset.py, verificando que la clase predicha coincida con la clase
real (la carpeta donde vive cada imagen).

Requiere haber ejecutado antes:
    python generar_dataset.py
    python clasificador_imagenes.py
"""
import csv
from pathlib import Path

import torch
from PIL import Image

from clasificador_imagenes import TRANSFORM_EVAL, construir_modelo

CARPETA = Path(__file__).parent
DATASET_TEST = CARPETA / "dataset" / "test"
RESULTADOS = CARPETA / "resultados"
PRUEBAS = CARPETA / "pruebas"
PRUEBAS.mkdir(exist_ok=True)

N_POR_CLASE = 3  # cuantas imagenes de prueba tomar por clase


def cargar_modelo():
    ruta = RESULTADOS / "modelo_imagenes.pt"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro {ruta}. Ejecuta primero: python generar_dataset.py y "
            "python clasificador_imagenes.py"
        )
    checkpoint = torch.load(ruta, map_location="cpu", weights_only=False)
    clases = checkpoint["clases"]
    modelo = construir_modelo(len(clases))
    modelo.load_state_dict(checkpoint["state_dict"])
    modelo.eval()
    return modelo, clases


def main():
    if not DATASET_TEST.exists():
        raise FileNotFoundError(
            f"No se encontro {DATASET_TEST}. Ejecuta primero: python generar_dataset.py"
        )
    modelo, clases = cargar_modelo()
    print(f"Clases: {clases}\n")

    filas = []
    aciertos = 0
    total = 0
    for carpeta_clase in sorted(DATASET_TEST.iterdir()):
        if not carpeta_clase.is_dir():
            continue
        for ruta_imagen in sorted(carpeta_clase.glob("*.png"))[:N_POR_CLASE]:
            imagen = Image.open(ruta_imagen).convert("RGB")
            tensor = TRANSFORM_EVAL(imagen).unsqueeze(0)
            with torch.no_grad():
                salida = modelo(tensor)
                indice = salida.argmax(dim=1).item()
            clase_predicha = clases[indice]
            correcto = clase_predicha == carpeta_clase.name
            aciertos += correcto
            total += 1
            filas.append({
                "imagen": ruta_imagen.name,
                "clase_esperada": carpeta_clase.name,
                "clase_predicha": clase_predicha,
                "correcto": correcto,
            })
            marca = "OK " if correcto else "XX "
            print(f"{marca}{ruta_imagen.name:30} -> esperado={carpeta_clase.name:18} predicho={clase_predicha}")

    precision = aciertos / total if total else 0
    print(f"\nPrecision: {aciertos}/{total} ({precision:.2%})")

    with open(PRUEBAS / "casos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["imagen", "clase_esperada", "clase_predicha", "correcto"]
        )
        writer.writeheader()
        writer.writerows(filas)
    print(f"Resultados guardados en: {PRUEBAS / 'casos.csv'}")


if __name__ == "__main__":
    main()
