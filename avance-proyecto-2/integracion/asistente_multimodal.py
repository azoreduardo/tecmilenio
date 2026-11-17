"""Integración multimodal: texto (intenciones) + imagen (tipo de documento).

Avance de Proyecto 2 - MBIA2602 - Instrucciones 9 y 10.
Combina el clasificador de intenciones (texto/clasificador_texto.py) con el
clasificador visual (imagenes/clasificador_imagenes.py) para que el Asistente
virtual de Servicios Escolares pueda:
    1) Procesar un mensaje de texto y responder según la intención detectada.
    2) Clasificar una imagen adjunta (documento) e interpretar su contenido.
    3) Combinar ambos: confirmar si lo que el usuario dice coincide con lo que
       se detecta en la imagen que adjuntó.

Requiere haber ejecutado antes:
    python ../texto/clasificador_texto.py
    python ../imagenes/clasificador_imagenes.py
"""
import json
import sys
from pathlib import Path

import joblib
import torch
from PIL import Image

CARPETA = Path(__file__).parent
TEXTO_DIR = CARPETA.parent / "texto"
IMAGENES_DIR = CARPETA.parent / "imagenes"

# Los módulos "preprocesamiento" y "clasificador_imagenes" deben ser importables
# para poder deserializar los modelos guardados con joblib/torch.save.
sys.path.insert(0, str(TEXTO_DIR))
sys.path.insert(0, str(IMAGENES_DIR))

from clasificador_imagenes import TRANSFORM_EVAL, construir_modelo  # noqa: E402

# --------------------------------------------------------------------------
# Respuestas del asistente según la intención detectada en el texto.
# Mismo dominio y tono que el Avance de Proyecto 1 (chatbot.py), pero ahora la
# intención se obtiene con el clasificador de Machine Learning (TF-IDF + SVM).
# --------------------------------------------------------------------------
RESPUESTAS_TEXTO = {
    "saludo": "¡Hola! Soy el asistente virtual de Servicios Escolares. ¿En qué te ayudo?",
    "consultar_horario": "Atendemos de lunes a viernes de 9:00 a 18:00 horas.",
    "pagar_colegiatura": "Puedes pagar tu colegiatura en el portal de pagos; la fecha límite es el día 5 de cada mes.",
    "solicitar_constancia": "Puedes solicitar tu constancia desde el portal del alumno; se entrega en 2 días hábiles.",
    "soporte_plataforma": "Levanté un reporte de soporte. Un asesor de TI te contactará en menos de 24 horas.",
    "despedida": "¡Gracias por escribir! Que tengas un excelente día.",
    "fallback": "No estoy seguro de haber entendido. Puedo ayudarte con horarios, pagos, constancias o soporte.",
}

# Qué significa cada clase visual y cómo se interpreta dentro de la conversación.
INTERPRETACION_IMAGEN = {
    "comprobante_pago": {
        "mensaje": "Veo que adjuntaste un comprobante de pago.",
        "intencion_relacionada": "pagar_colegiatura",
        "accion": "Quedó registrado el pago de tu colegiatura; no necesitas hacer nada más.",
    },
    "constancia": {
        "mensaje": "Veo que adjuntaste una constancia.",
        "intencion_relacionada": "solicitar_constancia",
        "accion": "Tu constancia fue recibida y validada por el sistema.",
    },
    "credencial": {
        "mensaje": "Veo que adjuntaste tu credencial de estudiante.",
        "intencion_relacionada": None,
        "accion": "Tu identidad quedó validada para continuar el trámite.",
    },
    "captura_error": {
        "mensaje": "Veo que adjuntaste una captura de un error de plataforma.",
        "intencion_relacionada": "soporte_plataforma",
        "accion": "Levanté un reporte de soporte con esta evidencia. Un asesor de TI te contactará en menos de 24 horas.",
    },
}


def cargar_clasificador_texto():
    ruta = TEXTO_DIR / "resultados" / "modelo_intenciones.joblib"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero: python ../texto/clasificador_texto.py"
        )
    return joblib.load(ruta)


def cargar_clasificador_imagenes():
    ruta = IMAGENES_DIR / "resultados" / "modelo_imagenes.pt"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero: python ../imagenes/clasificador_imagenes.py"
        )
    checkpoint = torch.load(ruta, map_location="cpu", weights_only=False)
    clases = checkpoint["clases"]
    modelo = construir_modelo(len(clases))
    modelo.load_state_dict(checkpoint["state_dict"])
    modelo.eval()
    return modelo, clases


