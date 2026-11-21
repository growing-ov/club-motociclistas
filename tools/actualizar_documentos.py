"""Actualiza docs/DOCUMENTACION.md y docs/TUTORIAL.md con las imagenes nuevas."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TECNICO = RAIZ / "docs" / "DOCUMENTACION.md"
TUTORIAL = RAIZ / "docs" / "TUTORIAL.md"


def quitar_bloque(texto, ancla_inicial, ancla_final):
    """Elimina el bloque cercado que va desde ancla_inicial hasta ancla_final."""
    inicio = texto.index(ancla_inicial)
    fin = texto.index(ancla_final, inicio)
    return texto[:inicio] + texto[fin:]


def actualizar_tecnico():
    texto = TECNICO.read_text(encoding="utf-8")

    # 4.2: el diagrama ya explica el flujo; se retira el bloque de texto.
    texto = texto.replace(
        "*Figura 2. Recorrido de una petición: navegador -> middleware -> resolución de\n"
        "URL -> vista -> formulario -> ORM (`django-mongodb-backend` + `pymongo`) ->\n"
        "MongoDB -> respuesta 302 (éxito) o 200 con el error de negocio bajo el campo.*",
        "*Figura 2. Recorrido completo de la petición, paso a paso: navegador, middleware,\n"
        "resolución de URL, vista con el código real de `crear_moto`, ORM y las dos\n"
        "respuestas posibles (302 al listado o 200 con el error de negocio bajo el campo).*",
    )
    inicio = texto.index("### 4.2 Flujo de una petición")
    bloque_inicio = texto.index("```text", inicio)
    bloque_fin = texto.index("```", bloque_inicio + 7) + 4
    texto = texto[:bloque_inicio] + texto[bloque_fin:]

    # 4.1: la tabla de capas ya no es necesaria (la imagen la contiene).
    texto = texto.replace("""| Capa | Ubicación | Responsabilidad |
|---|---|---|
| Presentación | `templates/`, `static/css/estilos.css`, `static/js/app.js` | HTML, CSS y JavaScript; `{% url %}`, `{% block content %}` |
| Vistas (FBV) | `club_motociclistas/views.py`, `club_motociclistas/api.py`, `socios/views.py`, `flota/views.py`, `eventos/views.py` | Orquestan la petición: validan, guardan, avisan y redirigen |
| Formularios | `socios/forms.py`, `flota/forms.py`, `eventos/forms.py`, `club_motociclistas/campos.py` | `ModelForm` y campos de referencia entre colecciones |
| Modelos | `socios/models.py`, `flota/models.py`, `eventos/models.py` | Colecciones de MongoDB; **sin** `ForeignKey` (referencias por `ObjectId` en texto) |
| Infraestructura | `nucleo/`, `club_motociclistas/settings.py`, `club_motociclistas/referencias.py` | Esquemas JSON, serializadores, templatetags y comandos de gestión |
| Datos | MongoDB (Atlas) | `socios_motociclista`, `socios_documentosocio`, `flota_moto`, `flota_mantenimiento`, `flota_accidente`, `eventos_rodada`, `eventos_inscripcion`, `eventos_galeria` |
""", "")

    # 5.10: la tabla de colecciones ya está dibujada en la imagen.
    texto = texto.replace("""| Colección | Documentos | Referencia a |
|---|---|---|
| `socios_motociclista` | Socio | — |
| `socios_documentosocio` | Documento (cédula, licencia, SOAT, tecnomecánica) | `socios_motociclista` |
| `flota_moto` | Moto | `socios_motociclista` |
| `flota_mantenimiento` | Intervención sobre una moto | `flota_moto` |
| `flota_accidente` | Siniestro de una moto | `flota_moto`, `socios_motociclista` |
| `eventos_rodada` | Salida grupal | — |
| `eventos_inscripcion` | Inscripción de un socio a una rodada | `eventos_rodada`, `socios_motociclista` |
| `eventos_galeria` | Fotografía de una rodada | `eventos_rodada` |
""", "")

    # 4.4: la tabla de piezas ya está en la imagen.
    texto = texto.replace("""| Pieza | Detalle |
