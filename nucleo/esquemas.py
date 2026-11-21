"""Carga y validacion de los JSON Schemas del proyecto.

Los esquemas viven en ``schemas/`` y siguen el estandar JSON Schema
Draft 2020-12. Se usan para tres cosas:

1. Describir el contrato de datos de cada coleccion.
2. Validar los documentos guardados en MongoDB
   (``python manage.py validar_esquemas``).
3. Validar la salida de la API JSON antes de devolverla.

Los esquemas referencian las definiciones comunes de ``base.schema.json``
mediante un registro (``referencing.Registry``) que resuelve las
referencias relativas entre archivos.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

BASE_DIR = Path(__file__).resolve().parent.parent
CARPETA_SCHEMAS = BASE_DIR / "schemas"

#: Definicion de cada coleccion: modelo de Django y archivo de esquema.
COLECCIONES = {
    "motociclistas": {
        "titulo": "Motociclistas",
        "modelo": "socios.Motociclista",
        "esquema": "motociclista.schema.json",
        "orden": ("apellido", "nombre"),
    },
    "documentos": {
        "titulo": "Documentos de socios",
        "modelo": "socios.DocumentoSocio",
        "esquema": "documento_socio.schema.json",
        "orden": ("-fechaEmision",),
    },
    "motos": {
        "titulo": "Motos",
        "modelo": "flota.Moto",
        "esquema": "moto.schema.json",
        "orden": ("placa",),
    },
    "mantenimientos": {
        "titulo": "Mantenimientos",
        "modelo": "flota.Mantenimiento",
        "esquema": "mantenimiento.schema.json",
        "orden": ("-fecha",),
    },
    "accidentes": {
        "titulo": "Accidentes",
        "modelo": "flota.Accidente",
        "esquema": "accidente.schema.json",
        "orden": ("-fecha",),
    },
    "rodadas": {
        "titulo": "Rodadas",
        "modelo": "eventos.Rodada",
        "esquema": "rodada.schema.json",
        "orden": ("fechaSalida",),
    },
    "inscripciones": {
        "titulo": "Inscripciones",
        "modelo": "eventos.Inscripcion",
        "esquema": "inscripcion.schema.json",
        "orden": ("-fechaInscripcion",),
    },
    "galeria": {
        "titulo": "Galeria de fotos",
        "modelo": "eventos.Galeria",
        "esquema": "galeria.schema.json",
        "orden": ("-fechaSubida",),
    },
}


class ErrorEsquema(Exception):
    """Se lanza cuando un documento no cumple su JSON Schema."""


@lru_cache(maxsize=1)
def _contenidos():
    """Lee todos los archivos de esquema una sola vez."""
    contenidos = {}
    for archivo in sorted(CARPETA_SCHEMAS.glob("*.schema.json")):
        datos = json.loads(archivo.read_text(encoding="utf-8"))
        contenidos[archivo.name] = datos
    return contenidos


@lru_cache(maxsize=1)
def _registro():
    """Construye el registro que resuelve los ``$ref`` entre archivos."""
    recursos = []
    for datos in _contenidos().values():
        identificador = datos.get("$id")
        if not identificador:
            continue
        recursos.append(
            (
                identificador,
                Resource.from_contents(datos, default_specification=DRAFT202012),
            )
        )
    return Registry().with_resources(recursos)


@lru_cache(maxsize=None)
def esquema(nombre_coleccion):
    """Devuelve el diccionario del JSON Schema de una coleccion."""
    try:
        archivo = COLECCIONES[nombre_coleccion]["esquema"]
    except KeyError as error:
        raise ErrorEsquema(f"Coleccion desconocida: {nombre_coleccion}") from error
    return _contenidos()[archivo]


@lru_cache(maxsize=None)
def validador(nombre_coleccion):
    """Devuelve un validador ``Draft202012Validator`` para la coleccion."""
    return Draft202012Validator(esquema(nombre_coleccion), registry=_registro())


def validar(nombre_coleccion, documento):
    """Valida un documento contra su esquema.

    Devuelve una lista de mensajes legibles; vacia significa que el
    documento cumple el esquema.
    """
    errores = []
    for error in sorted(validador(nombre_coleccion).iter_errors(documento), key=str):
        ruta = "/".join(str(parte) for parte in error.absolute_path)
        ubicacion = f"'{ruta}'" if ruta else "raiz"
        errores.append(f"{ubicacion}: {error.message}")
    return errores


def nombres_colecciones():
    """Lista de nombres de coleccion soportados."""
    return list(COLECCIONES.keys())


def normalizar(documento, modelo=None):
    """Convierte un documento crudo de MongoDB a la forma JSON del esquema.

    MongoDB guarda la clave primaria en ``_id`` (ObjectId) y las fechas como
    BSON Date. El esquema expone la clave como ``id`` en texto y las fechas
    en ISO 8601, asi que se traduce antes de validar.

    ``modelo`` es opcional: si se indica, los campos ``DateField`` se
    convierten a fecha sin hora (MongoDB los guarda a medianoche).
    """
    import datetime

    campos_fecha = set()
    if modelo is not None:
        for campo in modelo._meta.concrete_fields:
            if campo.get_internal_type() == "DateField":
                campos_fecha.add(campo.name)

    def _valor(clave, valor):
        if isinstance(valor, datetime.datetime):
            if clave in campos_fecha:
                return valor.date().isoformat()
            if valor.tzinfo is None:
                valor = valor.replace(tzinfo=datetime.timezone.utc)
            return valor.isoformat()
        if isinstance(valor, datetime.date):
            return valor.isoformat()
        return valor

    datos = {
        clave: _valor(clave, valor)
        for clave, valor in documento.items()
        if clave != "_id"
    }
    identificador = documento.get("_id")
    if identificador is not None:
        datos["id"] = str(identificador)
    return datos
