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

## Estructura

```
club_motociclistas/   configuracion (settings, urls, dashboard)
templates/            base.html y dashboard.html
static/css/           estilos.css
socios/               Motociclista, DocumentoSocio
flota/                Moto, Mantenimiento, Accidente
eventos/              Rodada, Inscripcion, Galeria
```

Cada app tiene `models.py`, `forms.py`, `views.py`, `urls.py` y su carpeta
`templates/` con los listados, formularios, detalle y confirmacion de
borrado. Las vistas son por funcion y usan `ModelForm`, `render()`,
`redirect()` y `messages`.

La logica del negocio esta explicada en `descripcion.txt` y los
validadores de las colecciones de MongoDB en `crear_colecciones.txt`.
