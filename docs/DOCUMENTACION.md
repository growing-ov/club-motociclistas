# Club de Motociclistas — Documentación Técnica

| Campo | Valor |
|---|---|
| **Proyecto** | Club de Motociclistas |
| **Versión del documento** | 1.0.0 |
| **Fecha de emisión** | 20 de noviembre de 2026 |
| **Versión de la aplicación** | 1.0.0 (indicada en `/api/` y en el pie de la interfaz) |
| **Estado** | Documento maestro del repositorio `growing-ov/club-motociclistas` |
| **Público objetivo** | Equipo de desarrollo, administradores del club, responsables de despliegue y mantenedores de la infraestructura |
| **Repositorio** | <https://github.com/growing-ov/club-motociclistas> (rama `main`) |

---

## 1. Introducción

### 1.1 ¿Qué es este documento?

Este documento es la referencia técnica unificada del proyecto **Club de Motociclistas**. Describe qué hace la aplicación, cómo está construida, qué reglas de negocio gobiernan sus datos, cómo se instala, cómo se ejecuta, cómo se empaqueta con Docker y cómo se despliega en producción.

La información presentada se ha derivado **exclusivamente del código fuente del repositorio**: cada afirmación sobre el comportamiento de la aplicación está respaldada por el archivo y la función que la implementa. Cuando una funcionalidad no existe en el código, este documento lo declara explícitamente como **no implementado** en lugar de describir un comportamiento supuesto.

### 1.2 Convenciones de lectura

- Los nombres de archivo se escriben tal como aparecen en el repositorio (por ejemplo `club_motociclistas/settings.py`).
- Los comandos de terminal se presentan en bloques con su lenguaje (`powershell`, `bash`, `python`, `json`, `yaml`).
- Las referencias a rutas HTTP se expresan siempre relativas a la raíz del servidor.
- Los bloques `> **Nota:**` señalan advertencias de entorno otechnical debt conocido.

### 1.3 Convenciones de nombres

El proyecto utiliza nombres de campos en `camelCase` (por ejemplo `fechaNacimiento`, `idMotociclista`, `cupoMaximo`), a diferencia de la convención `snake_case` habitual de Django. Esta decisión es deliberada y está extendida a modelos, formularios, plantillas, JSON Schemas y comandos de administración.

---

## 2. ¿En qué consiste el proyecto?

### 2.1 Descripción funcional

El **Club de Motociclistas** es una aplicación web que centraliza la administración integral de un club dedicado a las motocicletas. Permite:

1. Registrar y consultar los **socios** (motociclistas) del club y los **documentos** que cada uno presenta (cédula, licencia de conducción, SOAT, tecnomecánica).
2. Registrar las **motos** de cada socio —con fotografía—, y llevar control de los **mantenimientos** y los **accidentes** asociados a cada unidad.
3. Programar **rodadas** (salidas grupales), controlar el **cupo** de cada una y registrar las **inscripciones** de los socios, incluyendo la asistencia y observaciones.
4. Mantener una **galería fotográfica** por rodada.
5. Ofrecer un **panel de control (dashboard)** con contadores en vivo de las ocho colecciones.
6. Exponer una **API JSON de solo lectura** cuyos datos se validan contra JSON Schemas antes de servirse.

### 2.2 El problema que resuelve

Antes de la existencia de esta herramienta, un club de motociclistas distribuye su información entre planillas de cálculo, carpetas de fotografías en la nube y mensajes de chat. Esto genera tres problemas concretos:

- **Información fragmentada:** no hay una fuente única que responda "¿cuántas motos tiene el club?", "¿qué documentos vencen este mes?" o "¿cuántos lugares quedan en la rodada del sábado?".
- **Errores de cálculo manual:** los cupos de las rodadas y los límites por socio se controlaban a mano, con sobreinscripciones y vulneraciones de las reglas del club.
- **Trazabilidad nula de la flota:** los mantenimientos y accidentes de cada moto se anotaban en cuadernos, lo que impedía responder con precisión cuánto se ha invertido en una unidad o con qué frecuencia se accidente.

El proyecto centraliza esa información en MongoDB, la valida en la capa de aplicación y la publica tanto en interfaz web como en una API JSON consultable.

### 2.3 Alcance

#### Incluido en el alcance

- CRUD completo (listar, ver, crear, editar, eliminar) de las 7 entidades del dominio, 35 vistas en total.
- Panel de control con 8 contadores y accesos rápidos.
- API JSON de solo lectura para las 8 colecciones, con validación por JSON Schema.
- Publicación de los JSON Schemas como contrato de datos de la API.
- Validación de los datos almacenados contra los esquemas (comando de gestión).
- Datos de prueba coherentes (comando `seed_data`) y exportador de colecciones a JSON.
- Empaquetado reproducible con Docker (imagen multi-etapa) y orquestación con Docker Compose para desarrollo y producción.
- Servidor WSGI de producción (Gunicorn) y servicio de estáticos (WhiteNoise).

#### Fuera de alcance (no implementado)

- **Autenticación y autorización.** No hay `django.contrib.auth`, ni vistas de login, ni roles o permisos. La aplicación es abierta: cualquier persona con acceso al servidor puede crear, editar y eliminar registros.
- **Subida de archivos.** Las fotos y los archivos de documentos se referencian por URL; no hay carga binaria, ni almacenamiento de objetos, ni `MEDIA_ROOT` configurado.
- **API de escritura.** La API expone únicamente operaciones `GET` (decorador `@require_GET`); no hay endpoints `POST`, `PUT` ni `DELETE` públicos.
- **Correo electrónico.** No hay envío de notificaciones (vencimientos de documentos, confirmaciones de inscripción).
- **Paginación.** Los listados cargan el total de los registros de la colección en memoria.
- **Búsqueda en servidor.** El filtrado de los listados es del lado del navegador (JavaScript en `static/js/app.js`).
- **Pruebas automatizadas.** No existe el directorio `tests/` ni configuración de CI.

### 2.4 Actores

| Actor | Descripción | Interacción principal |
|---|---|---|
| **Administrador del club** | Persona encargada de la gestión operativa: socios, flota, agenda de eventos. | CRUD completo sobre las 7 entidades; consulta el panel de control; usa la API JSON para integraciones o reportes. |
| **Socio / motociclista** | Miembro registrado en el club, dueño de una o hasta tres motos. | Conceptualmente es el sujeto de los datos: aporta sus datos personales, documentos, motos e inscripciones. En esta versión **no existe un portal de autoservicio** ni un usuario asociado a su cuenta: el actor real que opera la interfaz es el administrador. |

> **Nota:** la distinción entre "administrador" y "socio" es conceptual y de negocio; el sistema no implementa dos roles autenticados. Se documenta aquí para dejar constancia de la intención de diseño.

### 2.5 Funcionalidades detalladas

#### 2.5.1 Panel general (dashboard)

Vista implementada en `club_motociclistas/views.py`. Consulta el conteo de las 8 colecciones y los presenta como tarjetas-métrica en `templates/dashboard.html`. Cada tarjeta es un enlace directo al listado correspondiente. La página incluye además un panel informativo sobre la arquitectura (chips de tecnología) y accesos rápidos a cuatro endpoints de la API.

![Panel general del club con los contadores de socios, motos, rodadas, inscripciones, accidentes, mantenimientos, documentos y fotos](docs/capturas/01-home.png)

#### 2.5.2 Socios y documentos (`app socios`)

- **Motociclista:** alta, edición, baja, listado y ficha de detalle. La ficha de detalle muestra, en un solo lugar, las motos del socio, sus documentos y sus inscripciones con las rodadas correspondientes.
- **DocumentoSocio:** alta, edición, baja, listado y ficha de detalle. El documento se asocia a un socio mediante un selector desplegable.

![Listado de socios del club](docs/capturas/02-socios-lista.png)

![Ficha de detalle de un socio con sus motos, documentos e inscripciones](docs/capturas/03-socios-detalle.png)

#### 2.5.3 Flota (`app flota`)

- **Moto:** alta, edición, baja, listado y ficha de detalle. La ficha agrega el historial de mantenimientos y los accidentes de la unidad, además del nombre de su dueño. La fotografía se referencia por URL.
- **Mantenimiento:** registro de intervenciones (tipo, descripción, costo, kilometraje, marca de "realizado").
- **Accidente:** registro de siniestros (descripción, ubicación, gravedad, costo estimado).

![Listado de motos de la flota](docs/capturas/04-flota-lista.png)

![Ficha de detalle de una moto con mantenimientos, accidentes y dueño](docs/capturas/05-moto-detalle.png)

#### 2.5.4 Eventos (`app eventos`)

- **Rodada:** alta, edición, baja, listado y ficha de detalle. La ficha muestra las inscripciones, la galería asociada y el **cupo disponible** (`cupoMaximo` menos inscritos, nunca negativo).
- **Inscripcion:** alta, edición, baja, listado y ficha de detalle, con validación de cupo, de rodada no vencida y de no duplicar socio.
- **Galeria:** alta, edición, baja y listado de fotografías por rodada.

![Listado de rodadas programadas y finalizadas](docs/capturas/06-eventos-lista.png)

![Ficha de detalle de una rodada con inscripciones, cupo disponible y galería](docs/capturas/07-rodada-detalle.png)

#### 2.5.5 API JSON y esquemas

Índice navegable en `/api/` que lista las 8 colecciones con su esquema asociado y su total de documentos; listado por colección; documento individual por identificador; y publicación de los JSON Schemas.

![Índice de la API JSON con el catálogo de colecciones](docs/capturas/08-api-indice.png)

---

## 3. Stack tecnológico

### 3.1 Tabla de componentes

| Componente | Tecnología | Versión | Rol en el proyecto |
|---|---|---|---|
| Lenguaje | Python | 3.12+ (entorno local de desarrollo: 3.13.3) | Lenguaje de la aplicación y de los comandos de gestión. |
| Framework web | Django | 6.1 (instalado: 6.1.2) | ORM, sistema de plantillas, formularios, mensajes, middleware, resolución de URLs. |
| Backend de base de datos | django-mongodb-backend | 6.1 (instalado: 6.1.0) | Backend oficial que permite usar la API de modelos de Django sobre MongoDB sin adaptaciones. |
| Driver de base de datos | pymongo | 4.18 (instalado: 4.18.3) | Cliente nativo de MongoDB; usado por el ORM y directamente por el comando `validar_esquemas`. |
| Validación de esquemas | jsonschema | 4.26 (instalado: 4.26.0) | Implementación de JSON Schema Draft 2020-12 con resolución de `$ref` entre archivos. |
| Resolución de `$ref` | referencing | 0.37 (instalado: 0.37.0) | Dependencia transitiva de `jsonschema`; construye el `Registry` que enlaza los esquemas del proyecto. |
| Servidor WSGI de producción | gunicorn | 27 (instalado: 27.0.1) | Sirve la aplicación `club_motociclistas.wsgi:application` en producción. |
| Servicio de archivos estáticos | whitenoise | 6.12 (instalado: 6.12.0) | Sirve CSS/JS/imágenes desde el propio proceso Python, con compresión y manifiesto. |
| Base de datos | MongoDB | 6+ (contenedor: `mongo:7`) | Almacén documental; admite instancia local o cluster de Atlas. |
| Contenedores | Docker / Docker Compose | Docker Desktop 29.9.3 (cliente) | Empaquetado reproducible y orquestación de dos servicios (`web`, `mongo`). |
| Plantillas | Django Template Language | Incluida en Django 6.1 | Herencia de plantilla única (`base.html`) con `{% block content %}`. |
| Estilos | CSS puro + JavaScript vanilla | `static/css/estilos.css`, `static/js/app.js` | Sin dependencias de terceros ni framework de front-end. |
| Internacionalización | Locale `es-mx`, TZ `America/Mexico_City` | Incluida en Django 6.1 | Formatos de fecha, moneda y mensajes en español de México. |
| Control de versiones | Git + GitHub | — | Repositorio `growing-ov/club-motociclistas`, rama `main`. |

### 3.2 Versiones declaradas en `requirements.txt`

```text
Django>=6.1,<7.0
django-mongodb-backend>=6.1,<7.0
pymongo>=4.6
jsonschema>=4.23
gunicorn>=22.0
whitenoise>=6.7
```

> **Nota:** `referencing` no aparece en `requirements.txt` porque llega como dependencia transitiva de `jsonschema`; se usa de forma explícita en `nucleo/esquemas.py`.

### 3.3 Dependencias del sistema operativo

| Dependencia | Motivo |
|---|---|
| MongoDB 6 o superior (servicio local, contenedor `mongo:7` o Atlas) | Almacén de datos. |
| Git | Clonado del repositorio y control de versiones. |
| pip | Instalación de dependencias dentro del entorno virtual. |
| Docker Desktop (opcional) | Ejecución de la imagen y de los archivos Compose. |

---

## 4. Arquitectura

### 4.1 Arquitectura de la aplicación Django (capas)

El proyecto sigue el patrón **MVC** de Django con vistas por función (FBV). La separación de responsabilidades es estrictamente vertical: cada app es autocontenida en modelos, formularios, vistas, URLs y plantillas.

