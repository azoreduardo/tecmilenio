"""Clasificador de intenciones: TF-IDF + Naive Bayes / SVM.

Avance de Proyecto 2 - MBIA2602 - Instrucciones 4 y 5.
Representa el texto con TF-IDF y entrena dos clasificadores (Naive Bayes y SVM
lineal) para comparar su desempeño sobre las 7 intenciones del Asistente
virtual de Servicios Escolares. Guarda el mejor modelo para usarlo en la
integración multimodal (ver ../integracion/asistente_multimodal.py).
"""
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from dataset_intenciones import INTENCIONES_ORDEN, textos_y_etiquetas
from preprocesamiento import preprocesar, sin_preprocesar

CARPETA = Path(__file__).parent
RESULTADOS = CARPETA / "resultados"
RESULTADOS.mkdir(exist_ok=True)


def vectorizar(x_train, x_test):
    """TF-IDF usando el pipeline de preprocesamiento propio como tokenizador."""
    vectorizador = TfidfVectorizer(
        tokenizer=preprocesar,
        preprocessor=sin_preprocesar,
        token_pattern=None,
        lowercase=False,
    )
    x_train_tfidf = vectorizador.fit_transform(x_train)
    x_test_tfidf = vectorizador.transform(x_test)
    return vectorizador, x_train_tfidf, x_test_tfidf


def evaluar_modelo(nombre, modelo, x_test, y_test, etiquetas):
    y_pred = modelo.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    reporte = classification_report(y_test, y_pred, labels=etiquetas, zero_division=0)
    matriz = confusion_matrix(y_test, y_pred, labels=etiquetas)

    print(f"\n=== {nombre} ===")
    print(f"Accuracy: {acc:.2%}")
    print(reporte)

    fig, ax = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay(matriz, display_labels=etiquetas).plot(
        ax=ax, xticks_rotation=45, cmap="Greens", colorbar=False
    )
    ax.set_title(f"Matriz de confusión - {nombre}")
    fig.tight_layout()
    ruta_png = RESULTADOS / f"matriz_confusion_{nombre.lower().replace(' ', '_')}.png"
    fig.savefig(ruta_png, dpi=150)
    plt.close(fig)

    return {
        "modelo": nombre,
        "accuracy": acc,
        "reporte_clasificacion": reporte,
        "matriz_confusion": matriz.tolist(),
        "imagen_matriz": str(ruta_png.name),
    }


def main():
    textos, etiquetas_y = textos_y_etiquetas()
    x_train, x_test, y_train, y_test = train_test_split(
        textos, etiquetas_y, test_size=0.25, random_state=42, stratify=etiquetas_y
    )

    vectorizador, x_train_tfidf, x_test_tfidf = vectorizar(x_train, x_test)

    nb = MultinomialNB()
    nb.fit(x_train_tfidf, y_train)
    resultado_nb = evaluar_modelo("Naive Bayes", nb, x_test_tfidf, y_test, INTENCIONES_ORDEN)

    svm = LinearSVC(random_state=42)
    svm.fit(x_train_tfidf, y_train)
    resultado_svm = evaluar_modelo("SVM", svm, x_test_tfidf, y_test, INTENCIONES_ORDEN)

    mejor = resultado_svm if resultado_svm["accuracy"] >= resultado_nb["accuracy"] else resultado_nb
    modelo_final = svm if mejor is resultado_svm else nb
    print(f"\nMejor modelo: {mejor['modelo']} (accuracy {mejor['accuracy']:.2%}) -> se guarda para la integración.")

    joblib.dump(
        {"vectorizador": vectorizador, "modelo": modelo_final, "etiquetas": INTENCIONES_ORDEN,
         "nombre_modelo": mejor["modelo"]},
        RESULTADOS / "modelo_intenciones.joblib",
    )

    resumen = {
        "n_ejemplos_train": len(x_train),
        "n_ejemplos_test": len(x_test),
        "vocabulario_tfidf": len(vectorizador.vocabulary_),
        "resultados": [
            {k: v for k, v in r.items() if k != "matriz_confusion"}
            for r in (resultado_nb, resultado_svm)
        ],
        "modelo_seleccionado": mejor["modelo"],
    }
    with open(RESULTADOS / "metricas_texto.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print(f"\nMétricas guardadas en: {RESULTADOS / 'metricas_texto.json'}")


if __name__ == "__main__":
    main()
