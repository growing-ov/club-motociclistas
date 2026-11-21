"""Dibuja los diagramas tecnicos del proyecto con su contenido real.

Uso:  python tools/generar_diagramas.py
Genera docs/diagramas/*.png: cada caja lleva el texto exacto del proyecto
(archivos, funciones, rutas y reglas), de modo que la imagen explica el
contenido en lugar de sustituirlo por iconos genericos.
"""

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "diagramas"

UNIDAD = 0.13          # pulgadas por unidad de lienzo
DPI = 120
FONDO = "#f8fafc"
TINTA = "#1e293b"
TINTA_SUAVE = "#64748b"
AZUL = "#0284c7"
AZUL_OSCURO = "#0b1220"
NARANJA = "#ea580c"
VERDE = "#15803d"
MONGO = "#0f7b3f"
ROJO = "#dc2626"
VIOLETA = "#7c3aed"
CODIGO = "#b31e3c"
FONDO_CODIGO = "#f1f5f9"


class Lienzo:
    """Lienzo en coordenadas unidades (y crece hacia abajo)."""

    def __init__(self, ancho=100, alto=70, titulo=None):
        self.ancho = ancho
        self.alto = alto
        self.figura = plt.figure(figsize=(ancho * UNIDAD, alto * UNIDAD), dpi=DPI)
        self.ax = self.figura.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, ancho)
        self.ax.set_ylim(alto, 0)
        self.ax.axis("off")
        self.ax.add_patch(Rectangle((0, 0), ancho, alto, color=FONDO, zorder=0))
        if titulo:
            self.ax.text(self.ancho / 2, 2.4, titulo, fontsize=13, color=AZUL_OSCURO,
                         weight="bold", ha="center", va="center", zorder=3)

    # ------------------------------------------------------------- primitivas
    def ancho_caracter(self, tamano):
        return (0.602 * tamano / 72.0) / UNIDAD

    def texto(self, x, y, contenido, tamano=8.3, color=TINTA, peso="normal",
              familia="monospace", alineacion="left", fondo=None):
        if fondo:
            self.ax.text(x, y, contenido, fontsize=tamano, color=color, weight=peso,
                         family=familia, ha=alineacion, va="center", zorder=3,
                         bbox=dict(boxstyle="round,pad=0.25", fc=fondo, ec="none"))
            return
        self.ax.text(x, y, contenido, fontsize=tamano, color=color, weight=peso,
                     family=familia, ha=alineacion, va="center", zorder=3)

    def texto_segmentado(self, x, y, contenido, tamano=8.3, color=TINTA):
        """Dibuja **negrita** y `codigo` dentro de una misma linea."""
        patron = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")
        cursor = x
        for trozo in patron.split(contenido):
            if not trozo:
                continue
            if trozo.startswith("**") and trozo.endswith("**"):
                self.texto(cursor, y, trozo[2:-2], tamano, AZUL_OSCURO, "bold")
                cursor += self.ancho_caracter(tamano) * len(trozo[2:-2])
            elif trozo.startswith("`") and trozo.endswith("`"):
                self.texto(cursor, y, trozo[1:-1], tamano, CODIGO)
                cursor += self.ancho_caracter(tamano) * len(trozo[1:-1])
            else:
                self.texto(cursor, y, trozo, tamano, color)
                cursor += self.ancho_caracter(tamano) * len(trozo)

    def caja(self, x, y, ancho, titulo, lineas=(), color=AZUL, fondo="#ffffff",
             alto=None, tamano_titulo=9.6, tamano_linea=8.3, subtitulo=None):
        alto = alto or (5.0 + len(lineas) * 1.5 + (1.6 if subtitulo else 0))
        self.ax.add_patch(FancyBboxPatch(
            (x, y), ancho, alto,
            boxstyle="round,pad=0.15,rounding_size=0.9",
            linewidth=1.5, edgecolor=color, facecolor=fondo, zorder=2,
        ))
        self.ax.add_patch(Rectangle((x, y), 0.55, alto, color=color, zorder=3))
        self.texto(x + 1.3, y + 2.2, titulo, tamano_titulo, color, "bold", "sans-serif")
        fila = y + 4.3
        if subtitulo:
            self.texto(x + 1.3, fila, subtitulo, tamano_linea - 0.3, TINTA_SUAVE,
                       familia="sans-serif")
            fila += 1.6
        for linea in lineas:
            self.texto_segmentado(x + 1.3, fila, linea, tamano_linea)
            fila += 1.5
        return y + alto

    def etiqueta(self, x, y, texto, tamano=7.6, color=TINTA_SUAVE, fondo="#ffffff"):
        self.texto(x, y, texto, tamano, color, "normal", "monospace",
                   "center", fondo)

    def flecha(self, x1, y1, x2, y2, texto=None, color=TINTA_SUAVE, curva=0.0,
               estilo="-|>", ancho_flecha=1.6):
        self.ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle=estilo, color=color, lw=ancho_flecha,
                            shrinkA=0, shrinkB=0,
                            connectionstyle=f"arc3,rad={curva}"),
            zorder=1,
        )
        if texto:
            medio_x = (x1 + x2) / 2
            medio_y = (y1 + y2) / 2
            self.etiqueta(medio_x, medio_y - 0.2, texto, 7.2, TINTA_SUAVE, "#f8fafc")

    def guardar(self, nombre):
        SALIDA.mkdir(parents=True, exist_ok=True)
        destino = SALIDA / nombre
        self.figura.savefig(destino, facecolor=FONDO, dpi=DPI)
        plt.close(self.figura)
        print(f"{nombre}: ok")


