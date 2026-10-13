from django.urls import path

from . import views

urlpatterns = [
    path("rodadas/", views.lista_rodadas, name="rodada_list"),
    path("rodadas/crear/", views.crear_rodada, name="rodada_create"),
    path("rodadas/<int:pk>/editar/", views.editar_rodada, name="rodada_update"),
    path("rodadas/<int:pk>/eliminar/", views.eliminar_rodada, name="rodada_delete"),
    path("inscripciones/", views.lista_inscripciones, name="inscripcion_list"),
    path("inscripciones/crear/", views.crear_inscripcion, name="inscripcion_create"),
    path("inscripciones/<int:pk>/editar/", views.editar_inscripcion, name="inscripcion_update"),
    path("inscripciones/<int:pk>/eliminar/", views.eliminar_inscripcion, name="inscripcion_delete"),
    path("galeria/", views.lista_galeria, name="galeria_list"),
    path("galeria/crear/", views.crear_galeria, name="galeria_create"),
    path("galeria/<int:pk>/editar/", views.editar_galeria, name="galeria_update"),
    path("galeria/<int:pk>/eliminar/", views.eliminar_galeria, name="galeria_delete"),
]
