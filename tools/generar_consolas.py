"""Dibuja las capturas de consola capturadas en docs/consolas.json.

Uso:  python tools/generar_consolas.py
Genera docs/consolas/<id>.png con el aspecto de una terminal de Windows.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "docs" / "consolas.json"
SALIDA = RAIZ / "docs" / "consolas"

FONDO = "#0d1426"
FONDO_BARRA = "#18213b"
TEXTO = "#cdd7ea"
COLOR_PROMPT = "#7dd3fc"
COMANDO = "#f8fafc"
SALIDA_OK = "#4ade80"
SALIDA_MAL = "#f87171"
TITULO = "#94a3b8"
MARCA = "#f97316"

CARACTERES_POR_LINEA = 118
ALTO_LINEA = 0.30   # pulgadas por linea
ALTO_BARRA = 0.42
MARGEN = 0.28
PROMPT = "PS C:\\club-motociclistas>"
PROMPT_LONGITUD = len(PROMPT) + 1


def color_de_salida(linea):
    minuscula = linea.lower()
    if any(marca in minuscula for marca in (
        "traceback", "failed", "fatal", "error:", "exception",
    )):
        return SALIDA_MAL
    if any(marca in minuscula for marca in (
        "successfully", "no issues", "seed completado", "total:", "todos los documentos",
        "no migrations to apply", "operations to perform", "running migrations",
    )):
        return SALIDA_OK
    return TEXTO


def dibujar(bloque):
    lineas = []
    for bloque_consola in bloque["consola"]:
        lineas.append(("cmd", bloque_consola["cmd"]))
        salida = bloque_consola["salida"]
        if len(salida) > 18:
            salida = ["   ... (salida completa en la consola)"] + salida[-17:]
        for texto in salida:
            lineas.append(("out", texto))

    ancho_maximo = 40
    for tipo, texto in lineas:
        largo = len(texto) + (len("PS C:\\club_motociclistas> ") if tipo == "cmd" else 0)
        ancho_maximo = max(ancho_maximo, largo)
    ancho_maximo = min(ancho_maximo, CARACTERES_POR_LINEA)

    ancho = MARGEN * 2 + ancho_maximo * 0.0685
    alto = MARGEN * 2 + ALTO_BARRA + len(lineas) * ALTO_LINEA

    figura = plt.figure(figsize=(ancho, alto), dpi=150)
    eje = figura.add_axes([0, 0, 1, 1])
    eje.set_xlim(0, 1)
    eje.set_ylim(0, 1)
    eje.axis("off")
    eje.add_patch(
        FancyBboxPatch(
            (0.004, 0.004), 0.992, 0.992,
            boxstyle="round,pad=0.004,rounding_size=0.012",
            linewidth=1.6, edgecolor="#26324f", facecolor=FONDO, zorder=0,
        )
    )
    eje.add_patch(
        FancyBboxPatch(
            (0.004, 0.955), 0.992, 0.041,
            boxstyle="round,pad=0.004,rounding_size=0.012",
            linewidth=0, facecolor=FONDO_BARRA, zorder=1,
        )
    )
    eje.add_patch(plt.Circle((0.022, 0.975), 0.0055, color="#ef4444", zorder=2))
    eje.add_patch(plt.Circle((0.038, 0.975), 0.0055, color="#f59e0b", zorder=2))
    eje.add_patch(plt.Circle((0.054, 0.975), 0.0055, color="#22c55e", zorder=2))
    eje.text(
        0.5, 0.975, bloque["titulo"], color=TITULO, fontsize=8.5,
        ha="center", va="center", family="monospace", zorder=2,
    )

    y = 0.935
    margen = MARGEN / ancho
    ancho_caracter = 0.0686 / ancho
    inicio_comando = margen + PROMPT_LONGITUD * ancho_caracter
    for tipo, texto in lineas:
        if tipo == "cmd":
            eje.text(margen, y, PROMPT, color=COLOR_PROMPT,
                     fontsize=8.2, family="monospace", va="center", zorder=3)
            eje.text(inicio_comando, y, texto, color=COMANDO,
                     fontsize=8.2, family="monospace", va="center", zorder=3)
        else:
            eje.text(margen, y, texto[:CARACTERES_POR_LINEA], color=color_de_salida(texto),
                     fontsize=8.2, family="monospace", va="center", zorder=3)
        y -= ALTO_LINEA / alto

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{bloque['id']}.png"
    figura.savefig(destino, facecolor=FONDO, dpi=150)
    plt.close(figura)
    return destino


def main():
    bloques = json.loads(DATOS.read_text(encoding="utf-8"))
    for bloque in bloques:
        destino = dibujar(bloque)
        print(f"{destino.name}: ok")


if __name__ == "__main__":
    main()

