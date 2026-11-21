"""Conversion de documentos de Django a documentos que cumplen el JSON Schema.

El serializador es generico: recorre los campos concretos del modelo y
produce un diccionario plano con la misma forma que declara el esquema.
La clave primaria se renombra ``id`` y las fechas se pasan a ISO 8601.
"""

from __future__ import annotations

import datetime

from django.apps import apps


def _valor(valor):
    """Normaliza un valor de Django a un tipo JSON."""
    if valor is None:
        return None
    if isinstance(valor, datetime.datetime):
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=datetime.timezone.utc)
        return valor.isoformat()
    if isinstance(valor, datetime.date):
        return valor.isoformat()
    if isinstance(valor, float):
        return round(valor, 2)
    if isinstance(valor, (list, tuple)):
        return [_valor(item) for item in valor]
    if isinstance(valor, dict):
        return {clave: _valor(item) for clave, item in valor.items()}
    if isinstance(valor, (str, int, bool)):
        return valor
    return str(valor)


def a_esquema(objeto):
    """Convierte una instancia de modelo en un diccionario con forma de esquema."""
    datos = {"id": str(objeto.pk)}
    for campo in objeto._meta.concrete_fields:
        if campo.primary_key:
            continue
        if campo.is_relation:
            raise TypeError(
                f"El modelo {objeto.__class__.__name__} declara la relacion '{campo.name}'. "
                "El proyecto debe funcionar sin relaciones en la base de datos."
            )
        datos[campo.name] = _valor(getattr(objeto, campo.name))
    return datos


def coleccion_a_esquema(nombre_coleccion, objetos):
    """Convierte una lista de instancias en una lista de documentos con forma de esquema."""
    return [a_esquema(objeto) for objeto in objetos]


def modelo_de(nombre_coleccion):
    """Devuelve la clase de modelo de una coleccion."""
    from nucleo.esquemas import COLECCIONES

    return apps.get_model(COLECCIONES[nombre_coleccion]["modelo"])


def documentos_de(nombre_coleccion):
    """Devuelve los documentos de una coleccion ya convertidos al formato de esquema."""
    from nucleo.esquemas import COLECCIONES

    modelo = modelo_de(nombre_coleccion)
    objetos = modelo.objects.all().order_by(*COLECCIONES[nombre_coleccion]["orden"])
    return coleccion_a_esquema(nombre_coleccion, objetos)


def documento_de(nombre_coleccion, identificador):
    """Devuelve un documento concreto (o ``None``) en formato de esquema."""
    modelo = modelo_de(nombre_coleccion)
    objeto = modelo.objects.filter(pk=str(identificador)).first()
    if objeto is None:
        return None
    return a_esquema(objeto)
