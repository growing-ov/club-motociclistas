"""API JSON de solo lectura del club.

Cada coleccion se expone con la misma forma que declara su JSON Schema
(ver ``schemas/``). Los datos se validan contra el esquema antes de
devolverse: si un documento se sale del contrato, la API responde con un
error 500 explicito en lugar de servir datos rotos.

Rutas:
    GET /api/                      indice de colecciones
    GET /api/<coleccion>/          listado completo
    GET /api/<coleccion>/<id>/     documento concreto
    GET /api/esquemas/             los JSON Schemas en bruto
"""

from __future__ import annotations

import json

from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from nucleo.esquemas import CARPETA_SCHEMAS, COLECCIONES, validar
from nucleo.serializadores import documento_de, documentos_de


@require_GET
def indice(request):
    """Devuelve el catalogo de colecciones disponibles."""
    colecciones = []
    for nombre, definicion in COLECCIONES.items():
        colecciones.append(
            {
                "nombre": nombre,
                "titulo": definicion["titulo"],
                "esquema": f"/api/esquemas/{definicion['esquema']}",
                "total": len(documentos_de(nombre)),
                "url": f"/api/{nombre}/",
            }
        )
    return JsonResponse(
        {
            "proyecto": "Club de Motociclistas",
            "version": "1.0.0",
            "formato": "JSON Schema Draft 2020-12",
            "relaciones": "Sin relaciones: las referencias son ObjectId en texto plano.",
            "colecciones": colecciones,
        }
    )


@require_GET
def coleccion(request, nombre):
    """Devuelve todos los documentos de una coleccion."""
    definicion = _definicion(nombre)
    documentos = documentos_de(nombre)
    invalidos = []
    for documento in documentos:
        errores = validar(nombre, documento)
        if errores:
            invalidos.append({"id": documento.get("id"), "errores": errores})
    if invalidos:
        return JsonResponse(
            {
                "error": "La coleccion no cumple su JSON Schema.",
                "detalle": invalidos,
            },
            status=500,
        )
    return JsonResponse(
        {
            "coleccion": nombre,
            "titulo": definicion["titulo"],
            "total": len(documentos),
            "datos": documentos,
        }
    )


@require_GET
def documento(request, nombre, identificador):
    """Devuelve un documento concreto de una coleccion."""
    _definicion(nombre)
    datos = documento_de(nombre, identificador)
    if datos is None:
        raise Http404("Documento no encontrado")
    return JsonResponse({"coleccion": nombre, "datos": datos})


@require_GET
def esquemas(request):
    """Devuelve todos los JSON Schemas del proyecto."""
    contenido = {}
    for archivo in sorted(CARPETA_SCHEMAS.glob("*.schema.json")):
        contenido[archivo.name] = json.loads(archivo.read_text(encoding="utf-8"))
    return JsonResponse({"total": len(contenido), "esquemas": contenido})


@require_GET
def esquema(request, nombre):
    """Devuelve un JSON Schema concreto."""
    archivo = CARPETA_SCHEMAS / nombre
    if not archivo.exists():
        raise Http404("Esquema no encontrado")
    return HttpResponse(
        archivo.read_text(encoding="utf-8"),
        content_type="application/schema+json",
    )


def _definicion(nombre):
    if nombre not in COLECCIONES:
        raise Http404(f"Coleccion desconocida: {nombre}")
    return COLECCIONES[nombre]
