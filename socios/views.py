from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocumentoSocioForm, MotociclistaForm
from .models import DocumentoSocio, Motociclista


def validar_motociclista(form):
    fecha = form.cleaned_data["fechaNacimiento"]
    hoy = date.today()
    edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
    if edad < 18:
        return ("fechaNacimiento", "Debe ser mayor de 18 anos")
    return None


def validar_documento(form):
    datos = form.cleaned_data
    if datos["fechaVencimiento"] <= datos["fechaEmision"]:
        return ("fechaVencimiento", "La fecha de vencimiento debe ser mayor a la de emision")
    return None


def lista_motociclistas(request):
    items = Motociclista.objects.all().order_by("apellido", "nombre")
    return render(request, "socios/motociclista_list.html", {"object_list": items})


def ver_motociclista(request, pk):
    obj = get_object_or_404(Motociclista, pk=pk)
    return render(
        request,
        "socios/motociclista_detail.html",
        {
            "object": obj,
            "motos": obj.motos.all().order_by("placa"),
            "documentos": obj.documentos.all().order_by("-fechaEmision"),
            "inscripciones": obj.inscripciones.select_related("idRodada").all().order_by(
                "-fechaInscripcion"
            ),
        },
    )


def crear_motociclista(request):
    form = MotociclistaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_motociclista(form)
        if error is None:
            form.save()
            messages.success(request, "Motociclista registrado correctamente.")
            return redirect("motociclista_list")
        form.add_error(*error)
    return render(request, "socios/motociclista_form.html", {"form": form})


def editar_motociclista(request, pk):
    obj = get_object_or_404(Motociclista, pk=pk)
    form = MotociclistaForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_motociclista(form)
        if error is None:
            form.save()
            messages.success(request, "Motociclista actualizado correctamente.")
            return redirect("motociclista_list")
        form.add_error(*error)
    return render(request, "socios/motociclista_form.html", {"form": form, "object": obj})


def eliminar_motociclista(request, pk):
    obj = get_object_or_404(Motociclista, pk=pk)
    if request.method == "POST":
        if obj.motos.exists() or obj.inscripciones.exists() or obj.documentos.exists():
            messages.error(
                request,
                "No se puede eliminar: tiene motos, inscripciones o documentos asociados.",
            )
        else:
            obj.delete()
            messages.success(request, "Motociclista eliminado correctamente.")
            return redirect("motociclista_list")
    return render(request, "socios/motociclista_confirm_delete.html", {"object": obj})


def lista_documentos(request):
    items = DocumentoSocio.objects.select_related("idMotociclista").all().order_by(
        "-fechaEmision"
    )
    return render(request, "socios/documento_list.html", {"object_list": items})


def ver_documento(request, pk):
    obj = get_object_or_404(DocumentoSocio.objects.select_related("idMotociclista"), pk=pk)
    return render(
        request,
        "socios/documento_detail.html",
        {"object": obj, "socio": obj.idMotociclista},
    )


def crear_documento(request):
    form = DocumentoSocioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        error = validar_documento(form)
        if error is None:
            form.save()
            messages.success(request, "Documento registrado correctamente.")
            return redirect("documento_list")
        form.add_error(*error)
    return render(request, "socios/documento_form.html", {"form": form})


def editar_documento(request, pk):
    obj = get_object_or_404(DocumentoSocio, pk=pk)
    form = DocumentoSocioForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        error = validar_documento(form)
        if error is None:
            form.save()
            messages.success(request, "Documento actualizado correctamente.")
            return redirect("documento_list")
        form.add_error(*error)
    return render(request, "socios/documento_form.html", {"form": form, "object": obj})


def eliminar_documento(request, pk):
    obj = get_object_or_404(DocumentoSocio, pk=pk)
    if request.method == "POST":
        if obj.fechaVencimiento and obj.fechaVencimiento >= date.today():
            messages.error(request, "No se puede eliminar un documento vigente.")
        else:
            obj.delete()
            messages.success(request, "Documento eliminado correctamente.")
            return redirect("documento_list")
    return render(request, "socios/documento_confirm_delete.html", {"object": obj})
