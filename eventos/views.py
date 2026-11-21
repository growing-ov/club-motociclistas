from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from club_motociclistas import referencias
from flota.models import Moto
from socios.models import Motociclista

from .forms import GaleriaForm, InscripcionForm, RodadaForm
from .models import Galeria, Inscripcion, Rodada


def validar_rodada(form):
    datos = form.cleaned_data
    fecha = datos["fechaSalida"]
    if fecha and fecha <= timezone.now():
        return ("fechaSalida", "La fecha de salida debe ser futura")
    if not (2 <= datos["cupoMaximo"] <= 80):
        return ("cupoMaximo", "El cupo debe estar entre 2 y 80")
    distancia = datos.get("distanciaKm")
    if distancia is not None and not (1 <= distancia <= 2000):
        return ("distanciaKm", "La distancia debe estar entre 1 y 2000 km")
    costo = datos.get("costo")
    if costo is not None and costo < 0:
        return ("costo", "El costo no puede ser negativo")
    return None


def validar_inscripcion(form):
    datos = form.cleaned_data
    rodada = referencias.por_id(Rodada, datos["idRodada"])
    if rodada is None:
        return ("idRodada", "La rodada seleccionada no existe")
    if rodada.fechaSalida and rodada.fechaSalida <= timezone.now():
        return ("idRodada", "La rodada ya paso")
    inscritos = referencias.inscripciones_de_rodada(rodada.pk)
    if form.instance.pk:
        inscritos = inscritos.exclude(pk=form.instance.pk)
    if inscritos.count() >= rodada.cupoMaximo:
        return ("idRodada", "El cupo de la rodada ya esta lleno")
    repetidas = Inscripcion.objects.filter(
        idMotociclista=datos["idMotociclista"],
        idRodada=rodada.pk,
    )
    if form.instance.pk:
        repetidas = repetidas.exclude(pk=form.instance.pk)
    if repetidas.exists():
        return ("idMotociclista", "El motociclista ya esta inscrito en esta rodada")
    return None


def lista_rodadas(request):
    items = Rodada.objects.all().order_by("fechaSalida")
    return render(request, "eventos/rodada_list.html", {"object_list": items})


def ver_rodada(request, pk):
    obj = get_object_or_404(Rodada, pk=pk)
    inscripciones = referencias.inscripciones_de_rodada(obj.pk)
    return render(
        request,
        "eventos/rodada_detail.html",
        {
            "object": obj,
            "inscripciones": inscripciones,
            "galeria": referencias.galeria_de_rodada(obj.pk),
            "cupo_disponible": max(obj.cupoMaximo - len(inscripciones), 0),
            "socios": referencias.mapa_por_id(
                Motociclista, referencias.ids_de(inscripciones, "idMotociclista")
            ),
        },
    )


def crear_rodada(request):
    form = RodadaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_rodada(form)
        if error is None:
            form.save()
            messages.success(request, "Rodada programada correctamente.")
            return redirect("rodada_list")
        form.add_error(*error)
    return render(request, "eventos/rodada_form.html", {"form": form})


def editar_rodada(request, pk):
    obj = get_object_or_404(Rodada, pk=pk)
    form = RodadaForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_rodada(form)
        if error is None:
            form.save()
            messages.success(request, "Rodada actualizada correctamente.")
            return redirect("rodada_list")
        form.add_error(*error)
    return render(request, "eventos/rodada_form.html", {"form": form, "object": obj})


def eliminar_rodada(request, pk):
    obj = get_object_or_404(Rodada, pk=pk)
    if request.method == "POST":
        tiene_inscripciones = referencias.existe_referencia(
            Inscripcion, "idRodada", obj.pk
        )
        tiene_fotos = referencias.existe_referencia(Galeria, "idRodada", obj.pk)
        if tiene_inscripciones or tiene_fotos:
            messages.error(request, "No se puede eliminar: tiene inscripciones o fotos.")
        else:
            obj.delete()
            messages.success(request, "Rodada eliminada correctamente.")
            return redirect("rodada_list")
    return render(request, "eventos/rodada_confirm_delete.html", {"object": obj})


def lista_inscripciones(request):
    items = Inscripcion.objects.all().order_by("-fechaInscripcion")
    return render(
        request,
        "eventos/inscripcion_list.html",
        {
            "object_list": items,
            "socios": referencias.mapa_por_id(
                Motociclista, referencias.ids_de(items, "idMotociclista")
            ),
            "rodadas": referencias.mapa_por_id(
                Rodada, referencias.ids_de(items, "idRodada")
            ),
        },
    )


def ver_inscripcion(request, pk):
    obj = get_object_or_404(Inscripcion, pk=pk)
    return render(
        request,
        "eventos/inscripcion_detail.html",
        {
            "object": obj,
            "socio": referencias.por_id(Motociclista, obj.idMotociclista),
            "rodada": referencias.por_id(Rodada, obj.idRodada),
        },
    )


def crear_inscripcion(request):
    form = InscripcionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_inscripcion(form)
        if error is None:
            form.save()
            messages.success(request, "Inscripcion registrada correctamente.")
            return redirect("inscripcion_list")
        form.add_error(*error)
    return render(request, "eventos/inscripcion_form.html", {"form": form})


def editar_inscripcion(request, pk):
    obj = get_object_or_404(Inscripcion, pk=pk)
    form = InscripcionForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_inscripcion(form)
        if error is None:
            form.save()
            messages.success(request, "Inscripcion actualizada correctamente.")
            return redirect("inscripcion_list")
        form.add_error(*error)
    return render(request, "eventos/inscripcion_form.html", {"form": form, "object": obj})


def eliminar_inscripcion(request, pk):
    obj = get_object_or_404(Inscripcion, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Inscripcion eliminada correctamente.")
        return redirect("inscripcion_list")
    return render(request, "eventos/inscripcion_confirm_delete.html", {"object": obj})


def lista_galeria(request):
    items = Galeria.objects.all().order_by("-fechaSubida")
    return render(
        request,
        "eventos/galeria_list.html",
        {
            "object_list": items,
            "rodadas": referencias.mapa_por_id(
                Rodada, referencias.ids_de(items, "idRodada")
            ),
        },
    )


def ver_galeria(request, pk):
    obj = get_object_or_404(Galeria, pk=pk)
    return render(
        request,
        "eventos/galeria_detail.html",
        {
            "object": obj,
            "rodada": referencias.por_id(Rodada, obj.idRodada),
        },
    )


def crear_galeria(request):
    form = GaleriaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Foto agregada a la galeria correctamente.")
        return redirect("galeria_list")
    return render(request, "eventos/galeria_form.html", {"form": form})


def editar_galeria(request, pk):
    obj = get_object_or_404(Galeria, pk=pk)
    form = GaleriaForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Foto actualizada correctamente.")
        return redirect("galeria_list")
    return render(request, "eventos/galeria_form.html", {"form": form, "object": obj})


def eliminar_galeria(request, pk):
    obj = get_object_or_404(Galeria, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Foto eliminada correctamente.")
        return redirect("galeria_list")
    return render(request, "eventos/galeria_confirm_delete.html", {"object": obj})