# ------------------------------------------------------------------ diagramas
def arquitectura_capas():
    lienzo = Lienzo(100, 84, "Arquitectura por capas del Club de Motociclistas")
    ancho = 94
    x = 3
    capas = [
        ("1 · CAPA DE PRESENTACIÓN", AZUL, [
            "`templates/base.html` · `templates/dashboard.html` · `templates/includes/formulario.html`",
            "`socios|flota|eventos` → `templates/<app>/<modelo>_{list,form,detail,confirm_delete}.html`",
            "`static/css/estilos.css` · `static/js/app.js`  (tema oscuro, menú lateral, buscador)",
        ]),
        ("2 · CAPA DE VISTAS (funciones, FBV)", AZUL, [
            "`club_motociclistas/views.py` → dashboard   ·   `api.py` → índice, colección, documento, esquemas",
            "`socios/views.py` · `flota/views.py` · `eventos/views.py`",
            "patrón: `ModelForm(request.POST or None)` → `validar_<modelo>()` → `form.save()` → `messages` → `redirect()`",
        ]),
        ("3 · CAPA DE FORMULARIOS (ModelForm)", VIOLETA, [
            "`socios/forms.py` · `flota/forms.py` · `eventos/forms.py`  → reglas de negocio en `clean()`",
            "`club_motociclistas/campos.py` → `campo_referencia()` / `ReferenciaModelChoiceField`",
        ]),
        ("4 · CAPA DE MODELOS (dominio)", NARANJA, [
            "`socios/models.py` → Motociclista, DocumentoSocio      `flota/models.py` → Moto, Mantenimiento, Accidente",
            "`eventos/models.py` → Rodada, Inscripcion, Galeria",
            "**sin ForeignKey**: la referencia se guarda como `ObjectId` en texto (`CharField` indexado)",
        ]),
        ("5 · CAPA DE INFRAESTRUCTURA (nucleo + ORM)", VERDE, [
            "`nucleo/esquemas.py` (JSON Schema) · `nucleo/serializadores.py` · `nucleo/templatetags/club.py`",
            "`nucleo/management/commands` → `seed_data` · `validar_esquemas` · `exportar_datos`",
            "`club_motociclistas/referencias.py` (resuelve referencias) · `settings.py` (lee `.env`, configura Atlas)",
            "ORM: `django-mongodb-backend` → `pymongo` → MongoDB",
        ]),
    ]
    y = 5
    fin = y
    for indice, (titulo, color, lineas) in enumerate(capas):
        fin = lienzo.caja(x, y, ancho, titulo, lineas, color=color)
        if indice < len(capas) - 1:
            etiqueta = [
                "render(request, …) · {% url %} · {% block content %}",
                "form.is_valid() · cleaned_data",
                "save() → INSERT en la colección",
                "find() / update() / delete()",
            ][indice]
            lienzo.flecha(x + ancho / 2, fin, x + ancho / 2, fin + 2.6, etiqueta, AZUL)
            y = fin + 2.6
    lienzo.caja(x, fin + 3.0, ancho, "6 · DATOS · MongoDB Atlas", [
        "`socios_motociclista` · `socios_documentosocio` · `flota_moto` · `flota_mantenimiento`",
        "`flota_accidente` · `eventos_rodada` · `eventos_inscripcion` · `eventos_galeria`",
        "conexión TLS con la URI de `MONGO_URI`; base `MONGO_DB=club_motociclistas`",
    ], color=MONGO, fondo="#f0fdf4")
    lienzo.guardar("01-arquitectura-capas.png")


