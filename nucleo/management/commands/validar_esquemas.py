"""Valida los documentos de MongoDB contra los JSON Schemas del proyecto.

Uso:
    python manage.py validar_esquemas
    python manage.py validar_esquemas --coleccion motos
    python manage.py validar_esquemas --detalle
"""

import pymongo
from django.conf import settings
from django.core.management.base import BaseCommand

from nucleo.esquemas import COLECCIONES, normalizar, validar
from nucleo.serializadores import modelo_de


class Command(BaseCommand):
    help = "Valida cada documento de MongoDB contra su JSON Schema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--coleccion",
            choices=sorted(COLECCIONES.keys()),
            help="Valida solo una coleccion (por defecto todas).",
        )
        parser.add_argument(
            "--detalle",
            action="store_true",
            help="Muestra cada documento con errores, no solo el resumen.",
        )
        parser.add_argument(
            "--limite",
            type=int,
            default=20,
            help="Maximo de errores mostrados por coleccion.",
        )

    def handle(self, *args, **options):
        configuracion = settings.DATABASES["default"]
        cliente = pymongo.MongoClient(configuracion["HOST"], serverSelectionTimeoutMS=8000)
        base = cliente[configuracion["NAME"]]
        try:
            cliente.admin.command("ping")
        except Exception as error:  # pragma: no cover - depende del entorno
            self.stderr.write(self.style.ERROR(f"No se pudo conectar a MongoDB: {error}"))
            return

        colecciones = [options["coleccion"]] if options["coleccion"] else list(COLECCIONES)
        total_documentos = 0
        total_errores = 0
        colecciones_con_problemas = []

        for nombre in colecciones:
            modelo = modelo_de(nombre)
            coleccion = base[modelo._meta.db_table]
            documentos = list(coleccion.find({}))
            total_documentos += len(documentos)
            errores = []
            for documento in documentos:
                problemas = validar(nombre, normalizar(documento, modelo))
                if problemas:
                    errores.append((documento.get("_id"), problemas))
            total_errores += len(errores)
            estado = self.style.SUCCESS("OK") if not errores else self.style.ERROR("FALLOS")
            self.stdout.write(
                f"{nombre:<15} {len(documentos):>4} documentos  "
                f"{len(errores):>3} con errores  [{estado}]"
            )
            if errores:
                colecciones_con_problemas.append(nombre)
                if options["detalle"]:
                    for identificador, problemas in errores[: options["limite"]]:
                        self.stdout.write(f"  - _id={identificador}")
                        for problema in problemas:
                            self.stdout.write(f"      {problema}")
                    if len(errores) > options["limite"]:
                        self.stdout.write(
                            f"  ... y {len(errores) - options['limite']} documento(s) mas"
                        )

        self.stdout.write("")
        self.stdout.write(
            f"Total: {total_documentos} documentos, {total_errores} con errores."
        )
        if colecciones_con_problemas:
            self.stderr.write(
                self.style.ERROR(
                    "Colecciones con errores: " + ", ".join(colecciones_con_problemas)
                )
            )
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("Todos los documentos cumplen su JSON Schema."))
