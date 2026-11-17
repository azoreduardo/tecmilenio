# Asistente virtual de Servicios Escolares — Avance de Proyecto 2

Amplía el chatbot basado en reglas del Avance 1 con un clasificador de intenciones
entrenado (TF-IDF + SVM/Naive Bayes), un clasificador visual (CNN ResNet50 con
transferencia de aprendizaje) y una integración multimodal entre ambos.

## Estructura

```text
avance-proyecto-2/
├── README.md                        # este archivo
├── AVANCE DE PROYECTO 2.md          # documento de entrega completo
├── texto/
│   ├── dataset_intenciones.py       # 105 frases etiquetadas (7 intenciones)
│   ├── preprocesamiento.py          # tokenización, stopwords, stemming (NLTK)
│   ├── clasificador_texto.py        # TF-IDF + Naive Bayes / SVM + métricas
│   ├── evaluar.py                   # pruebas funcionales (14 frases nuevas)
│   ├── pruebas/casos.csv            # resultado de evaluar.py (generado)
│   └── resultados/                  # métricas, matrices de confusión, modelo (.joblib)
├── imagenes/
│   ├── generar_dataset.py           # genera 520 imágenes sintéticas (4 clases)
│   ├── dataset/                     # train/val/test por clase (generado, *no versionado*)
│   ├── clasificador_imagenes.py     # ResNet50 (transfer learning) + métricas
│   ├── evaluar.py                   # pruebas funcionales (12 imágenes de prueba)
│   ├── pruebas/casos.csv            # resultado de evaluar.py (generado)
│   └── resultados/                  # métricas, matrices, curvas, modelo .pt (*no versionado*)
└── integracion/
    ├── asistente_multimodal.py      # combina texto + imagen en una sola respuesta
    ├── evaluar.py                   # pruebas funcionales (texto + imagen + ambos)
    ├── pruebas/casos.csv            # resultado de evaluar.py (generado)
    └── resultados_integracion.json  # transcripción de la demo (generado)
```

> **Nota:** `imagenes/dataset/` (46 MB de imágenes sintéticas) y
> `imagenes/resultados/modelo_imagenes.pt` (90 MB, el ResNet50 ya entrenado) están
> en `.gitignore` porque son **regenerables** con los scripts de abajo; no tiene
> sentido versionar artefactos binarios grandes que un script reproduce en minutos.

## Cómo ejecutarlo

```bash
pip install nltk scikit-learn pillow matplotlib joblib torch torchvision

# 1) Generar el dataset de imágenes sintéticas
python imagenes/generar_dataset.py

# 2) Entrenar y evaluar el clasificador de texto (TF-IDF + Naive Bayes/SVM)
python texto/clasificador_texto.py

# 3) Entrenar y evaluar el clasificador visual (ResNet50 + transfer learning)
python imagenes/clasificador_imagenes.py

# 4) Correr la demo del asistente multimodal (texto + imagen)
python integracion/asistente_multimodal.py
```

## Pruebas

Cada componente tiene su propio `evaluar.py` (pruebas funcionales, mismo criterio
que [`avance-proyecto-1/evaluar.py`](../avance-proyecto-1/evaluar.py)): corre una
lista fija de casos **no usados en el entrenamiento**, compara lo esperado contra
lo detectado y guarda el resultado en `pruebas/casos.csv`.

```bash
# Requiere haber corrido antes el paso correspondiente de "Cómo ejecutarlo"
python texto/evaluar.py          # 14 frases nuevas -> texto/pruebas/casos.csv
python imagenes/evaluar.py       # 12 imágenes de prueba (3 por clase) -> imagenes/pruebas/casos.csv
python integracion/evaluar.py    # texto, imagen y ambos combinados -> integracion/pruebas/casos.csv
```

## Resultados

| Componente | Métrica principal |
| --- | --- |
| Clasificador de texto (SVM + TF-IDF) | 92.59 % accuracy |
| Clasificador visual (ResNet50) | 100 % accuracy / precision / recall / F1 |

Ver el análisis completo (incluyendo limitaciones y conclusiones) en
[`AVANCE DE PROYECTO 2.md`](./AVANCE%20DE%20PROYECTO%202.md).