```
+-----------------------------------------------------------------------+
|                          CAPA DE PRESENTACIÓN                        |
|  templates/base.html  ·  templates/dashboard.html                   |
|  templates/includes/formulario.html                                   |
|  socios/templates/socios/*.html  ·  flota/templates/flota/*.html    |
|  eventos/templates/eventos/*.html                                    |
|  static/css/estilos.css  ·  static/js/app.js                        |
+-----------------------------------------------------------------------+
              |  render(request, ...)  ·  {% url %}  ·  {% block content %}
              v
+-----------------------------------------------------------------------+
|                       CAPA DE VISTAS (FBV)                           |
|  club_motociclistas/views.py     -> dashboard                        |
|  club_motociclistas/api.py       -> indice, coleccion, documento,    |
|                                     esquemas, esquema                |
|  socios/views.py   flota/views.py   eventos/views.py                 |
|  patron: ModelForm(request.POST or None) -> validar_<modelo>(form)   |
|           -> form.add_error(*error) | form.save()                   |
|           -> messages.success() -> redirect()                        |
+-----------------------------------------------------------------------+
              |  form.is_valid()  ·  cleaned_data  ·  save()
              v
+-----------------------------------------------------------------------+
|                    CAPA DE FORMULARIOS (ModelForm)                   |
|  socios/forms.py   flota/forms.py   eventos/forms.py                 |
|  club_motociclistas/campos.py -> campo_referencia() /               |
|                                    ReferenciaModelChoiceField        |
+-----------------------------------------------------------------------+
              |
              v
+-----------------------------------------------------------------------+
|                   CAPA DE DOMINIO / MODELOS                          |
|  socios/models.py    -> Motociclista, DocumentoSocio                 |
|  flota/models.py     -> Moto, Mantenimiento, Accidente              |
|  eventos/models.py   -> Rodada, Inscripcion, Galeria                 |
|  SIN ForeignKey: referencias por ObjectId en texto (CharField)      |
+-----------------------------------------------------------------------+
              |
              v
+-----------------------------------------------------------------------+
|        CAPA DE INFRAESTRUCTURA (nucleo) + ORM django-mongodb-backend |
|  nucleo/esquemas.py       -> carga de JSON Schemas, validacion      |
|  nucleo/serializadores.py -> conversion modelo -> JSON de esquema   |
|  nucleo/templatetags/club.py -> filtros de plantilla (get, vigente, |
|                                 iniciales, moneda, estado_clase,    |
|                                 gravedad_clase)                     |
|  nucleo/management/commands/ -> seed_data, validar_esquemas,        |
|                                 exportar_datos                      |
|  club_motociclistas/referencias.py -> resolucion de referencias     |
|  club_motociclistas/settings.py    -> configuracion, .env, MongoDB  |
+-----------------------------------------------------------------------+
              |
              v
+-----------------------------------------------------------------------+
|                        MongoDB (mongod / Atlas)                      |
|  colecciones: socios_motociclista, socios_documentosocio,           |
|               flota_moto, flota_mantenimiento, flota_accidente,     |
|               eventos_rodada, eventos_inscripcion, eventos_galeria   |
+-----------------------------------------------------------------------+
```

### 4.2 Flujo de una petición (ejemplo: crear una moto)

```
Navegador
  │  POST /flota/motos/crear/   (datos del formulario + CSRF token)
  v
1. MIDDLEWARE
   SecurityMiddleware -> WhiteNoiseMiddleware -> CommonMiddleware
   -> CsrfViewMiddleware -> MessageMiddleware
2. RESOLUCION DE URL
   ROOT_URLCONF = club_motociclistas.urls
   -> path("flota/", include("flota.urls"))
   -> path("motos/crear/", views.crear_moto, name="moto_create")
3. VISTA  (flota/views.py::crear_moto)
   form = MotoForm(request.POST or None)
   if request.method == "POST" and form.is_valid():
       error = validar_moto(form)          # reglas de negocio
       if error is None:
           form.save()                     # INSERT en la coleccion Mongo
           messages.success(request, "Moto registrada correctamente.")
           return redirect("moto_list")
       form.add_error(*error)              # (campo, mensaje)
   return render(request, "flota/moto_form.html", {"form": form})
4. ORM  ->  django-mongodb-backend  ->  pymongo  ->  MongoDB
5. RESPUESTA
   302 -> /flota/motos/   (listado, con el mensaje de exito en la cookie)
   o bien 200 con el formulario y el error de negocio bajo el campo
```

### 4.3 Diagrama de aplicaciones y dependencias entre ellas

```
                    +-----------------------------------+
                    |     club_motociclistas            |
                    |  (paquete de configuracion)      |
                    |  settings · urls · views         |
                    |  api · campos · referencias      |
                    |  asgi · wsgi                     |
                    +-----------------------------------+
                       |        |        |        |
        +--------------+        |        |        +------------------+
        |                       |        |                           |
        v                       v        v                           v
+---------------+     +---------------+  |            +----------------------+
|     nucleo    |     |    socios     |  |            |  schemas/ (JSON)      |
|---------------|     |---------------|  |            |  base, moto, rodada,  |
| esquemas.py   |     | models.py    |  |            |  galeria, ...         |
| serializadores|     | forms.py     |  |            +----------------------+
| templatetags/ |     | views.py     |  |                      ^
| management/    |     | urls.py      |  |                      |
+---------------+     +---------------+  |            +----------------------+
        |                                |            |     eventos          |
        |  importa (COLECCIONES)          +---------->| models/forms/views/  |
        |                                |            | urls + templates     |
        |  importa (apps.get_model)      |            +----------------------+
        +--------------------------------+                        ^
                                                                 |
                    +-----------------------------------+        |
                    |                flota               |--------+
                    |  models.py · forms.py · views.py   |
                    |  urls.py + templates/flota/        |
                    +-----------------------------------+
```

**Reglas de dependencia efectivas:**

- `club_motociclistas` (configuración) importa de `socios`, `flota`, `eventos` y `nucleo`.
- `nucleo` **no importa modelos al nivel de módulo**: usa `apps.get_model(...)` en tiempo de ejecución (`nucleo/serializadores.py::modelo_de`) para evitar ciclos de importación.
- `socios` **no importa** `flota` ni `eventos` en `models.py`; la dependencia existe únicamente en `socios/views.py` (para comprobar dependencias al eliminar un socio) y en `socios/forms.py` (para el selector de socios).
- `flota/views.py` importa `socios.models.Motociclista` para el selector de dueño y el nombre del propietario.
- `eventos/views.py` importa `flota.models.Moto` (referencia en los mensajes de error) y `socios.models.Motociclista`.
- `club_motociclistas/referencias.py` centraliza la resolución de referencias: **las importaciones de modelos se hacen dentro de las funciones**, de forma deliberada, para que ninguna app dependa de otra en el nivel de módulo.

### 4.4 Arquitectura de contenedores y contexto de ejecución

```
+=====================================================================+
|  CONTENEDOR: club-motociclistas-web                                |
|                                                                     |
|  USER appuser (uid 10001, sin privilegios)                          |
|                                                                     |
|  +---------------------------------------------------------------+  |
|  | entrypoint.sh                                                   |  |
|  |  1. espera a que MongoDB acepte conexiones (ESPERA_MONGO, 60 s)|  |
|  |  2. python manage.py collectstatic --noinput                  |  |
|  |  3. python manage.py migrate --noinput  (no-op en MongoDB)     |  |
|  |  4. exec "$@"  ->  gunicorn                                    |  |
|  +-------------------------------+-------------------------------+  |
|                                  |                                  |
|                                  v                                  |
|  +---------------------------------------------------------------+  |
|  | gunicorn  club_motociclistas.wsgi:application                  |  |
|  |   --bind 0.0.0.0:8000 --workers 3 --timeout 120                |  |
|  +-------------------------------+-------------------------------+  |
|                                  |                                  |
|          +-----------------------+------------------------+         |
|          |  Django 6.1 (WSGI)                            |         |
|          |   MIDDLEWARE -> URLconf -> FBV -> ModelForm   |         |
|          |   -> ORM django-mongodb-backend -> pymongo     |         |
|          +-----------------------+------------------------+         |
|                                  |                                  |
|          +-----------------------+------------------------+         |
|          |  WhiteNoise  (estaticos comprimidos + manifiesto)|       |
|          +-----------------------+------------------------+         |
|                                  |                                  |
|  EXPOSE 8000   HEALTHCHECK -> http://127.0.0.1:8000/api/esquemas/ |
+=====================================================================+
                                   |
                                   |  MONGO_URI=mongodb://mongo:27017
                                   v
+=====================================================================+
|  CONTENEDOR: club-motociclistas-mongo   (imagen mongo:7)           |
|  puerto 27017   volumen mongo_data -> /data/db                     |
|  HEALTHCHECK: mongosh --eval "db.adminCommand('ping').ok"          |
+=====================================================================+
```

**Contexto de ejecución (proceso):**

| Aspecto | Valor |
|---|---|
| Directorio de trabajo | `/app` |
| Entorno virtual | `/opt/venv` (copiado desde la etapa builder) |
| `DJANGO_SETTINGS_MODULE` | `club_motociclistas.settings` |
| Variables de entorno | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `MONGO_URI`, `MONGO_DB`, `ESPERA_MONGO`, `SKIP_COLLECTSTATIC` |
| Fuente de configuración | `.env` (si existe) + variables del sistema; las variables del sistema **tienen precedencia** (`valores.update(os.environ)` en `settings.py`). |

### 4.5 Diagrama de despliegue con Docker

```
                          Internet / Intranet
                                    |
                          :8000 (host)
                                    |
        +---------------------------+----------------------------+
        |                    RED DOCKER                            |
        |                                                            |
        |   +-------------------------+      +-------------------+   |
        |   |  servicio: web          |      |  servicio: mongo |   |
        |   |  image: club-motociclistas:dev  |  image: mongo:7 |   |
        |   |  container: club-motociclistas-web                 |   |
        |   |                         |      |                   |   |
        |   |  gunicorn (3 workers)   |      |  mongod           |   |
        |   |  WhiteNoise             |      |  puerto 27017     |   |
        |   |  EXPOSE 8000            |      |                   |   |
        |   |  healthcheck: /api/esquemas/  |  healthcheck: ping|   |
        |   +------------+-------------+      +---------+---------+   |
        |                |                              |             |
        |                |  MONGO_URI=mongodb://mongo:27017         |
        |                +------------------------------+             |
        |                                               |             |
        |              +--------------------------------+            |
        |              |  volumen: mongo_data  (/data/db) |            |
        |              |  volumen: media_data  (/app/media)|           |
        |              +--------------------------------+            |
        +------------------------------------------------------------+
                                    |
                                    v
                          usuario (navegador)
```

En el archivo de producción (`docker-compose.prod.yml`) el mismo esquema se aplica con `DEBUG=False`, 2 workers de Gunicorn, `restart: unless-stopped` y `SECRET_KEY` obligatoria.

### 4.6 Árbol de directorios del proyecto

```text
club-motociclistas/
├── .dockerignore                     Contexto de build de Docker (excluye secretos y artefactos)
├── .env.example                      Plantilla de variables de entorno
├── .gitignore                        Reglas de exclusión de Git
├── Dockerfile                        Imagen multi-etapa (builder + final no-root)
├── docker-compose.yml                Orquestación de desarrollo (web + mongo)
├── docker-compose.prod.yml           Orquestación de producción (DEBUG=False)
├── entrypoint.sh                     Punto de entrada del contenedor
├── manage.py                         Utilidad de línea de comandos de Django
├── README.md                         Guía rápida de instalación y uso
├── crear_colecciones.txt             Script mongosh con validadores $jsonSchema por colección
├── descripcion.txt                   Descripción funcional y reglas de negocio en texto plano
├── requirements.txt                  Dependencias de Python
│
├── club_motociclistas/              Paquete de configuración del proyecto
│   ├── __init__.py
│   ├── api.py                        API JSON de solo lectura
│   ├── asgi.py                       Punto de entrada ASGI
│   ├── campos.py                     Campos de formulario para referencias sin relación
│   ├── referencias.py                Resolución centralizada de referencias entre documentos
│   ├── settings.py                   Configuración (lee .env, define MongoDB)
│   ├── urls.py                       URLconf raíz
│   ├── views.py                      Vista del dashboard
│   └── wsgi.py                       Punto de entrada WSGI
│
├── eventos/                          App: salidas grupales y participación
│   ├── __init__.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py                     Rodada, Inscripcion, Galeria
│   ├── urls.py
│   ├── views.py
│   └── templates/eventos/
│       ├── galeria_confirm_delete.html
│       ├── galeria_detail.html
│       ├── galeria_form.html
│       ├── galeria_list.html
│       ├── inscripcion_confirm_delete.html
│       ├── inscripcion_detail.html
│       ├── inscripcion_form.html
│       ├── inscripcion_list.html
│       ├── rodada_confirm_delete.html
│       ├── rodada_detail.html
│       ├── rodada_form.html
│       └── rodada_list.html
│
├── flota/                            App: motos y su cuidado
│   ├── __init__.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py                     Moto, Mantenimiento, Accidente
│   ├── urls.py
│   ├── views.py
│   └── templates/flota/
│       ├── accidente_confirm_delete.html
│       ├── accidente_detail.html
│       ├── accidente_form.html
│       ├── accidente_list.html
│       ├── mantenimiento_confirm_delete.html
│       ├── mantenimiento_detail.html
│       ├── mantenimiento_form.html
│       ├── mantenimiento_list.html
│       ├── moto_confirm_delete.html
│       ├── moto_detail.html
│       ├── moto_form.html
│       └── moto_list.html
│
├── nucleo/                           App auxiliar: esquemas, serialización y utilidades
│   ├── __init__.py
│   ├── apps.py
│   ├── esquemas.py                   Carga y validación de JSON Schemas
│   ├── serializadores.py             Conversión modelo Django -> documento de esquema
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── exportar_datos.py     Exporta colecciones a JSON validado
│   │       ├── seed_data.py          Poblado con datos de prueba coherentes
│   │       └── validar_esquemas.py   Valida los documentos contra su esquema
│   └── templatetags/
│       ├── __init__.py
│       └── club.py                   Filtros de plantilla propios del club
│
├── schemas/                          JSON Schemas (Draft 2020-12)
│   ├── accidente.schema.json
│   ├── base.schema.json              Definiciones comunes ($defs)
│   ├── documento_socio.schema.json
│   ├── galeria.schema.json
│   ├── inscripcion.schema.json
│   ├── mantenimiento.schema.json
│   ├── moto.schema.json
│   ├── motociclista.schema.json
│   └── rodada.schema.json
│
├── socios/                           App: miembros del club
│   ├── __init__.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py                     Motociclista, DocumentoSocio
│   ├── urls.py
│   ├── views.py
│   └── templates/socios/
│       ├── documento_confirm_delete.html
│       ├── documento_detail.html
│       ├── documento_form.html
│       ├── documento_list.html
│       ├── motociclista_confirm_delete.html
│       ├── motociclista_detail.html
│       ├── motociclista_form.html
│       └── motociclista_list.html
│
├── static/                           Archivos estáticos
│   ├── css/estilos.css
│   ├── img/favicon.svg
│   └── js/app.js
│
├── templates/                        Plantillas globales
│   ├── base.html                     Layout común: menú, migas, mensajes, {% block content %}
│   ├── dashboard.html                Panel general con contadores
│   └── includes/formulario.html      Render común de formularios ModelForm
│
└── docs/                             Documentación del proyecto
    ├── DOCUMENTACION.md              Este documento
    └── capturas/                     Capturas de pantalla de la aplicación
```

