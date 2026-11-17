r"""Convierte 'AVANCE DE PROYECTO 2.md' a un .docx con formato basico (APA-friendly),
incluyendo tablas, bloques de codigo y el diagrama Mermaid representado como tabla
(mismo criterio que generar_docx.py del Avance de Proyecto 1).

Uso: python generar_docx.py
Requiere: pip install python-docx
"""
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

CARPETA = Path(__file__).parent
MD_PATH = CARPETA / "AVANCE DE PROYECTO 2.md"
DOCX_PATH = CARPETA / "AVANCE DE PROYECTO 2.docx"

FONT_NAME = "Times New Roman"
FONT_SIZE = Pt(12)
IMG_LINK_RE = re.compile(r"\[`?([^\]`]+?)`?\]\((\S+?\.png)\)")
IMG_MAX_WIDTH = Inches(5.5)


def set_base_style(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = FONT_NAME
    style.font.size = FONT_SIZE
    style.paragraph_format.line_spacing = 2.0
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)


def add_paragraph(doc: Document, text: str, *, indent=True, italic=False, bold=False, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2.0
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.5)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = FONT_NAME
    run.font.size = FONT_SIZE
    run.italic = italic
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    return p


def add_label_paragraph(doc: Document, label: str, rest: str):
    """Parrafo tipo '**Curso:** Desarrollo...' -> 'Curso:' en negritas + resto normal."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.first_line_indent = 0
    r1 = p.add_run(label)
    r1.bold = True
    r1.font.name = FONT_NAME
    r1.font.size = FONT_SIZE
    r2 = p.add_run(rest)
    r2.font.name = FONT_NAME
    r2.font.size = FONT_SIZE
    return p


def add_bullet(doc: Document, label: str, rest: str):
    try:
        p = doc.add_paragraph(style="List Bullet")
    except KeyError:
        p = doc.add_paragraph()
        p.add_run("• ")
    p.paragraph_format.line_spacing = 2.0
    if label:
        r1 = p.add_run(label)
        r1.bold = True
        r1.font.name = FONT_NAME
        r1.font.size = FONT_SIZE
    r2 = p.add_run(rest)
    r2.font.name = FONT_NAME
    r2.font.size = FONT_SIZE


def add_numbered(doc: Document, text: str):
    try:
        p = doc.add_paragraph(style="List Number")
    except KeyError:
        p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2.0
    run = p.add_run(text)
    run.font.name = FONT_NAME
    run.font.size = FONT_SIZE


def add_code_block(doc: Document, lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = 0
        run = p.add_run(line if line.strip() else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)


def set_cell_background(cell, color_hex: str):
    """Colorea el fondo de una celda (python-docx no lo expone directo, se hace a bajo nivel)."""
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color_hex)
    cell._tc.get_or_add_tcPr().append(shd)


def add_table(doc: Document, header, rows):
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    for cell, text in zip(table.rows[0].cells, header):
        cell.text = text
        set_cell_background(cell, "00554B")
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.name = FONT_NAME
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for idx, row in enumerate(rows):
        cells = table.add_row().cells
        if idx % 2 == 1:
            for cell in cells:
                set_cell_background(cell, "F2F2F2")
        for cell, text in zip(cells, row):
            cell.text = text
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = FONT_NAME
                    r.font.size = Pt(10)


def extraer_imagenes(texto: str):
    """Quita del texto los enlaces a .png y devuelve (texto_limpio, [(label, ruta), ...])."""
    encontradas = IMG_LINK_RE.findall(texto)
    texto = IMG_LINK_RE.sub("", texto)
    texto = re.sub(r"\s+y\s+\.", ".", texto)
    texto = re.sub(r":\s*\.", ":", texto)
    texto = re.sub(r"\s{2,}", " ", texto).strip()
    return texto, encontradas


def add_imagen(doc: Document, label: str, ruta_relativa: str):
    ruta = (CARPETA / ruta_relativa).resolve()
    if not ruta.exists():
        add_paragraph(doc, f"[Figura no encontrada: {label}]", indent=False, italic=True)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = 0
    run = p.add_run()
    run.add_picture(str(ruta), width=IMG_MAX_WIDTH)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = 0
    cap.paragraph_format.space_after = Pt(12)
    r = cap.add_run(label)
    r.italic = True
    r.font.name = FONT_NAME
    r.font.size = Pt(9.5)


def render_paragraph_con_imagenes(doc: Document, texto: str, *, label=None):
    """Igual que add_paragraph/add_label_paragraph, pero incrusta las imágenes .png
    referenciadas en el texto (en vez de dejarlas como un nombre de archivo suelto)."""
    texto_limpio, imagenes = extraer_imagenes(texto)
    if texto_limpio:
        if label:
            add_label_paragraph(doc, label, clean_inline(texto_limpio))
        else:
            add_paragraph(doc, clean_inline(texto_limpio))
    for etiqueta, ruta in imagenes:
        add_imagen(doc, etiqueta, ruta)


def clean_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


# El unico diagrama Mermaid de este documento (arquitectura multimodal) se traduce a
# una tabla redactada a mano -convierte mejor a Word/PDF que un volcado en texto de
# cajas y flechas- en lugar de intentar parsear el Mermaid automaticamente.
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


def render_body(doc: Document, lines):
    i = 0
    mermaid_vistos = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.strip() == "---":
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
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # saltar cierre ```
            if lang == "mermaid":
                if mermaid_vistos < len(DIAGRAMAS_COMO_TABLA):
                    header, rows = DIAGRAMAS_COMO_TABLA[mermaid_vistos]
                    add_table(doc, header, rows)
                mermaid_vistos += 1
            else:
                add_code_block(doc, block)
            continue

        if line.startswith("##### "):
            doc.add_heading(clean_inline(line[6:].strip()), level=4)
            i += 1
            continue

        if line.startswith("#### "):
            doc.add_heading(clean_inline(line[5:].strip()), level=3)
            i += 1
            continue

        if line.startswith("### "):
            doc.add_heading(clean_inline(line[4:].strip()), level=2)
            i += 1
            continue

        if line.startswith("## "):
            doc.add_heading(clean_inline(line[3:].strip()), level=1)
            i += 1
            continue

        if line.startswith("# "):
            doc.add_heading(clean_inline(line[2:].strip()), level=0)
            i += 1
            continue

        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = [
                [clean_inline(c.strip()) for c in tl.strip("|").split("|")]
                for tl in table_lines
                if not set(tl.replace("|", "").strip()) <= {"-", " ", ":"}
            ]
            if rows:
                add_table(doc, rows[0], rows[1:])
            continue

        if line.startswith("- "):
            buffer = [line[2:]]
            i += 1
            while i < len(lines) and lines[i].strip() and not _es_inicio_de_bloque(lines[i]):
                buffer.append(lines[i].strip())
                i += 1
            content = " ".join(buffer)
            m = re.match(r"\*\*(.+?):\*\*\s*(.*)", content)
            if m:
                add_bullet(doc, m.group(1) + ": ", clean_inline(m.group(2)))
            else:
                add_bullet(doc, "", clean_inline(content))
            continue

        if re.match(r"^\d+\.\s", line):
            buffer = [re.sub(r"^\d+\.\s", "", line)]
            i += 1
            while i < len(lines) and lines[i].strip() and not _es_inicio_de_bloque(lines[i]):
                buffer.append(lines[i].strip())
                i += 1
            content = " ".join(buffer)
            add_numbered(doc, clean_inline(content))
            continue

        if line.startswith(">"):
            buffer = []
            while i < len(lines) and lines[i].rstrip().startswith(">"):
                buffer.append(lines[i].rstrip().lstrip(">").strip())
                i += 1
            texto = " ".join(p for p in buffer if p)
            add_paragraph(doc, clean_inline(texto), indent=False, italic=True)
            continue

        # Parrafo normal: en Markdown, lineas seguidas sin blanco entre ellas
        # son el MISMO parrafo (salto de linea "suave" por ancho de columna).
        # Hay que juntarlas antes de limpiar negritas/enlaces, si no, una
        # palabra en negritas partida a la mitad por el ancho de linea deja
        # asteriscos sueltos y genera un parrafo de Word por cada linea del
        # archivo en lugar de un parrafo por idea.
        buffer = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not _es_inicio_de_bloque(lines[i]):
            buffer.append(lines[i].rstrip())
            i += 1
        texto = " ".join(buffer)
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)", texto)
        if m:
            render_paragraph_con_imagenes(doc, m.group(2), label=m.group(1) + ": ")
        else:
            render_paragraph_con_imagenes(doc, texto)


def _es_inicio_de_bloque(line: str) -> bool:
    """True si esta linea empieza una construccion especial (no es texto corrido)."""
    l = line.rstrip()
    return (
        l.strip() == "---"
        or l.startswith("```")
        or l.startswith("#")
        or l.startswith("|")
        or l.startswith("- ")
        or l.startswith(">")
        or bool(re.match(r"^\d+\.\s", l))
        or bool(re.match(r"^\*\*(.+?):\*\*", l.strip()))
    )


def main():
    raw = MD_PATH.read_text(encoding="utf-8")
    lines = raw.split("\n")

    doc = Document()
    set_base_style(doc)
    render_body(doc, lines)
    doc.save(DOCX_PATH)
    print(f"Documento generado: {DOCX_PATH}")


if __name__ == "__main__":
    main()
