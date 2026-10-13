from django import forms

from .models import DocumentoSocio, Motociclista


class MotociclistaForm(forms.ModelForm):
    class Meta:
        model = Motociclista
        fields = ["nombre", "apellido", "correo", "telefono", "fechaNacimiento", "activo", "tipoLicencia"]


class DocumentoSocioForm(forms.ModelForm):
    class Meta:
        model = DocumentoSocio
        fields = ["nombreDocumento", "numeroDocumento", "fechaEmision", "fechaVencimiento", "archivoUrl", "idMotociclista"]
