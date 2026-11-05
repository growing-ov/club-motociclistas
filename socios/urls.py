from django.urls import path

from . import views

urlpatterns = [
    path("motociclistas/", views.lista_motociclistas, name="motociclista_list"),
    path("motociclistas/crear/", views.crear_motociclista, name="motociclista_create"),
    path("motociclistas/<str:pk>/", views.ver_motociclista, name="motociclista_detail"),
    path("motociclistas/<str:pk>/editar/", views.editar_motociclista, name="motociclista_update"),
    path("motociclistas/<str:pk>/eliminar/", views.eliminar_motociclista, name="motociclista_delete"),
    path("documentos/", views.lista_documentos, name="documento_list"),
    path("documentos/crear/", views.crear_documento, name="documento_create"),
    path("documentos/<str:pk>/", views.ver_documento, name="documento_detail"),
    path("documentos/<str:pk>/editar/", views.editar_documento, name="documento_update"),
    path("documentos/<str:pk>/eliminar/", views.eliminar_documento, name="documento_delete"),
]