|---|---|
| Imagen base | `python:3.12-slim` (etapas `builder` y `final`) |
| Usuario | `appuser` (uid 10001, shell `nologin`, sin privilegios) |
| Entrada | `entrypoint.sh`: espera a MongoDB, `collectstatic`, `migrate`, `exec "$@"` |
| Servidor | Gunicorn (`--bind 0.0.0.0:8000`, 3 workers en dev, 2 en prod) |
| Estáticos | WhiteNoise con `CompressedManifestStaticFilesStorage` |
| Base de datos | MongoDB Atlas mediante `MONGO_URI` (TLS) |
""", "")

    # 6.3: la imagen explica el borrado en cascada.
    texto = texto.replace(
        "> **Nota:** los esquemas corresponden a las colecciones que usa el ORM (§5.1).",
        "> **Nota:** los esquemas corresponden a las colecciones que usa el ORM (§5.1).",
    )

    TECNICO.write_text(texto, encoding="utf-8")
    print("DOCUMENTACION.md actualizado")


def actualizar_tutorial():
    texto = TUTORIAL.read_text(encoding="utf-8")

    inserciones = [
        (
            "4. Configurar el autor de los commits (solo la primera vez):",
            "```powershell\ngit config --global user.name \"Octavio Velasco\"\ngit config --global user.email \"octavio.velasco@club-moto.co\"\n```",
            "```powershell\ngit config --global user.name \"Octavio Velasco\"\ngit config --global user.email \"octavio.velasco@club-moto.co\"\n```",
            "![Consola con la clonación del repositorio y el primer commit](consolas/clonar.png)\n\n"
            "*Figura 2. Clonar el repositorio y comprobar el historial con `git log`.*",
        ),
        (
            "```powershell\npython -m venv venv\n.\\venv\\Scripts\\Activate.ps1\npython -m pip install --upgrade pip\n```",
            "El `venv/` queda fuera del repositorio porque ya está en el `.gitignore`.",
            "```powershell\npython -m venv venv\n.\\venv\\Scripts\\Activate.ps1\npython -m pip install --upgrade pip\n```\n\n"
            "El `venv/` queda fuera del repositorio porque ya está en el `.gitignore`.",
            "![Consola con la creación del entorno virtual y la instalación de dependencias](consolas/venv.png)\n\n"
            "*Figura 3. Entorno virtual creado y dependencias instaladas (`pip install -r requirements.txt`).*",
        ),
        (
            "Comprobación:\n\n```powershell\npython manage.py check\n```",
            "Comprobación:",
            "Comprobación:\n\n```powershell\npython manage.py check\n```\n\n"
            "![Consola con la creación del proyecto Django](consolas/startproject.png)\n\n"
            "*Figura 4. `startproject` genera el paquete `club_motociclistas/` y `manage.py`.*",
            "![Consola con la creación del proyecto Django](consolas/startproject.png)\n\n"
            "*Figura 4. `startproject` genera el paquete `club_motociclistas/` y `manage.py`.*",
        ),
        (
            "Comprobación del enrutado:\n\n```powershell\npython manage.py show_urls\n```",
            "Comprobación del enrutado:",
            "Comprobación del enrutado:\n\n```powershell\npython manage.py show_urls\n```",
            "![Consola con la creación de las cuatro aplicaciones](consolas/startapp.png)\n\n"
            "*Figura 5. Las cuatro aplicaciones quedan creadas dentro del proyecto.*",
        ),
        (
            "La aplicación queda disponible en <http://127.0.0.1:8000/>.",
            "La aplicación queda disponible en <http://127.0.0.1:8000/>.",
            "La aplicación queda disponible en <http://127.0.0.1:8000/>.",
            "![Consola con las migraciones de Django](consolas/migraciones.png)\n\n"
            "*Figura 7. `makemigrations` y `migrate`: en MongoDB son un no-op para el esquema.*",
        ),
        (
            "Comprobar que los datos cumplen los esquemas JSON del proyecto:\n\n```powershell\npython manage.py validar_esquemas\n```",
            "Comprobar que los datos cumplen los esquemas JSON del proyecto:",
            "Comprobar que los datos cumplen los esquemas JSON del proyecto:\n\n```powershell\npython manage.py validar_esquemas\n```",
            "![Consola con la carga de los datos de prueba](consolas/seed.png)\n\n"
            "*Figura 9. `seed_data --flush` deja el club con socios, motos, rodadas y galería.*\n\n"
            "![Consola con la validación de los esquemas JSON](consolas/esquemas.png)\n\n"
            "*Figura 10. Los 97 documentos creados cumplen los JSON Schemas de `schemas/`.*",
        ),
        (
            "El `docker-compose.yml` toma la configuración del archivo `.env`:",
            "El `docker-compose.yml` toma la configuración del archivo `.env`:",
            "El `docker-compose.yml` toma la configuración del archivo `.env`:",
            "![Consola con el contenedor en marcha y sus logs](consolas/docker.png)\n\n"
            "*Figura 12. `docker compose up -d --build` levanta el contenedor y el healthcheck pasa a `healthy`.*",
        ),
        (
            "```powershell\ngit status\ngit add .\ngit commit -m \"feat(app): proyecto inicial del Club de Motociclistas\"\ngit push origin main\n```",
            "```powershell\ngit status\ngit add .\ngit commit -m \"feat(app): proyecto inicial del Club de Motociclistas\"\ngit push origin main\n```",
            "```powershell\ngit status\ngit add .\ngit commit -m \"feat(app): proyecto inicial del Club de Motociclistas\"\ngit push origin main\n```",
            "![Consola con la publicación en GitHub](consolas/git.png)\n\n"
            "*Figura 14. `git add`, `git commit` y `git push` con la rama `main` al día.*",
        ),
    ]

    for ancla, sustituto_ancla, sustituto, extra in inserciones:
        if ancla not in texto:
            print(f"  (ancla no encontrada) {ancla[:50]}")
            continue
        texto = texto.replace(ancla, sustituto + "\n\n" + extra, 1)

    # Renumerar las figuras del tutorial de forma coherente.
    contador = [0]

    def renumerar(match):
        contador[0] += 1
        return f"*Figura {contador[0]}. "

    import re

    texto = re.sub(r"\*Figura \d+\. ", renumerar, texto)

    TUTORIAL.write_text(texto, encoding="utf-8")
    print("TUTORIAL.md actualizado con", contador[0], "figuras")


if __name__ == "__main__":
    actualizar_tecnico()
    actualizar_tutorial()
