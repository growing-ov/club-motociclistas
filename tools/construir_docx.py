"""Convierte un documento Markdown del proyecto en un archivo DOCX con imagenes.

Uso (PowerShell):
    python tools/construir_docx.py docs/DOCUMENTACION.md docs/Club_de_Motociclistas_Documentacion.docx --titulo "Club de Motociclistas" --subtitulo "Documentacion tecnica"

Soporta el subconjunto de Markdown usado en docs/: titulos, parrafos, listas,
tablas, bloques de codigo, citas, imagenes, pies de imagen y separadores.
"""

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AZUL = RGBColor(0x1B, 0x4F, 0x9C)
AZUL_OSCURO = RGBColor(0x10, 0x2A, 0x43)
GRIS = RGBColor(0x44, 0x4B, 0x54)
CODIGO_BG = "F4F6F8"
TABLA_CABECERA = "1B4F9C"
ANCHO_IMAGEN = Cm(16.0)


# ---------------------------------------------------------------- utilidades
def sombrear(celda, color_hex):
    tc_pr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def borde_parrafo(parrafo, color="D0D7DE", tamano=6):
    p_pr = parrafo._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    for lado in ("top", "left", "bottom", "right"):
        elemento = OxmlElement(f"w:{lado}")
        elemento.set(qn("w:val"), "single")
        elemento.set(qn("w:sz"), str(tamano))
        elemento.set(qn("w:space"), "4")
        elemento.set(qn("w:color"), color)
        borders.append(elemento)
    p_pr.append(borders)


def sombrear_parrafo(parrafo, color_hex):
    p_pr = parrafo._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), color_hex)
    p_pr.append(shd)


def escribir_campo(parrafo, instruccion):
    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    texto = OxmlElement("w:instrText")
    texto.set(qn("xml:space"), "preserve")
    texto.text = instruccion
    separador = OxmlElement("w:fldChar")
    separador.set(qn("w:fldCharType"), "separate")
    fin = OxmlElement("w:fldChar")
    fin.set(qn("w:fldCharType"), "end")
    run = parrafo.add_run()
    run._r.append(inicio)
    run._r.append(texto)
    run._r.append(separador)
    run._r.append(fin)


# ------------------------------------------------------------------- Markdown
def partes_en_linea(texto):
    """Divide el texto en (tipo, contenido) para formato en linea."""
    patron = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+?\*)")
    for trozo in patron.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**"):
            yield "negrita", trozo[2:-2]
        elif trozo.startswith("`") and trozo.endswith("`"):
            yield "codigo", trozo[1:-1]
        elif trozo.startswith("*") and trozo.endswith("*"):
            yield "cursiva", trozo[1:-1]
        else:
            yield "texto", trozo


def escribir_en_linea(parrafo, texto, base=None):
    base = base or Pt(11)
    for tipo, contenido in partes_en_linea(texto):
        run = parrafo.add_run(contenido)
        run.font.size = base
        if tipo == "negrita":
            run.bold = True
        elif tipo == "codigo":
            run.font.name = "Consolas"
            run.font.size = Pt(base.pt - 1)
            run.font.color.rgb = RGBColor(0xB3, 0x1E, 0x3C)
        elif tipo == "cursiva":
            run.italic = True
            run.font.color.rgb = GRIS
        else:
            run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)


def celdas_de_fila(linea):
    linea = linea.strip()
    if linea.startswith("|"):
        linea = linea[1:]
    if linea.endswith("|"):
        linea = linea[:-1]
    return [celda.strip() for celda in linea.split("|")]