def flujo_peticion():
    lienzo = Lienzo(100, 80, "Flujo de una petición: crear una moto (POST /flota/motos/crear/)")
    ancho = 88
    x = 6
    pasos = [
        ("NAVEGADOR", AZUL, [
            "POST /flota/motos/crear/   (datos del formulario + token CSRF)",
        ]),
        ("1 · MIDDLEWARE", VIOLETA, [
            "SecurityMiddleware → WhiteNoiseMiddleware → CommonMiddleware",
            "→ CsrfViewMiddleware → MessageMiddleware",
        ]),
        ("2 · RESOLUCIÓN DE URL", AZUL, [
            "ROOT_URLCONF = club_motociclistas.urls",
            "→ path(\"flota/\", include(\"flota.urls\"))",
            "→ path(\"motos/crear/\", views.crear_moto, name=\"moto_create\")",
        ]),
        ("3 · VISTA  (flota/views.py::crear_moto)", NARANJA, [
            "form = MotoForm(request.POST or None)",
            "if request.method == \"POST\" and form.is_valid():",
            "    error = validar_moto(form)          # reglas de negocio",
            "    if error is None:",
            "        form.save()                     # INSERT en la colección Mongo",
            "        messages.success(request, \"Moto registrada correctamente.\")",
            "        return redirect(\"moto_list\")",
            "    form.add_error(*error)              # (campo, mensaje)",
            "return render(request, \"flota/moto_form.html\", {\"form\": form})",
        ]),
        ("4 · ORM", VERDE, [
            "django-mongodb-backend → pymongo → MongoDB (Atlas)",
        ]),
    ]
    y = 5
    for indice, (titulo, color, lineas) in enumerate(pasos):
        fin = lienzo.caja(x, y, ancho, titulo, lineas, color=color)
        if indice < len(pasos) - 1:
            lienzo.flecha(x + ancho / 2, fin, x + ancho / 2, fin + 2.4, None, TINTA_SUAVE)
            y = fin + 2.4
    fin = lienzo.caja(x, y, ancho, "5 · RESPUESTA", [], color=AZUL_OSCURO, alto=4.0)
    y = fin + 1.6
    lienzo.caja(x, y, 42, "ÉXITO · 302", [
        "→ /flota/motos/  (listado)",
        "mensaje de éxito en la cookie",
    ], color=VERDE, fondo="#f0fdf4")
    lienzo.caja(x + 46, y, 42, "ERROR DE NEGOCIO · 200", [
        "formulario con el error bajo el campo",
        "`form.add_error(*error)`",
    ], color=ROJO, fondo="#fef2f2")
    lienzo.flecha(x + ancho / 2, fin, x + ancho / 2, y, None, TINTA_SUAVE)
    lienzo.guardar("02-flujo-peticion.png")


