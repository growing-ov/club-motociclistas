"""Filtros de plantilla propios del club.

Se usan para resolver referencias planas (``{id: documento}``) desde las
plantillas y para formatear fechas y montos de forma consistente.
"""

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def get(mapa, clave):
    """Devuelve ``mapa[clave]`` o ``None`` si el mapa no existe.

    Sirve para resolver referencias por ``ObjectId`` sin consultar la base
    de datos desde la plantilla.
    """
    if mapa is None or clave is None:
        return None
    try:
        return mapa.get(clave)
    except AttributeError:
        return None


@register.filter
def vigente(fecha):
    """Indica si una fecha de vencimiento sigue vigente."""
    if not fecha:
        return False
    return fecha >= timezone.localdate()


@register.filter
def initiales(texto):
    """Iniciales de un nombre, para los avatares de texto."""
    partes = [parte for parte in str(texto or "").split() if parte]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[1][0]).upper()


@register.filter
def moneda(valor):
    """Formatea un monto con separador de miles."""
    if valor is None:
        return "-"
    try:
        return f"{valor:,.0f}"
    except (TypeError, ValueError):
        return str(valor)


@register.filter
def estado_clase(estado):
    """Traduce el estado de una rodada a la clase de pastilla del CSS."""
    return {
        "programada": "pastilla--info",
        "en_curso": "pastilla--aviso",
        "finalizada": "pastilla--neutro",
    }.get(str(estado), "pastilla--neutro")


@register.filter
def gravedad_clase(gravedad):
    """Traduce la gravedad de un accidente a la clase de pastilla del CSS."""
    return {
        "leve": "pastilla--exito",
        "moderado": "pastilla--aviso",
        "grave": "pastilla--peligro",
    }.get(str(gravedad), "pastilla--neutro")
