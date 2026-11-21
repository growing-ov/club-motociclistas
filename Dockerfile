# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Club de Motociclistas - imagen de produccion (Django 6.1 + MongoDB)
# Construccion multi-etapa: builder instala dependencias y genera los
# estaticos; la imagen final solo lleva el codigo y el entorno virtual.
# ---------------------------------------------------------------------------

# ========================= ETAPA 1: BUILDER ================================
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=club_motociclistas.settings

WORKDIR /app

# Entorno virtual aislado del sistema: la imagen final solo copia /opt/venv.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Primero las dependencias (aprovecha la cache de capas de Docker).
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Codigo fuente completo (el .dockerignore excluye .env, venv, .git, etc.).
COPY . /app

# Whitenoise usa CompressedManifestStaticFilesStorage: el manifiesto de
# estaticos debe generarse ANTES de arrancar gunicorn, o las plantillas
# con {% static %} devolveran 404. Se usa una clave ficticia de compilacion.
RUN SECRET_KEY=clave-ficticia-solo-para-compilar DEBUG=False \
    python manage.py collectstatic --noinput

# ========================= ETAPA 2: FINAL ==================================
FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=club_motociclistas.settings

# Usuario sin privilegios (no-root) para ejecutar la aplicacion.
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# Entorno virtual con las dependencias ya instaladas.
COPY --from=builder /opt/venv /opt/venv

# Codigo + estaticos ya compilados (staticfiles/ con su manifiesto).
COPY --from=builder --chown=appuser:appuser /app /app

# El script espera a Mongo y prepara los estaticos antes de gunicorn.
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER appuser
EXPOSE 8000

# Healthcheck con python (la imagen slim no trae curl). Se consulta
# /api/esquemas/ porque solo lee archivos y no depende de MongoDB.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/esquemas/', timeout=4).status == 200 else 1)"]

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "club_motociclistas.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-"]
