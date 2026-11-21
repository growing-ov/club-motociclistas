"""Genera los diagramas del proyecto con el modelo de imagen de OpenAI.

Uso (PowerShell):
    $env:OPENAI_API_KEY="sk-..."
    python tools/generar_imagenes.py

Las imagenes se guardan en docs/diagramas/. Los prompts piden explicitamente
diagramas sin texto: las etiquetas se agregan despues como pie de imagen en
Markdown y en el documento DOCX, para que no aparezcan letras deformadas.
"""

import base64
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API = "https://api.openai.com/v1/images/generations"
MODELO = "gpt-image-2"
SALIDA = Path(__file__).resolve().parent.parent / "docs" / "diagramas"

BASE = (
    "flat vector technical diagram, clean white background, blue, light blue and "
    "slate gray palette, thin crisp strokes, professional minimal infographic style, "
    "no words, no letters, no numbers, no labels, high clarity"
)

DIAGRAMAS = [
    (
        "01-arquitectura-capas.png",
        "1536x1024",
        "low",
        "of a layered web application architecture: at the top a browser window icon, "
        "below it four horizontal stacked rounded rectangle layers connected by straight "
        "downward arrows, the layers holding simple icons: browser window, layout grid, "
        "gear, and a database cylinder, at the bottom a database cylinder with a cloud "
        "shape behind it representing an external server " + BASE,
    ),
    (
        "02-flujo-peticion.png",
        "1536x1024",
        "low",
        "of an http request flow: a horizontal pipeline of six rounded rectangles "
        "connected by right arrows, each holding a simple icon: browser window, server "
        "rack, gear, checklist, database cylinder, and a cloud database with a document "
        "icon, blue and slate gray palette, no words, no letters, no numbers " + BASE,
    ),
    (
        "03-arquitectura-docker.png",
        "1536x1024",
        "low",
        "of a containerized deployment: on the left two stacked build stage boxes with a "
        "large arrow pointing to a shipping container icon holding a server rack and a "
        "box of static files, on the right a cloud icon representing a remote database "
        "reached through a dashed line with a small shield icon, blue and slate gray "
        "palette, no words, no letters, no numbers " + BASE,
    ),
    (
        "04-modelo-datos.png",
        "1536x1024",
        "low",
        "of an entity relationship diagram: one central rounded node icon connected with "
        "lines to six smaller rounded node icons arranged around it, each containing a "
        "simple pictogram: person, document, motorcycle, wrench, calendar and picture "
        "frame, the connection lines end in small crow's foot marks, blue and slate "
        "gray palette, no words, no letters, no numbers " + BASE,
    ),
    (
        "05-integridad-borrado.png",
        "1024x1024",
        "low",
        "of a referential integrity rule: three parent icons, a person, a motorcycle and "
        "a calendar, each one above a group of small child icons connected by arrows, "
        "some child icons crossed out with a red diagonal line, blue and slate gray "
        "palette with red accents, no words, no letters, no numbers " + BASE,
    ),
    (
        "06-pipeline-docker.png",
        "1536x1024",
        "low",
        "of a build and deploy pipeline: five stages from left to right connected by "
        "arrows, a code repository branching icon, a folder with a gear, a container box, "
        "a browser window with a checkmark, and a terminal window, blue and slate gray "
        "palette, no words, no letters, no numbers " + BASE,
    ),
    (
        "07-flujo-tutorial.png",
        "1536x1024",
        "low",
        "of a step by step roadmap: seven circular steps connected in a rising path from "
        "the bottom left to the top right, each circle containing a simple pictogram: git "
        "branches, folder, database, gear, container box, wand, browser window, blue and "
        "slate gray palette, no words, no letters, no numbers " + BASE,
    ),
    (
        "08-estructura-proyecto.png",
        "1024x1024",
        "low",
        "of a project folder tree: one root folder icon on top branching into three "
        "folder icons, each branching into small document file icons, one branch "
        "highlighted in orange, blue and slate gray palette, no words, no letters, no "
        "numbers " + BASE,
    ),
    (
        "10-apps-dependencias.png",
        "1536x1024",
        "low",
        "of a python package dependency graph: one box on top branching down with arrows "
        "to three boxes in the middle, each of them branching down with arrows to two "
        "smaller boxes, clean dependency graph with arrow heads, blue and slate gray "
        "palette, no words, no letters, no numbers " + BASE,
    ),
    (
        "11-despliegue.png",
        "1536x1024",
        "low",
        "of a deployment topology: a user laptop on the left connected by an arrow to a "
        "docker container in the middle sitting on a docker whale block, and from the "
        "container a dashed arrow to a cloud with a database cylinder on the right, a "
        "shield icon on the connection, blue and slate gray palette, no words, no "
        "letters, no numbers " + BASE,
    ),
    (
        "09-portada.png",
        "1536x1024",
        "medium",
        "illustration of a motorcycle club management application: a laptop and a tablet "
        "showing abstract dashboard cards and charts, a stylized motorcycle silhouette "
        "beside them, dark navy background with orange and cyan accents, geometric "
        "flat shapes, no words, no letters, no numbers " + BASE,
    ),
]


def generar(nombre, size, quality, prompt, api_key):
    destino = SALIDA / nombre
    if destino.exists() and os.environ.get("FORZAR") != "1":
        return nombre, "ya existia"
    cuerpo = {
        "model": MODELO,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }
    peticion = urllib.request.Request(
        API,
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(peticion, timeout=600) as respuesta:
        datos = json.loads(respuesta.read())
    destino.write_bytes(base64.b64decode(datos["data"][0]["b64_json"]))
    return nombre, "generada"


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Falta la variable de entorno OPENAI_API_KEY.")
    SALIDA.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        resultados = list(
            pool.map(lambda args: generar(*args, api_key), DIAGRAMAS)
        )
    for nombre, estado in resultados:
        print(f"{nombre}: {estado}")


if __name__ == "__main__":
    main()
