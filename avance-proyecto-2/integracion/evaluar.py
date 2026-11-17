"""Pruebas funcionales de la integracion multimodal (texto + imagen).

Avance de Proyecto 2 - MBIA2602.
Reutiliza AsistenteMultimodal (texto y visión ya entrenados) y verifica que:
  1) el texto solo detecte la intencion esperada,
  2) la imagen sola detecte la clase visual esperada,
  3) al combinarse, cada canal siga detectando lo correcto por separado.

Requiere haber ejecutado antes:
    python ../texto/clasificador_texto.py
    python ../imagenes/generar_dataset.py
    python ../imagenes/clasificador_imagenes.py
"""
import csv
from pathlib import Path

from asistente_multimodal import AsistenteMultimodal, ejemplo_imagen

CARPETA = Path(__file__).parent
PRUEBAS = CARPETA / "pruebas"
PRUEBAS.mkdir(exist_ok=True)

CASOS_PRUEBA = [
    {"mensaje": "hola, buenas tardes", "imagen": None,
     "intencion_esperada": "saludo", "clase_esperada": None},
    {"mensaje": "cual es el horario de atencion", "imagen": None,
     "intencion_esperada": "consultar_horario", "clase_esperada": None},
    {"mensaje": None, "imagen": "comprobante_pago",
     "intencion_esperada": None, "clase_esperada": "comprobante_pago"},
    {"mensaje": None, "imagen": "captura_error",
     "intencion_esperada": None, "clase_esperada": "captura_error"},
    {"mensaje": "ya pague mi colegiatura, aqui esta mi comprobante", "imagen": "comprobante_pago",
     "intencion_esperada": "pagar_colegiatura", "clase_esperada": "comprobante_pago"},
    {"mensaje": "no puedo entrar a canvas", "imagen": "captura_error",
     "intencion_esperada": "soporte_plataforma", "clase_esperada": "captura_error"},
]


def main():
    asistente = AsistenteMultimodal()
    print(f"Modelo de texto: {asistente.nombre_modelo_texto} | Clases visuales: {asistente.clases_imagenes}\n")

    filas = []
    aciertos = 0
    for caso in CASOS_PRUEBA:
        intencion = asistente.clasificar_texto(caso["mensaje"]) if caso["mensaje"] else None
        clase_img = asistente.clasificar_imagen(ejemplo_imagen(caso["imagen"])) if caso["imagen"] else None

        correcto_texto = caso["intencion_esperada"] is None or intencion == caso["intencion_esperada"]
        correcto_imagen = caso["clase_esperada"] is None or clase_img == caso["clase_esperada"]
        correcto = correcto_texto and correcto_imagen
        aciertos += correcto

        fila = {
            "mensaje": caso["mensaje"] or "",
            "imagen": caso["imagen"] or "",
            "intencion_esperada": caso["intencion_esperada"] or "",
            "intencion_detectada": intencion or "",
            "clase_esperada": caso["clase_esperada"] or "",
            "clase_detectada": clase_img or "",
            "correcto": correcto,
        }
        filas.append(fila)
        marca = "OK " if correcto else "XX "
        print(f"{marca}{fila}")

    precision = aciertos / len(CASOS_PRUEBA)
    print(f"\nPrecision: {aciertos}/{len(CASOS_PRUEBA)} ({precision:.2%})")

    with open(PRUEBAS / "casos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)
    print(f"Resultados guardados en: {PRUEBAS / 'casos.csv'}")


if __name__ == "__main__":
    main()