> **Nota:** el directorio `venv/` (entorno virtual local) y `.git/` no se versionan y se excluyen del árbol por legibilidad.

---

## 5. Modelo de datos

### 5.1 Convenciones del modelo

- **Sin relaciones en la base de datos.** Ningún modelo declara `ForeignKey`, `OneToOneField` ni `ManyToManyField`. Las referencias entre documentos se materializan con campos `CharField` de 24 caracteres que guardan el `ObjectId` en texto hexadecimal, indexados (`db_index=True`).
- **Clave primaria.** `DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"`, es decir, el `_id` nativo de MongoDB.
- **Convenciones de referencia** (definidas en `club_motociclistas/referencias.py`):

| Nombre del campo | Apunta a |
|---|---|
| `idMotociclista` | `socios.Motociclista` |
| `idMoto` | `flota.Moto` |
| `idRodada` | `eventos.Rodada` |

- **Nombres de colección reales** (derivados de `model._meta.db_table`, que Django compone como `<app_label>_<nombre_del_modelo_en_minúsculas>`):

| Modelo | Colección en MongoDB |
|---|---|
| `socios.Motociclista` | `socios_motociclista` |
| `socios.DocumentoSocio` | `socios_documentosocio` |
| `flota.Moto` | `flota_moto` |
| `flota.Mantenimiento` | `flota_mantenimiento` |
| `flota.Accidente` | `flota_accidente` |
| `eventos.Rodada` | `eventos_rodada` |
| `eventos.Inscripcion` | `eventos_inscripcion` |
| `eventos.Galeria` | `eventos_galeria` |

> **Nota importante:** el script `crear_colecciones.txt` crea las colecciones con nombres en plural (`motociclistas`, `documentos`, `motos`, `mantenimientos`, `accidentes`, `rodadas`, `inscripciones`, `galeria`), que **no coinciden** con los nombres que usa el ORM (`socios_motociclista`, etc.). Si se ejecuta ese script, los validadores de servidor quedan aplicados a colecciones que la aplicación no utiliza. Para que los validadores de MongoDB apliquen a las colecciones reales, es necesario renombrar las colecciones del script o generar las migraciones de Django (ver §8.6).

### 5.2 `socios.Motociclista` — Socio del club

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único del documento (24 caracteres hexadecimales). |
| `nombre` | `CharField(max_length=100)` | Sí | Nombres de pila del socio. |
| `apellido` | `CharField(max_length=100)` | Sí | Apellidos del socio. |
| `correo` | `EmailField(max_length=254, unique=True)` | Sí | Correo electrónico; **clave de unicidad** del registro. |
| `telefono` | `CharField(max_length=20, blank=True, null=True)` | No | Teléfono de contacto. |
| `fechaNacimiento` | `DateField()` | Sí | Fecha de nacimiento; base del cálculo de edad mínima. |
| `activo` | `BooleanField(default=True)` | Sí | Indica si el socio sigue activo en el club. |
| `tipoLicencia` | `CharField(max_length=50, blank=True, null=True)` | No | Categoría de la licencia de conducción (por ejemplo `A1`, `A2`). |
| `fotoUrl` | `URLField(max_length=500, blank=True, null=True)` | No | URL http/https de la foto de perfil; validada con `URLValidator`. |

**Representación textual:** `"{nombre} {apellido}"`.

### 5.3 `socios.DocumentoSocio` — Documento de un socio

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `nombreDocumento` | `CharField(max_length=80)` | Sí | Tipo de documento (por ejemplo "Licencia de Conduccion A2"). |
| `numeroDocumento` | `CharField(max_length=60)` | Sí | Número o código del documento. |
| `fechaEmision` | `DateField()` | Sí | Fecha de emisión. |
| `fechaVencimiento` | `DateField()` | Sí | Fecha de vencimiento; debe ser posterior a la de emisión. |
| `archivoUrl` | `URLField(max_length=500, blank=True, null=True)` | No | URL http/https del archivo digital associated al documento. |
| `idMotociclista` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto del socio propietario. |

**Representación textual:** `"{nombreDocumento} - {numeroDocumento}"`.

### 5.4 `flota.Moto` — Moto de un socio

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `placa` | `CharField(max_length=10, unique=True)` | Sí | Placa de la moto; **clave de unicidad**. |
| `marca` | `CharField(max_length=80)` | Sí | Fabricante (Triumph, Ducati, Yamaha, ...). |
| `modelo` | `CharField(max_length=80)` | Sí | Nombre comercial del modelo. |
| `anio` | `IntegerField()` | Sí | Año del modelo; debe estar entre 1990 y 2026. |
| `tipoMoto` | `CharField(max_length=50)` | Sí | Categoría (Adventure, Naked, Deportiva, Supermotard, ...). |
| `cilindrada` | `IntegerField(blank=True, null=True)` | No | Cilindrada en centímetros cúbicos; entre 50 y 2500 si se informa. |
| `color` | `CharField(max_length=40, blank=True, null=True)` | No | Color de la unidad. |
| `fotoUrl` | `URLField(max_length=500, blank=True, null=True)` | No | URL http/https de la fotografía de la moto. |
| `idMotociclista` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto del socio dueño. |

**Representación textual:** `"{marca} {modelo} ({placa})"`.

### 5.5 `flota.Mantenimiento` — Intervención sobre una moto

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `idMoto` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto de la moto intervenida. |
| `fecha` | `DateTimeField()` | Sí | Fecha y hora de la intervención; no puede ser futura. |
| `tipo` | `CharField(max_length=80)` | Sí | Tipo de trabajo realizado (cambio de aceite, frenos, ...). |
| `descripcion` | `TextField()` | Sí | Detalle de lo ejecutado. |
| `costo` | `FloatField()` | Sí | Costo de la intervención; no puede ser negativo. |
| `kilometraje` | `IntegerField()` | Sí | Kilometraje al momento del servicio; no puede ser negativo. |
| `realizado` | `BooleanField(default=False)` | Sí | Indica si la intervención ya se efectuó. |

**Representación textual:** `"{tipo} - {idMoto}"`.

### 5.6 `flota.Accidente` — Siniestro de una moto

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `idMoto` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto de la moto involucrada. |
| `fecha` | `DateTimeField()` | Sí | Fecha y hora del accidente; no puede ser futura. |
| `descripcion` | `TextField()` | Sí | Relato de cómo ocurrió. |
| `ubicacion` | `CharField(max_length=200)` | Sí | Lugar donde ocurrió. |
| `gravedad` | `CharField(max_length=20, choices=...)` | Sí | Nivel de gravedad: `leve`, `moderado` o `grave`. |
| `costoEstimado` | `FloatField(blank=True, null=True)` | No | Costo estimado de la reparación. |

**Valores de `gravedad`:** `leve` (Leve), `moderado` (Moderado), `grave` (Grave).
**Representación textual:** `"{gravedad legible} - {fecha}"`.

### 5.7 `eventos.Rodada` — Salida grupal

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `nombre` | `CharField(max_length=150)` | Sí | Nombre de la rodada. |
| `fechaSalida` | `DateTimeField()` | Sí | Fecha y hora de salida; debe ser futura. |
| `puntoEncuentro` | `CharField(max_length=200)` | Sí | Lugar de reunión del grupo. |
| `destino` | `CharField(max_length=200)` | Sí | Destino de la rodada. |
| `estado` | `CharField(max_length=40, choices=...)` | Sí | `programada`, `en_curso` o `finalizada`. |
| `cupoMaximo` | `IntegerField()` | Sí | Número máximo de inscritos; entre 2 y 80. |
| `distanciaKm` | `IntegerField(blank=True, null=True)` | No | Distancia aproximada en kilómetros; entre 1 y 2000. |
| `costo` | `FloatField(blank=True, null=True)` | No | Costo de inscripción; no puede ser negativo. |

**Valores de `estado`:** `programada` (Programada), `en_curso` (En curso), `finalizada` (Finalizada).
**Representación textual:** `"{nombre} - {fechaSalida}"`.

### 5.8 `eventos.Inscripcion` — Inscripción de un socio a una rodada

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `idMotociclista` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto del socio inscrito. |
| `idRodada` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto de la rodada. |
| `fechaInscripcion` | `DateTimeField()` | Sí | Momento en que se realizó la inscripción. |
| `asistio` | `BooleanField(default=False)` | Sí | Indica si el socio asistió a la rodada. |
| `observaciones` | `TextField(blank=True, null=True)` | No | Notas del organizador sobre la inscripción. |

**Representación textual:** `"{idMotociclista} -> {idRodada}"`.

### 5.9 `eventos.Galeria` — Fotografía de una rodada

| Campo | Tipo Django | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `ObjectIdAutoField` (PK) | Automático | Identificador único. |
| `idRodada` | `CharField(max_length=24, db_index=True)` | Sí | `ObjectId` en texto de la rodada a la que pertenece la foto. |
| `titulo` | `CharField(max_length=150)` | Sí | Título de la fotografía. |
| `descripcion` | `TextField(blank=True, null=True)` | No | Descripción del contenido de la imagen. |
| `urlFoto` | `URLField(max_length=500)` | Sí | URL http/https de la imagen; **obligatoria** en este modelo. |
| `fechaSubida` | `DateTimeField()` | Sí | Fecha en que se agregó la foto. |

**Representación textual:** `"{titulo}"`.

### 5.10 Diagrama de relaciones entre colecciones

```
+---------------------------+
|   socios_motociclista     |
|  (Motociclista)           |
|  PK: ObjectId             |
+---+-------+-------+-------+
    |       |       |
    | 1..N  | 1..N  | 1..N
    |       |       |
    v       |       |
+----------+---+   |   +---------------------+
|socios_docu-|   |   | eventos_inscripcion  |
|mentosocio  |   |   | PK: ObjectId         |
|(Documento   |   |   | idMotociclista (idx) |
| Socio)      |   |   | idRodada      (idx)  |
| idMotociclis|   |   | fechaInscripcion     |
|  ta (idx)   |   |   | asistio              |
+--------------+   |   | observaciones        |
                   |   +----------+----------+
                   |              |
                   |              | N..1
                   |              v
                   |      +-------------------+
                   |      |  eventos_rodada   |
                   |      |  (Rodada)         |
                   |      |  PK: ObjectId     |
                   |      +---------+---------+
                   |                |
                   |                | 1..N
                   |                v
                   |      +-------------------+
                   |      |  eventos_galeria  |
                   |      |  (Galeria)        |
                   |      |  idRodada (idx)   |
                   |      +-------------------+
                   |
                   |  1..N
                   v
        +----------------------+
        |     flota_moto       |
        |  (Moto)             |
        |  PK: ObjectId       |
        |  placa (unique)     |
        |  idMotociclista(idx)|
        +----------+-----------+
                   |
        +----------+-----------+
        |                      |
        | 1..N                 | 1..N
        v                      v
+-------------------+  +-------------------+
| flota_mantenimiento| |  flota_accidente  |
| (Mantenimiento)    | |  (Accidente)      |
| idMoto (idx)       | |  idMoto (idx)     |
| fecha · tipo       | |  fecha · gravedad |
| descripcion        | |  ubicacion        |
| costo · kilometraje| |  costoEstimado    |
| realizado          | |                   |
+-------------------+  +-------------------+

Leyenda: las flechas representan referencias logicas resueltas por
`club_motociclistas/referencias.py`. NO existen joins ni claves foraneas en
MongoDB: cada flecha es un `CharField` de 24 caracteres con el ObjectId.
```

**Resumen de cardinalidades:**

| Relación | Cardinalidad | Campo |
|---|---|---|
| Socio → Documentos | 1 : N | `DocumentoSocio.idMotociclista` |
| Socio → Motos | 1 : N | `Moto.idMotociclista` |
| Socio → Inscripciones | 1 : N | `Inscripcion.idMotociclista` |
| Moto → Mantenimientos | 1 : N | `Mantenimiento.idMoto` |
| Moto → Accidentes | 1 : N | `Accidente.idMoto` |
| Rodada → Inscripciones | 1 : N | `Inscripcion.idRodada` |
| Rodada → Galería | 1 : N | `Galeria.idRodada` |

### 5.11 JSON Schemas asociados

Cada colección tiene un JSON Schema (Draft 2020-12) en `schemas/`, que describe su contrato de datos y se usa para validar la salida de la API.

| Colección (API) | Modelo | Archivo de esquema |
|---|---|---|
| `motociclistas` | `socios.Motociclista` | `schemas/motociclista.schema.json` |
| `documentos` | `socios.DocumentoSocio` | `schemas/documento_socio.schema.json` |
| `motos` | `flota.Moto` | `schemas/moto.schema.json` |
| `mantenimientos` | `flota.Mantenimiento` | `schemas/mantenimiento.schema.json` |
| `accidentes` | `flota.Accidente` | `schemas/accidente.schema.json` |
| `rodadas` | `eventos.Rodada` | `schemas/rodada.schema.json` |
| `inscripciones` | `eventos.Inscripcion` | `schemas/inscripcion.schema.json` |
| `galeria` | `eventos.Galeria` | `schemas/galeria.schema.json` |

