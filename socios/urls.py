from django.urls import path

from . import views

urlpatterns = [
    path("motociclistas/", views.lista_motociclistas, name="motociclista_list"),
    path("motociclistas/crear/", views.crear_motociclista, name="motociclista_create"),
    path("motociclistas/<int:pk>/editar/", views.editar_motociclista, name="motociclista_update"),
    path("motociclistas/<int:pk>/eliminar/", views.eliminar_motociclista, name="motociclista_delete"),
    path("documentos/", views.lista_documentos, name="documento_list"),
    path("documentos/crear/", views.crear_documento, name="documento_create"),
    path("documentos/<int:pk>/editar/", views.editar_documento, name="documento_update"),
    path("documentos/<int:pk>/eliminar/", views.eliminar_documento, name="documento_delete"),
]
