# Club de Motociclistas

Aplicacion web en Django + MongoDB para administrar un club de motos:
socios, documentos, motos, mantenimientos, accidentes, rodadas,
inscripciones y galeria de fotos.

## Requisitos

- Python 3.12 o superior
- MongoDB (local o Atlas)

## Instalacion

```
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` con tus datos:

```
SECRET_KEY=cambia-esta-clave
DEBUG=True
ALLOWED_HOSTS=*
MONGO_URI=mongodb+srv://usuario:clave@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=club_motociclistas
```

## Ejecucion

```
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador. La raiz muestra el resumen
del club (home) y cualquier ruta inexistente regresa al inicio.

## Ejecucion con Docker

Sin instalar Python ni MongoDB: solo Docker (Docker Desktop en Windows y
macOS, Docker Engine en Linux).

```
copy .env.example .env      # define MONGO_URI con la URI de tu Atlas
docker compose up --build
```

Abre http://127.0.0.1:8000/ . La base de datos es **MongoDB Atlas**: la URI
se toma de `.env` y es obligatoria, asi que Compose aborta con un mensaje
claro si falta. Cada maquina solo necesita su propio `.env`.

Comandos utiles:

```
docker compose ps                # estado y healthchecks
docker compose logs -f web       # logs de la aplicacion
docker compose exec web python manage.py seed_data --flush   # datos de prueba
docker compose exec web python manage.py validar_esquemas    # validar esquemas
docker compose down              # detener (conserva los datos)
docker compose down -v           # detener y borrar los volumenes
```

Para produccion (DEBUG=False, Gunicorn con 2 workers, `SECRET_KEY`
obligatoria en `.env`):

```
docker compose -f docker-compose.prod.yml up -d --build
```

Si necesitas un MongoDB efimero para pruebas (perfil opcional `mongo-local`):

```
docker compose --profile mongo-local up --build
```

## Variables de entorno

| Variable | Por defecto | Descripcion |
|---|---|---|
| `SECRET_KEY` | insegura | Clave de Django. Obligatoria y unica en produccion. |
| `DEBUG` | `True` | Modo depuracion. En produccion `False`. |
| `ALLOWED_HOSTS` | `*` | Hosts permitidos, separados por comas. |
| `MONGO_URI` | — | Conexion a MongoDB Atlas. **Obligatoria**: sin ella Docker Compose aborta. |
| `MONGO_DB` | `club_motociclistas` | Nombre de la base de datos. |
| `PUERTO_WEB` | `8000` | Puerto del host donde se publica la app (solo Docker). |
| `ESPERA_MONGO` | `60` | Segundos de espera de MongoDB al arrancar el contenedor. |

## Estructura

```
club_motociclistas/   configuracion (settings, urls, dashboard, api)
nucleo/               nucleo: esquemas JSON, serializadores, comandos de gestion
templates/            base.html y dashboard.html
static/css/           estilos.css
schemas/              esquemas JSON de las colecciones de MongoDB
socios/               Motociclista, DocumentoSocio
flota/                Moto, Mantenimiento, Accidente
eventos/              Rodada, Inscripcion, Galeria
docs/                 documentacion tecnica y capturas
```

Cada app tiene `models.py`, `forms.py`, `views.py`, `urls.py` y su carpeta
`templates/` con los listados, formularios, detalle y confirmacion de
borrado. Las vistas son por funcion y usan `ModelForm`, `render()`,
`redirect()` y `messages`.

La documentacion completa del proyecto esta en `docs/DOCUMENTACION.md` y los
validadores de las colecciones de MongoDB en `schemas/`.