Definiciones comunes en `schemas/base.schema.json` (`$defs`): `objectId`, `fecha`, `fechaHora`, `url`, `email`, `telefono`, `dinero`, `texto`. Los esquemas de colección referencian estas definiciones mediante `$ref` relativos (`base.schema.json#/$defs/...`), resueltos con un `referencing.Registry` construido en `nucleo/esquemas.py`.

---

## 6. Reglas de negocio y validaciones

### 6.1 Tabla maestra de reglas

| # | Regla | Entidad | Dónde se valida | Mensaje al usuario |
|---|---|---|---|---|
| 1 | El correo del socio debe ser único | Motociclista | `unique=True` en el modelo + `ModelForm.validate_unique()` (consulta a MongoDB) | Error de campo estándar de Django ("Motociclista with this Correo already exists.") |
| 2 | El socio debe ser mayor de 18 años | Motociclista | `socios/views.py::validar_motociclista` (cálculo de edad con `date.today()`) | "Debe ser mayor de 18 anos" |
| 3 | La fecha de vencimiento debe ser posterior a la de emisión | DocumentoSocio | `socios/views.py::validar_documento` | "La fecha de vencimiento debe ser mayor a la de emision" |
| 4 | No se puede eliminar un documento vigente | DocumentoSocio | `socios/views.py::eliminar_documento` (`fechaVencimiento >= date.today()`) | "No se puede eliminar un documento vigente." |
| 5 | No se puede eliminar un socio con motos, documentos o inscripciones | Motociclista | `socios/views.py::eliminar_motociclista` (`referencias.existe_referencia`) | "No se puede eliminar: tiene motos, inscripciones o documentos asociados." |
| 6 | La placa de la moto debe ser única | Moto | `unique=True` en el modelo + validación del formulario | Error de campo estándar de Django |
| 7 | El año de la moto debe estar entre 1990 y 2026 | Moto | `flota/views.py::validar_moto` | "El anio debe estar entre 1990 y 2026" |
| 8 | La cilindrada debe estar entre 50 y 2500 cc (si se informa) | Moto | `flota/views.py::validar_moto` | "La cilindrada debe estar entre 50 y 2500" |
| 9 | Máximo 3 motos por socio | Moto | `flota/views.py::validar_moto` (cuenta `referencias.motos_de(...)`, excluyendo la instancia en edición) | "El motociclista ya tiene 3 motos (maximo)" |
| 10 | No se puede eliminar una moto con mantenimientos o accidentes | Moto | `flota/views.py::eliminar_moto` | "No se puede eliminar: tiene mantenimientos o accidentes registrados." |
| 11 | La fecha del mantenimiento no puede ser futura | Mantenimiento | `flota/views.py::validar_mantenimiento` (`timezone.now()`) | "La fecha no puede ser futura" |
| 12 | El kilometraje no puede ser negativo | Mantenimiento | `flota/views.py::validar_mantenimiento` | "El kilometraje no puede ser negativo" |
| 13 | El costo del mantenimiento no puede ser negativo | Mantenimiento | `flota/views.py::validar_mantenimiento` | "El costo no puede ser negativo" |
| 14 | La gravedad del accidente debe ser `leve`, `moderado` o `grave` | Accidente | `flota/views.py::validar_accidente` + `choices=GRAVEDADES` en el modelo | "La gravedad debe ser: leve, moderado, grave" |
| 15 | La fecha del accidente no puede ser futura | Accidente | `flota/views.py::validar_accidente` | "La fecha no puede ser futura" |
| 16 | La fecha de salida de la rodada debe ser futura | Rodada | `eventos/views.py::validar_rodada` | "La fecha de salida debe ser futura" |
| 17 | El cupo de la rodada debe estar entre 2 y 80 | Rodada | `eventos/views.py::validar_rodada` | "El cupo debe estar entre 2 y 80" |
| 18 | La distancia debe estar entre 1 y 2000 km (si se informa) | Rodada | `eventos/views.py::validar_rodada` | "La distancia debe estar entre 1 y 2000 km" |
| 19 | El costo de la rodada no puede ser negativo (si se informa) | Rodada | `eventos/views.py::validar_rodada` | "El costo no puede ser negativo" |
| 20 | No se puede eliminar una rodada con inscripciones o fotos | Rodada | `eventos/views.py::eliminar_rodada` | "No se puede eliminar: tiene inscripciones o fotos." |
| 21 | No se puede inscribir a una rodada que ya pasó | Inscripcion | `eventos/views.py::validar_inscripcion` | "La rodada ya paso" |
| 22 | La rodada seleccionada debe existir | Inscripcion | `eventos/views.py::validar_inscripcion` | "La rodada seleccionada no existe" |
| 23 | No se puede superar el cupo de la rodada | Inscripcion | `eventos/views.py::validar_inscripcion` (cuenta de inscritos, excluyendo la instancia en edición) | "El cupo de la rodada ya esta lleno" |
| 24 | El mismo socio no puedearse inscribir dos veces en la misma rodada | Inscripcion | `eventos/views.py::validar_inscripcion` | "El motociclista ya esta inscrito en esta rodada" |
| 25 | Las URLs de fotos y archivos deben ser http o https | Motociclista, DocumentoSocio, Moto, Galeria | `URLField` con `URLValidator(schemes=["http", "https"])` | Error de campo estándar de Django |
| 26 | Los documentos deben cumplir su JSON Schema | Las 8 colecciones | `nucleo/esquemas.py::validar` + comando `validar_esquemas` + capa de la API | Salida del comando de validación |

### 6.2 Notas sobre la implementación de las reglas

- **Las reglas se aplican en dos fases.** Primero Django valida el formulario (`form.is_valid()`: tipos, campos obligatorios, formatos, unicidad). Después se ejecuta la función `validar_<modelo>(form)`, que devuelve una tupla `(campo, mensaje)` o `None`. El error se inyecta con `form.add_error(*error)` y se muestra bajo el campo correspondiente.
- **La regla 9 (máximo 3 motos) es consciente del modo edición.** Al editar, la moto actual se excluye del conteo (`motos.exclude(pk=form.instance.pk)`), de modo que editar una moto existente nunca dispara el error de límite.
- **La regla 23 (cupo) también es consciente del modo edición.** La inscripción en edición se excluye del conteo antes de comparar con `cupoMaximo`.
- **El campo `activo` no dispara ninguna regla automática.** Un socio inactivo (`activo=False`) puede tener motos, documentos e inscripciones; la marca es informativa.
- **La galería no tiene reglas de negocio adicionales.** No existe una función `validar_galeria`; el único control es la validación del formulario (`urlFoto` obligatorio y con formato http/https) y la validación contra el JSON Schema.
- **Las eliminaciones de mantenimientos, accidentes, inscripciones y fotografías no tienen bloqueos.** Se borran directamente; la protección aplica a los cuatro objetos "padre" (socio, moto, rodada, documento).

### 6.3 Restricciones a nivel de base de datos

El script `crear_colecciones.txt` define validadores `$jsonSchema` del lado del servidor MongoDB que replican las reglas 1 a 24 (rangos de `anio`, `cilindrada`, `cupoMaximo`, `distanciaKm`, `minimum` en costos y kilometrajes, `enum` de `gravedad` y `estado`, campos `required`, etc.).

> **Nota:** como se explica en §5.1, los nombres de colección del script no coinciden con los que usa el ORM. Para que estas restricciones se apliquen en el servidor, hay que alinear los nombres o generar y aplicar las migraciones de Django, que crean los índices únicos (`correo`, `placa`) en las colecciones reales.

---

## 7. Rutas y endpoints

### 7.1 Rutas del proyecto (`club_motociclistas/urls.py`)

| Ruta | Nombre de URL | Vista | Descripción |
|---|---|---|---|
| `/` | `home` | `views.dashboard` | Panel general con los 8 contadores del club. |
| `/home/` | `inicio` | `views.dashboard` | Alias de `/` (misma vista). |
| `/socios/…` | — | `include("socios.urls")` | Rutas de la app de socios. |
| `/flota/…` | — | `include("flota.urls")` | Rutas de la app de flota. |
| `/eventos/…` | — | `include("eventos.urls")` | Rutas de la app de eventos. |
| `/api/` | `api_indice` | `api.indice` | Índice JSON con el catálogo de colecciones. |
| `/api/esquemas/` | `api_esquemas` | `api.esquemas` | Todos los JSON Schemas del proyecto. |
| `/api/esquemas/<nombre>` | `api_esquema` | `api.esquema` | Un JSON Schema concreto; `Content-Type: application/schema+json`. |
| `/api/<coleccion>/` | `api_coleccion` | `api.coleccion` | Listado completo de una colección. |
| `/api/<coleccion>/<id>/` | `api_documento` | `api.documento` | Documento individual por `ObjectId`. |
| `/<ruta>` | `ruta_default` | `RedirectView` (302) | **Cualquier ruta no reconocida redirige a `/`.** |

> **Nota:** la redirección genérica se declara al final del `urlpatterns`, por lo que solo actúa cuando ninguna otra ruta coincide. Es permanente (`permanent=False`), es decir, responde con HTTP 302.

### 7.2 Rutas de `socios` (prefijo `/socios/`)

| Ruta | Nombre de URL | Vista | Descripción |
|---|---|---|---|
| `/socios/motociclistas/` | `motociclista_list` | `lista_motociclistas` | Listado de socios (ordenado por apellido y nombre). |
| `/socios/motociclistas/crear/` | `motociclista_create` | `crear_motociclista` | Formulario de alta de socio. |
| `/socios/motociclistas/<pk>/` | `motociclista_detail` | `ver_motociclista` | Ficha del socio con motos, documentos e inscripciones. |
| `/socios/motociclistas/<pk>/editar/` | `motociclista_update` | `editar_motociclista` | Formulario de edición de socio. |
| `/socios/motociclistas/<pk>/eliminar/` | `motociclista_delete` | `eliminar_motociclista` | Confirmación y borrado de socio. |
| `/socios/documentos/` | `documento_list` | `lista_documentos` | Listado de documentos (ordenado por fecha de emisión descendente). |
| `/socios/documentos/crear/` | `documento_create` | `crear_documento` | Formulario de alta de documento. |
| `/socios/documentos/<pk>/` | `documento_detail` | `ver_documento` | Ficha del documento y su socio. |
| `/socios/documentos/<pk>/editar/` | `documento_update` | `editar_documento` | Formulario de edición de documento. |
| `/socios/documentos/<pk>/eliminar/` | `documento_delete` | `eliminar_documento` | Confirmación y borrado de documento. |

### 7.3 Rutas de `flota` (prefijo `/flota/`)

| Ruta | Nombre de URL | Vista | Descripción |
|---|---|---|---|
| `/flota/motos/` | `moto_list` | `lista_motos` | Listado de motos (ordenado por placa). |
| `/flota/motos/crear/` | `moto_create` | `crear_moto` | Formulario de alta de moto. |
| `/flota/motos/<pk>/` | `moto_detail` | `ver_moto` | Ficha de la moto con mantenimientos, accidentes y dueño. |
| `/flota/motos/<pk>/editar/` | `moto_update` | `editar_moto` | Formulario de edición de moto. |
| `/flota/motos/<pk>/eliminar/` | `moto_delete` | `eliminar_moto` | Confirmación y borrado de moto. |
| `/flota/mantenimientos/` | `mantenimiento_list` | `lista_mantenimientos` | Listado de mantenimientos (fecha descendente). |
| `/flota/mantenimientos/crear/` | `mantenimiento_create` | `crear_mantenimiento` | Formulario de alta de mantenimiento. |
| `/flota/mantenimientos/<pk>/` | `mantenimiento_detail` | `ver_mantenimiento` | Ficha del mantenimiento y su moto. |
| `/flota/mantenimientos/<pk>/editar/` | `mantenimiento_update` | `editar_mantenimiento` | Formulario de edición de mantenimiento. |
| `/flota/mantenimientos/<pk>/eliminar/` | `mantenimiento_delete` | `eliminar_mantenimiento` | Confirmación y borrado de mantenimiento. |
| `/flota/accidentes/` | `accidente_list` | `lista_accidentes` | Listado de accidentes (fecha descendente). |
| `/flota/accidentes/crear/` | `accidente_create` | `crear_accidente` | Formulario de alta de accidente. |
| `/flota/accidentes/<pk>/` | `accidente_detail` | `ver_accidente` | Ficha del accidente y su moto. |
| `/flota/accidentes/<pk>/editar/` | `accidente_update` | `editar_accidente` | Formulario de edición de accidente. |
| `/flota/accidentes/<pk>/eliminar/` | `accidente_delete` | `eliminar_accidente` | Confirmación y borrado de accidente. |

### 7.4 Rutas de `eventos` (prefijo `/eventos/`)

| Ruta | Nombre de URL | Vista | Descripción |
|---|---|---|---|
| `/eventos/rodadas/` | `rodada_list` | `lista_rodadas` | Listado de rodadas (ordenado por fecha de salida). |
| `/eventos/rodadas/crear/` | `rodada_create` | `crear_rodada` | Formulario de alta de rodada. |
| `/eventos/rodadas/<pk>/` | `rodada_detail` | `ver_rodada` | Ficha de la rodada con inscripciones, cupo disponible y galería. |
| `/eventos/rodadas/<pk>/editar/` | `rodada_update` | `editar_rodada` | Formulario de edición de rodada. |
| `/eventos/rodadas/<pk>/eliminar/` | `rodada_delete` | `eliminar_rodada` | Confirmación y borrado de rodada. |
| `/eventos/inscripciones/` | `inscripcion_list` | `lista_inscripciones` | Listado de inscripciones (fecha de inscripción descendente). |
| `/eventos/inscripciones/crear/` | `inscripcion_create` | `crear_inscripcion` | Formulario de alta de inscripción. |
| `/eventos/inscripciones/<pk>/` | `inscripcion_detail` | `ver_inscripcion` | Ficha de la inscripción, el socio y la rodada. |
| `/eventos/inscripciones/<pk>/editar/` | `inscripcion_update` | `editar_inscripcion` | Formulario de edición de inscripción. |
| `/eventos/inscripciones/<pk>/eliminar/` | `inscripcion_delete` | `eliminar_inscripcion` | Confirmación y borrado de inscripción. |
| `/eventos/galeria/` | `galeria_list` | `lista_galeria` | Listado de fotografías (fecha de subida descendente). |
| `/eventos/galeria/crear/` | `galeria_create` | `crear_galeria` | Formulario de alta de fotografía. |
| `/eventos/galeria/<pk>/` | `galeria_detail` | `ver_galeria` | Ficha de la fotografía y su rodada. |
| `/eventos/galeria/<pk>/editar/` | `galeria_update` | `editar_galeria` | Formulario de edición de fotografía. |
| `/eventos/galeria/<pk>/eliminar/` | `galeria_delete` | `eliminar_galeria` | Confirmación y borrado de fotografía. |

