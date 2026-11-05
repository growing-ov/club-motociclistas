from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AccidenteForm, MantenimientoForm, MotoForm
from .models import GRAVEDADES, Accidente, Mantenimiento, Moto


def validar_moto(form):
    datos = form.cleaned_data
    if not (1990 <= datos["anio"] <= 2026):
        return ("anio", "El anio debe estar entre 1990 y 2026")
    cilindrada = datos.get("cilindrada")
    if cilindrada is not None and not (50 <= cilindrada <= 2500):
        return ("cilindrada", "La cilindrada debe estar entre 50 y 2500")
    dueno = datos["idMotociclista"]
    motos = dueno.motos.all()
    if form.instance.pk:
        motos = motos.exclude(pk=form.instance.pk)
    if motos.count() >= 3:
        return ("idMotociclista", "El motociclista ya tiene 3 motos (maximo)")
    return None


def validar_mantenimiento(form):
    datos = form.cleaned_data
    fecha = datos["fecha"]
    if fecha and fecha > timezone.now():
        return ("fecha", "La fecha no puede ser futura")
    if datos["kilometraje"] is not None and datos["kilometraje"] < 0:
        return ("kilometraje", "El kilometraje no puede ser negativo")
    if datos["costo"] is not None and datos["costo"] < 0:
        return ("costo", "El costo no puede ser negativo")
    return None


def validar_accidente(form):
    datos = form.cleaned_data
    if datos["gravedad"] not in [clave for clave, _ in GRAVEDADES]:
        return ("gravedad", "La gravedad debe ser: " + ", ".join(clave for clave, _ in GRAVEDADES))
    fecha = datos["fecha"]
    if fecha and fecha > timezone.now():
        return ("fecha", "La fecha no puede ser futura")
    return None


def lista_motos(request):
    items = Moto.objects.select_related("idMotociclista").all().order_by("placa")
    return render(request, "flota/moto_list.html", {"object_list": items})


def ver_moto(request, pk):
    obj = get_object_or_404(Moto.objects.select_related("idMotociclista"), pk=pk)
    return render(
        request,
        "flota/moto_detail.html",
        {
            "object": obj,
            "mantenimientos": obj.mantenimientos.all().order_by("-fecha"),
            "accidentes": obj.accidentes.all().order_by("-fecha"),
        },
    )


def crear_moto(request):
    form = MotoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_moto(form)
        if error is None:
            form.save()
            messages.success(request, "Moto registrada correctamente.")
            return redirect("moto_list")
        form.add_error(*error)
    return render(request, "flota/moto_form.html", {"form": form})


def editar_moto(request, pk):
    obj = get_object_or_404(Moto, pk=pk)
    form = MotoForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_moto(form)
        if error is None:
            form.save()
            messages.success(request, "Moto actualizada correctamente.")
            return redirect("moto_list")
        form.add_error(*error)
    return render(request, "flota/moto_form.html", {"form": form, "object": obj})


def eliminar_moto(request, pk):
    obj = get_object_or_404(Moto, pk=pk)
    if request.method == "POST":
        if obj.mantenimientos.exists() or obj.accidentes.exists():
            messages.error(request, "No se puede eliminar: tiene mantenimientos o accidentes registrados.")
        else:
            obj.delete()
            messages.success(request, "Moto eliminada correctamente.")
            return redirect("moto_list")
    return render(request, "flota/moto_confirm_delete.html", {"object": obj})


def lista_mantenimientos(request):
    items = Mantenimiento.objects.select_related("idMoto").all().order_by("-fecha")
    return render(request, "flota/mantenimiento_list.html", {"object_list": items})


def ver_mantenimiento(request, pk):
    obj = get_object_or_404(Mantenimiento.objects.select_related("idMoto"), pk=pk)
    return render(
        request,
        "flota/mantenimiento_detail.html",
        {"object": obj, "moto": obj.idMoto},
    )


def crear_mantenimiento(request):
    form = MantenimientoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_mantenimiento(form)
        if error is None:
            form.save()
            messages.success(request, "Mantenimiento registrado correctamente.")
            return redirect("mantenimiento_list")
        form.add_error(*error)
    return render(request, "flota/mantenimiento_form.html", {"form": form})


def editar_mantenimiento(request, pk):
    obj = get_object_or_404(Mantenimiento, pk=pk)
    form = MantenimientoForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_mantenimiento(form)
        if error is None:
            form.save()
            messages.success(request, "Mantenimiento actualizado correctamente.")
            return redirect("mantenimiento_list")
        form.add_error(*error)
    return render(request, "flota/mantenimiento_form.html", {"form": form, "object": obj})


def eliminar_mantenimiento(request, pk):
    obj = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Mantenimiento eliminado correctamente.")
        return redirect("mantenimiento_list")
    return render(request, "flota/mantenimiento_confirm_delete.html", {"object": obj})


def lista_accidentes(request):
    items = Accidente.objects.select_related("idMoto").all().order_by("-fecha")
    return render(request, "flota/accidente_list.html", {"object_list": items})


def ver_accidente(request, pk):
    obj = get_object_or_404(Accidente.objects.select_related("idMoto"), pk=pk)
    return render(
        request,
        "flota/accidente_detail.html",
        {"object": obj, "moto": obj.idMoto},
    )


def crear_accidente(request):
    form = AccidenteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_accidente(form)
        if error is None:
            form.save()
            messages.success(request, "Accidente registrado correctamente.")
            return redirect("accidente_list")
        form.add_error(*error)
    return render(request, "flota/accidente_form.html", {"form": form})


def editar_accidente(request, pk):
    obj = get_object_or_404(Accidente, pk=pk)
    form = AccidenteForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_accidente(form)
        if error is None:
            form.save()
            messages.success(request, "Accidente actualizado correctamente.")
            return redirect("accidente_list")
        form.add_error(*error)
    return render(request, "flota/accidente_form.html", {"form": form, "object": obj})


def eliminar_accidente(request, pk):
    obj = get_object_or_404(Accidente, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Accidente eliminado correctamente.")
        return redirect("accidente_list")
    return render(request, "flota/accidente_confirm_delete.html", {"object": obj})
