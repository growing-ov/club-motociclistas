from django.apps import AppConfig


class NucleoConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "nucleo"
    verbose_name = "Nucleo (esquemas JSON y utilidades)"
