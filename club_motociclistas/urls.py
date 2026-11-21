from django.urls import include, path
from django.views.generic import RedirectView

from . import api, views

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("home/", views.dashboard, name="inicio"),
    path("socios/", include("socios.urls")),
    path("flota/", include("flota.urls")),
    path("eventos/", include("eventos.urls")),
    path("api/", api.indice, name="api_indice"),
    path("api/esquemas/", api.esquemas, name="api_esquemas"),
    path("api/esquemas/<str:nombre>", api.esquema, name="api_esquema"),
    path("api/<str:nombre>/", api.coleccion, name="api_coleccion"),
    path("api/<str:nombre>/<str:identificador>/", api.documento, name="api_documento"),
    path("<path:ruta>", RedirectView.as_view(url="/", permanent=False), name="ruta_default"),
]
