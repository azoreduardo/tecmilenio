"""Clasificador de imágenes: CNN con transferencia de aprendizaje (ResNet50).

Avance de Proyecto 2 - MBIA2602 - Instrucciones 7 y 8.
Clasifica el tipo de documento/imagen que un estudiante podría adjuntar al
Asistente virtual de Servicios Escolares: constancia, comprobante de pago,
credencial o captura de un error de plataforma (ver ../imagenes/generar_dataset.py).

Usa ResNet50 preentrenada en ImageNet, congela el backbone y entrena solo la
cabeza de clasificación (transfer learning por extracción de características).
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import ResNet50_Weights, resnet50

CARPETA = Path(__file__).parent
DATASET_DIR = CARPETA / "dataset"
RESULTADOS = CARPETA / "resultados"
RESULTADOS.mkdir(exist_ok=True)

DISPOSITIVO = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NORMALIZACION = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

TRANSFORM_TRAIN = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(8),
    transforms.ColorJitter(brightness=0.15, contrast=0.15),
    transforms.ToTensor(),
    NORMALIZACION,
])
TRANSFORM_EVAL = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    NORMALIZACION,
])


def cargar_datos(batch_size: int = 16):
    train_ds = datasets.ImageFolder(DATASET_DIR / "train", transform=TRANSFORM_TRAIN)
    val_ds = datasets.ImageFolder(DATASET_DIR / "val", transform=TRANSFORM_EVAL)
    test_ds = datasets.ImageFolder(DATASET_DIR / "test", transform=TRANSFORM_EVAL)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    test_loader = DataLoader(test_ds, batch_size=batch_size)
    return train_loader, val_loader, test_loader, train_ds.classes


def construir_modelo(n_clases: int) -> nn.Module:
    """ResNet50 preentrenada en ImageNet con el backbone congelado."""
    modelo = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    for parametro in modelo.parameters():
        parametro.requires_grad = False
    # Solo se entrena la cabeza de clasificación (transferencia de aprendizaje).
    modelo.fc = nn.Linear(modelo.fc.in_features, n_clases)
    return modelo.to(DISPOSITIVO)


def evaluar(modelo, loader) -> tuple[list[int], list[int]]:
    modelo.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(DISPOSITIVO)
            salidas = modelo(x)
            pred = salidas.argmax(dim=1).cpu().numpy()
            y_true.extend(y.numpy())
            y_pred.extend(pred)
    return y_true, y_pred


def entrenar(modelo, train_loader, val_loader, epocas: int = 8, lr: float = 1e-3):
    criterio = nn.CrossEntropyLoss()
    optimizador = optim.Adam(modelo.fc.parameters(), lr=lr)
    historial = {"train_loss": [], "val_accuracy": []}

    for epoca in range(1, epocas + 1):
        modelo.train()
        perdida_total = 0.0
        for x, y in train_loader:
            x, y = x.to(DISPOSITIVO), y.to(DISPOSITIVO)
            optimizador.zero_grad()
            salidas = modelo(x)
            perdida = criterio(salidas, y)
            perdida.backward()
            optimizador.step()
            perdida_total += perdida.item() * x.size(0)

        perdida_media = perdida_total / len(train_loader.dataset)
        y_true, y_pred = evaluar(modelo, val_loader)
        acc_val = accuracy_score(y_true, y_pred)
        historial["train_loss"].append(perdida_media)
        historial["val_accuracy"].append(acc_val)
        print(f"Época {epoca}/{epocas} - pérdida: {perdida_media:.4f} - val_accuracy: {acc_val:.2%}")

    return historial


def graficar_historial(historial):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(historial["train_loss"], marker="o", color="#006644")
    ax1.set_title("Pérdida de entrenamiento")
    ax1.set_xlabel("Época")
    ax1.set_ylabel("Loss")

    ax2.plot(historial["val_accuracy"], marker="o", color="#2f7d4f")
    ax2.set_title("Accuracy de validación")
    ax2.set_xlabel("Época")
    ax2.set_ylabel("Accuracy")
    ax2.set_ylim(0, 1.05)

    fig.tight_layout()
    fig.savefig(RESULTADOS / "curvas_entrenamiento.png", dpi=150)
    plt.close(fig)


def main():
    train_loader, val_loader, test_loader, clases = cargar_datos()
    print(f"Clases detectadas: {clases}")
    print(f"Dispositivo: {DISPOSITIVO}")

    modelo = construir_modelo(len(clases))
    historial = entrenar(modelo, train_loader, val_loader)
    graficar_historial(historial)

    y_true, y_pred = evaluar(modelo, test_loader)
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    matriz = confusion_matrix(y_true, y_pred)

    print("\n=== Evaluación en conjunto de prueba ===")
    print(f"Accuracy:  {acc:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1-score:  {f1:.2%}")

    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(matriz, display_labels=clases).plot(
        ax=ax, xticks_rotation=30, cmap="Greens", colorbar=False
    )
    ax.set_title("Matriz de confusión - Clasificador visual (ResNet50)")
    fig.tight_layout()
    fig.savefig(RESULTADOS / "matriz_confusion_imagenes.png", dpi=150)
    plt.close(fig)

    torch.save(
        {"state_dict": modelo.state_dict(), "clases": clases},
        RESULTADOS / "modelo_imagenes.pt",
    )

    metricas = {
        "clases": clases,
        "accuracy": acc,
        "precision_macro": precision,
        "recall_macro": recall,
        "f1_macro": f1,
        "matriz_confusion": matriz.tolist(),
        "historial_entrenamiento": historial,
    }
    with open(RESULTADOS / "metricas_imagenes.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)
    print(f"\nModelo y métricas guardados en: {RESULTADOS}")


if __name__ == "__main__":
    main()
