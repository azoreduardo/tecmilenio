"""Asistente virtual de Servicios Escolares - chatbot basado en reglas.

Avance de Proyecto 1 - MBIA2602.
Desarrollado originalmente en Google Colab con Python 3.10+ y NLTK.

Resuelve consultas frecuentes de estudiantes sobre horarios, pago de colegiatura,
constancias y soporte de plataformas, y canaliza a un asesor humano (fallback)
cuando no reconoce la intención.
"""
import re
import unicodedata

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

stemmer = SnowballStemmer("spanish")


def normalizar(texto: str) -> str:
    """Minusculas, sin acentos y sin signos de puntuacion."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", texto)


STOP = {normalizar(p).strip() for p in stopwords.words("spanish")}

# --------------------------------------------------------------------------
# Base de conocimiento: intenciones, ejemplos (como lo dice el usuario)
# y la respuesta que debe dar el chatbot.
# --------------------------------------------------------------------------
INTENCIONES = {
    "saludo": {
        "ejemplos": ["hola", "buenos dias", "buenas tardes", "que tal", "hola buenas"],
        "respuesta": (
            "¡Hola! Soy el asistente virtual de Servicios Escolares. Puedo ayudarte "
            "con horarios, pago de colegiatura, constancias y soporte de plataformas."
        ),
    },
    "consultar_horario": {
        "ejemplos": [
            "cual es el horario de atencion",
            "a que hora abren",
            "cuando atienden",
            "horario de servicios escolares",
            "a que hora cierran",
        ],
        "respuesta": "Atendemos de lunes a viernes de 9:00 a 18:00 horas.",
    },
    "pagar_colegiatura": {
        "ejemplos": [
            "como pago mi colegiatura",
            "quiero pagar la colegiatura",
            "fecha limite de pago",
            "donde pago la colegiatura",
            "cuanto cuesta la colegiatura",
        ],
        "respuesta": (
            "Puedes pagar tu colegiatura{mes_txt} en el portal de pagos con tarjeta "
            "o referencia bancaria; la fecha límite es el día 5 de cada mes."
        ),
    },
    "solicitar_constancia": {
        "ejemplos": [
            "necesito una constancia de estudios",
            "como pido una constancia",
            "quiero mi carta de no adeudo",
            "necesito el kardex",
            "como saco una constancia",
        ],
        "respuesta": (
            "Puedes solicitar tu constancia{tipo_txt} desde el portal del alumno, "
            "en la sección de trámites; se entrega en un plazo de 2 días hábiles."
        ),
    },
    "soporte_plataforma": {
        "ejemplos": [
            "no puedo entrar a canvas",
            "olvide mi contrasena",
            "mi correo institucional no funciona",
            "blackboard no carga",
            "no me deja iniciar sesion",
        ],
        "respuesta": (
            "Levanté un reporte de soporte{plataforma_txt}. Un asesor de TI te "
            "contactará en menos de 24 horas."
        ),
    },
    "despedida": {
        "ejemplos": ["gracias", "hasta luego", "adios", "eso es todo", "nos vemos"],
        "respuesta": "¡Gracias por escribir! Que tengas un excelente día.",
    },
}

# --------------------------------------------------------------------------
# Entidades: datos concretos que puede traer el mensaje.
# --------------------------------------------------------------------------
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
    "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

TIPOS_CONSTANCIA = {
    "estudios": ["estudios", "inscripcion"],
    "no adeudo": ["no adeudo", "noadeudo", "adeudo"],
    "kardex": ["kardex", "historial academico"],
}

PLATAFORMAS = {
    "canvas": ["canvas"],
    "correo institucional": ["correo", "outlook"],
    "blackboard": ["blackboard", "collaborate"],
}


def preprocesar(texto: str):
    """Normaliza, tokeniza y reduce a raiz, quitando palabras vacias."""
    tokens = word_tokenize(normalizar(texto), language="spanish")
    return [stemmer.stem(t) for t in tokens if t not in STOP]


# Verbos genericos ("quiero", "necesito"...) aparecen en casi todas las
# intenciones y, si no se excluyen, generan falsos positivos con mensajes
# fuera de alcance como "quiero pizza". Se excluyen solo para DETECTAR la
# intencion (no para extraer entidades ni para el resto del preprocesamiento).
GENERICAS = {stemmer.stem(v) for v in ("quiero", "quisiera", "necesito", "podria", "quiere")}


def tokens_para_intencion(texto: str):
    return [t for t in preprocesar(texto) if t not in GENERICAS]


# Vocabulario de raices por intencion (se calcula una sola vez).
VOCAB = {
    intencion: {raiz for ejemplo in datos["ejemplos"] for raiz in tokens_para_intencion(ejemplo)}
    for intencion, datos in INTENCIONES.items()
}


def detectar_intencion(mensaje: str, umbral: int = 1) -> str:
    """Compara las raices del mensaje contra el vocabulario de cada intencion."""
    tokens = set(tokens_para_intencion(mensaje))
    puntajes = {intencion: len(tokens & vocab) for intencion, vocab in VOCAB.items()}
    mejor = max(puntajes, key=puntajes.get)
    return mejor if puntajes[mejor] >= umbral else "fallback"


def extraer_entidades(mensaje: str) -> dict:
    """Busca mes, tipo de constancia y plataforma mediante diccionarios y regex."""
    texto = normalizar(mensaje)
    entidades = {}

    for mes in MESES:
        if re.search(rf"\b{mes}\b", texto):
            entidades["mes"] = mes

    for tipo, palabras in TIPOS_CONSTANCIA.items():
        if any(re.search(rf"\b{normalizar(p)}\b", texto) for p in palabras):
            entidades["tipo"] = tipo

    for plataforma, palabras in PLATAFORMAS.items():
        if any(re.search(rf"\b{normalizar(p)}\b", texto) for p in palabras):
            entidades["plataforma"] = plataforma

    return entidades


def responder(mensaje: str) -> str:
    """Detecta la intencion, extrae entidades y arma la respuesta final."""
    intencion = detectar_intencion(mensaje)
    if intencion == "fallback":
        return (
            "No estoy seguro de haber entendido. Puedo ayudarte con horarios, "
            "pagos, constancias o soporte de plataformas. ¿Sobre cuál quieres saber?"
        )

    entidades = extraer_entidades(mensaje)
    plantilla = INTENCIONES[intencion]["respuesta"]
    return plantilla.format(
        mes_txt=f" de {entidades['mes']}" if "mes" in entidades else "",
        tipo_txt=f" de {entidades['tipo']}" if "tipo" in entidades else "",
        plataforma_txt=f" para {entidades['plataforma']}" if "plataforma" in entidades else "",
    )


def chat():
    """Bucle de conversacion interactivo (uso en Google Colab)."""
    print("Bot:", responder("hola"))
    while True:
        mensaje = input("Tú: ")
        if mensaje.strip().lower() in ("salir", "exit"):
            break
        respuesta = responder(mensaje)
        print("Bot:", respuesta)
        if detectar_intencion(mensaje) == "despedida":
            break


if __name__ == "__main__":
    chat()