### 7.5 Colecciones expuestas por la API

| Colección | Ruta | Modelo | Orden por defecto |
|---|---|---|---|
| `motociclistas` | `/api/motociclistas/` | `socios.Motociclista` | `apellido`, `nombre` |
| `documentos` | `/api/documentos/` | `socios.DocumentoSocio` | `-fechaEmision` |
| `motos` | `/api/motos/` | `flota.Moto` | `placa` |
| `mantenimientos` | `/api/mantenimientos/` | `flota.Mantenimiento` | `-fecha` |
| `accidentes` | `/api/accidentes/` | `flota.Accidente` | `-fecha` |
| `rodadas` | `/api/rodadas/` | `eventos.Rodada` | `fechaSalida` |
| `inscripciones` | `/api/inscripciones/` | `eventos.Inscripcion` | `-fechaInscripcion` |
| `galeria` | `/api/galeria/` | `eventos.Galeria` | `-fechaSubida` |

### 7.6 Plantillas asociadas a cada ruta

Para cada modelo existen cuatro plantillas con nombres estables:

```text
templates/<app>/<modelo>_list.html            Listado
templates/<app>/<modelo>_form.html            Alta / edición (comparten plantilla)
templates/<app>/<modelo>_detail.html          Ficha de detalle
templates/<app>/<modelo>_confirm_delete.html  Confirmación de borrado
```

Todas heredan de `templates/base.html` y escriben dentro de `{% block content %}`. Los formularios usan la parcial `templates/includes/formulario.html`, que recorre los campos del `ModelForm` y dibuja los errores junto a cada campo.

---

## 8. Instalación y entorno de desarrollo

### 8.1 Requisitos previos

| Requisito | Versión mínima | Comprobación |
|---|---|---|
| Python | 3.12 | `python --version` |
| MongoDB | 6.0 (o MongoDB Atlas) | `mongosh --eval "db.runCommand({ping:1})"` |
| pip | incluido con Python | `python -m pip --version` |
| Git | cualquiera | `git --version` |
| Docker Desktop (opcional) | Engine Linux habilitado | `docker version` |

### 8.2 Procedimiento en Windows (PowerShell)

```powershell
# 1) Clonar el repositorio
git clone https://github.com/growing-ov/club-motociclistas.git
cd club-motociclistas

# 2) Crear el entorno virtual
python -m venv venv

# 3) Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# 4) Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Nota (ExecutionPolicy):** si PowerShell muestra el error
> `No se puede cargar el archivo ... porque la ejecución de scripts está deshabilitada en este sistema`,
> es porque la política de ejecución restringe los scripts `.ps1`. Resuélvelo **para tu usuario actual** con:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> Alternativa sin cambiar la política: activar el entorno con el *script* de la derecha en lugar del de PowerShell:
>
> ```powershell
> .\venv\Scripts\activate.bat
> ```

### 8.3 Procedimiento en Linux / macOS

```bash
# 1) Clonar el repositorio
git clone https://github.com/growing-ov/club-motociclistas.git
cd club-motociclistas

# 2) Crear el entorno virtual
python3 -m venv venv

# 3) Activar el entorno virtual
source venv/bin/activate

# 4) Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 8.4 Configuración del archivo `.env`

El archivo `.env` **no está versionado** (aparece en `.gitignore` y en `.dockerignore`). Se crea a partir de `.env.example`:

```powershell
# Windows PowerShell
copy .env.example .env
```

```bash
# Linux / macOS
cp .env.example .env
```

#### Variables de entorno

| Variable | Obligatoria | Valor por defecto | Descripción |
|---|---|---|---|
| `SECRET_KEY` | En producción | `django-insecure-club-motociclistas-cambiar-en-produccion` | Clave criptográfica de Django (firmado de cookies y CSRF). **Debe ser fuerte y única en producción.** |
| `DEBUG` | No | `True` | Modo depuración. Se interpreta como booleano: solo `"true"` (sin distinguir mayúsculas) activa `DEBUG=True`. En producción debe ser `False`. |
| `ALLOWED_HOSTS` | En producción | `*` | Lista de hosts permitidos separada por comas. En producción, lista explícita (por ejemplo `club.example.com`). |
| `MONGO_URI` | No | `mongodb://localhost:27017` | Cadena de conexión a MongoDB. Local, `mongodb://localhost:27017`, o Atlas `mongodb+srv://usuario:clave@cluster.mongodb.net/?retryWrites=true&w=majority`. |
| `MONGO_DB` | No | `club_motociclistas` | Nombre de la base de datos dentro del servidor MongoDB. |

#### Ejemplo completo de `.env` (desarrollo local)

```dotenv
# Copia este archivo como .env y cambia los valores.
SECRET_KEY=cambia-esta-clave
DEBUG=True
ALLOWED_HOSTS=*
MONGO_URI=mongodb://localhost:27017
MONGO_DB=club_motociclistas
```

#### Ejemplo de `.env` con MongoDB Atlas

```dotenv
SECRET_KEY=una-clave-larga-y-aleatoria-de-al-menos-50-caracteres
DEBUG=False
ALLOWED_HOSTS=club.example.com
MONGO_URI=mongodb+srv://usuario:clave@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=club_motociclistas
```

> **Nota:** `settings.py::leer_variables()` lee el archivo `.env` y después aplica `os.environ.update()` sobre el resultado. Por lo tanto, **las variables de entorno del sistema tienen prioridad sobre el archivo `.env`**. Esto es lo que permite a Docker Compose sobrescribir `MONGO_URI` con la dirección interna del servicio `mongo`.

### 8.5 Creación de la base de datos y carga de datos

MongoDB es una base de datos sin esquema: no requiere `CREATE DATABASE`. Sin embargo, el proyecto expone comandos de gestión propios:

```bash
# 1) Verificar la configuración del proyecto (no necesita conexión a Mongo)
python manage.py check

# 2) Aplicar migraciones (crea índices y validadores cuando existen migraciones)
python manage.py migrate

# 3) Poblar con datos de prueba coherentes (7 socios, 7 motos, 5 rodadas, 22 inscripciones, 5 fotos, ...)
python manage.py seed_data

# 4) Validar los documentos almacenados contra sus JSON Schemas
python manage.py validar_esquemas
```

Opciones útiles de `seed_data`:

```bash
python manage.py seed_data --flush       # vacía las colecciones antes de poblar
python manage.py seed_data --sin-fotos    # no asigna imágenes remotas a socios y motos
```

Opciones útiles de `validar_esquemas`:

```bash
python manage.py validar_esquemas                       # todas las colecciones
python manage.py validar_esquemas --coleccion motos     # solo una colección
python manage.py validar_esquemas --detalle             # muestra cada documento con errores
python manage.py validar_esquemas --limite 50           # máximo de errores mostrados
```

> **Nota:** el repositorio **no incluye el directorio `migrations/`** en las apps `socios`, `flota` y `eventos`. Por lo tanto `python manage.py migrate` no crea índices únicos sobre `correo` ni `placa` en MongoDB. La unicidad se sigue garantizando en la capa de aplicación porque `ModelForm.validate_unique()` consulta la base de datos antes de guardar. Para materializar los índices en el servidor, genera y aplica las migraciones:
>
> ```bash
> python manage.py makemigrations socios flota eventos
> python manage.py migrate
> ```

### 8.6 Ejecución del servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación queda disponible en <http://127.0.0.1:8000/>. La raíz (`/`) muestra el panel general; cualquier ruta inexistente redirige a `/`.

Para exponer el servidor en la red local (por ejemplo, para tomar capturas desde otra máquina):

```bash
python manage.py runserver 0.0.0.0:8000
```

### 8.7 Comandos útiles de Django

```bash
# Diagnóstico del proyecto (detecta errores de configuración)
python manage.py check

# Comprobaciones más estrictas, incluyendo migraciones pendientes
python manage.py check --deploy

# Generación y aplicación de migraciones
python manage.py makemigrations
python manage.py makemigrations socios flota eventos
python manage.py migrate
python manage.py showmigrations

# Consola de Django (ORM disponible)
python manage.py shell

# Consola de Django con IPython (si está instalado)
python manage.py shell -i ipython

# Consola de MongoDB via pymongo (según el backend oficial, `dbshell` abre mongosh)
python manage.py dbshell

# Recopilación de archivos estáticos (obligatoria antes de servir en producción)
python manage.py collectstatic --noinput

# Limpieza de archivos .pyc obsoletos
python manage.py clean
```

Ejemplo de uso de la consola para consultar datos:

```python
>>> from eventos.models import Rodada
>>> Rodada.objects.count()
5
>>> for r in Rodada.objects.order_by("fechaSalida"):
...     print(r.nombre, r.cupoMaximo)
```

### 8.8 Exportación de datos

El comando `exportar_datos` vuelca las colecciones a archivos JSON que cumplen los JSON Schemas:

```bash
python manage.py exportar_datos                          # -> ./datos_exportados/*.json
python manage.py exportar_datos --salida respaldo_2026   # carpeta destino personalizada
python manage.py exportar_datos --coleccion rodadas       # solo una colección
python manage.py exportar_datos --sin-validar            # omite la validación
```

El comando valida cada documento antes de escribirlo y termina con código de salida `1` si algún documento no cumple el esquema.

### 8.9 Solución de problemas

#### `ModuleNotFoundError: No module named 'django'`

El intérprete activo no es el del entorno virtual.

```powershell
# Windows
.\venv\Scripts\Activate.ps1
python -c "import django; print(django.get_version())"
```

```bash
# Linux / macOS
source venv/bin/activate
python -c "import django; print(django.get_version())"
```

Si persiste, reinstala las dependencias dentro del entorno:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Error de conexión a MongoDB (`ServerSelectionTimeoutError`, `Connection refused`)

1. **Verifica que MongoDB esté corriendo.** En Windows, el servicio aparece en *Administrador de servicios* como `MongoDB Server`; en Linux, con `systemctl status mongod`; en macOS, con `brew services list`.
2. **Comprueba el puerto.** Debe ser el 27017:

   ```bash
   mongosh --eval "db.adminCommand({ping:1})"
   ```

3. **Verifica el `.env`.** `MONGO_URI` debe apuntar a donde realmente está la base:
   - MongoDB local: `mongodb://localhost:27017`
   - Dentro de Docker Compose: `mongodb://mongo:27017` (nunca `localhost`, que apunta al propio contenedor).
   - Atlas: la cadena `mongodb+srv://...` completa.
4. **Comprueba la red y el cortafuegos.** Atlas exige que la IP de salida esté en la lista de acceso del cluster.
5. **Verifica el nombre de la base.** `MONGO_DB=club_motociclistas`.

#### Las hojas de estilo o el JavaScript no cargan (404 en `/static/...`)

`WhiteNoiseMiddleware` sirve los archivos estáticos desde `STATIC_ROOT`. Si el manifiesto no existe, las plantillas con `{% static %}` fallan.

```bash
python manage.py collectstatic --noinput
```

En Docker, el `entrypoint.sh` ejecuta `collectstatic` automáticamente salvo que se defina `SKIP_COLLECTSTATIC=1`. El `Dockerfile` también lo ejecuta en la etapa *builder*, porque usa `CompressedManifestStaticFilesStorage`, que exige el manifiesto para resolver los nombres con hash.

#### `CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False`

Se inició el servidor con `DEBUG=False` sin declarar los hosts. Añade `ALLOWED_HOSTS` al `.env`:

```dotenv
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### `ImperativeRoutingMonitor` / `django_mongodb_backend` no encuentra la colección

El backend crea las colecciones de forma implícita al insertar. Si una colección existe con validadores del script `crear_colecciones.txt` y los nombres no coinciden con los del ORM (§5.1), usa el nombre real (`socios_motociclista`, etc.) o alinea el script.

#### La consola de PowerShell no encuentra `python`

Windows Store aliases pueden interferir. Usa el lanzador explícito:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python --version
```

---

## 9. Docker

### 9.1 Componentes

| Archivo | Propósito |
|---|---|
| `Dockerfile` | Imagen de producción multi-etapa (`builder` → `final`). |
| `.dockerignore` | Excluye del contexto de build todo lo que no debe entrar en la imagen. |
| `docker-compose.yml` | Entorno de desarrollo: servicios `web` + `mongo`. |
| `docker-compose.prod.yml` | Variante de producción: `DEBUG=False`, 2 workers, `SECRET_KEY` obligatoria. |
| `entrypoint.sh` | Punto de entrada: espera a Mongo, `collectstatic`, `migrate`, `exec "$@"`. |

### 9.2 Construcción de la imagen

```bash
docker build -t club-motociclistas .
```

**Detalles de la construcción multi-etapa:**

