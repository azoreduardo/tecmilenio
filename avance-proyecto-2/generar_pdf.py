r"""Convierte 'AVANCE DE PROYECTO 2.md' directamente a PDF (sin pasar por Word/.docx).

Se generó porque la conversión automática .docx -> PDF vía Word (COM) no está
disponible en este entorno (no hay sesión interactiva de Office). Este script
construye el PDF directamente desde el Markdown con reportlab e incrusta las
imágenes reales de resultados (matrices de confusión, curvas de entrenamiento)
en vez de dejarlas solo como texto con el nombre del archivo.

Uso: python generar_pdf.py
Requiere: pip install reportlab pillow
"""
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

CARPETA = Path(__file__).parent
MD_PATH = CARPETA / "AVANCE DE PROYECTO 2.md"
PDF_PATH = CARPETA / "AVANCE DE PROYECTO 2.pdf"

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = inch
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

FONT = "Times-Roman"
FONT_BOLD = "Times-Bold"
FONT_ITALIC = "Times-Italic"

# ---------------------------------------------------------------------------
# Estilos de párrafo (Times 12pt, interlineado doble, estilo APA-friendly)
# ---------------------------------------------------------------------------
STYLES = {
    "title": ParagraphStyle(
        "title", fontName=FONT_BOLD, fontSize=18, leading=22,
        alignment=TA_CENTER, spaceAfter=10, spaceBefore=4,
    ),
    "h1": ParagraphStyle(
        "h1", fontName=FONT_BOLD, fontSize=14, leading=18,
        spaceBefore=14, spaceAfter=8,
    ),
    "h2": ParagraphStyle(
        "h2", fontName=FONT_BOLD, fontSize=12.5, leading=16,
        spaceBefore=10, spaceAfter=6,
    ),
    "h3": ParagraphStyle(
        "h3", fontName=FONT_BOLD, fontSize=11.5, leading=15,
        spaceBefore=8, spaceAfter=5,
    ),
    "normal": ParagraphStyle(
        "normal", fontName=FONT, fontSize=11, leading=22,
        alignment=TA_JUSTIFY, spaceAfter=10,
    ),
    "label": ParagraphStyle(
        "label", fontName=FONT, fontSize=11, leading=18,
        alignment=TA_LEFT, spaceAfter=4,
    ),
    "quote": ParagraphStyle(
        "quote", fontName=FONT_ITALIC, fontSize=10.5, leading=16,
        leftIndent=24, spaceAfter=10, textColor=colors.HexColor("#333333"),
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName=FONT, fontSize=11, leading=16, spaceAfter=4,
    ),
    "cell": ParagraphStyle(
        "cell", fontName=FONT, fontSize=9, leading=12,
    ),
    "cell_bold": ParagraphStyle(
        "cell_bold", fontName=FONT_BOLD, fontSize=9, leading=12,
        textColor=colors.white,
    ),
    "caption": ParagraphStyle(
        "caption", fontName=FONT_ITALIC, fontSize=9, leading=12,
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=12,
        textColor=colors.HexColor("#444444"),
    ),
}

CODE_STYLE = ParagraphStyle(
    "code", fontName="Courier", fontSize=7.6, leading=9.5,
    leftIndent=6, spaceAfter=10, backColor=colors.HexColor("#f5f5f5"),
)

# Único diagrama Mermaid del documento (arquitectura multimodal): se traduce a
# una tabla redactada a mano, igual que en generar_docx.py.
TABLA_ARQUITECTURA = (
    ["Paso", "De", "Hacia", "Qué se envía"],
    [
        ["1", "Usuario", "Asistente multimodal", "Mensaje de texto y/o imagen"],
        ["2", "Asistente multimodal", "Clasificador de texto (TF-IDF + SVM)", "Mensaje de texto"],
        ["3", "Asistente multimodal", "Clasificador visual (ResNet50)", "Imagen adjunta"],
        ["4", "Clasificador de texto (TF-IDF + SVM)", "Integrador", "Intención detectada"],
        ["5", "Clasificador visual (ResNet50)", "Integrador", "Tipo de documento detectado"],
        ["6", "Integrador", "Usuario", "Respuesta combinada"],
    ],
)
DIAGRAMAS_COMO_TABLA = [TABLA_ARQUITECTURA]

