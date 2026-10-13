from django import forms

from .models import Galeria, Inscripcion, Rodada


class RodadaForm(forms.ModelForm):
    class Meta:
        model = Rodada
        fields = ["nombre", "fechaSalida", "puntoEncuentro", "destino", "estado", "cupoMaximo", "distanciaKm", "costo"]


class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ["idMotociclista", "idRodada", "fechaInscripcion", "asistio", "observaciones"]


class GaleriaForm(forms.ModelForm):
    class Meta:
        model = Galeria
        fields = ["idRodada", "titulo", "descripcion", "urlFoto", "fechaSubida"]
