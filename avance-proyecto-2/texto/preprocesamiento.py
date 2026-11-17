"""Preprocesamiento de texto para el clasificador de intenciones.

Avance de Proyecto 2 - MBIA2602.
Aplica las 4 técnicas requeridas por la instrucción 3:
tokenización, normalización, eliminación de stopwords y lematización/stemming.
Reutiliza el mismo criterio de normalización del Avance de Proyecto 1
(minúsculas, sin acentos, sin puntuación) para mantener coherencia.
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
STOPWORDS_ES = {
    unicodedata.normalize("NFD", p.lower())
    .encode("ascii", "ignore")
    .decode("utf-8")
    for p in stopwords.words("spanish")
}


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos y sin signos de puntuación."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", texto)


def tokenizar(texto: str) -> list[str]:
    """Normaliza y tokeniza el texto."""
    return word_tokenize(normalizar(texto), language="spanish")


def quitar_stopwords(tokens: list[str]) -> list[str]:
    """Elimina palabras vacías del español."""
    return [t for t in tokens if t not in STOPWORDS_ES]


def lematizar(tokens: list[str]) -> list[str]:
    """Reduce cada token a su raíz (stemming con SnowballStemmer)."""
    return [stemmer.stem(t) for t in tokens]


def preprocesar(texto: str) -> list[str]:
    """Pipeline completo: tokenización -> normalización -> stopwords -> stemming.

    Se usa tanto para entrenar el vectorizador TF-IDF/BoW como para clasificar
    mensajes nuevos en la integración multimodal.
    """
    tokens = tokenizar(texto)
    tokens = quitar_stopwords(tokens)
    return lematizar(tokens)


def preprocesar_a_texto(texto: str) -> str:
    """Igual que preprocesar(), pero devuelve una cadena (para CountVectorizer/TfidfVectorizer)."""
    return " ".join(preprocesar(texto))


def sin_preprocesar(texto: str) -> str:
    """Desactiva el preprocesador por defecto de sklearn (ya normalizamos en preprocesar()).

    Definida aquí (no en el script del clasificador) para que joblib pueda
    encontrarla siempre como 'preprocesamiento.sin_preprocesar', sin importar
    si el modelo se entrena ejecutando el script directamente o importándolo.
    """
    return texto


if __name__ == "__main__":
    ejemplo = "¿Cuál es el horario de atención de Servicios Escolares?"
    print("Original:     ", ejemplo)
    print("Tokenizado:   ", tokenizar(ejemplo))
    print("Sin stopwords:", quitar_stopwords(tokenizar(ejemplo)))
    print("Preprocesado: ", preprocesar(ejemplo))
