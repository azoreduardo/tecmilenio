"""Generador del dataset sintético de imágenes (instrucción 6).

Avance de Proyecto 2 - MBIA2602.
Crea imágenes sintéticas de 4 clases ligadas al dominio del Asistente virtual de
Servicios Escolares (mismo problema del Avance de Proyecto 1): documentos que un
estudiante podría adjuntar al chatbot.

Clases:
    - constancia        : constancia de estudios / no adeudo / kardex
    - comprobante_pago   : recibo de pago de colegiatura
    - credencial         : credencial de estudiante
    - captura_error      : captura de un error de plataforma (Canvas/Blackboard/correo)

Se generan por código (sin descargar nada de internet) para evitar cualquier
problema de derechos de autor y para que el dataset sea 100 % reproducible.
Cada imagen varía textos, colores, ruido y posición para simular variabilidad real.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CARPETA = Path(__file__).parent
DATASET_DIR = CARPETA / "dataset"

ANCHO, ALTO = 224, 224
VERDE_TEC = (0, 102, 68)
VERDE_CLARO = (190, 225, 205)

NOMBRES = [
    "Ana López García", "Luis Martínez Hernández", "María Fernández Ruiz",
    "Carlos Jiménez Torres", "Sofía Ramírez Cruz", "Jorge Pérez Flores",
    "Daniela Gómez Castro", "Pedro Sánchez Morales", "Laura Díaz Romero",
    "Miguel Ángel Vargas",
]
MATRICULAS = [f"T{random.randint(1000000, 9999999)}" for _ in range(30)]
TIPOS_CONSTANCIA = ["ESTUDIOS", "NO ADEUDO", "KARDEX"]
PLATAFORMAS_ERROR = ["Canvas", "Blackboard", "Correo institucional"]
MENSAJES_ERROR = [
    "No se pudo iniciar sesión",
    "Error de conexión con el servidor",
    "Tu sesión ha expirado",
    "Pago no procesado",
    "Usuario o contraseña incorrectos",
]


def _fuente(tam: int) -> ImageFont.FreeTypeFont:
    return ImageFont.load_default(size=tam)


def _ruido(img: Image.Image, intensidad: float = 0.03) -> Image.Image:
    """Agrega ruido leve y una ligera difuminación para simular fotos/capturas reales."""
    import numpy as np

    arr = np.array(img).astype(np.int16)
    ruido = np.random.normal(0, 255 * intensidad, arr.shape).astype(np.int16)
    arr = np.clip(arr + ruido, 0, 255).astype("uint8")
    img = Image.fromarray(arr)
    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))
    return img


def _fondo(color_base=(255, 255, 255), variacion=6):
    r, g, b = color_base
    r = max(0, min(255, r + random.randint(-variacion, variacion)))
    g = max(0, min(255, g + random.randint(-variacion, variacion)))
    b = max(0, min(255, b + random.randint(-variacion, variacion)))
    return (r, g, b)


def generar_constancia() -> Image.Image:
    img = Image.new("RGB", (ANCHO, ALTO), _fondo((250, 250, 245)))
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, ANCHO - 4, ALTO - 4], outline=VERDE_TEC, width=3)
    d.rectangle([0, 0, ANCHO, 26], fill=VERDE_TEC)
    d.text((8, 5), "UNIVERSIDAD TECMILENIO", font=_fuente(11), fill="white")

    tipo = random.choice(TIPOS_CONSTANCIA)
    d.text((10, 34), "CONSTANCIA DE", font=_fuente(13), fill=VERDE_TEC)
    d.text((10, 50), tipo, font=_fuente(13), fill=VERDE_TEC)

    nombre = random.choice(NOMBRES)
    matricula = random.choice(MATRICULAS)
    folio = random.randint(1000, 9999)
    d.line([(10, 72), (ANCHO - 10, 72)], fill=VERDE_CLARO, width=1)
    d.text((10, 80), "Se hace constar que:", font=_fuente(9), fill=(60, 60, 60))
    d.text((10, 95), nombre, font=_fuente(10), fill=(20, 20, 20))
    d.text((10, 112), f"Matrícula: {matricula}", font=_fuente(9), fill=(60, 60, 60))
    d.text((10, 128), "se encuentra inscrito(a) en el", font=_fuente(9), fill=(60, 60, 60))
    d.text((10, 142), "periodo escolar vigente.", font=_fuente(9), fill=(60, 60, 60))
    d.text((10, 164), f"Folio: {folio:04d}", font=_fuente(9), fill=(60, 60, 60))
    for y in (184, 190, 196):
        d.line([(10, y), (ANCHO - 10, y)], fill=(225, 225, 220), width=1)
    d.text((ANCHO - 70, ALTO - 24), "[SELLO]", font=_fuente(9), fill=(150, 150, 150))
    return _ruido(img)


def generar_comprobante_pago() -> Image.Image:
    img = Image.new("RGB", (ANCHO, ALTO), _fondo((255, 255, 255)))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, ANCHO - 10, ALTO - 10], outline=(80, 80, 80), width=2)
    d.text((16, 16), "COMPROBANTE DE PAGO", font=_fuente(12), fill=(20, 20, 20))
    d.line([(16, 34), (ANCHO - 16, 34)], fill=(180, 180, 180), width=1)

    concepto = "Colegiatura - " + random.choice(
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    )
    monto = random.randint(3500, 9800)
    referencia = random.randint(100000000, 999999999)

    d.text((16, 44), f"Concepto: {concepto}", font=_fuente(9), fill=(40, 40, 40))
    d.text((16, 60), f"Referencia: {referencia}", font=_fuente(9), fill=(40, 40, 40))
    d.text((16, 76), "Estatus: PAGADO", font=_fuente(9), fill=(0, 130, 60))
    d.text((16, 100), f"$ {monto:,.2f}", font=_fuente(20), fill=(20, 20, 20))

    # "código de barras" simulado
    x = 16
    for _ in range(60):
        w = random.choice([1, 1, 2, 3])
        if random.random() < 0.55:
            d.rectangle([x, ALTO - 34, x + w, ALTO - 18], fill=(20, 20, 20))
        x += w + random.choice([1, 2])
        if x > ANCHO - 16:
            break
    return _ruido(img)


def generar_credencial() -> Image.Image:
    img = Image.new("RGB", (ANCHO, ALTO), _fondo(VERDE_CLARO))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, ANCHO, ALTO], outline=VERDE_TEC, width=4)
    d.rectangle([0, 0, ANCHO, 22], fill=VERDE_TEC)
    d.text((8, 4), "CREDENCIAL DE ESTUDIANTE", font=_fuente(10), fill="white")

    # Foto placeholder (silueta simple)
    d.rectangle([14, 34, 74, 104], fill=(230, 230, 230), outline=(120, 120, 120))
    d.ellipse([30, 42, 58, 70], fill=(180, 180, 180))
    d.pieslice([24, 66, 64, 110], 180, 360, fill=(180, 180, 180))

    nombre = random.choice(NOMBRES)
    matricula = random.choice(MATRICULAS)
    d.text((82, 40), nombre, font=_fuente(10), fill=(20, 20, 20))
    d.text((82, 58), f"Matrícula: {matricula}", font=_fuente(9), fill=(40, 40, 40))
    d.text((82, 74), "Lic. en Ciencia de Datos", font=_fuente(8), fill=(40, 40, 40))
    d.text((82, 90), "Vigencia: 2026", font=_fuente(8), fill=(40, 40, 40))

    # "QR" simulado: cuadrícula aleatoria blanco/negro
    qr_x, qr_y, celda = 14, 118, 7
    for i in range(12):
        for j in range(12):
            if random.random() < 0.5:
                x0 = qr_x + i * celda
                y0 = qr_y + j * celda
                d.rectangle([x0, y0, x0 + celda - 1, y0 + celda - 1], fill=(20, 20, 20))
    return _ruido(img)


def generar_captura_error() -> Image.Image:
    img = Image.new("RGB", (ANCHO, ALTO), _fondo((235, 235, 238)))
    d = ImageDraw.Draw(img)
    plataforma = random.choice(PLATAFORMAS_ERROR)
    mensaje = random.choice(MENSAJES_ERROR)

    # Barra de titulo de "ventana"
    d.rectangle([0, 0, ANCHO, 20], fill=(60, 60, 65))
    d.text((6, 4), plataforma, font=_fuente(9), fill="white")
    for i, color in enumerate([(230, 90, 80), (230, 190, 70), (110, 200, 110)]):
        d.ellipse([ANCHO - 18 - i * 14, 6, ANCHO - 10 - i * 14, 14], fill=color)

    # Icono de alerta
    cx, cy, r = ANCHO // 2, 80, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 60, 60))
    d.text((cx - 5, cy - 14), "!", font=_fuente(26), fill="white")

    d.text((ANCHO // 2 - len(mensaje) * 3, 118), mensaje, font=_fuente(9), fill=(30, 30, 30))
    d.rectangle([ANCHO // 2 - 40, 150, ANCHO // 2 + 40, 174], fill=(70, 120, 200))
    d.text((ANCHO // 2 - 28, 156), "Reintentar", font=_fuente(9), fill="white")
    return _ruido(img, intensidad=0.015)


GENERADORES = {
    "constancia": generar_constancia,
    "comprobante_pago": generar_comprobante_pago,
    "credencial": generar_credencial,
    "captura_error": generar_captura_error,
}

# train/val/test por clase
SPLITS = {"train": 90, "val": 20, "test": 20}


def main():
    random.seed(42)
    total = 0
    for clase, generador in GENERADORES.items():
        for split, cantidad in SPLITS.items():
            carpeta = DATASET_DIR / split / clase
            carpeta.mkdir(parents=True, exist_ok=True)
            for i in range(cantidad):
                img = generador()
                img.save(carpeta / f"{clase}_{split}_{i:03d}.png")
                total += 1
        print(f"Clase '{clase}': {sum(SPLITS.values())} imágenes generadas.")
    print(f"\nTotal de imágenes generadas: {total}")
    print(f"Guardadas en: {DATASET_DIR}")


if __name__ == "__main__":
    main()