# ------------------------------------------------------------------ documento
def construir(md_ruta, docx_ruta, titulo, subtitulo, portada=None):
    md = Path(md_ruta)
    base = md.parent
    texto = md.read_text(encoding="utf-8")
    lineas = texto.splitlines()

    documento = Document()
    configurar_pagina(documento)
    estilos = configurar_estilos(documento)

    if portada and (base / portada).exists():
        agregar_portada(documento, titulo, subtitulo, base / portada)

    indice = documento.add_paragraph()
    indice.alignment = WD_ALIGN_PARAGRAPH.LEFT
    escribir_campo(indice, r'TOC \o "1-3" \h \z \u')
    documento.add_page_break()

    i = 0
    total = len(lineas)
    while i < total:
        linea = lineas[i]
        stripped = linea.strip()

        if not stripped:
            i += 1
            continue

        # Separador horizontal
        if re.fullmatch(r"-{3,}", stripped):
            i += 1
            continue

        # Bloque de codigo
        if stripped.startswith("```"):
            lenguaje = stripped[3:].strip()
            i += 1
            codigo = []
            while i < total and not lineas[i].strip().startswith("```"):
                codigo.append(lineas[i])
                i += 1
            i += 1
            agregar_codigo(documento, "\n".join(codigo), lenguaje)
            continue

        # Imagen
        imagen = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if imagen:
            alt, ruta = imagen.group(1), imagen.group(2)
            i += 1
            pie = ""
            if i < total and lineas[i].strip().startswith("*") and lineas[i].strip().endswith("*"):
                pie = lineas[i].strip().strip("*")
                i += 1
            agregar_imagen(documento, base / ruta, alt, pie)
            continue

        # Tabla
        if stripped.startswith("|") and i + 1 < total and re.match(
            r"^\|[\s\-:|]+\|?$", lineas[i + 1].strip()
        ):
            cabecera = celdas_de_fila(linea)
            i += 2
            filas = []
            while i < total and lineas[i].strip().startswith("|"):
                filas.append(celdas_de_fila(lineas[i]))
                i += 1
            agregar_tabla(documento, cabecera, filas)
            continue

        # Titulos
        titulo_nivel = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if titulo_nivel:
            nivel = len(titulo_nivel.group(1))
            texto_titulo = titulo_nivel.group(2)
            if nivel == 1:
                documento.add_page_break()
            parrafo = documento.add_heading(level=nivel)
            escribir_en_linea(parrafo, texto_titulo, Pt(20 if nivel == 1 else 16))
            for run in parrafo.runs:
                run.font.color.rgb = AZUL_OSCURO if nivel <= 2 else AZUL
            i += 1
            continue

        # Cita
        if stripped.startswith(">"):
            contenido = []
            while i < total and lineas[i].strip().startswith(">"):
                contenido.append(lineas[i].strip().lstrip(">").strip())
                i += 1
            agregar_cita(documento, " ".join(contenido))
            continue

        # Listas
        if re.match(r"^([-*]|\d+\.)\s+", stripped):
            elementos = []
            while i < total and re.match(r"^([-*]|\d+\.)\s+", lineas[i].strip()):
                marca = re.match(r"^([-*]|\d+\.)\s+", lineas[i].strip())
                tipo = "numero" if marca.group(1)[0].isdigit() else "vinieta"
                elementos.append((tipo, lineas[i].strip()[len(marca.group(0)):]))
                i += 1
            agregar_lista(documento, elementos)
            continue

        # Parrafo normal (puede ocupar varias lineas)
        parrafo_texto = []
        while i < total and lineas[i].strip() and not re.match(
            r"^(#{1,4}\s|```|\||>|([-*]|\d+\.)\s|!\[)", lineas[i].strip()
        ):
            parrafo_texto.append(lineas[i].strip())
            i += 1
        if parrafo_texto:
            parrafo = documento.add_paragraph()
            parrafo.paragraph_format.space_after = Pt(6)
            parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            escribir_en_linea(parrafo, " ".join(parrafo_texto))
        else:
            i += 1

    agregar_pie(documento)
    destino = Path(docx_ruta)
    documento.save(destino)
    return destino


def configurar_pagina(documento):
    seccion = documento.sections[0]
    seccion.page_width = Cm(21.0)
    seccion.page_height = Cm(29.7)
    seccion.top_margin = Cm(2.2)
    seccion.bottom_margin = Cm(2.0)
    seccion.left_margin = Cm(2.4)
    seccion.right_margin = Cm(2.2)


def configurar_estilos(documento):
    normal = documento.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    return documento.styles


def agregar_portada(documento, titulo, subtitulo, imagen):
    documento.add_paragraph()
    parrafo = documento.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = parrafo.add_run(titulo)
    run.bold = True
    run.font.size = Pt(30)
    run.font.color.rgb = AZUL_OSCURO

    parrafo = documento.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = parrafo.add_run(subtitulo)
    run.font.size = Pt(15)
    run.font.color.rgb = AZUL

    documento.add_paragraph()
    parrafo = documento.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.add_run().add_picture(str(imagen), width=Cm(15.5))

    documento.add_paragraph()
    parrafo = documento.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = parrafo.add_run("Club de Motociclistas · Django 6.1 + MongoDB Atlas + Docker")
    run.font.size = Pt(11)
    run.font.color.rgb = GRIS
    documento.add_page_break()