IMG_LINK_RE = re.compile(r"\[`?([^\]`]+?)`?\]\((\S+?\.png)\)")
GENERIC_LINK_RE = re.compile(r"\[(.+?)\]\(.+?\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
CODE_RE = re.compile(r"`(.+?)`")


def extraer_imagenes(texto: str):
    """Quita del texto los enlaces a .png y devuelve (texto_limpio, [(label, path), ...])."""
    encontradas = IMG_LINK_RE.findall(texto)
    texto = IMG_LINK_RE.sub("", texto)
    texto = re.sub(r"\s+y\s+\.", ".", texto)
    texto = re.sub(r":\s*\.", ":", texto)
    texto = re.sub(r"\s{2,}", " ", texto).strip()
    return texto, encontradas


def escapar_xml(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_a_markup(texto: str) -> str:
    """Convierte markdown inline (negritas, cursivas, código, enlaces) al mini-XML de reportlab."""
    texto = escapar_xml(texto)
    texto = CODE_RE.sub(r'<font face="Courier" size="9">\1</font>', texto)
    texto = BOLD_RE.sub(r"<b>\1</b>", texto)
    texto = ITALIC_RE.sub(r"<i>\1</i>", texto)
    texto = GENERIC_LINK_RE.sub(r"\1", texto)
    return texto


def imagen_flowable(ruta_relativa: str, ancho_max=5.4 * inch):
    ruta = (CARPETA / ruta_relativa).resolve()
    if not ruta.exists():
        return None
    with PILImage.open(ruta) as im:
        w, h = im.size
    escala = min(ancho_max / w, 1.0)
    ancho, alto = w * escala, h * escala
    return Image(str(ruta), width=ancho, height=alto, hAlign="CENTER")


def parrafo(story, texto, estilo="normal"):
    texto_limpio, imagenes = extraer_imagenes(texto)
    if texto_limpio:
        story.append(Paragraph(md_a_markup(texto_limpio), STYLES[estilo]))
    for label, ruta in imagenes:
        img = imagen_flowable(ruta)
        if img is not None:
            story.append(Spacer(1, 4))
            story.append(img)
            story.append(Paragraph(md_a_markup(label), STYLES["caption"]))
        else:
            story.append(Paragraph(f"[Figura no encontrada: {escapar_xml(label)}]", STYLES["caption"]))


def tabla(story, header, rows):
    n = len(header)
    col_w = USABLE_WIDTH / n
    data = [[Paragraph(md_a_markup(h), STYLES["cell_bold"]) for h in header]]
    for row in rows:
        data.append([Paragraph(md_a_markup(c), STYLES["cell"]) for c in row])
    t = Table(data, colWidths=[col_w] * n, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00554B")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def es_inicio_de_bloque(line: str) -> bool:
    l = line.rstrip()
    return (
        l.strip() == "---"
        or l.startswith("```")
        or l.startswith("#")
        or l.startswith("|")
        or l.startswith("- ")
        or l.startswith(">")
        or bool(re.match(r"^\d+\.\s", l))
    )


def construir_story(lines):
    story = []
    i = 0
    mermaid_vistos = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.strip() == "---":
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#bbbbbb")))
            story.append(Spacer(1, 8))
            i += 1
            continue

        if line.strip().startswith("<details>"):
            while i < len(lines) and not lines[i].strip().startswith("</details>"):
                i += 1
            i += 1
            continue

        if line.startswith("```"):
            lang = line.strip("`").strip()
            i += 1
            bloque = []
            while i < len(lines) and not lines[i].startswith("```"):
                bloque.append(lines[i])
                i += 1
            i += 1
            if lang == "mermaid":
                if mermaid_vistos < len(DIAGRAMAS_COMO_TABLA):
                    header, rows = DIAGRAMAS_COMO_TABLA[mermaid_vistos]
                    tabla(story, header, rows)
                mermaid_vistos += 1
            else:
                texto_codigo = "\n".join(l if l.strip() else " " for l in bloque)
                story.append(Preformatted(texto_codigo, CODE_STYLE))
                story.append(Spacer(1, 8))
            continue

        if line.startswith("##### "):
            story.append(Paragraph(md_a_markup(line[6:].strip()), STYLES["h3"]))
            i += 1
            continue
        if line.startswith("#### "):
            story.append(Paragraph(md_a_markup(line[5:].strip()), STYLES["h3"]))
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(md_a_markup(line[4:].strip()), STYLES["h2"]))
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(md_a_markup(line[3:].strip()), STYLES["h1"]))
            i += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(md_a_markup(line[2:].strip()), STYLES["title"]))
            i += 1
            continue

        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = [
                [c.strip() for c in tl.strip("|").split("|")]
                for tl in table_lines
                if not set(tl.replace("|", "").strip()) <= {"-", " ", ":"}
            ]
            if rows:
                tabla(story, rows[0], rows[1:])
            continue

        if line.startswith("- "):
            items = []
            while True:
                buffer = [line[2:]]
                i += 1
                while i < len(lines) and lines[i].strip() and not es_inicio_de_bloque(lines[i]):
                    buffer.append(lines[i].strip())
                    i += 1
                contenido = " ".join(buffer)
                texto_limpio, _ = extraer_imagenes(contenido)
                items.append(ListItem(Paragraph(md_a_markup(texto_limpio), STYLES["bullet"]), leftIndent=14))
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].startswith("- "):
                    i, line = j, lines[j]
                    continue
                break
            story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14))
            continue

        if re.match(r"^\d+\.\s", line):
            items = []
            while True:
                buffer = [re.sub(r"^\d+\.\s", "", line)]
                i += 1
                while i < len(lines) and lines[i].strip() and not es_inicio_de_bloque(lines[i]):
                    buffer.append(lines[i].strip())
                    i += 1
                contenido = " ".join(buffer)
                texto_limpio, _ = extraer_imagenes(contenido)
                items.append(ListItem(Paragraph(md_a_markup(texto_limpio), STYLES["bullet"]), leftIndent=14))
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and re.match(r"^\d+\.\s", lines[j]):
                    i, line = j, lines[j]
                    continue
                break
            story.append(ListFlowable(items, bulletType="1", start=1, leftIndent=14))
            continue

        if line.startswith(">"):
            buffer = []
            while i < len(lines) and lines[i].rstrip().startswith(">"):
                buffer.append(lines[i].rstrip().lstrip(">").strip())
                i += 1
            texto = " ".join(p for p in buffer if p)
            story.append(Paragraph(md_a_markup(texto), STYLES["quote"]))
            continue

        # Párrafo normal: juntar líneas de "soft wrap" del Markdown en un solo párrafo.
        buffer = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not es_inicio_de_bloque(lines[i]):
            buffer.append(lines[i].rstrip())
            i += 1
        texto = " ".join(buffer)
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)", texto)
        if m:
            parrafo(story, f"**{m.group(1)}:** {m.group(2)}", estilo="label")
        else:
            parrafo(story, texto)

    return story


def main():
    raw = MD_PATH.read_text(encoding="utf-8")
    lines = raw.split("\n")
    story = construir_story(lines)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        topMargin=MARGIN, bottomMargin=MARGIN,
        leftMargin=MARGIN, rightMargin=MARGIN,
        title="Avance de Proyecto 2 - Asistente virtual de Servicios Escolares",
        author="José Eduardo Patena Ovalle",
    )
    doc.build(story)
    print(f"PDF generado: {PDF_PATH}")


if __name__ == "__main__":
    main()
