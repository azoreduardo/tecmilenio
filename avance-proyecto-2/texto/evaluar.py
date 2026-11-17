"""Pruebas funcionales del clasificador de intenciones (texto).

Avance de Proyecto 2 - MBIA2602.
Carga el modelo ya entrenado (texto/resultados/modelo_intenciones.joblib) y lo
prueba contra una lista fija de mensajes NUEVOS (con redacciones distintas a
las usadas en dataset_intenciones.py), igual que evaluar.py del Avance de
Proyecto 1.

Requiere haber ejecutado antes: python clasificador_texto.py
"""
import csv
from pathlib import Path

import joblib

CARPETA = Path(__file__).parent
RESULTADOS = CARPETA / "resultados"
PRUEBAS = CARPETA / "pruebas"
PRUEBAS.mkdir(exist_ok=True)

CASOS_PRUEBA = [
    ("hola, buenas tardes", "saludo"),
    ("que tal, como estas", "saludo"),
    ("en que horario atienden los lunes", "consultar_horario"),
    ("hasta que hora dan servicio hoy", "consultar_horario"),
    ("quiero pagar mi colegiatura de este mes", "pagar_colegiatura"),
    ("donde saco la ficha para pagar", "pagar_colegiatura"),
    ("necesito mi constancia de inscripcion", "solicitar_constancia"),
    ("como descargo mi kardex", "solicitar_constancia"),
    ("canvas no me deja entrar", "soporte_plataforma"),
    ("se me olvido la contrasena del correo institucional", "soporte_plataforma"),
    ("muchas gracias, hasta luego", "despedida"),
    ("listo, eso era todo, gracias", "despedida"),
    ("cual es tu color favorito", "fallback"),
    ("recomiendame una serie para ver", "fallback"),
]


def main():
    ruta_modelo = RESULTADOS / "modelo_intenciones.joblib"
    if not ruta_modelo.exists():
        raise FileNotFoundError(
            f"No se encontro {ruta_modelo}. Ejecuta primero: python clasificador_texto.py"
        )
    paquete = joblib.load(ruta_modelo)
    vectorizador, modelo = paquete["vectorizador"], paquete["modelo"]
    print(f"Modelo cargado: {paquete['nombre_modelo']}\n")

    filas = []
    aciertos = 0
    for mensaje, esperado in CASOS_PRUEBA:
        vector = vectorizador.transform([mensaje])
        detectado = modelo.predict(vector)[0]
        correcto = detectado == esperado
        aciertos += correcto
        filas.append({
            "mensaje": mensaje,
            "intencion_esperada": esperado,
            "intencion_detectada": detectado,
            "correcto": correcto,
        })
        marca = "OK " if correcto else "XX "
        print(f"{marca}{mensaje!r:55} -> esperado={esperado:22} detectado={detectado}")

    precision = aciertos / len(CASOS_PRUEBA)
    print(f"\nPrecision: {aciertos}/{len(CASOS_PRUEBA)} ({precision:.2%})")

    with open(PRUEBAS / "casos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["mensaje", "intencion_esperada", "intencion_detectada", "correcto"]
        )
        writer.writeheader()
        writer.writerows(filas)
    print(f"Resultados guardados en: {PRUEBAS / 'casos.csv'}")


if __name__ == "__main__":
    main()
