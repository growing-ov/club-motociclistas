from django import forms

from club_motociclistas.campos import campo_referencia

from .models import DocumentoSocio, Motociclista


class MotociclistaForm(forms.ModelForm):
    class Meta:
        model = Motociclista
        fields = [
            "nombre",
            "apellido",
            "correo",
            "telefono",
            "fechaNacimiento",
            "activo",
            "tipoLicencia",
            "fotoUrl",
        ]


class DocumentoSocioForm(forms.ModelForm):
    """Formulario de documento con selector de socio sin relacion en la base."""

    class Meta:
        model = DocumentoSocio
        fields = [
            "nombreDocumento",
            "numeroDocumento",
            "fechaEmision",
            "fechaVencimiento",
            "archivoUrl",
            "idMotociclista",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idMotociclista"] = campo_referencia(
            Motociclista,
            "Motociclista",
            label="Motociclista",
        )
