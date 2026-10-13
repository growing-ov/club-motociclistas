from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocumentoSocioForm, MotociclistaForm
from .models import DocumentoSocio, Motociclista


def lista_motociclistas(request):
    items = Motociclista.objects.all().order_by("apellido", "nombre")
    return render(request, "socios/motociclista_list.html", {"object_list": items})


def crear_motociclista(request):
    if request.method == "POST":
        form = MotociclistaForm(request.POST)
        if form.is_valid():
            fn = form.cleaned_data["fechaNacimiento"]
            hoy = date.today()
            edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
            if edad < 18:
                form.add_error("fechaNacimiento", "Debe ser mayor de 18 anos")
            else:
                form.save()
                return redirect("motociclista_list")
    else:
        form = MotociclistaForm()
    return render(request, "socios/motociclista_form.html", {"form": form})


def editar_motociclista(request, pk):
    obj = get_object_or_404(Motociclista, pk=pk)
    if request.method == "POST":
        form = MotociclistaForm(request.POST, instance=obj)
        if form.is_valid():
            fn = form.cleaned_data["fechaNacimiento"]
            hoy = date.today()
            edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
            if edad < 18:
                form.add_error("fechaNacimiento", "Debe ser mayor de 18 anos")
            else:
                form.save()
                return redirect("motociclista_list")
    else:
        form = MotociclistaForm(instance=obj)
    return render(request, "socios/motociclista_form.html", {"form": form, "object": obj})


def eliminar_motociclista(request, pk):
    obj = get_object_or_404(Motociclista, pk=pk)
    if request.method == "POST":
        if obj.motos.exists() or obj.inscripciones.exists() or obj.documentos.exists():
            messages.error(request, "No se puede eliminar: tiene motos, inscripciones o documentos asociados.")
        else:
            obj.delete()
            return redirect("motociclista_list")
    return render(request, "socios/motociclista_confirm_delete.html", {"object": obj})


def lista_documentos(request):
    items = DocumentoSocio.objects.all()
    return render(request, "socios/documento_list.html", {"object_list": items})


def crear_documento(request):
    if request.method == "POST":
        form = DocumentoSocioForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["fechaVencimiento"] <= form.cleaned_data["fechaEmision"]:
                form.add_error("fechaVencimiento", "Debe ser mayor a la fecha de emision")
            else:
                form.save()
                return redirect("documento_list")
    else:
        form = DocumentoSocioForm()
    return render(request, "socios/documento_form.html", {"form": form})


def editar_documento(request, pk):
    obj = get_object_or_404(DocumentoSocio, pk=pk)
    if request.method == "POST":
        form = DocumentoSocioForm(request.POST, instance=obj)
        if form.is_valid():
            if form.cleaned_data["fechaVencimiento"] <= form.cleaned_data["fechaEmision"]:
                form.add_error("fechaVencimiento", "Debe ser mayor a la fecha de emision")
            else:
                form.save()
                return redirect("documento_list")
    else:
        form = DocumentoSocioForm(instance=obj)
    return render(request, "socios/documento_form.html", {"form": form, "object": obj})


def eliminar_documento(request, pk):
    obj = get_object_or_404(DocumentoSocio, pk=pk)
    if request.method == "POST":
        if obj.fechaVencimiento and obj.fechaVencimiento >= date.today():
            messages.error(request, "No se puede eliminar un documento vigente.")
        else:
            obj.delete()
            return redirect("documento_list")
    return render(request, "socios/documento_confirm_delete.html", {"object": obj})