def arquitectura_docker():
    lienzo = Lienzo(100, 70, "Anatomía del contenedor: build multi-etapa, ejecución y Atlas")
    fin1 = lienzo.caja(3, 6, 30, "ETAPA 1 · builder", [
        "FROM python:3.12-slim AS builder",
        "python -m venv /opt/venv",
        "pip install -r requirements.txt",
        "COPY . /app",
        "collectstatic (SECRET_KEY ficticia)",
    ], color=VIOLETA)
    fin2 = lienzo.caja(36, 6, 30, "ETAPA 2 · final", [
        "COPY --from=builder /opt/venv /opt/venv",
        "COPY --from=builder /app /app",
        "USER appuser (uid 10001, nologin)",
        "ENTRYPOINT /app/entrypoint.sh",
        "CMD gunicorn --bind 0.0.0.0:8000",
    ], color=AZUL)
    fin3 = lienzo.caja(69, 6, 28, "SERVICIO DE DATOS", [
        "MongoDB Atlas (externo)",
        "MONGO_URI (mongodb+srv://…)",
        "MONGO_DB=club_motociclistas",
        "TLS · base en el proyecto",
    ], color=MONGO, fondo="#f0fdf4")
    lienzo.flecha(33.5, 20, 36, 20, "COPY", AZUL)
    lienzo.flecha(66.5, 20, 69, 20, "pymongo / TLS", VERDE)

    lienzo.caja(3, 34, 60, "DENTRO DEL CONTENEDOR · entrypoint.sh", [
        "1. espera a MongoDB (ping con pymongo, hasta ESPERA_MONGO=60 s)",
        "2. python manage.py collectstatic --noinput  (manifiesto de estáticos)",
        "3. python manage.py migrate --noinput        (no-op en MongoDB)",
        "4. exec \"$@\"  →  gunicorn club_motociclistas.wsgi:application",
    ], color=AZUL)
    lienzo.caja(67, 34, 30, "ESTÁTICOS Y SALUD", [
        "whitenoise: estáticos comprimidos",
        "CompressedManifestStaticFilesStorage",
        "HEALTHCHECK /api/esquemas/ (200)",
        "volumen media_data → /app/media",
    ], color=NARANJA)
    lienzo.flecha(50, 30, 33, 34, None, TINTA_SUAVE)
    lienzo.flecha(83, 30, 83, 34, None, TINTA_SUAVE)
    lienzo.texto(50, 64, "El contenedor no lleva código de Django: solo /opt/venv + /app + staticfiles",
                 8.3, TINTA_SUAVE, familia="sans-serif")
    lienzo.guardar("03-arquitectura-docker.png")


def modelo_datos():
    lienzo = Lienzo(100, 86, "Modelo de datos: ocho colecciones y sus referencias")
    cajas = {
        "socio": (2, 5, 30, "socios_motociclista", [
            "PK  _id (ObjectId)",
            "nombre · apellido",
            "correo (único)",
            "telefono · fechaNacimiento",
            "activo · tipoLicencia · fotoUrl",
        ], AZUL),
        "documento": (2, 33, 30, "socios_documentosocio", [
            "PK  _id",
            "nombreDocumento · numeroDocumento",
            "fechaEmision · fechaVencimiento",
            "archivoUrl",
            "→ idMotociclista",
        ], AZUL),
        "moto": (35, 5, 30, "flota_moto", [
            "PK  _id",
            "placa (única) · marca · modelo",
            "anio · tipoMoto · cilindrada",
            "color · fotoUrl",
            "→ idMotociclista",
        ], NARANJA),
        "mantenimiento": (35, 33, 30, "flota_mantenimiento", [
            "PK  _id",
            "fecha · tipo · descripcion",
            "costo · kilometraje",
            "realizado",
            "→ idMoto",
        ], NARANJA),
        "accidente": (35, 61, 30, "flota_accidente", [
            "PK  _id",
            "fecha · descripcion · ubicacion",
            "gravedad · costoEstimado",
            "→ idMoto · → idMotociclista",
        ], NARANJA),
        "rodada": (68, 5, 30, "eventos_rodada", [
            "PK  _id",
            "nombre · fechaSalida",
            "puntoEncuentro · destino",
            "estado · cupoMaximo",
            "distanciaKm · costo",
        ], VIOLETA),
        "inscripcion": (68, 33, 30, "eventos_inscripcion", [
            "PK  _id",
            "fechaInscripcion · asistio",
            "observaciones",
            "→ idRodada · → idMotociclista",
        ], VIOLETA),
        "galeria": (68, 61, 30, "eventos_galeria", [
            "PK  _id",
            "titulo · descripcion",
            "urlFoto · fechaSubida",
            "→ idRodada",
        ], VIOLETA),
    }
    for _, (x, y, w, titulo, lineas, color) in cajas.items():
        lienzo.caja(x, y, w, titulo, lineas, color=color)

    def relacion(x1, y1, x2, y2, texto, curva=0.0, color=TINTA_SUAVE):
        lienzo.flecha(x1, y1, x2, y2, None, color, curva)
        lienzo.etiqueta((x1 + x2) / 2, (y1 + y2) / 2 - 1.6, texto, 7.0, CODIGO, "#f8fafc")

    relacion(17, 27.5, 17, 33, "idMotociclista", color=AZUL)
    relacion(32, 16, 35, 16, "idMotociclista", color=AZUL)
    relacion(50, 27.5, 50, 33, "idMoto", color=NARANJA)
    relacion(83, 27.5, 83, 33, "idRodada", color=VIOLETA)
    relacion(83, 55.5, 83, 61, "idRodada", curva=0.25, color=VIOLETA)
    lienzo.texto(50, 84, "Referencias por ObjectId en texto: no hay claves foráneas ni cascadas automáticas",
                 8.2, TINTA_SUAVE, familia="sans-serif")
    lienzo.guardar("04-modelo-datos.png")


