from django.contrib import admin
from .models import Moto, Mantenimiento, Accidente

admin.site.register(Moto)
admin.site.register(Mantenimiento)
admin.site.register(Accidente)
