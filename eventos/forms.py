from django import forms

from club_motociclistas.campos import campo_referencia

from .models import Galeria, Inscripcion, Rodada
from socios.models import Motociclista


class RodadaForm(forms.ModelForm):
    class Meta:
        model = Rodada
        fields = [
            "nombre",
            "fechaSalida",
            "puntoEncuentro",
            "destino",
            "estado",
            "cupoMaximo",
            "distanciaKm",
            "costo",
        ]


class InscripcionForm(forms.ModelForm):
    """Formulario de inscripcion con selectores sin relacion en la base."""

    class Meta:
        model = Inscripcion
        fields = [
            "idMotociclista",
            "idRodada",
            "fechaInscripcion",
            "asistio",
            "observaciones",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idMotociclista"] = campo_referencia(
            Motociclista,
            "Motociclista",
            label="Motociclista",
        )
        self.fields["idRodada"] = campo_referencia(
            Rodada,
            "Rodada",
            label="Rodada",
        )


class GaleriaForm(forms.ModelForm):
    """Formulario de foto con selector de rodada sin relacion en la base."""

    class Meta:
        model = Galeria
        fields = ["idRodada", "titulo", "descripcion", "urlFoto", "fechaSubida"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idRodada"] = campo_referencia(Rodada, "Rodada", label="Rodada")
