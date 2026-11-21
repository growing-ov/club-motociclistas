from django import forms

from club_motociclistas.campos import campo_referencia

from .models import Accidente, Mantenimiento, Moto
from socios.models import Motociclista


class MotoForm(forms.ModelForm):
    """Formulario de moto con selector de dueno sin relacion en la base."""

    class Meta:
        model = Moto
        fields = [
            "placa",
            "marca",
            "modelo",
            "anio",
            "tipoMoto",
            "cilindrada",
            "color",
            "fotoUrl",
            "idMotociclista",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idMotociclista"] = campo_referencia(
            Motociclista,
            "Motociclista",
            label="Motociclista (dueno)",
        )


class MantenimientoForm(forms.ModelForm):
    """Formulario de mantenimiento con selector de moto sin relacion en la base."""

    class Meta:
        model = Mantenimiento
        fields = [
            "idMoto",
            "fecha",
            "tipo",
            "descripcion",
            "costo",
            "kilometraje",
            "realizado",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idMoto"] = campo_referencia(Moto, "Moto", label="Moto")


class AccidenteForm(forms.ModelForm):
    """Formulario de accidente con selector de moto sin relacion en la base."""

    class Meta:
        model = Accidente
        fields = [
            "idMoto",
            "fecha",
            "descripcion",
            "ubicacion",
            "gravedad",
            "costoEstimado",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idMoto"] = campo_referencia(Moto, "Moto", label="Moto")
