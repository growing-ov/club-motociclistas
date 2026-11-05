from django.urls import include, path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("home/", views.dashboard, name="inicio"),
    path("socios/", include("socios.urls")),
    path("flota/", include("flota.urls")),
    path("eventos/", include("eventos.urls")),
    path("<path:ruta>", RedirectView.as_view(url="/", permanent=False), name="ruta_default"),
]
