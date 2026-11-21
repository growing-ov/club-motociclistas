#!/bin/sh
# ---------------------------------------------------------------------------
# Punto de entrada del contenedor del Club de Motociclistas.
# Espera a MongoDB, genera los estaticos (whitenoise los necesita) y lanza
# el comando recibido; por defecto ese comando es el CMD del Dockerfile:
#   gunicorn club_motociclistas.wsgi:application --bind 0.0.0.0:8000 ...
# Variables opcionales: MONGO_URI, MONGO_DB, ESPERA_MONGO (segundos, 0=sin
# espera), SKIP_COLLECTSTATIC (1 = omitir collectstatic).
# ---------------------------------------------------------------------------
set -e

MONGO_URI="${MONGO_URI:-mongodb://mongo:27017}"
ESPERA_MONGO="${ESPERA_MONGO:-60}"

echo "[entrypoint] Mongo: ${MONGO_URI} | Base: ${MONGO_DB:-club_motociclistas}"

# Comprueba que el puerto de MongoDB acepta conexiones.
mongo_listo() {
    python -c "import os,socket,sys;from urllib.parse import urlparse;u=urlparse(os.environ.get('MONGO_URI','mongodb://mongo:27017'));s=socket.socket();s.settimeout(2);s.connect((u.hostname or 'mongo',u.port or 27017))" >/dev/null 2>&1
}

# 1) Esperar a MongoDB (el compose ya usa depends_on: service_healthy).
if [ "${ESPERA_MONGO}" != "0" ]; then
    echo "[entrypoint] Esperando a MongoDB (max ${ESPERA_MONGO}s) ..."
    restantes="${ESPERA_MONGO}"
    while [ "${restantes}" -gt 0 ]; do
        if mongo_listo; then
            break
        fi
        restantes=$((restantes - 2))
        sleep 2 || true
    done
    if mongo_listo; then
        echo "[entrypoint] MongoDB disponible."
    else
        echo "[entrypoint] AVISO: MongoDB no responde; se arranca de todos modos."
    fi
fi

# 2) Whitenoise con CompressedManifestStaticFilesStorage exige el manifiesto
#    de estaticos: sin collectstatic las plantillas con {% static %} fallan.
if [ "${SKIP_COLLECTSTATIC:-0}" = "1" ]; then
    echo "[entrypoint] collectstatic omitido (SKIP_COLLECTSTATIC=1)."
else
    echo "[entrypoint] Generando estaticos (collectstatic) ..."
    python manage.py collectstatic --noinput
fi

# 3) MongoDB no usa migraciones de Django: se aplican si existen y, si fallan,
#    el contenedor sigue arrancando (los datos viven en Mongo).
echo "[entrypoint] Aplicando migraciones (no-op en MongoDB) ..."
python manage.py migrate --noinput || echo "[entrypoint] AVISO: migrate fallo; se continua."

# 4) Ejecutar el comando del contenedor (gunicorn por defecto).
exec "$@"
