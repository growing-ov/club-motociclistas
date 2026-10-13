from django.urls import path

from . import views

urlpatterns = [
    path("motos/", views.lista_motos, name="moto_list"),
    path("motos/crear/", views.crear_moto, name="moto_create"),
    path("motos/<int:pk>/editar/", views.editar_moto, name="moto_update"),
    path("motos/<int:pk>/eliminar/", views.eliminar_moto, name="moto_delete"),
    path("mantenimientos/", views.lista_mantenimientos, name="mantenimiento_list"),
    path("mantenimientos/crear/", views.crear_mantenimiento, name="mantenimiento_create"),
    path("mantenimientos/<int:pk>/editar/", views.editar_mantenimiento, name="mantenimiento_update"),
    path("mantenimientos/<int:pk>/eliminar/", views.eliminar_mantenimiento, name="mantenimiento_delete"),
    path("accidentes/", views.lista_accidentes, name="accidente_list"),
    path("accidentes/crear/", views.crear_accidente, name="accidente_create"),
    path("accidentes/<int:pk>/editar/", views.editar_accidente, name="accidente_update"),
    path("accidentes/<int:pk>/eliminar/", views.eliminar_accidente, name="accidente_delete"),
]
