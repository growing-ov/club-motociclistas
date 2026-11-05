from django.apps import AppConfig


class EventosConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "eventos"
    verbose_name = "Eventos"
