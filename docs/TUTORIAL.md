# Tutorial: cómo se construyó el Club de Motociclistas

Guía práctica, paso a paso, para crear desde cero el proyecto **Club de Motociclistas**
(Django 6.1 + MongoDB Atlas + Docker) tal como está en este repositorio.

El objetivo es que puedas repetir el proceso completo: crear el repositorio, generar
el proyecto Django, conectar la base de datos, crear las aplicaciones, probarlas y
publicarlas.

![Ruta de trabajo del tutorial, de la creación del repositorio a las pruebas en el navegador](diagramas/07-flujo-tutorial.png)

*Figura 1. Ruta de trabajo: repositorio → entorno virtual → proyecto Django → apps →
modelos y vistas → base de datos → Docker → pruebas → publicación.*

---

## 1. Requisitos previos

| Herramienta | Versión | Para qué se usa | Cómo se comprueba |
|---|---|---|---|
| Python | 3.12 o superior | Ejecutar Django | `python --version` |
| pip | incluido con Python | Instalar dependencias | `python -m pip --version` |
| MongoDB Atlas | Cluster gratuito | Base de datos del club | Panel de Atlas > *Connect* |
| Git | cualquiera | Control de versiones | `git --version` |
| Docker Desktop | Engine Linux habilitado | Ejecutar la aplicación en contenedor | `docker version` |

> Todo el tutorial se ejecuta en **Windows con PowerShell**. En Linux o macOS los
> comandos son iguales, cambiando `copy` por `cp` y activando el entorno con
> `source venv/bin/activate`.

---

## 2. Paso 1 — Crear el repositorio en GitHub

1. Entrar a <https://github.com/new> y crear el repositorio **`club-motociclistas`**.
2. Marcar **"Add a README"** para que GitHub inicialice la rama `main`.
3. Clonarlo en el equipo:

```powershell
git clone https://github.com/growing-ov/club-motociclistas.git
cd club-motociclistas
```

```powershell
git config --global user.name "Octavio Velasco"
git config --global user.email "octavio.velasco@club-moto.co"
```

![Consola con la clonación del repositorio y el primer commit](consolas/clonar.png)

*Figura 2. Clonar el repositorio y comprobar el historial con `git log`.*

```powershell
git config --global user.name "Octavio Velasco"
git config --global user.email "octavio.velasco@club-moto.co"
```

---

## 3. Paso 2 — Preparar el entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

El `venv/` queda fuera del repositorio porque ya está en el `.gitignore`.

![Consola con la creación del entorno virtual y la instalación de dependencias](consolas/venv.png)

*Figura 3. Entorno virtual creado y dependencias instaladas (`pip install -r requirements.txt`).*

El `venv/` queda fuera del repositorio porque ya está en el `.gitignore`.

---

## 4. Paso 3 — Crear el proyecto Django

```powershell
pip install "Django>=6.1,<7.0"
django-admin startproject club_motociclistas .
```

El punto final es importante: crea el paquete `club_motociclistas/` en la raíz del
repositorio, junto a `manage.py`.

Comprobación:

```powershell
python manage.py check
```

![Consola con la creación del proyecto Django](consolas/startproject.png)

*Figura 4. `startproject` genera el paquete `club_motociclistas/` y `manage.py`.*

---

## 5. Paso 4 — Conectar MongoDB

### 5.1 Dependencias

```powershell
pip install "django-mongodb-backend>=6.1,<7.0" "pymongo>=4.6" "jsonschema>=4.23" "whitenoise>=6.7" "gunicorn>=22.0"
pip freeze > requirements.txt
```

### 5.2 Configuración de la base de datos

En `club_motociclistas/settings.py` se declara el backend de MongoDB:

```python
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": VARIABLES.get("MONGO_URI", "mongodb://localhost:27017"),
        "NAME": VARIABLES.get("MONGO_DB", "club_motociclistas"),
    }
}
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
```

### 5.3 Archivo `.env`

Las credenciales nunca se versionan. Se copia la plantilla y se rellena:

```powershell
copy .env.example .env
```

```dotenv
SECRET_KEY=django-insecure-club-motociclistas-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=*
MONGO_URI=mongodb+srv://usuario:clave@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=club_motociclistas
```

La URI se obtiene en **MongoDB Atlas > Connect > Drivers**. El archivo `.env` está en
`.gitignore` y en `.dockerignore`, así que GitHub nunca recibe la contraseña.

Comprobación de la conexión:

```powershell
python -c "import pymongo; c=pymongo.MongoClient('mongodb+srv://...'); print(c.admin.command('ping'))"
```

---

## 6. Paso 5 — Crear las aplicaciones

```powershell
python manage.py startapp nucleo
python manage.py startapp socios
python manage.py startapp flota
python manage.py startapp eventos
```

