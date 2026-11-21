"""Resolucion de referencias entre documentos del club.

El proyecto esta disenado **sin relaciones en la base de datos**: no hay
``ForeignKey``, ni joins, ni cascadas. Cada documento que apunta a otro
guarda unicamente el identificador (``ObjectId`` en texto) dentro de un
campo ``CharField`` indexado.

Este modulo centraliza la logica para resolver esas referencias sin
acoplar las apps entre si: todas las importaciones de modelos se hacen
dentro de las funciones para evitar ciclos de importacion.

Convencion de nombres
---------------------
- ``idMotociclista`` -> referencia a :class:`socios.models.Motociclista`
- ``idMoto``         -> referencia a :class:`flota.models.Moto`
- ``idRodada``       -> referencia a :class:`eventos.models.Rodada`
"""

LONGITUD_ID = 24
PATRON_ID = "^[0-9a-fA-F]{24}$"


def a_texto(valor):
    """Normaliza un identificador a su forma textual (hex de 24 caracteres)."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor.strip()
    return str(valor)


def es_id_valido(valor):
    """Indica si el valor tiene forma de ObjectId de MongoDB."""
    texto = a_texto(valor)
    return len(texto) == LONGITUD_ID


def por_id(modelo, identificador):
    """Devuelve el documento con ese id o ``None`` si no existe."""
    identificador = a_texto(identificador)
    if not identificador:
        return None
    return modelo.objects.filter(pk=identificador).first()


def mapa_por_id(modelo, identificadores):
    """Devuelve ``{id: documento}`` resolviendo todos los ids con una sola consulta.

    Se usa en los listados para evitar el problema de N+1 al mostrar el
    nombre del documento referenciado.
    """
    ids = {a_texto(valor) for valor in identificadores if a_texto(valor)}
    if not ids:
        return {}
    return {a_texto(obj.pk): obj for obj in modelo.objects.filter(pk__in=list(ids))}


def ids_de(objetos, campo):
    """Extrae los ids referenciados por ``campo`` de una lista de documentos."""
    return [a_texto(getattr(objeto, campo)) for objeto in objetos]


# ---------------------------------------------------------------------------
# Referencias de socios
# ---------------------------------------------------------------------------

def documentos_de(socio_id):
    """Documentos que pertenecen a un socio."""
    from socios.models import DocumentoSocio

    return DocumentoSocio.objects.filter(idMotociclista=a_texto(socio_id)).order_by(
        "-fechaEmision"
    )


def motos_de(socio_id):
    """Motos registradas a nombre de un socio."""
    from flota.models import Moto

    return Moto.objects.filter(idMotociclista=a_texto(socio_id)).order_by("placa")


def inscripciones_de_socio(socio_id):
    """Inscripciones de un socio a rodadas."""
    from eventos.models import Inscripcion

    return Inscripcion.objects.filter(idMotociclista=a_texto(socio_id)).order_by(
        "-fechaInscripcion"
    )


# ---------------------------------------------------------------------------
# Referencias de motos
# ---------------------------------------------------------------------------

def mantenimientos_de(moto_id):
    """Mantenimientos registrados para una moto."""
    from flota.models import Mantenimiento

    return Mantenimiento.objects.filter(idMoto=a_texto(moto_id)).order_by("-fecha")


def accidentes_de(moto_id):
    """Accidentes registrados para una moto."""
    from flota.models import Accidente

    return Accidente.objects.filter(idMoto=a_texto(moto_id)).order_by("-fecha")


# ---------------------------------------------------------------------------
# Referencias de rodadas
# ---------------------------------------------------------------------------

def inscripciones_de_rodada(rodada_id):
    """Inscripciones de una rodada."""
    from eventos.models import Inscripcion

    return Inscripcion.objects.filter(idRodada=a_texto(rodada_id)).order_by(
        "fechaInscripcion"
    )


def galeria_de_rodada(rodada_id):
    """Fotos de la galeria de una rodada."""
    from eventos.models import Galeria

    return Galeria.objects.filter(idRodada=a_texto(rodada_id)).order_by("-fechaSubida")


# ---------------------------------------------------------------------------
# Utilidades de apoyo
# ---------------------------------------------------------------------------

def nombre_de(modelo, identificador, defecto="-"):
    """Nombre legible de un documento referenciado, o ``defecto`` si no existe."""
    objeto = por_id(modelo, identificador)
    if objeto is None:
        return defecto
    return str(objeto)


def contar(modelo, campo, valor):
    """Cuenta los documentos de ``modelo`` que apuntan a ``valor``."""
    return modelo.objects.filter(**{campo: a_texto(valor)}).count()


def existe_referencia(modelo, campo, valor):
    """Indica si existe al menos un documento que apunte a ``valor``."""
    return modelo.objects.filter(**{campo: a_texto(valor)}).exists()
