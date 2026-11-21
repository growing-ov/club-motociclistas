from django.core.validators import URLValidator
from django.db import models

from club_motociclistas.referencias import LONGITUD_ID

VALIDADORES_URL = [URLValidator(schemes=["http", "https"])]

GRAVEDADES = (
    ("leve", "Leve"),
    ("moderado", "Moderado"),
    ("grave", "Grave"),
)


class Moto(models.Model):
    """Moto de un socio.

    ``idMotociclista`` es una referencia sin relacion: guarda el ObjectId
    del dueno en texto, indexado para buscar rapido.
    """

    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=80)
    anio = models.IntegerField()
    tipoMoto = models.CharField(max_length=50)
    cilindrada = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=40, blank=True, null=True)
    fotoUrl = models.URLField(
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
        return f"{self.marca} {self.modelo} ({self.placa})"

    class Meta:
        verbose_name = "Moto"
        verbose_name_plural = "Motos"


class Mantenimiento(models.Model):
    """Mantenimiento de una moto.

    ``idMoto`` es una referencia sin relacion: guarda el ObjectId de la
    moto en texto, indexado para buscar rapido.
    """

    idMoto = models.CharField(
        max_length=LONGITUD_ID,
        db_index=True,
        verbose_name="Moto",
    )
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=80)
    descripcion = models.TextField()
    costo = models.FloatField()
    kilometraje = models.IntegerField()
    realizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} - {self.idMoto}"

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"


class Accidente(models.Model):
    """Accidente de una moto.

    ``idMoto`` es una referencia sin relacion: guarda el ObjectId de la
    moto en texto, indexado para buscar rapido.
    """

    idMoto = models.CharField(
        max_length=LONGITUD_ID,
        db_index=True,
        verbose_name="Moto",
    )
    fecha = models.DateTimeField()
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=200)
    gravedad = models.CharField(max_length=20, choices=GRAVEDADES)
    costoEstimado = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_gravedad_display()} - {self.fecha.date()}"

    class Meta:
        verbose_name = "Accidente"
        verbose_name_plural = "Accidentes"
