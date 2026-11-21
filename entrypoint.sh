#!/bin/sh
# ---------------------------------------------------------------------------
# Punto de entrada del contenedor del Club de Motociclistas.
# Espera a MongoDB, genera los estaticos (whitenoise los necesita) y lanza
# el comando recibido; por defecto ese comando es el CMD del Dockerfile:
#   gunicorn club_motociclistas.wsgi:application --bind 0.0.0.0:8000 ...
# Variables opcionales: MONGO_URI, MONGO_DB, ESPERA_MONGO (segundos, 0=sin
# espera), SKIP_COLLECTSTATIC (1 = omitir collectstatic).
#
# MONGO_URI admite cualquier servidor: el contenedor "mongo" de Docker Compose,
# un Mongo local o MongoDB Atlas (mongodb+srv://). Si apunta a localhost, se
# reescribe al host "mongo" de la red de Compose, porque dentro del contenedor
# localhost es el propio servicio web.
# ---------------------------------------------------------------------------
set -e

MONGO_URI="${MONGO_URI:-mongodb://mongo:27017}"
ESPERA_MONGO="${ESPERA_MONGO:-60}"
export MONGO_URI

# 0) Reescribe localhost/127.0.0.1 al servicio "mongo" de Compose.
case "$MONGO_URI" in
    *://localhost*|*://127.0.0.1*)
        MONGO_URI=$(printf '%s' "$MONGO_URI" | sed 's|//localhost|//mongo|; s|//127\.0\.0\.1|//mongo|')
        export MONGO_URI
        echo "[entrypoint] MONGO_URI apuntaba a localhost: se usa el servicio 'mongo' de Compose."
        ;;
esac

# Muestra solo el host, nunca la contrasena de la URI.
MONGO_HOST=$(python - <<'PY' 2>/dev/null || echo "desconocido"
import os
from urllib.parse import urlparse

print(urlparse(os.environ.get("MONGO_URI", "")).hostname or "desconocido")
PY
)
echo "[entrypoint] Mongo: ${MONGO_HOST} | Base: ${MONGO_DB:-club_motociclistas}"

# Comprueba que MongoDB responde: ping con pymongo (soporta mongodb+srv) y,
# si falla, comprueba el puerto TCP como respaldo.
mongo_listo() {
    python - <<'PY' >/dev/null 2>&1
import os
import sys

uri = os.environ.get("MONGO_URI", "mongodb://mongo:27017")

try:
    import pymongo

    cliente = pymongo.MongoClient(
        uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000
    )
    cliente.admin.command("ping")
    sys.exit(0)
except Exception:
    pass

try:
    from urllib.parse import urlparse
    import socket

    partes = urlparse(uri)
    host = partes.hostname or "mongo"
    puerto = partes.port or 27017
    conexion = socket.socket()
    conexion.settimeout(2)
    conexion.connect((host, puerto))
    conexion.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
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
