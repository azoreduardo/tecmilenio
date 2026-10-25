"""Pruebas funcionales del chatbot (Avance de Proyecto 1).

Ejecuta un conjunto de mensajes de prueba contra el chatbot y registra:
mensaje, intencion esperada, intencion detectada y si coincide.
Calcula la tasa de comprension y la tasa de fallback, e imprime la
conversacion completa turno a turno (para las evidencias de ejecucion).
"""
import csv
from pathlib import Path

from chatbot import detectar_intencion, responder

CASOS = [
    ("Hola, buenas tardes", "saludo"),
    ("¿Cuál es el horario de atención?", "consultar_horario"),
    ("¿A qué hora cierran los viernes?", "consultar_horario"),
    ("Quiero pagar mi colegiatura de noviembre", "pagar_colegiatura"),
    ("¿Cuál es la fecha límite de pago?", "pagar_colegiatura"),
    ("Necesito una constancia de estudios", "solicitar_constancia"),
    ("¿Cómo saco mi carta de no adeudo?", "solicitar_constancia"),
    ("No puedo entrar a Canvas", "soporte_plataforma"),
    ("Olvidé mi contraseña del correo institucional", "soporte_plataforma"),
    ("Gracias, hasta luego", "despedida"),
    ("Quiero pizza", "fallback"),
    ("xq no me deja entrar jaja", "fallback"),
]

CARPETA = Path(__file__).parent
CSV_PATH = CARPETA / "pruebas" / "casos.csv"


def main():
    filas = []
    print("=== Conversacion de prueba (turno a turno) ===\n")
    print("Bot:", responder("hola"))
    aciertos = 0
    fallbacks = 0

    for mensaje, esperado in CASOS:
        detectado = detectar_intencion(mensaje)
        correcto = detectado == esperado
        aciertos += correcto
        fallbacks += detectado == "fallback"
        print(f"Tú: {mensaje}")
        print(f"Bot: {responder(mensaje)}")
        print(f"   [esperado={esperado} | detectado={detectado} | correcto={correcto}]\n")
        filas.append(
            {
                "mensaje": mensaje,
                "intencion_esperada": esperado,
                "intencion_detectada": detectado,
                "correcto": "si" if correcto else "no",
            }
        )

    total = len(CASOS)
    print("=== Resultados ===")
    print(f"Conversaciones probadas: {total}")
    print(f"Intención correcta: {aciertos}/{total} ({aciertos / total:.0%})")
    print(f"Fallback: {fallbacks}/{total} ({fallbacks / total:.0%})")

    CSV_PATH.parent.mkdir(exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["mensaje", "intencion_esperada", "intencion_detectada", "correcto"]
        )
        writer.writeheader()
        writer.writerows(filas)
    print(f"\nCasos guardados en: {CSV_PATH}")


if __name__ == "__main__":
    main()
