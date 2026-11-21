from django.core.validators import URLValidator
from django.db import models

from club_motociclistas.referencias import LONGITUD_ID

VALIDADORES_URL = [URLValidator(schemes=["http", "https"])]


class Motociclista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=254, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fechaNacimiento = models.DateField()
    activo = models.BooleanField(default=True)
    tipoLicencia = models.CharField(max_length=50, blank=True, null=True)
    fotoUrl = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        validators=VALIDADORES_URL,
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Motociclista"
        verbose_name_plural = "Motociclistas"


class DocumentoSocio(models.Model):
    """Documento de un socio.

    ``idMotociclista`` es una referencia sin relacion: guarda el ObjectId
    del socio en texto, indexado para buscar rapido.
    """

    nombreDocumento = models.CharField(max_length=80)
    numeroDocumento = models.CharField(max_length=60)
    fechaEmision = models.DateField()
    fechaVencimiento = models.DateField()
    archivoUrl = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        validators=VALIDADORES_URL,
    )
    idMotociclista = models.CharField(
        max_length=LONGITUD_ID,
        db_index=True,
        verbose_name="Motociclista",
    )

    def __str__(self):
        return f"{self.nombreDocumento} - {self.numeroDocumento}"

    class Meta:
        verbose_name = "Documento de socio"
        verbose_name_plural = "Documentos de socios"
