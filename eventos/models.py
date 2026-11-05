from django.core.validators import URLValidator
from django.db import models

from socios.models import Motociclista

VALIDADORES_URL = [URLValidator(schemes=["http", "https"])]

ESTADOS = (
    ("programada", "Programada"),
    ("en_curso", "En curso"),
    ("finalizada", "Finalizada"),
)


class Rodada(models.Model):
    nombre = models.CharField(max_length=150)
    fechaSalida = models.DateTimeField()
    puntoEncuentro = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    estado = models.CharField(max_length=40, choices=ESTADOS)
    cupoMaximo = models.IntegerField()
    distanciaKm = models.IntegerField(blank=True, null=True)
    costo = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.fechaSalida.date()}"

    class Meta:
        verbose_name = "Rodada"
        verbose_name_plural = "Rodadas"


class Inscripcion(models.Model):
    idMotociclista = models.ForeignKey(
        Motociclista,
        on_delete=models.CASCADE,
        related_name="inscripciones",
    )
    idRodada = models.ForeignKey(
        Rodada,
        on_delete=models.CASCADE,
        related_name="inscripciones",
    )
    fechaInscripcion = models.DateTimeField()
    asistio = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.idMotociclista} -> {self.idRodada}"

    class Meta:
        verbose_name = "Inscripcion"
        verbose_name_plural = "Inscripciones"


class Galeria(models.Model):
    idRodada = models.ForeignKey(
        Rodada,
        on_delete=models.CASCADE,
        related_name="galeria",
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    urlFoto = models.URLField(max_length=500, validators=VALIDADORES_URL)
    fechaSubida = models.DateTimeField()

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Foto galeria"
        verbose_name_plural = "Galeria"