class AsistenteMultimodal:
    def __init__(self):
        paquete_texto = cargar_clasificador_texto()
        self.vectorizador = paquete_texto["vectorizador"]
        self.modelo_texto = paquete_texto["modelo"]
        self.nombre_modelo_texto = paquete_texto["nombre_modelo"]
        self.modelo_imagenes, self.clases_imagenes = cargar_clasificador_imagenes()

    def clasificar_texto(self, mensaje: str) -> str:
        vector = self.vectorizador.transform([mensaje])
        return self.modelo_texto.predict(vector)[0]

    def clasificar_imagen(self, ruta_imagen: Path) -> str:
        imagen = Image.open(ruta_imagen).convert("RGB")
        tensor = TRANSFORM_EVAL(imagen).unsqueeze(0)
        with torch.no_grad():
            salida = self.modelo_imagenes(tensor)
            indice = salida.argmax(dim=1).item()
        return self.clases_imagenes[indice]

    def procesar(self, mensaje: str | None = None, ruta_imagen: Path | None = None) -> str:
        """Procesa texto, imagen o ambos y arma una respuesta combinada."""
        partes = []
        intencion = None
        clase_imagen = None

        if mensaje:
            intencion = self.clasificar_texto(mensaje)
            partes.append(RESPUESTAS_TEXTO.get(intencion, RESPUESTAS_TEXTO["fallback"]))

        if ruta_imagen:
            clase_imagen = self.clasificar_imagen(ruta_imagen)
            info = INTERPRETACION_IMAGEN[clase_imagen]
            partes.append(info["mensaje"])
            partes.append(info["accion"])

            # Integración real: si el texto y la imagen coinciden, el asistente
            # lo confirma explícitamente en vez de solo concatenar respuestas.
            if intencion and info["intencion_relacionada"] == intencion:
                partes.append(
                    "(Tu mensaje y la imagen que adjuntaste coinciden, así que ya "
                    "puedo continuar con el trámite sin pedirte más datos.)"
                )
            elif intencion and info["intencion_relacionada"] not in (None, intencion):
                partes.append(
                    "(Nota: lo que escribiste no coincide con lo que detecté en la "
                    "imagen; revisa que sea el archivo correcto.)"
                )

        return " ".join(partes)


CASOS_DEMO = [
    {"mensaje": "Hola, buenas tardes", "imagen": None},
    {"mensaje": "¿Cuál es el horario de atención?", "imagen": None},
    {"mensaje": None, "imagen": "comprobante_pago"},
    {"mensaje": None, "imagen": "captura_error"},
    {"mensaje": "Ya pagué mi colegiatura, aquí está mi comprobante", "imagen": "comprobante_pago"},
    {"mensaje": "No puedo entrar a Canvas", "imagen": "captura_error"},
    {"mensaje": "Necesito mi constancia de estudios", "imagen": "credencial"},
]


def ejemplo_imagen(clase: str) -> Path:
    """Toma una imagen de prueba del split 'test' generado para esa clase."""
    carpeta = IMAGENES_DIR / "dataset" / "test" / clase
    return next(carpeta.glob("*.png"))


def main():
    asistente = AsistenteMultimodal()
    print(f"Modelo de texto cargado: {asistente.nombre_modelo_texto}")
    print(f"Clases visuales: {asistente.clases_imagenes}\n")

    transcripcion = []
    for caso in CASOS_DEMO:
        ruta_imagen = ejemplo_imagen(caso["imagen"]) if caso["imagen"] else None
        respuesta = asistente.procesar(caso["mensaje"], ruta_imagen)

        entrada_txt = caso["mensaje"] or "(sin texto)"
        entrada_img = f"[imagen: {caso['imagen']}]" if caso["imagen"] else "(sin imagen)"
        print(f"Tú: {entrada_txt} {entrada_img}")
        print(f"Bot: {respuesta}\n")
        transcripcion.append(
            {"entrada_texto": caso["mensaje"], "entrada_imagen": caso["imagen"], "respuesta": respuesta}
        )

    salida = CARPETA / "resultados_integracion.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(transcripcion, f, ensure_ascii=False, indent=2)
    print(f"Transcripción guardada en: {salida}")


if __name__ == "__main__":
    main()
