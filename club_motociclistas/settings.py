import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def leer_variables():
    """Lee el archivo ``.env`` y lo mezcla con las variables del sistema."""
    valores = {}
    archivo = BASE_DIR / ".env"
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip('"').strip("'")
    valores.update(os.environ)
    return valores


VARIABLES = leer_variables()

SECRET_KEY = VARIABLES.get(
    "SECRET_KEY", "django-insecure-club-motociclistas-cambiar-en-produccion"
)
DEBUG = VARIABLES.get("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    host.strip() for host in VARIABLES.get("ALLOWED_HOSTS", "*").split(",") if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "nucleo.apps.NucleoConfig",
    "socios.apps.SociosConfig",
    "flota.apps.FlotaConfig",
    "eventos.apps.EventosConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "club_motociclistas.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "club_motociclistas.wsgi.application"

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": VARIABLES.get("MONGO_URI", "mongodb://localhost:27017"),
        "NAME": VARIABLES.get("MONGO_DB", "club_motociclistas"),
    }
}

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