def agregar_codigo(documento, codigo, lenguaje):
    parrafo = documento.add_paragraph()
    parrafo.paragraph_format.space_before = Pt(6)
    parrafo.paragraph_format.space_after = Pt(10)
    parrafo.paragraph_format.left_indent = Cm(0.4)
    sombrear_parrafo(parrafo, CODIGO_BG)
    borde_parrafo(parrafo)
    run = parrafo.add_run(codigo if codigo.strip() else "")
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)


def agregar_imagen(documento, ruta, alt, pie):
    if not ruta.exists():
        parrafo = documento.add_paragraph()
        run = parrafo.add_run(f"[imagen no encontrada: {ruta.name}]")
        run.italic = True
        run.font.color.rgb = GRIS
        return
    parrafo = documento.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.paragraph_format.space_before = Pt(10)
    parrafo.add_run().add_picture(str(ruta), width=ANCHO_IMAGEN)
    if pie:
        parrafo_pie = documento.add_paragraph()
        parrafo_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
        parrafo_pie.paragraph_format.space_after = Pt(12)
        escribir_en_linea(parrafo_pie, pie, Pt(9.5))
        for run in parrafo_pie.runs:
            run.italic = True
            run.font.color.rgb = GRIS


def agregar_tabla(documento, cabecera, filas):
    if not cabecera:
        return
    tabla = documento.add_table(rows=1, cols=len(cabecera))
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    for indice, texto in enumerate(cabecera):
        celda = tabla.rows[0].cells[indice]
        celda.text = ""
        parrafo = celda.paragraphs[0]
        run = parrafo.add_run(texto)
        run.bold = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        sombrear(celda, TABLA_CABECERA)
    for fila in filas:
        celdas = tabla.add_row().cells
        for indice, texto in enumerate(fila[: len(cabecera)]):
            celdas[indice].text = ""
            parrafo = celdas[indice].paragraphs[0]
            parrafo.paragraph_format.space_after = Pt(2)
            escribir_en_linea(parrafo, texto, Pt(9.5))
    documento.add_paragraph().paragraph_format.space_after = Pt(4)


def agregar_cita(documento, texto):
    parrafo = documento.add_paragraph()
    parrafo.paragraph_format.left_indent = Cm(0.6)
    parrafo.paragraph_format.right_indent = Cm(0.4)
    parrafo.paragraph_format.space_before = Pt(6)
    sombrear_parrafo(parrafo, "EEF3FA")
    borde_parrafo(parrafo, color="1B4F9C")
    escribir_en_linea(parrafo, texto, Pt(10.5))


def agregar_lista(documento, elementos):
    for tipo, texto in elementos:
        parrafo = documento.add_paragraph(style="List Bullet" if tipo == "vinieta" else "List Number")
        parrafo.paragraph_format.space_after = Pt(2)
        escribir_en_linea(parrafo, texto, Pt(10.5))


def agregar_pie(documento):
    seccion = documento.sections[0]
    pie = seccion.footer.paragraphs[0]
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = pie.add_run("Club de Motociclistas · pagina ")
    run.font.size = Pt(8.5)
    run.font.color.rgb = GRIS
    escribir_campo(pie, "PAGE")
    run = pie.add_run(" de ")
    run.font.size = Pt(8.5)
    run.font.color.rgb = GRIS
    escribir_campo(pie, "NUMPAGES")


def main():
    analizador = argparse.ArgumentParser()
    analizador.add_argument("markdown")
    analizador.add_argument("docx")
    analizador.add_argument("--titulo", default="Club de Motociclistas")
    analizador.add_argument("--subtitulo", default="Documentacion tecnica")
    analizador.add_argument("--portada", default=None)
    argumentos = analizador.parse_args()
    destino = construir(
        argumentos.markdown,
        argumentos.docx,
        argumentos.titulo,
        argumentos.subtitulo,
        argumentos.portada,
    )
    print(f"DOCX generado: {destino}")


if __name__ == "__main__":
    main()
