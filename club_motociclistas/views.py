from django.shortcuts import render

from eventos.models import Galeria, Inscripcion, Rodada
from flota.models import Accidente, Mantenimiento, Moto
from socios.models import DocumentoSocio, Motociclista


def dashboard(request):
    datos = {
        "socios": Motociclista.objects.count(),
        "documentos": DocumentoSocio.objects.count(),
        "motos": Moto.objects.count(),
        "mantenimientos": Mantenimiento.objects.count(),
        "accidentes": Accidente.objects.count(),
        "rodadas": Rodada.objects.count(),
        "inscripciones": Inscripcion.objects.count(),
        "fotos": Galeria.objects.count(),
    }
    return render(request, "dashboard.html", {"datos": datos})