def integridad_borrado():
    lienzo = Lienzo(100, 54, "Integridad referencial al eliminar")
    lienzo.caja(3, 6, 45, "PADRE · el borrado se bloquea si tiene dependientes", [
        "Motociclista → documentos y motos",
        "Moto → mantenimientos y accidentes",
        "Rodada → inscripciones y fotos",
        "DocumentoSocio → solo documentos",
    ], color=ROJO, fondo="#fef2f2")
    lienzo.caja(52, 6, 45, "HIJO · se borran sin restricción", [
        "Mantenimiento (sin bloqueos)",
        "Accidente (sin bloqueos)",
        "Inscripcion (sin bloqueos)",
        "Galeria / fotos (sin bloqueos)",
    ], color=VERDE, fondo="#f0fdf4")
    lienzo.caja(3, 32, 94, "CÓMO SE RESUELVE EN EL CÓDIGO", [
        "1. La vista comprueba si existen dependientes (`cascada.plan_para(...)`) y avisa en la pantalla",
        "2. El botón de eliminar se rotula con el número de documentos afectados",
        "3. `cascada.aplicar(...)` borra primero los hijos y después el padre",
        "4. En MongoDB no hay `on_delete=CASCADE`: la cascada es explícita y controlada",
    ], color=AZUL)
    lienzo.flecha(25, 28, 25, 32, None, ROJO)
    lienzo.flecha(74, 28, 74, 32, None, VERDE)
    lienzo.guardar("05-integridad-borrado.png")


def dependencias_apps():
    lienzo = Lienzo(100, 66, "Paquetes del proyecto y dependencias entre ellos")
    lienzo.caja(30, 6, 40, "club_motociclistas · configuración", [
        "settings.py · urls.py · views.py",
        "api.py · campos.py · referencias.py",
        "asgi.py · wsgi.py",
    ], color=AZUL_OSCURO)
    lienzo.caja(3, 30, 26, "nucleo", [
        "esquemas.py · serializadores.py",
        "templatetags/club.py",
        "management/commands/",
    ], color=VERDE)
    lienzo.caja(33, 30, 26, "socios", [
        "models.py · forms.py",
        "views.py · urls.py",
        "templates/socios/",
    ], color=AZUL)
    lienzo.caja(63, 30, 26, "flota", [
        "models.py · forms.py",
        "views.py · urls.py",
        "templates/flota/",
    ], color=NARANJA)
    lienzo.caja(78, 6, 19, "eventos", [
        "models.py",
        "forms.py",
        "views.py",
        "urls.py",
    ], color=VIOLETA)
    lienzo.flecha(42, 20, 16, 30, "importa", VERDE)
    lienzo.flecha(46, 20, 46, 30, "importa", AZUL)
    lienzo.flecha(54, 20, 76, 30, "importa", NARANJA)
    lienzo.flecha(56, 16, 78, 16, "importa", VIOLETA)
    lienzo.caja(3, 50, 94, "REGLAS DE DEPENDENCIA", [
        "`nucleo` NO importa modelos a nivel de módulo: usa `apps.get_model(...)` en tiempo de ejecución",
        "`socios` no importa `flota` ni `eventos` en `models.py`; solo en `views.py` (borrado) y `forms.py`",
        "`flota/views.py` importa `socios.models.Motociclista` para el selector de dueño",
        "`eventos/views.py` importa `flota.models.Moto` y `socios.models.Motociclista`",
    ], color=TINTA_SUAVE, fondo="#f1f5f9")
    lienzo.guardar("10-apps-dependencias.png")


