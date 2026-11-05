from django.apps import AppConfig


class SociosConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "socios"
    verbose_name = "Socios"
