"""Campos de formulario para referencias sin relacion en la base de datos.

Los campos de referencia (``idMotociclista``, ``idMoto``, ``idRodada``) son
``CharField`` que guardan el ``ObjectId`` en texto. Para que el usuario
siga eligiendo el documento desde una lista desplegable, estos campos
muestran un ``<select>`` pero guardan el identificador en texto plano.
"""

from django import forms


class ReferenciaModelChoiceField(forms.ModelChoiceField):
    """Desplegable que devuelve el identificador del documento en texto.

    hereda de :class:`django.forms.ModelChoiceField`, pero en lugar de
    devolver la instancia del modelo devuelve ``str(instancia.pk)``, que
    es exactamente lo que se guarda en el documento referenciador.
    """

    def clean(self, value):
        referencia = super().clean(value)
        if referencia is None:
            return None
        return str(referencia.pk)

    def prepare_value(self, value):
        if value is None:
            return ""
        if hasattr(value, "_meta"):
            return str(value.pk)
        return value


def campo_referencia(modelo, etiqueta, **opciones):
    """Crea un :class:`ReferenciaModelChoiceField` para ``modelo``."""
    opciones.setdefault("queryset", modelo.objects.all())
    opciones.setdefault("required", True)
    opciones.setdefault("label", etiqueta)
    opciones.setdefault("to_field_name", "pk")
    return ReferenciaModelChoiceField(**opciones)
