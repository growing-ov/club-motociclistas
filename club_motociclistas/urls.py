from django.urls import include, path

urlpatterns = [
    path("socios/", include("socios.urls")),
    path("flota/", include("flota.urls")),
    path("eventos/", include("eventos.urls")),
]
