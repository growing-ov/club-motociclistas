from django.apps import AppConfig


class FlotaConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "flota"
    verbose_name = "Flota"
