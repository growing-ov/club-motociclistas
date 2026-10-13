from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AccidenteForm, MantenimientoForm, MotoForm
from .models import Accidente, Mantenimiento, Moto

GRAVEDADES = ("leve", "moderado", "grave")


def lista_motos(request):
    items = Moto.objects.all()
    return render(request, "flota/moto_list.html", {"object_list": items})


def crear_moto(request):
    if request.method == "POST":
        form = MotoForm(request.POST)
        if form.is_valid():
            anio = form.cleaned_data["anio"]
            if anio < 1990 or anio > 2026:
                form.add_error("anio", "El anio debe estar entre 1990 y 2026")
            else:
                cil = form.cleaned_data.get("cilindrada")
                if cil is not None and not (50 <= cil <= 2500):
                    form.add_error("cilindrada", "La cilindrada debe estar entre 50 y 2500")
                else:
                    dueno = form.cleaned_data["idMotociclista"]
                    if dueno.motos.count() >= 3:
                        form.add_error("idMotociclista", "El motociclista ya tiene 3 motos (maximo)")
                    else:
                        form.save()
                        return redirect("moto_list")
    else:
        form = MotoForm()
    return render(request, "flota/moto_form.html", {"form": form})


def editar_moto(request, pk):
    obj = get_object_or_404(Moto, pk=pk)
    if request.method == "POST":
        form = MotoForm(request.POST, instance=obj)
        if form.is_valid():
            anio = form.cleaned_data["anio"]
            if anio < 1990 or anio > 2026:
                form.add_error("anio", "Anio fuera de rango")
            else:
                cil = form.cleaned_data.get("cilindrada")
                if cil is not None and not (50 <= cil <= 2500):
                    form.add_error("cilindrada", "Cilindrada fuera de rango")
                else:
                    form.save()
                    return redirect("moto_list")
    else:
        form = MotoForm(instance=obj)
    return render(request, "flota/moto_form.html", {"form": form, "object": obj})


def eliminar_moto(request, pk):
    obj = get_object_or_404(Moto, pk=pk)
    if request.method == "POST":
        if obj.mantenimientos.exists() or obj.accidentes.exists():
            messages.error(request, "No se puede eliminar: tiene mantenimientos o accidentes registrados.")
        else:
            obj.delete()
            return redirect("moto_list")
    return render(request, "flota/moto_confirm_delete.html", {"object": obj})


def lista_mantenimientos(request):
    items = Mantenimiento.objects.all()
    return render(request, "flota/mantenimiento_list.html", {"object_list": items})


def crear_mantenimiento(request):
    if request.method == "POST":
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data["fecha"]
            if fecha and fecha > timezone.now():
                form.add_error("fecha", "La fecha no puede ser futura")
            elif form.cleaned_data["kilometraje"] is not None and form.cleaned_data["kilometraje"] < 0:
                form.add_error("kilometraje", "No puede ser negativo")
            elif form.cleaned_data["costo"] is not None and form.cleaned_data["costo"] < 0:
                form.add_error("costo", "No puede ser negativo")
            else:
                form.save()
                return redirect("mantenimiento_list")
    else:
        form = MantenimientoForm()
    return render(request, "flota/mantenimiento_form.html", {"form": form})


def editar_mantenimiento(request, pk):
    obj = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == "POST":
        form = MantenimientoForm(request.POST, instance=obj)
        if form.is_valid():
            fecha = form.cleaned_data["fecha"]
            if fecha and fecha > timezone.now():
                form.add_error("fecha", "La fecha no puede ser futura")
            elif form.cleaned_data["kilometraje"] is not None and form.cleaned_data["kilometraje"] < 0:
                form.add_error("kilometraje", "No puede ser negativo")
            elif form.cleaned_data["costo"] is not None and form.cleaned_data["costo"] < 0:
                form.add_error("costo", "No puede ser negativo")
            else:
                form.save()
                return redirect("mantenimiento_list")
    else:
        form = MantenimientoForm(instance=obj)
    return render(request, "flota/mantenimiento_form.html", {"form": form, "object": obj})


def eliminar_mantenimiento(request, pk):
    obj = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("mantenimiento_list")
    return render(request, "flota/mantenimiento_confirm_delete.html", {"object": obj})


def lista_accidentes(request):
    items = Accidente.objects.all()
    return render(request, "flota/accidente_list.html", {"object_list": items})


def crear_accidente(request):
    if request.method == "POST":
        form = AccidenteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["gravedad"] not in GRAVEDADES:
                form.add_error("gravedad", f"Debe ser una de {GRAVEDADES}")
            elif form.cleaned_data["fecha"] and form.cleaned_data["fecha"] > timezone.now():
                form.add_error("fecha", "La fecha no puede ser futura")
            else:
                form.save()
                return redirect("accidente_list")
    else:
        form = AccidenteForm()
    return render(request, "flota/accidente_form.html", {"form": form})


def editar_accidente(request, pk):
    obj = get_object_or_404(Accidente, pk=pk)
    if request.method == "POST":
        form = AccidenteForm(request.POST, instance=obj)
        if form.is_valid():
            if form.cleaned_data["gravedad"] not in GRAVEDADES:
                form.add_error("gravedad", f"Debe ser una de {GRAVEDADES}")
            elif form.cleaned_data["fecha"] and form.cleaned_data["fecha"] > timezone.now():
                form.add_error("fecha", "La fecha no puede ser futura")
            else:
                form.save()
                return redirect("accidente_list")
    else:
        form = AccidenteForm(instance=obj)
    return render(request, "flota/accidente_form.html", {"form": form, "object": obj})


def eliminar_accidente(request, pk):
    obj = get_object_or_404(Accidente, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("accidente_list")
    return render(request, "flota/accidente_confirm_delete.html", {"object": obj})