Cada app contiene `models.py`, `forms.py`, `views.py`, `urls.py` y su carpeta de
plantillas. En `settings.py` se registran en `INSTALLED_APPS`.

![Estructura de carpetas del proyecto Django](diagramas/08-estructura-proyecto.png)

*Figura 5. Estructura final: un paquete de configuración, tres apps de dominio
(`socios`, `flota`, `eventos`), el núcleo auxiliar (`nucleo`) y las carpetas de
plantillas y estáticos.*

| App | Modelos | Ruta |
|---|---|---|
| `socios` | `Motociclista`, `DocumentoSocio` | `/socios/` |
| `flota` | `Moto`, `Mantenimiento`, `Accidente` | `/flota/` |
| `eventos` | `Rodada`, `Inscripcion`, `Galeria` | `/eventos/` |

---

## 7. Paso 6 — Modelos, formularios, vistas y plantillas

El orden de trabajo dentro de cada app es siempre el mismo:

1. **Modelos** (`models.py`): se declara la colección y sus campos. **No se usan
   `ForeignKey`**: las referencias entre documentos se guardan como `ObjectId` en texto.
2. **Formularios** (`forms.py`): `ModelForm` con las reglas de negocio en `clean()`.
3. **Vistas** (`views.py`: funciones, no clases): validan, guardan y redirigen.
4. **URLs** (`urls.py`): cada ruta con su `name`, para poder usar `{% url %}`.
5. **Plantillas** (`templates/<app>/<modelo>_list|_form|_detail|_confirm_delete.html`).

Comprobación del enrutado:

```powershell
python manage.py show_urls
```

![Consola con la creación de las cuatro aplicaciones](consolas/startapp.png)

*Figura 6. Las cuatro aplicaciones quedan creadas dentro del proyecto.*

---

## 8. Paso 7 — Migraciones y servidor de desarrollo

```powershell
python manage.py makemigrations socios flota eventos
python manage.py migrate
python manage.py runserver
```

MongoDB no necesita migraciones de esquema: `migrate` crea índices y registra las
migraciones de Django, y los datos viven en las colecciones.

La aplicación queda disponible en <http://127.0.0.1:8000/>.

![Consola con las migraciones de Django](consolas/migraciones.png)

*Figura 7. `makemigrations` y `migrate`: en MongoDB son un no-op para el esquema.*

![Panel principal de la aplicación con los contadores del club](capturas/01-home.png)

*Figura 8. Home del Club de Motociclistas: resumen con los ocho contadores del club.*

---

## 9. Paso 8 — Cargar datos de prueba

El comando `seed_data` crea socios, documentos, motos, mantenimientos, accidentes,
rodadas, inscripciones y galería coherentes entre sí:

```powershell
python manage.py seed_data --flush
```

Comprobar que los datos cumplen los esquemas JSON del proyecto:

```powershell
python manage.py validar_esquemas
```

![Consola con la carga de los datos de prueba](consolas/seed.png)

*Figura 9. `seed_data --flush` deja el club con socios, motos, rodadas y galería.*

![Consola con la validación de los esquemas JSON](consolas/esquemas.png)

*Figura 10. Los 97 documentos creados cumplen los JSON Schemas de `schemas/`.*

---

## 10. Paso 9 — Probar la aplicación

### 10.1 Crear un registro

1. Entrar a **Socios → Motociclistas → Nuevo socio**.
2. Rellenar nombre, apellido, correo, teléfono, fecha de nacimiento y licencia.
3. Guardar y comprobar que aparece en el listado.

![Formulario de alta de socio](capturas/13-formulario-socio.png)

*Figura 11. Formulario de alta: un `ModelForm` con los campos del modelo y los
errores de validación mostrados junto al campo.*

![Listado de socios del club](capturas/02-socios-lista.png)

*Figura 12. Listado de socios: la tabla se dibuja con los datos leídos de MongoDB.*

![Ficha de detalle de un socio](capturas/03-socios-detalle.png)

*Figura 13. Ficha de detalle: documentos y motos del socio, con enlaces a cada ficha.*

### 10.2 Recorrer el resto de módulos

![Listado de motos de la flota](capturas/04-flota-lista.png)

*Figura 14. Módulo de flota: motos, mantenimientos y accidentes.*

![Detalle de una moto con su historial](capturas/05-moto-detalle.png)

*Figura 15. Ficha de moto con los mantenimientos registrados.*

![Listado de rodadas y eventos](capturas/06-eventos-lista.png)

*Figura 16. Módulo de eventos: rodadas, inscripciones y galería de fotos.*

![Detalle de una rodada con sus inscripciones](capturas/07-rodada-detalle.png)

*Figura 17. Ficha de rodada: control de aforo y fotografías asociadas.*

