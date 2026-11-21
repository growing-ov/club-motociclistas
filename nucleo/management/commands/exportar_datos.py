"""Exporta las colecciones del club a archivos JSON que cumplen los esquemas.

Uso:
    python manage.py exportar_datos
    python manage.py exportar_datos --salida datos_exportados
    python manage.py exportar_datos --coleccion rodadas
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from nucleo.esquemas import COLECCIONES, validar
from nucleo.serializadores import documentos_de


class Command(BaseCommand):
    help = "Exporta las colecciones a archivos JSON validados contra los JSON Schemas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--salida",
            default="datos_exportados",
            help="Carpeta destino de los archivos JSON.",
        )
        parser.add_argument(
            "--coleccion",
            choices=sorted(COLECCIONES.keys()),
            help="Exporta solo una coleccion.",
        )
        parser.add_argument(
            "--sin-validar",
            action="store_true",
            help="No valida los datos contra el esquema antes de exportar.",
        )

    def handle(self, *args, **options):
        destino = Path(options["salida"])
        destino.mkdir(parents=True, exist_ok=True)

        colecciones = [options["coleccion"]] if options["coleccion"] else list(COLECCIONES)
        problemas = 0

        for nombre in colecciones:
            documentos = documentos_de(nombre)
            if not options["sin_validar"]:
                for documento in documentos:
                    errores = validar(nombre, documento)
                    if errores:
                        problemas += 1
                        self.stderr.write(
                            self.style.ERROR(f"{nombre}: documento invalido -> {errores}")
                        )
            archivo = destino / f"{nombre}.json"
            archivo.write_text(
                json.dumps(documentos, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self.stdout.write(
                self.style.SUCCESS(f"{nombre:<15} {len(documentos):>4} documentos -> {archivo}")
            )

        self.stdout.write("")
        self.stdout.write(f"Archivos escritos en: {destino.resolve()}")
        if problemas:
            self.stderr.write(self.style.ERROR(f"{problemas} documento(s) no cumplen el esquema."))
            raise SystemExit(1)