def despliegue():
    lienzo = Lienzo(100, 62, "Topología de despliegue con Docker Compose")
    lienzo.caja(3, 8, 24, "NAVEGADOR", [
        "http://localhost:8000",
        "(o el dominio en producción)",
    ], color=AZUL)
    lienzo.caja(32, 8, 32, "CONTENEDOR web", [
        "club-motociclistas:dev",
        "gunicorn (3 workers dev / 2 prod)",
        "whitenoise (estáticos)",
        "volumen media_data → /app/media",
    ], color=VIOLETA)
    lienzo.caja(69, 8, 28, "MongoDB Atlas", [
        "cluster externo (TLS)",
        "MONGO_URI · MONGO_DB",
        "8 colecciones",
    ], color=MONGO, fondo="#f0fdf4")
    lienzo.flecha(27, 20, 32, 20, "HTTP :8000", AZUL)
    lienzo.flecha(64, 20, 69, 20, "pymongo/TLS", VERDE)
    lienzo.caja(3, 36, 94, "CONFIGURACIÓN QUE ENTRA AL CONTENEDOR", [
        "`docker-compose.yml` → `MONGO_URI: ${MONGO_URI:?define MONGO_URI en .env}` (obligatoria)",
        "`.env` (no versionado): SECRET_KEY · DEBUG · ALLOWED_HOSTS · MONGO_URI · MONGO_DB · PUERTO_WEB",
        "`entrypoint.sh`: ping a Mongo → collectstatic → migrate → exec gunicorn",
        "HEALTHCHECK en `http://127.0.0.1:8000/api/esquemas/` (no depende de MongoDB)",
    ], color=AZUL)
    lienzo.flecha(50, 33, 50, 36, None, TINTA_SUAVE)
    lienzo.guardar("11-despliegue.png")


def estructura():
    lienzo = Lienzo(100, 74, "Estructura de carpetas del proyecto")
    columnas = [
        (3, [
            ("club_motociclistas/", "configuración"),
            ("  settings.py", "lee .env, Atlas, whitenoise"),
            ("  urls.py · views.py", "rutas y dashboard"),
            ("  api.py", "API JSON de solo lectura"),
            ("  campos.py", "campo_referencia()"),
            ("  referencias.py", "resuelve referencias"),
            ("nucleo/", "núcleo auxiliar"),
            ("  esquemas.py", "carga JSON Schemas"),
            ("  serializadores.py", "modelo → JSON"),
            ("  templatetags/club.py", "filtros de plantilla"),
            ("  management/commands/", "seed · validar · exportar"),
        ]),
        (35, [
            ("socios/", "Motociclista · DocumentoSocio"),
            ("  models.py · forms.py", "modelo y reglas"),
            ("  views.py · urls.py", "FBV y rutas"),
            ("  templates/socios/", "list · form · detail · delete"),
            ("flota/", "Moto · Mantenimiento · Accidente"),
            ("  models.py · forms.py", "modelo y reglas"),
            ("  views.py · urls.py", "FBV y rutas"),
            ("  templates/flota/", "list · form · detail · delete"),
            ("eventos/", "Rodada · Inscripcion · Galeria"),
            ("  models.py · forms.py", "modelo y reglas"),
            ("  views.py · urls.py", "FBV y rutas"),
        ]),
        (67, [
            ("templates/", "base · dashboard"),
            ("  includes/formulario.html", "formulario común"),
            ("static/", "css/estilos.css · js/app.js"),
            ("schemas/", "JSON Schema por colección"),
            ("docs/", "DOCUMENTACION.md · TUTORIAL.md"),
            ("  diagramas/ · capturas/ · consolas/", "imágenes de la doc"),
            ("tools/", "generar diagramas y DOCX"),
            ("Dockerfile", "build multi-etapa"),
            ("docker-compose.yml", "web + Atlas"),
            ("docker-compose.prod.yml", "producción"),
            ("entrypoint.sh", "espera Mongo → gunicorn"),
            ("requirements.txt · .env.example", "dependencias y entorno"),
        ]),
    ]
    for x, entradas in columnas:
        y = 6
        for nombre, detalle in entradas:
            lienzo.texto(x, y, nombre, 8.4, AZUL_OSCURO, "bold")
            lienzo.texto(x + 1.6, y + 2.0, detalle, 7.7, TINTA_SUAVE, familia="sans-serif")
            y += 4.8
    lienzo.guardar("08-estructura-proyecto.png")


