from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import GaleriaForm, InscripcionForm, RodadaForm
from .models import Galeria, Inscripcion, Rodada


def lista_rodadas(request):
    items = Rodada.objects.all().order_by("fechaSalida")
    return render(request, "eventos/rodada_list.html", {"object_list": items})


def crear_rodada(request):
    if request.method == "POST":
        form = RodadaForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data["fechaSalida"]
            if fecha and fecha <= timezone.now():
                form.add_error("fechaSalida", "La fecha de salida debe ser futura")
            elif not (2 <= form.cleaned_data["cupoMaximo"] <= 80):
                form.add_error("cupoMaximo", "El cupo debe estar entre 2 y 80")
            else:
                distancia = form.cleaned_data.get("distanciaKm")
                if distancia is not None and not (1 <= distancia <= 2000):
                    form.add_error("distanciaKm", "La distancia debe estar entre 1 y 2000 km")
                else:
                    costo = form.cleaned_data.get("costo")
                    if costo is not None and costo < 0:
                        form.add_error("costo", "No puede ser negativo")
                    else:
                        form.save()
                        return redirect("rodada_list")
    else:
        form = RodadaForm()
    return render(request, "eventos/rodada_form.html", {"form": form})


def editar_rodada(request, pk):
    obj = get_object_or_404(Rodada, pk=pk)
    if request.method == "POST":
        form = RodadaForm(request.POST, instance=obj)
        if form.is_valid():
            fecha = form.cleaned_data["fechaSalida"]
            if fecha and fecha <= timezone.now():
                form.add_error("fechaSalida", "La fecha debe ser futura")
            elif not (2 <= form.cleaned_data["cupoMaximo"] <= 80):
                form.add_error("cupoMaximo", "Cupo fuera de rango")
            else:
                form.save()
                return redirect("rodada_list")
    else:
        form = RodadaForm(instance=obj)
    return render(request, "eventos/rodada_form.html", {"form": form, "object": obj})


def eliminar_rodada(request, pk):
    obj = get_object_or_404(Rodada, pk=pk)
    if request.method == "POST":
        if obj.inscripciones.exists() or obj.galeria.exists():
            messages.error(request, "No se puede eliminar: tiene inscripciones o fotos.")
        else:
            obj.delete()
            return redirect("rodada_list")
    return render(request, "eventos/rodada_confirm_delete.html", {"object": obj})


def lista_inscripciones(request):
    items = Inscripcion.objects.all()
    return render(request, "eventos/inscripcion_list.html", {"object_list": items})


def crear_inscripcion(request):
    if request.method == "POST":
        form = InscripcionForm(request.POST)
        if form.is_valid():
            rodada = form.cleaned_data["idRodada"]
            if rodada.fechaSalida and rodada.fechaSalida <= timezone.now():
                form.add_error("idRodada", "La rodada ya paso")
            elif rodada.inscripciones.count() >= rodada.cupoMaximo:
                form.add_error("idRodada", "Cupo lleno")
            elif Inscripcion.objects.filter(
                idMotociclista=form.cleaned_data["idMotociclista"],
                idRodada=rodada,
            ).exists():
                form.add_error("idMotociclista", "El motociclista ya esta inscrito en esta rodada")
            else:
                form.save()
                return redirect("inscripcion_list")
    else:
        form = InscripcionForm()
    return render(request, "eventos/inscripcion_form.html", {"form": form})


def editar_inscripcion(request, pk):
    obj = get_object_or_404(Inscripcion, pk=pk)
    if request.method == "POST":
        form = InscripcionForm(request.POST, instance=obj)
        if form.is_valid():
            if Inscripcion.objects.filter(
                idMotociclista=form.cleaned_data["idMotociclista"],
                idRodada=form.cleaned_data["idRodada"],
            ).exclude(pk=obj.pk).exists():
                form.add_error("idMotociclista", "Inscripcion duplicada")
            else:
                form.save()
                return redirect("inscripcion_list")
    else:
        form = InscripcionForm(instance=obj)
    return render(request, "eventos/inscripcion_form.html", {"form": form, "object": obj})


def eliminar_inscripcion(request, pk):
    obj = get_object_or_404(Inscripcion, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("inscripcion_list")
    return render(request, "eventos/inscripcion_confirm_delete.html", {"object": obj})


def lista_galeria(request):
    items = Galeria.objects.all()
    return render(request, "eventos/galeria_list.html", {"object_list": items})


def crear_galeria(request):
    if request.method == "POST":
        form = GaleriaForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["urlFoto"] or ""
            if not (url.startswith("http://") or url.startswith("https://")):
                form.add_error("urlFoto", "URL invalida (debe iniciar con http:// o https://)")
            else:
                form.save()
                return redirect("galeria_list")
    else:
        form = GaleriaForm()
    return render(request, "eventos/galeria_form.html", {"form": form})


def editar_galeria(request, pk):
    obj = get_object_or_404(Galeria, pk=pk)
    if request.method == "POST":
        form = GaleriaForm(request.POST, instance=obj)
        if form.is_valid():
            url = form.cleaned_data["urlFoto"] or ""
            if not (url.startswith("http://") or url.startswith("https://")):
                form.add_error("urlFoto", "URL invalida")
            else:
                form.save()
                return redirect("galeria_list")
    else:
        form = GaleriaForm(instance=obj)
    return render(request, "eventos/galeria_form.html", {"form": form, "object": obj})


def eliminar_galeria(request, pk):
    obj = get_object_or_404(Galeria, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("galeria_list")
    return render(request, "eventos/galeria_confirm_delete.html", {"object": obj})