| Etapa | Base | Operaciones | Resultado |
|---|---|---|---|
| `builder` | `python:3.12-slim` | Crea `/opt/venv`, instala `requirements.txt`, copia el código, ejecuta `collectstatic` con una `SECRET_KEY` ficticia y `DEBUG=False`. | Entorno virtual con dependencias + `staticfiles/` con manifiesto. |
| `final` | `python:3.12-slim` | Copia `/opt/venv` y `/app` desde *builder*, crea el usuario `appuser` (uid/gid 10001, shell `nologin`), copia `entrypoint.sh`, cambia a `USER appuser`. | Imagen mínima que no contiene las herramientas de compilación. |

### 9.3 Ejecución con Docker Compose

```bash
# Construir y levantar los servicios en primer plano
docker compose up --build
```

| Servicio | Imagen | Puerto en el host | Puerto interno |
|---|---|---|---|
| `web` | `club-motociclistas:dev` (construida localmente) | `8000` | `8000` |
| `mongo` | `mongo:7` | `27017` | `27017` |

La aplicación queda disponible en <http://localhost:8000> y MongoDB en `localhost:27017`.

```bash
# Levantar en segundo plano
docker compose up -d --build

# Ver el estado de los servicios
docker compose ps

# Detener y eliminar los contenedores (conserva los volúmenes)
docker compose down

# Detener y eliminar también los volúmenes (¡borra la base de datos!)
docker compose down -v
```

### 9.4 Variables de entorno en Docker

| Variable | Servicio | Valor por defecto | Notas |
|---|---|---|---|
| `MONGO_URI` | `web` | `mongodb://mongo:27017` | **Forzado** por Compose: nunca debe ser `localhost`. |
| `MONGO_DB` | `web` | `club_motociclistas` | Interpolado desde el `.env` o valor por defecto. |
| `DEBUG` | `web` | `True` (dev) / `False` (prod) | El valor de producción está fijado a `"False"`. |
| `ALLOWED_HOSTS` | `web` | `*` (dev) / `localhost,127.0.0.1` (prod) | Separados por comas. |
| `SECRET_KEY` | `web` | *(dev)* / **obligatoria** (prod) | En producción: `SECRET_KEY: ${SECRET_KEY:?define SECRET_KEY en .env para produccion}`; Compose **aborta el arranque** si no está definida. |
| `DJANGO_SETTINGS_MODULE` | `web` | `club_motociclistas.settings` | Requerido por WSGI. |
| `ESPERA_MONGO` | `web` | `60` | Segundos máximos de espera a MongoDB en el `entrypoint.sh`. `0` desactiva la espera. |
| `SKIP_COLLECTSTATIC` | `web` | `1` (prod) / `0` (dev) | Omite `collectstatic` en el arranque cuando el manifiesto ya existe en la imagen. |

El archivo `.env` se carga opcionalmente en ambos Compose mediante `env_file` con `required: false`, de modo que el proyecto puede levantarse sin él en desarrollo.

### 9.5 Volúmenes

| Volumen | Contenedor | Ruta | Contenido |
|---|---|---|---|
| `mongo_data` | `mongo` | `/data/db` | Datos de MongoDB (sobreviven a `docker compose down`). |
| `media_data` | `web` | `/app/media` | Reservado para archivos subidos. |

> **Nota:** `settings.py` **no define `MEDIA_ROOT`** ni existe carga de archivos en la aplicación (todas las fotos y documentos se referencian por URL). El volumen `media_data` está preparado, pero para usarlo habría que añadir `MEDIA_ROOT = "/app/media"` y `MEDIA_URL = "/media/"` a la configuración.

### 9.6 Healthchecks

| Servicio | Prueba | Intervalo | Timeout | Reintentos | Inicio |
|---|---|---|---|---|---|
| `web` | `urllib.request.urlopen('http://127.0.0.1:8000/api/esquemas/')` → HTTP 200 | 30 s | 5 s | 3 | 20 s |
| `mongo` | `mongosh --quiet --eval "db.adminCommand('ping').ok"` | 10 s | 5 s | 5 | 20 s |

El `web` consulta **`/api/esquemas/`** de forma intencionada: ese endpoint solo lee archivos del disco y **no depende de MongoDB**, de modo que un fallo de base de datos no se confunde con un fallo de la aplicación.

Además, `depends_on: mongo: condition: service_healthy` garantiza que `web` no arranque hasta que MongoDB responde.

### 9.7 Comandos de depuración

```bash
# Seguir los logs del servicio web en tiempo real
docker compose logs -f web

# Logs de MongoDB
docker compose logs -f mongo

# Últimas 100 líneas
docker compose logs --tail=100 web

# Entrar en un contenedor en ejecución
docker compose exec web sh
docker compose exec web python manage.py check
docker compose exec web python manage.py validar_esquemas
docker compose exec web python manage.py shell

# Entrar en la consola de MongoDB
docker compose exec mongo mongosh
docker compose exec mongo mongosh --eval "db.getSiblingDB('club_motociclistas').getCollectionNames()"

# Ver el estado de salud
docker compose ps
docker inspect --format='{{json .State.Health}}' club-motociclistas-web

# Reconstruir sin caché
docker compose build --no-cache web
```

### 9.8 Advertencia de entorno sobre Docker Desktop en esta máquina

> **Advertencia:** en el equipo donde se preparó esta documentación, **Docker Desktop no dispone de un engine Linux operativo** (WSL2 no está disponible/habilitado en la máquina). El cliente Docker responde, pero cualquier comando que requiera el daemon falla con:
>
> ```text
> docker : request returned 500 Internal Server Error for API route and version
> http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.56/version, check if the server supports the requested API version
> ```
>
> En consecuencia, **la imagen `club-motociclistas` no pudo construirse ni ejecutarse en este entorno**, y por tanto el `docker compose up --build` no se pudo verificar de extremo a extremo en esta máquina.
>
> Este hecho es **una limitación del entorno de ejecución, no un defecto del `Dockerfile` ni de los archivos Compose**: el `Dockerfile` está construido como una imagen multi-etapa convencional (builder con `collectstatic`, etapa final sin privilegios con `USER appuser`), y los dos Compose están correctamente formados. La verificación deberá realizarse en un equipo con Docker Desktop funcional (o en Linux/CI con Docker Engine).
>
> Comprobaciones que deben ejecutarse en un entorno con Docker operativo:
>
> ```bash
> docker build -t club-motociclistas .
> docker compose up --build
> docker compose ps          # ambos servicios en estado "healthy"
> curl -i http://localhost:8000/api/esquemas/
> ```

---

## 10. Despliegue en producción

### 10.1 Checklist de despliegue

#### Configuración

- [ ] `DEBUG=False` en el `.env` (o variable de entorno del sistema, que tiene prioridad).
- [ ] `SECRET_KEY` con valor fuerte, aleatorio y **único por despliegue**. Nunca la cadena de desarrollo.

  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] `ALLOWED_HOSTS` con la lista explícita de dominios: `ALLOWED_HOSTS=club.example.com,www.club.example.com`.
- [ ] `MONGO_URI` apuntando a la instancia de producción (Atlas con IP de salida en la lista de acceso, o un MongoDB autoalojado con autenticación habilitada).
- [ ] `MONGO_DB` con el nombre definitivo de la base de datos.
- [ ] `.env` **fuera** del control de versiones y con permisos restringidos en el servidor.

#### Archivos estáticos

- [ ] Ejecutar `python manage.py collectstatic --noinput` (en la imagen se hace en la etapa *builder*; en un despliegue sin Docker, hacerlo en el paso de build).
- [ ] Verificar que `whitenoise.middleware.WhiteNoiseMiddleware` está en `MIDDLEWARE` y que `STATICFILES_STORAGE` usa `CompressedManifestStaticFilesStorage` (ya configurado en `settings.py`).

#### Servidor de aplicación

- [ ] Usar Gunicorn como servidor WSGI: `gunicorn club_motociclistas.wsgi:application --bind 0.0.0.0:8000`.
- [ ] Dimensionar los workers con la fórmula **`workers = 2 × nCPU + 1`** (con `nproc` o `sysctl -n hw.ncpu`). Como referencia, el `Dockerfile` usa 3 workers y `docker-compose.prod.yml` usa 2.
- [ ] Definir `--timeout 120` (el valor por defecto de Gunicorn, 30 s, es corto para respuestas lentas de MongoDB).
- [ ] Considerar `--max-requests` y `--max-requests-jitter` para reciclar workers y evitar fugas de memoria.
- [ ] Planificar el reinicio de workers durante despliegues (por ejemplo, `SIGHUP` o el orquestador de contenedores con `restart: unless-stopped`).

#### Proxy inverso

- [ ] Colocar **nginx** (o Apache/Caddy) delante de Gunicorn para terminar TLS, servir `/static/` directamente y comprimir las respuestas.

  ```nginx
  server {
      listen 80;
      server_name club.example.com;

      location /static/ {
          alias /app/staticfiles/;
          expires 30d;
      }

      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host              $host;
          proxy_set_header X-Real-IP         $remote_addr;
          proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

- [ ] Si el proxy termina TLS, añadir `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` en `settings.py` y `SECURE_SSL_REDIRECT = True`.
- [ ] Configurar HSTS (`SECURE_HSTS_SECONDS`), cookies seguras (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) y `SECURE_CONTENT_TYPE_NOSNIFF = True`.

#### Arranque y migraciones

- [ ] Ejecutar las migraciones en el arranque del servicio (el `entrypoint.sh` ya lo hace con `python manage.py migrate --noinput`, tolerante a fallos porque en MongoDB no hay esquema).
- [ ] Ejecutar `python manage.py check --deploy` antes de publicar.
- [ ] Verificar la salud del servicio: `GET /api/esquemas/` debe devolver HTTP 200.

#### Datos y respaldos

- [ ] Definir una política de respaldos de MongoDB (`mongodump` diario, retención de 30 días, copia fuera del servidor).
- [ ] Verificar la restauración de los respaldos al menos una vez por trimestre.
- [ ] Planificar el crecimiento de la base: MongoDB no impose límites rígidos, pero conviene vigilar el tamaño del documento de WiredTiger y el número de índices.
- [ ] Considerar un plan de respaldo del repositorio (GitHub ya actúa como respaldo del código).

#### Observabilidad

- [ ] Centralizar los logs de Gunicorn (`--access-logfile -` escribe a stdout, útil con Docker).
- [ ] Configurar alertas sobre el `HEALTHCHECK` del contenedor.
- [ ] Vigilar el uso de memoria de los workers y la latencia de las consultas a MongoDB.

### 10.2 Despliegue con Docker Compose en producción

```bash
# 1) Preparar el .env de producción
cat > .env <<'EOF'
SECRET_KEY=una-clave-larga-y-aleatoria-de-al-menos-50-caracteres
DEBUG=False
ALLOWED_HOSTS=club.example.com
MONGO_DB=club_motociclistas
EOF

# 2) Construir y levantar en segundo plano
docker compose -f docker-compose.prod.yml up -d --build