def pipeline_docker():
    lienzo = Lienzo(100, 62, "Del código a la aplicación servida")
    pasos = [
        ("1 · IMAGEN", ["docker compose build web",
                        "etapa builder: pip install",
                        "etapa final: /opt/venv + /app",
                        "usuario appuser (sin privilegios)"]),
        ("2 · ARRANQUE", ["docker compose up -d",
                          "entrypoint.sh: ping a Atlas",
                          "collectstatic + migrate",
                          "exec gunicorn"]),
        ("3 · SALUD", ["HEALTHCHECK /api/esquemas/",
                       "docker compose ps → healthy",
                       "docker compose logs -f web",
                       "docker compose exec web …"]),
        ("4 · DATOS", ["docker compose exec web \\",
                       "  python manage.py seed_data",
                       "docker compose exec web \\",
                       "  python manage.py validar_esquemas"]),
    ]
    x = 2
    for titulo, lineas in pasos:
        lienzo.caja(x, 8, 22, titulo, lineas, color=AZUL)
        x += 24
    for indice in range(3):
        lienzo.flecha(24.5 + indice * 24, 22, 26 + indice * 24, 22, None, TINTA_SUAVE)
    lienzo.caja(3, 36, 94, "RESULTADO", [
        "http://localhost:8000/  →  home con los contadores del club",
        "http://localhost:8000/socios/motociclistas/  →  listado con los datos de Atlas",
        "contenedor: club-motociclistas-web   imagen: club-motociclistas:dev",
        "sin base de datos local: MONGO_URI apunta a MongoDB Atlas",
    ], color=VERDE, fondo="#f0fdf4")
    lienzo.guardar("06-pipeline-docker.png")


def flujo_tutorial():
    lienzo = Lienzo(100, 75, "Ruta de trabajo del tutorial, paso a paso")
    pasos = [
        ("1", "Repositorio", "git clone  ·  copy .env.example .env  ·  MONGO_URI de Atlas"),
        ("2", "Entorno virtual", "python -m venv venv  ·  Activate.ps1  ·  pip install -r requirements.txt"),
        ("3", "Proyecto Django", "startproject club_motociclistas .  ·  settings.py: DATABASES  ·  MIDDLEWARE"),
        ("4", "Apps y modelos", "startapp nucleo|socios|flota|eventos  ·  models.py sin ForeignKey  ·  forms.py · views.py"),
        ("5", "Migraciones y datos", "makemigrations · migrate  ·  seed_data --flush  ·  validar_esquemas"),
        ("6", "Pruebas en la app", "runserver  ·  crear un socio  ·  revisar listados y fichas"),
        ("7", "Docker y Git", "Dockerfile multi-etapa  ·  docker compose up --build  ·  git add · commit · push"),
    ]
    y = 8
    for numero, titulo, comandos in pasos:
        lienzo.ax.add_patch(FancyBboxPatch(
            (4, y), 92, 6.4, boxstyle="round,pad=0.15,rounding_size=0.9",
            linewidth=1.4, edgecolor=AZUL, facecolor="#ffffff", zorder=2))
        lienzo.ax.add_patch(plt.Circle((8, y + 3.2), 2.2, color=AZUL, zorder=3))
        lienzo.texto(8, y + 3.2, numero, 9.4, "#ffffff", "bold", "sans-serif", "center")
        lienzo.texto(12, y + 3.2, titulo, 9.2, AZUL_OSCURO, "bold", "sans-serif")
        lienzo.texto(30, y + 3.2, comandos, 7.8, TINTA)
        if numero != "7":
            lienzo.flecha(8, y + 6.4, 8, y + 7.6, None, AZUL)
        y += 7.8
    lienzo.caja(4, y + 1.0, 92, "RESULTADO FINAL", [
        "Un proyecto Django 6.1 + MongoDB Atlas, dockerizado, con datos de prueba, API JSON,",
        "esquemas validados y documentación técnica y tutorial en DOCX.",
    ], color=VERDE, fondo="#f0fdf4")
    lienzo.guardar("07-flujo-tutorial.png")


def main():
    arquitectura_capas()
    flujo_peticion()
    arquitectura_docker()
    modelo_datos()
    integridad_borrado()
    dependencias_apps()
    despliegue()
    estructura()
    pipeline_docker()
    flujo_tutorial()


if __name__ == "__main__":
    main()

