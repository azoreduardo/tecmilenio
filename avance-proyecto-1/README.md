# Asistente virtual de Servicios Escolares — Avance de Proyecto 1

Chatbot basado en reglas (Python 3.10+ y NLTK) que responde consultas frecuentes de
estudiantes sobre horarios, pago de colegiatura, constancias y soporte de plataformas.

## Qué hace

- Detecta la **intención** del mensaje comparando raíces de palabras (stemming) contra
  un vocabulario por intención.
- Extrae **entidades** (mes, tipo de constancia, plataforma) con diccionarios y regex.
- Responde con una plantilla personalizada o con un mensaje de **fallback** cuando no
  reconoce la consulta.

## Cómo ejecutarlo

```bash
pip install nltk
python chatbot.py      # modo conversación interactiva (consola)
python evaluar.py       # corre las 12 pruebas funcionales y genera pruebas/casos.csv
```

## Estructura

```text
avance-proyecto-1/
├── README.md                    # este archivo
├── AVANCE DE PROYECTO 1.md      # documento de entrega completo
├── chatbot.py                   # intenciones, entidades, detección y respuesta
├── evaluar.py                   # pruebas funcionales automatizadas
└── pruebas/
    └── casos.csv                # resultado real de las 12 conversaciones de prueba
```

## Resultado de las pruebas

11 de 12 conversaciones (92 %) obtuvieron la intención esperada. Ver el análisis
completo en la sección "Resultados" de
[`AVANCE DE PROYECTO 1.md`](./AVANCE%20DE%20PROYECTO%201.md).