# 3) Verificar el estado
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
```

> **Nota:** `docker-compose.prod.yml` usa `SECRET_KEY: ${SECRET_KEY:?...}`. Si la variable no está definida, **Compose aborta el despliegue con un error explícito**, lo que evita publicar la aplicación con la clave insegura por defecto.

### 10.3 Consideraciones sobre MongoDB en producción

- **Autenticación:** en producción es obligatorio habilitar el acceso con usuario y contraseña (`MONGO_URI` con credenciales) y restringir los orígenes con la lista de acceso de Atlas o con reglas de firewall.
- **Réplica:** Atlas ofrece réplicas resilientes; para instalaciones propias se recomienda un conjunto de réplicas (`rs0`) en lugar de un `mongod` aislado.
- **Índices:** revisar con `db.collection.getIndexes()` que los índices de `correo`, `placa`, `idMotociclista`, `idMoto` e `idRodada` existan (ver §8.5 sobre la generación de migraciones).

---

## 11. API JSON interna

### 11.1 Descripción

La API es de **solo lectura** y está implementada en `club_motociclistas/api.py`. Todas sus vistas están protegidas con `@require_GET`, por lo que cualquier otro método HTTP devuelve **HTTP 405 Method Not Allowed**.

Característica distintiva: **los datos se validan contra su JSON Schema antes de devolverse**. Si un documento almacenado se sale del contrato, la API responde con un **HTTP 500 explícito** que enumera los documentos problemáticos, en lugar de servir datos rotos.

| Endpoint | Descripción |
|---|---|
| `GET /api/` | Índice con el catálogo de las 8 colecciones, su esquema, su URL y su total de documentos. |
| `GET /api/<coleccion>/` | Listado completo de una colección, serializado conforme a su esquema. |
| `GET /api/<coleccion>/<id>/` | Un documento concreto, buscado por `ObjectId`. |
| `GET /api/esquemas/` | Los 9 JSON Schemas del proyecto (`base` + 8 colecciones). |
| `GET /api/esquemas/<nombre>` | Un JSON Schema en crudo, con `Content-Type: application/schema+json`. |

### 11.2 Formato de respuesta

Los documentos se serializan con `nucleo/serializadores.py`, que produce un diccionario plano donde:

- La clave primaria se renombra de `_id` a **`id`** y se expresa como texto hexadecimal de 24 caracteres.
- Las fechas `DateField` se expresan en ISO 8601 (`AAAA-MM-DD`).
- Las fechas `DateTimeField` se expresan en ISO 8601 con zona horaria (`AAAA-MM-DDTHH:MM:SS+00:00`).
- Los `float` se redondean a dos decimales.
- Los `None` se conservan como `null`.

### 11.3 Ejemplos

#### `GET /api/`

```json
{
  "proyecto": "Club de Motociclistas",
  "version": "1.0.0",
  "formato": "JSON Schema Draft 2020-12",
  "relaciones": "Sin relaciones: las referencias son ObjectId en texto plano.",
  "colecciones": [
    {
      "nombre": "motociclistas",
      "titulo": "Motociclistas",
      "esquema": "/api/esquemas/motociclista.schema.json",
      "total": 7,
      "url": "/api/motociclistas/"
    },
    {
      "nombre": "motos",
      "titulo": "Motos",
      "esquema": "/api/esquemas/moto.schema.json",
      "total": 7,
      "url": "/api/motos/"
    }
  ]
}
```

#### `GET /api/motociclistas/`

```json
{
  "coleccion": "motociclistas",
  "titulo": "Motociclistas",
  "total": 7,
  "datos": [
    {
      "id": "66a1b2c3d4e5f60718293a4b",
      "nombre": "Octavio",
      "apellido": "Velasco",
      "correo": "octavio.velasco@club-moto.co",
      "telefono": "+57 311 456 7821",
      "fechaNacimiento": "2005-04-20",
      "activo": true,
      "tipoLicencia": "A2",
      "fotoUrl": "https://picsum.photos/seed/socio-triumph/640/640"
    }
  ]
}
```

#### `GET /api/motos/`

```json
{
  "coleccion": "motos",
  "titulo": "Motos",
  "total": 7,
  "datos": [
    {
      "id": "66a1b2c3d4e5f60718293a4c",
      "placa": "OVL11",
      "marca": "Triumph",
      "modelo": "Tiger 1200 GT Explorer",
      "anio": 2024,
      "tipoMoto": "Adventure",
      "cilindrada": 1200,
      "color": "Verde Mate",
      "fotoUrl": "https://picsum.photos/seed/moto-triumph/800/600",
      "idMotociclista": "66a1b2c3d4e5f60718293a4b"
    }
  ]
}
```

#### `GET /api/motociclistas/<id>/`

```json
{
  "coleccion": "motociclistas",
  "datos": {
    "id": "66a1b2c3d4e5f60718293a4b",
    "nombre": "Octavio",
    "apellido": "Velasco",
    "correo": "octavio.velasco@club-moto.co",
    "telefono": "+57 311 456 7821",
    "fechaNacimiento": "2005-04-20",
    "activo": true,
    "tipoLicencia": "A2",
    "fotoUrl": "https://picsum.photos/seed/socio-triumph/640/640"
  }
}
```

### 11.4 Formato de error

#### Documento que no cumple el esquema → HTTP 500

```json
{
  "error": "La coleccion no cumple su JSON Schema.",
  "detalle": [
    {
      "id": "66a1b2c3d4e5f60718293a4b",
      "errores": [
        "raiz: 'correo' is not a 'email'"
      ]
    }
  ]
}
```

#### Colección inexistente → HTTP 404

`GET /api/inexistente/` lanza `Http404("Coleccion desconocida: inexistente")` y Django devuelve la página 404 estándar.

#### Documento inexistente → HTTP 404

`GET /api/motociclistas/no-existe/` lanza `Http404("Documento no encontrado")`.

#### Método HTTP no permitido → HTTP 405

Cualquier `POST`, `PUT`, `PATCH` o `DELETE` sobre los endpoints de la API es rechazado por el decorador `@require_GET`.

### 11.5 Consideraciones de seguridad de la API

> **Advertencia:** la API **no está protegida**. No requiere autenticación, token ni encabezado especial, y expone la totalidad de las colecciones, incluidos los correos y teléfonos de los socios. Antes de exponerla en una red pública debe añadirse al menos un mecanismo de control de acceso (por ejemplo, HTTP Basic con `django.http.HttpBasicAuth`, un token estático o una restricción de red en el proxy inverso). Este punto está recogido como tarea pendiente en §14.

---

## 12. Git y repositorio

### 12.1 Repositorio

| Elemento | Valor |
|---|---|
| URL | `https://github.com/growing-ov/club-motociclistas.git` |
| URL web | <https://github.com/growing-ov/club-motociclistas> |
| Rama principal | `main` |
| Remoto | `origin` |
| Organización/Usuario | `growing-ov` |

> **Nota de seguridad:** la URL del remoto configurada localmente puede contener un token de acceso personal incrustado. La URL **sin credenciales** que debe usarse en la documentación y en cualquier clone nuevo es `https://github.com/growing-ov/club-motociclistas.git`.

### 12.2 Historial de commits existente

| Commit | Mensaje |
|---|---|
| `d612818` | Club de Motociclistas: 3 apps Django (socios, flota, eventos) con CRUD, MongoDB via django-mongodb-backend |
| `85d94fe` | Club de Motociclistas: proyecto reorganizado con home/dashboard, plantilla unica, vistas de detalle y fotos por URL |

### 12.3 Flujo de trabajo recomendado

1. **Crear una rama de feature** desde `main`:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Hacer commits lógicos.** Un commit = un cambio con sentido. Se recomienda el formato del proyecto: prefijo `Club de Motociclistas: ` seguido de una descripción en minúsculas y sin acentos (consistente con los dos commits existentes).

   ```bash
   git add socios/views.py
   git commit -m "Club de Motociclistas: validacion de edad minima en alta de socio"
   ```

3. **Actualizar la rama** con los cambios de `main` antes de abrir la Pull Request:

   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Abrir la Pull Request** hacia `main`, describing qué cambia, por qué y cómo se verifica.

5. **Revisión y fusión.** Tras la aprobación, integrar en `main` y eliminar la rama:

   ```bash
   git checkout main
   git merge --ff-only feature/nueva-funcionalidad
   git push origin main
   git branch -d feature/nueva-funcionalidad
   ```

### 12.4 Estructura de commits de esta entrega

Los cambios de esta entrega están organizados en commits independientes y atómicos, cada uno con un alcance bien delimitado:

| # | Alcance | Archivos principales | Descripción |
|---|---|---|---|
| 1 | Núcleo de la aplicación | `club_motociclistas/api.py`, `campos.py`, `referencias.py`, `settings.py`, `urls.py`, `nucleo/**`, `schemas/**` | API JSON de solo lectura, resolución centralizada de referencias, campos de formulario con referencias sin relación, app `nucleo` con esquemas/serializadores/comandos y los 9 JSON Schemas. |
| 2 | Ajustes de dominio y validaciones | `socios/**`, `flota/**`, `eventos/**` | Modelos, formularios, vistas y plantillas de las tres apps de dominio, con las reglas de negocio y las vistas de detalle. |
| 3 | Interfaz y estáticos | `templates/base.html`, `templates/dashboard.html`, `templates/includes/formulario.html`, `static/**` | Plantilla base única, panel general, render común de formularios, hoja de estilos y JavaScript de la aplicación. |
| 4 | Empaquetado y despliegue | `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `docker-compose.prod.yml`, `entrypoint.sh` | Imagen multi-etapa sin privilegios, orquestación de desarrollo y producción, punto de entrada con espera a MongoDB y healthchecks. |
| 5 | Documentación | `docs/DOCUMENTACION.md`, `docs/capturas/**` | Documentación técnica completa y capturas de pantalla de la aplicación en ejecución. |

### 12.5 `.gitignore` y archivos que NO se versionan

El `.gitignore` del proyecto excluye:

```text
# Byte-compiled
__pycache__/
*.py[cod]
*$py.class

# Virtualenv
venv/
env/
.venv/

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Env
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

**No deben(versionarse nunca):**

| Patrón | Motivo |
|---|---|
| `.env` | Contiene `SECRET_KEY` y las credenciales de MongoDB. Solo se versiona `.env.example`. |
| `venv/`, `.env/`, `.venv/` | Entornos virtuales: específicos de cada máquina. |
| `__pycache__/`, `*.pyc` | Artefactos de compilación de Python. |
| `staticfiles/` | Salida de `collectstatic`; se regenera en cada compilación. |
| `media/` | Archivos subidos por los usuarios (cuando exista carga de archivos). |
| `db.sqlite3` | Residuo de un proyecto SQLite; el proyecto usa MongoDB. |
| `*.log` | Registros de ejecución. |
| `.vscode/`, `.idea/` | Configuración del editor. |
| `docs/capturas/*.png` de formatos pesados | `.dockerignore` excluye `docs/capturas/` para no inflar el contexto de build. |

---

## 13. Tabla de agentes opencode y tareas asignadas

| Agente | Modelo | Tarea asignada en esta entrega |
|---|---|---|
| orquesta (orquestador) | MiniMax-M3 | Orquestación: clasifica cada tarea, enruta a los subagentes correctos y consolida la entrega final |
| grok | Grok | Documentación técnica completa (este archivo): arquitectura, modelo de datos, reglas de negocio, despliegue y glosario |
| minimax | MiniMax-M3 | Verificación funcional: arranque de MongoDB, generación de .env, check/migrate/seed, servidor local y pruebas HTTP de todas las rutas |
| minimax | MiniMax-M3 | Dockerfile, .dockerignore, docker-compose.yml y docker-compose.prod.yml (imagen multi-stage, whitenoise, healthcheck y servicio MongoDB) |
| minimax | MiniMax-M3 | Capturas de pantalla de la aplicación en ejecución (Edge headless) guardadas en docs/capturas/ |
| minimax | MiniMax-M3 | Generación del DOCX (python-docx) con la documentación, las capturas, el repo de git y la tabla de agentes |
| minimax | MiniMax-M3 | Commits lógicos en git y push al repositorio remoto |
| explore | (reservado) | Disponible para explorar el código y responder preguntas sobre el proyecto |
| general | (reservado) | Disponible para tareas generales y de investigación |

---

## 14. Calidad, pruebas y mantenimiento

### 14.1 Cómo se valida el proyecto hoy

| Mecanismo | Comando / acción | Qué comprueba |
|---|---|---|
| Comprobación de configuración | `python manage.py check` | Que los módulos, la configuración y las apps son coherentes. |
| Comprobación de despliegue | `python manage.py check --deploy` | Advertencias de seguridad de Django (DEBUG, cookies, SSL, `SECRET_KEY`). |
| Validación de esquemas | `python manage.py validar_esquemas` | Que **todos** los documentos almacenados en MongoDB cumplen su JSON Schema. Devuelve código de salida 1 si hay inconsistencias. |
| Datos de prueba | `python manage.py seed_data` | Genera un conjunto coherente y referencialmente consistente de 7 socios, 28 documentos, 7 motos, 17 mantenimientos, 2 accidentes, 5 rodadas, 22 inscripciones y 5 fotos. |
| Exportación validada | `python manage.py exportar_datos` | Vuelca las colecciones a JSON validado: sirve como respaldo y como smoke test del contrato de datos. |
| Verificación HTTP | Recorrido manual de las rutas | El agente de verificación funcional recorre todas las rutas de la aplicación y comprueba los códigos de respuesta. |

### 14.2 Cobertura funcional actual

- **7 modelos** con **35 vistas** (5 por modelo: lista, detalle, crear, editar, eliminar).
- **4 plantillas por modelo** = 28 plantillas de dominio, más `base.html`, `dashboard.html` e `includes/formulario.html`.
- **8 colecciones** expuestas por la API, cada una con su JSON Schema.
- **3 comandos de gestión** propios (`seed_data`, `validar_esquemas`, `exportar_datos`).
- **26 reglas de negocio** documentadas y verificadas en el código (§6.1).

### 14.3 Qué falta por hacer

| Área | Situación actual | Recomendación |
|---|---|---|
| **Pruebas automatizadas** | No existe el directorio `tests/` ni pruebas unitarias o de integración. | Crear `tests/` con `pytest` + `pytest-django` (o el runner nativo). Prioridad alta: probar las 26 reglas de negocio con casos de límite (18 años exactos, 3 motos, cupo lleno, fecha futura) y las vistas de borrado bloqueado. |
| **Integración continua (CI)** | No hay workflows de GitHub Actions. | Añadir `.github/workflows/ci.yml` que ejecute `pip install -r requirements.txt`, `python manage.py check` y `python manage.py test` en cada PR. |
| **Autenticación y autorización** | No implementado; la aplicación y la API son abiertas. | Incorporar `django.contrib.auth` y un middleware de sesión. En la API, añadir al menos HTTP Basic o un token. Prioridad **crítica** antes de exponer el servicio en Internet. |
| **Subida real de archivos** | Las fotos y los documentos se referencian por URL; no hay carga binaria. | Implementar `MEDIA_ROOT` + almacenamiento (local o S3) y cambiar los `URLField` por `FileField`/`ImageField` con `ImageField` para validar el formato. |
| **Paginación** | Los listados cargan la colección completa en memoria. | Implementar `Paginator` de Django en las vistas `lista_*`. Relevante si el club crece o si el tráfico de la API crece. |
| **Búsqueda en servidor** | El filtrado es del lado del cliente (JavaScript). | Añadir un parámetro `?q=` con `icontains` sobre los campos clave. |
| **Índices en MongoDB** | El repositorio no incluye migraciones; los índices únicos (`correo`, `placa`) no se crean en el servidor. | Generar y versionar `migrations/` (`makemigrations socios flota eventos`) y aplicarlas en el despliegue, o alinear los nombres de colección de `crear_colecciones.txt` con los del ORM (§5.1). |
| **Gestión de secretos** | La URL del remoto Git puede contener un token incrustado. | Rotar el token, configurar el remoto con la URL limpia y usar un gestor de secretos o un gestor de credenciales de Git en producción. |
| **Observabilidad** | No hay registro estructurado ni métricas. | Añadir `django-environ`/logging a archivo, y considerar `django-prometheus` o un endpoint de métricas. |
| **Respaldo y recuperación** | El comando `exportar_datos` genera respaldos en JSON, pero no hay política automática. | Programar `mongodump` diario y documentar la restauración (§10.1). |
| **Paginación y filtros en la API** | La API devuelve colecciones completas sin parámetros. | Añadir `?page=`, `?limit=` y `?campo=valor` manteniendo la validación por esquema. |
| **Verificación de la imagen Docker** | No se pudo construir en esta máquina por falta de engine Linux (§9.8). | Ejecutar `docker build` y `docker compose up --build` en un entorno con Docker operativo, o añadir la construcción de la imagen al pipeline de CI. |
| **Localización** | `LANGUAGE_CODE = "es-mx"` está configurado, pero no hay archivos de traducción. | Añadir `locale/` con `makemessages` / `compilemessages` si se requieren las cadenas traducidas del propio Django. |

### 14.4 Mantenimiento rutinario

| Frecuencia | Tarea |
|---|---|
| Semanal | `python manage.py validar_esquemas` para detectar documentos corruptos. |
| Mensual | `python manage.py check --deploy`; revisar dependencias con `pip list --outdated`. |
| Trimestral | Restaurar un respaldo y verificar la integridad; revisar los índices de MongoDB; revisar el tamaño de la base. |
| Por versión | Actualizar Django, `django-mongodb-backend` y `pymongo` siguiendo la matriz de compatibilidad del backend; regenerar el `collectstatic`; reconstruir la imagen. |

---

## 15. Glosario de términos

| Término | Definición |
|---|---|
| **Socio** | Miembro registrado del club. Se modela como `socios.Motociclista`. Cada socio puede registrar como máximo 3 motos y debe ser mayor de 18 años. |
| **Motociclista** | Sinónimo de socio. Nombre de la clase de modelo (`socios.Motociclista`) y nombre de la colección en la API (`motociclistas`). |
| **Documento de socio** | Documento legal o administrativo asociado a un socio (`socios.DocumentoSocio`): cédula, licencia de conducción, SOAT, tecnomecánica. Se identifica por tipo, número, fecha de emisión y fecha de vencimiento. |
| **Documento vigente** | Documento cuya `fechaVencimiento` es igual o posterior a la fecha actual. Los documentos vigentes **no se pueden eliminar** desde la interfaz. |
| **Flota** | Conjunto de motos registradas en el club, con su historial de mantenimiento y sus accidentes (`app flota`). |
| **Moto** | Unidad que pertenece a un socio (`flota.Moto`), identificada de forma única por su `placa`. |
| **Mantenimiento** | Intervención técnica registrada sobre una moto (`flota.Mantenimiento`): tipo, descripción, costo, kilometraje y marca de "realizado". |
| **Accidente** | Siniestro registrado sobre una moto (`flota.Accidente`), clasificado por gravedad (`leve`, `moderado`, `grave`) y con un costo estimado de reparación. |
| **Gravedad** | Nivel de clasificación de un accidente. Valor único de tres opciones: `leve` (Leve), `moderado` (Moderado), `grave` (Grave). |
| **Rodada** | Salida grupal programada (`eventos.Rodada`): fecha de salida, punto de encuentro, destino, estado, cupo máximo, distancia y costo. |
| **Punto de encuentro** | Lugar donde se reúne el grupo antes de partir en una rodada. |
| **Cupo** | Número máximo de participantes de una rodada (`cupoMaximo`). Rango permitido: de 2 a 80 personas. |
| **Cupo disponible** | Diferencia entre el cupo máximo y el número de inscripciones registradas. Se muestra en la ficha de la rodada y nunca es negativo (`max(cupoMaximo - len(inscripciones), 0)`). |
| **Inscripción** | Registro de la participación de un socio en una rodada (`eventos.Inscripcion`). Lleva fecha de inscripción, marca de asistencia y observaciones. |
| **Asistencia** | Indicador booleano (`asistio`) que registra si el socio asistió efectivamente a la rodada. |
| **Galería** | Conjunto de fotografías asociadas a una rodada (`eventos.Galeria`), con título, descripción, URL de la imagen y fecha de subida. |
| **Estado de rodada** | Situación de la salida: `programada` (Programada), `en_curso` (En curso) o `finalizada` (Finalizada). |
| **Dashboard / panel general** | Página de inicio (`/`) que muestra los 8 contadores del club y accesos rápidos a la API. |
| **API JSON** | Interfaz de solo lectura en `/api/` que expone las 8 colecciones y valida cada documento contra su JSON Schema antes de servirlo. |
| **JSON Schema** | Documento JSON (Draft 2020-12) que define el contrato de datos de una colección. En este proyecto hay 9: `base` (definiciones comunes) y 8 de colección. |
| **Esquema base** | `schemas/base.schema.json`, que define los tipos reutilizados (`objectId`, `fecha`, `fechaHora`, `url`, `email`, `telefono`, `dinero`, `texto`) mediante `$defs`. |
| **Referencia sin relación** | Patrón de diseño del proyecto: en lugar de `ForeignKey`, el campo `CharField` de 24 caracteres guarda el `ObjectId` del documento apuntado, indexado para búsqueda rápida. |
| **ObjectId** | Identificador nativo de MongoDB: 24 caracteres hexadecimales. Es la clave primaria de todos los modelos. |
| **Colección** | Equivalente de una tabla en MongoDB. Las 8 colecciones reales se llaman `socios_motociclista`, `socios_documentosocio`, `flota_moto`, `flota_mantenimiento`, `flota_accidente`, `eventos_rodada`, `eventos_inscripcion` y `eventos_galeria`. |
| **CRM ligero** | Descripción informal del alcance del proyecto: gestión de socios, flota y eventos sin dejar de ser un CRUD trazable. |
| **FBV (Function Based View)** | Vista de Django implementada como función Python. Todo el CRUD del proyecto usa FBV; no hay vistas de clase. |
| **ModelForm** | Formulario de Django generado automáticamente a partir de un modelo, con sus validadores de campo. |
| **`add_error`** | Método de Django que adjunta un error a un campo concreto del formulario; es el mecanismo con el que las reglas de negocio se muestran al usuario. |
| **`messages`** | Framework de mensajes de Django (`django.contrib.messages`), usado para los avisos de éxito y error tras cada operación. |
| **Whitenoise** | Middleware y backend de almacenamiento que sirve los archivos estáticos desde el propio proceso Python, con compresión y manifiesto. |
| **Gunicorn** | Servidor WSGI de producción para Python. |
| **Collectstatic** | Comando de Django que recopila los archivos estáticos en `STATIC_ROOT`; obligatorio con `CompressedManifestStaticFilesStorage`. |
| **Healthcheck** | Prueba de salud que ejecutan Docker y los orquestadores para saber si un contenedor está operativo. |
| **Entrada multi-etapa (multi-stage build)** | Técnica de Docker que construye la imagen en etapas intermedias (por ejemplo, instalar dependencias) para que la imagen final contenga solo lo necesario. |
| **Usuario no-root** | Usuario de sistema sin privilegios con el que corre el proceso de la aplicación dentro del contenedor (`appuser`, uid 10001). |
| **`entrypoint.sh`** | Script ejecutado al inicio del contenedor: espera a MongoDB, genera los estáticos, aplica migraciones y lanza el comando final. |
| **Variable de entorno** | Par clave-valor leída por `settings.py` desde el archivo `.env` o desde el entorno del sistema (con prioridad sobre el archivo). |
| **`SECRET_KEY`** | Clave criptográfica de Django. Firma cookies de sesión y CSRF; en producción debe ser larga, aleatoria y secreta. |
| **`DEBUG`** | Bandera de depuración. En producción debe ser `False`; con `DEBUG=True` Django muestra trazas completas ante errores. |
| **`ALLOWED_HOSTS`** | Lista de nombres de host aceptados en las cabeceras `Host`. Con `DEBUG=False` debe configurarse explícitamente. |
| **Locale / zona horaria** | Configuración regional del proyecto: `LANGUAGE_CODE = "es-mx"` y `TIME_ZONE = "America/Mexico_City"`. |
| **N+1** | Antipatrón de consultas sucesivas por cada elemento de una lista. El proyecto lo evita con `referencias.mapa_por_id()`, que resuelve todos los identificadores en una sola consulta. |

---

## 16. Anexo: rutas de archivos clave del proyecto

### 16.1 Configuración del proyecto

| Ruta | Contenido |
|---|---|
| `manage.py` | Utilidad de línea de comandos de Django. |
| `club_motociclistas/__init__.py` | Paquete de configuración. |
| `club_motociclistas/settings.py` | Lectura del `.env`, apps instaladas, middleware, plantillas, base de datos MongoDB, estáticos, locale y zona horaria. |
| `club_motociclistas/urls.py` | URLconf raíz: dashboard, `include()` de las tres apps, API y redirección genérica a `/`. |
| `club_motociclistas/views.py` | Vista `dashboard` con los 8 contadores. |
| `club_motociclistas/api.py` | API JSON de solo lectura (5 endpoints). |
| `club_motociclistas/campos.py` | `ReferenciaModelChoiceField` y `campo_referencia()` para los campos de referencia sin relación. |
| `club_motociclistas/referencias.py` | Resolución de referencias: `por_id`, `mapa_por_id`, `ids_de`, `nombre_de`, `contar`, `existe_referencia` y los accesores por entidad. |
| `club_motociclistas/wsgi.py` | Punto de entrada WSGI (destino de Gunicorn). |
| `club_motociclistas/asgi.py` | Punto de entrada ASGI. |

### 16.2 Núcleo de dominio

| Ruta | Contenido |
|---|---|
| `socios/models.py` | `Motociclista`, `DocumentoSocio`. |
| `socios/forms.py` | `MotociclistaForm`, `DocumentoSocioForm`. |
| `socios/views.py` | 10 vistas + `validar_motociclista`, `validar_documento`. |
| `socios/urls.py` | 10 rutas de socios y documentos. |
| `flota/models.py` | `Moto`, `Mantenimiento`, `Accidente`, constante `GRAVEDADES`. |
| `flota/forms.py` | `MotoForm`, `MantenimientoForm`, `AccidenteForm`. |
| `flota/views.py` | 15 vistas + `validar_moto`, `validar_mantenimiento`, `validar_accidente`. |
| `flota/urls.py` | 15 rutas de motos, mantenimientos y accidentes. |
| `eventos/models.py` | `Rodada`, `Inscripcion`, `Galeria`, constante `ESTADOS`. |
| `eventos/forms.py` | `RodadaForm`, `InscripcionForm`, `GaleriaForm`. |
| `eventos/views.py` | 15 vistas + `validar_rodada`, `validar_inscripcion`. |
| `eventos/urls.py` | 15 rutas de rodadas, inscripciones y galería. |

### 16.3 Núcleo auxiliar (`nucleo`)

| Ruta | Contenido |
|---|---|
| `nucleo/apps.py` | `NucleoConfig` con `default_auto_field` del backend de MongoDB. |
| `nucleo/esquemas.py` | `COLECCIONES`, `validar()`, `normalizar()`, carga de esquemas y `Registry` de referencias. |
| `nucleo/serializadores.py` | `a_esquema()`, `documentos_de()`, `documento_de()`, `modelo_de()`. |
| `nucleo/templatetags/club.py` | Filtros `get`, `vigente`, `iniciales`, `moneda`, `estado_clase`, `gravedad_clase`. |
| `nucleo/management/commands/seed_data.py` | Command `seed_data` con opciones `--flush` y `--sin-fotos`. |
| `nucleo/management/commands/validar_esquemas.py` | Command `validar_esquemas` con opciones `--coleccion`, `--detalle`, `--limite`. |
| `nucleo/management/commands/exportar_datos.py` | Command `exportar_datos` con opciones `--salida`, `--coleccion`, `--sin-validar`. |

### 16.4 Esquemas de datos

| Ruta | Contenido |
|---|---|
| `schemas/base.schema.json` | Definiciones comunes (`$defs`). |
| `schemas/motociclista.schema.json` | Contrato de la colección `motociclistas`. |
| `schemas/documento_socio.schema.json` | Contrato de la colección `documentos`. |
| `schemas/moto.schema.json` | Contrato de la colección `motos`. |
| `schemas/mantenimiento.schema.json` | Contrato de la colección `mantenimientos`. |
| `schemas/accidente.schema.json` | Contrato de la colección `accidentes`. |
| `schemas/rodada.schema.json` | Contrato de la colección `rodadas`. |
| `schemas/inscripcion.schema.json` | Contrato de la colección `inscripciones`. |
| `schemas/galeria.schema.json` | Contrato de la colección `galeria`. |
| `crear_colecciones.txt` | Script `mongosh` con los validadores `$jsonSchema` del lado del servidor. |

### 16.5 Plantillas y estáticos

| Ruta | Contenido |
|---|---|
| `templates/base.html` | Layout común: menú lateral con `{% url %}`, migas, mensajes, `{% block content %}`, pie. |
| `templates/dashboard.html` | Panel general con los 8 contadores y accesos rápidos. |
| `templates/includes/formulario.html` | Render común de los formularios `ModelForm`. |
| `socios/templates/socios/*.html` | 8 plantillas (2 modelos × 4). |
| `flota/templates/flota/*.html` | 12 plantillas (3 modelos × 4). |
| `eventos/templates/eventos/*.html` | 12 plantillas (3 modelos × 4). |
| `static/css/estilos.css` | Hoja de estilos completa del proyecto. |
| `static/js/app.js` | JavaScript de la interfaz (menú, tema, filtrado en cliente). |
| `static/img/favicon.svg` | Icono del sitio. |

### 16.6 Empaquetado, despliegue y configuración de entorno

| Ruta | Contenido |
|---|---|
| `Dockerfile` | Imagen multi-etapa: `builder` (dependencias + `collectstatic`) y `final` (`appuser`, `EXPOSE 8000`, `HEALTHCHECK`). |
| `.dockerignore` | Exclusiones del contexto de build. |
| `docker-compose.yml` | Servicios `web` + `mongo` para desarrollo. |
| `docker-compose.prod.yml` | Servicios `web` + `mongo` para producción. |
| `entrypoint.sh` | Espera a Mongo → `collectstatic` → `migrate` → `exec "$@"`. |
| `.env.example` | Plantilla de variables de entorno. |
| `.gitignore` | Exclusiones de Git. |
| `requirements.txt` | Dependencias de Python. |
| `README.md` | Guía rápida de instalación y uso. |
| `descripcion.txt` | Descripción funcional y reglas de negocio en texto plano. |
| `docs/DOCUMENTACION.md` | Este documento. |
| `docs/capturas/` | Capturas de pantalla de la aplicación en ejecución. |

---

*Documento generado el 20 de noviembre de 2026. Club de Motociclistas v1.0.0 — Django 6.1 + MongoDB.*