### 10.3 Consultar la API interna

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/esquemas/ | Select-Object StatusCode
```

![Índice de la API JSON del proyecto](capturas/08-api-indice.png)

*Figura 18. API interna: índice, colecciones, documentos y esquemas en JSON.*

---

## 11. Paso 10 — Dockerizar la aplicación

### 11.1 Dockerfile multi-etapa

La imagen se construye en dos etapas: la primera instala dependencias y genera los
estáticos; la segunda copia solo el resultado y usa un usuario sin privilegios.

```dockerfile
FROM python:3.12-slim AS builder
RUN python -m venv /opt/venv
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
RUN SECRET_KEY=compilacion DEBUG=False python manage.py collectstatic --noinput

FROM python:3.12-slim AS final
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder --chown=appuser:appuser /app /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "club_motociclistas.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 11.2 Construir y ejecutar

![Proceso de construcción de la imagen y arranque del contenedor](diagramas/06-pipeline-docker.png)

*Figura 19. Del código fuente a la aplicación servida: build de la imagen, arranque
del contenedor, healthcheck y Gunicorn.*

```powershell
docker build -t club-motociclistas .
docker compose up --build
docker compose ps
```

El `docker-compose.yml` toma la configuración del archivo `.env`:

![Consola con el contenedor en marcha y sus logs](consolas/docker.png)

*Figura 20. `docker compose up -d --build` levanta el contenedor y el healthcheck pasa a `healthy`.*

```yaml
environment:
  MONGO_URI: ${MONGO_URI:?define MONGO_URI (MongoDB Atlas) en el archivo .env}
  MONGO_DB: ${MONGO_DB:-club_motociclistas}
  SECRET_KEY: ${SECRET_KEY:-django-insecure-cambia-esta-clave-en-produccion}
```

### 11.3 Verificar el contenedor

```powershell
docker compose logs -f web
docker compose exec web python manage.py check
docker compose exec web python manage.py validar_esquemas
```

---

## 12. Paso 11 — Publicar el proyecto en GitHub

```powershell
git status
git add .
git commit -m "feat(app): proyecto inicial del Club de Motociclistas"
git push origin main
```

![Consola con la publicación en GitHub](consolas/git.png)

*Figura 21. `git add`, `git commit` y `git push` con la rama `main` al día.*

Antes de publicar hay que comprobar que **no** se\subieron credenciales:

```powershell
git ls-files | Select-String ".env$"
```

Si el `.env` aparece, se añade al `.gitignore` y se elimina del índice:

```powershell
git rm --cached .env
```

---

## 13. Paso 12 — Ejecutar el proyecto en otra máquina

```powershell
git clone https://github.com/growing-ov/club-motociclistas.git
cd club-motociclistas
copy .env.example .env
docker compose up --build
```

Cada máquina define su propio `.env` con la URI de Atlas; el resto es idéntico.

---

## 14. Resumen de comandos

| Objetivo | Comando |
|---|---|
| Crear el entorno virtual | `python -m venv venv` |
| Activar el entorno | `.\venv\Scripts\Activate.ps1` |
| Crear el proyecto | `django-admin startproject club_motociclistas .` |
| Crear una app | `python manage.py startapp socios` |
| Migraciones | `python manage.py makemigrations socios` / `python manage.py migrate` |
| Arrancar en local | `python manage.py runserver` |
| Comprobar el proyecto | `python manage.py check` |
| Datos de prueba | `python manage.py seed_data --flush` |
| Validar esquemas | `python manage.py validar_esquemas` |
| Exportar datos | `python manage.py exportar_datos` |
| Construir la imagen | `docker build -t club-motociclistas .` |
| Levantar con Compose | `docker compose up --build` |
| Ver estado y logs | `docker compose ps` / `docker compose logs -f web` |
| Detener | `docker compose down` |
| Publicar cambios | `git add .` / `git commit -m "..."` / `git push origin main` |

---

## 15. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'jsonschema'` | Faltan dependencias | `pip install -r requirements.txt` |
| `ServerSelectionTimeoutError` al arrancar | URI de Atlas incorrecta o IP bloqueada | Revisar `.env` y la lista de acceso del cluster |
| Las fotos no cargan | URL externa inaccesible | Comprobar la red o usar `--sin-fotos` en el seed |
| Los estilos devuelven 404 | Falta el manifiesto de estáticos | `python manage.py collectstatic --noinput` |
| Compose aborta al arrancar | Falta `MONGO_URI` en `.env` | Definir `MONGO_URI` con la URI de Atlas |
| El contenedor no arranca con `sh\r` | Fines de línea CRLF en `entrypoint.sh` | Clonar con el `.gitattributes` del repositorio (normaliza a LF) |

---

*Tutorial del Club de Motociclistas — Django 6.1 + MongoDB Atlas + Docker.*
