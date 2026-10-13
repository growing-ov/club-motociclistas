from django import forms

from .models import Accidente, Mantenimiento, Moto


class MotoForm(forms.ModelForm):
    class Meta:
        model = Moto
        fields = ["placa", "marca", "modelo", "anio", "tipoMoto", "cilindrada", "color", "idMotociclista"]


class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = ["idMoto", "fecha", "tipo", "descripcion", "costo", "kilometraje", "realizado"]


class AccidenteForm(forms.ModelForm):
    class Meta:
        model = Accidente
        fields = ["idMoto", "fecha", "descripcion", "ubicacion", "gravedad", "costoEstimado"]
