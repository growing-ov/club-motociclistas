from django.urls import path

from . import views

urlpatterns = [
    path("rodadas/", views.lista_rodadas, name="rodada_list"),
    path("rodadas/crear/", views.crear_rodada, name="rodada_create"),
    path("rodadas/<str:pk>/", views.ver_rodada, name="rodada_detail"),
    path("rodadas/<str:pk>/editar/", views.editar_rodada, name="rodada_update"),
    path("rodadas/<str:pk>/eliminar/", views.eliminar_rodada, name="rodada_delete"),
    path("inscripciones/", views.lista_inscripciones, name="inscripcion_list"),
    path("inscripciones/crear/", views.crear_inscripcion, name="inscripcion_create"),
    path("inscripciones/<str:pk>/", views.ver_inscripcion, name="inscripcion_detail"),
    path("inscripciones/<str:pk>/editar/", views.editar_inscripcion, name="inscripcion_update"),
    path("inscripciones/<str:pk>/eliminar/", views.eliminar_inscripcion, name="inscripcion_delete"),
    path("galeria/", views.lista_galeria, name="galeria_list"),
    path("galeria/crear/", views.crear_galeria, name="galeria_create"),
    path("galeria/<str:pk>/", views.ver_galeria, name="galeria_detail"),
    path("galeria/<str:pk>/editar/", views.editar_galeria, name="galeria_update"),
    path("galeria/<str:pk>/eliminar/", views.eliminar_galeria, name="galeria_delete"),
]
