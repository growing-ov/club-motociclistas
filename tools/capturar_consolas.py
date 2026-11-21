"""Captura la salida real de los comandos del tutorial para ilustrarlos.

Uso:  python tools/capturar_consolas.py
Genera docs/consolas.json con los bloques de consola que luego se dibujan
como imagenes en tools/generar_consolas.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PYTHON = RAIZ / "venv" / "Scripts" / "python.exe"
SALIDA = RAIZ / "docs" / "consolas.json"


def ejecutar(comando, cwd=None, timeout=600):
    proceso = subprocess.run(
        comando,
        cwd=str(cwd or RAIZ),
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    salida = (proceso.stdout or "") + (proceso.stderr or "")
    lineas = [linea.rstrip() for linea in salida.splitlines()]
    while lineas and not lineas[-1].strip():
        lineas.pop()
    return lineas


def ultimas(lineas, cantidad):
    return lineas[-cantidad:] if len(lineas) > cantidad else lineas


def main():
    bloques = []

    # 1) Clonar el repositorio
    temporal = Path(tempfile.mkdtemp(prefix="consola-"))
    destino = temporal / "club-motociclistas"
    lineas = ejecutar(f'git clone https://github.com/growing-ov/club-motociclistas.git "{destino}"')
    bloques.append({
        "id": "clonar",
        "titulo": "Clonar el repositorio",
        "consola": [
            {"cmd": "git clone https://github.com/growing-ov/club-motociclistas.git", "salida": lineas},
            {"cmd": "cd club-motociclistas", "salida": []},
            {"cmd": "git log --oneline -3", "salida": ejecutar("git log --oneline -3")},
        ],
    })

    # 2) Crear el entorno virtual e instalar dependencias
    temporal_venv = Path(tempfile.mkdtemp(prefix="venv-demo-"))
    lineas_venv = ejecutar(f'"{PYTHON}" -m venv "{temporal_venv}"', timeout=300)
    instalacion = ejecutar(
        f'"{temporal_venv / "Scripts" / "pip.exe"}" install -r "{RAIZ / "requirements.txt"}"',
        timeout=900,
    )
    shutil.rmtree(temporal_venv, ignore_errors=True)
    bloques.append({
        "id": "venv",
        "titulo": "Crear el entorno virtual e instalar las dependencias",
        "consola": [
            {"cmd": "python -m venv venv", "salida": lineas_venv},
            {"cmd": ".\\venv\\Scripts\\Activate.ps1", "salida": []},
            {"cmd": "pip install -r requirements.txt", "salida": instalacion},
        ],
    })

    # 3) Crear el proyecto Django desde cero
    proyecto = temporal / "club-nuevo"
    proyecto.mkdir()
    lineas = ejecutar(f'"{PYTHON}" -m django startproject club_motociclistas .', cwd=proyecto)
    comprobar = ejecutar(f'"{PYTHON}" manage.py check', cwd=proyecto)
    listado = ejecutar("dir", cwd=proyecto)
    bloques.append({
        "id": "startproject",
        "titulo": "Crear el proyecto Django",
        "consola": [
            {"cmd": "python -m django startproject club_motociclistas .", "salida": lineas},
            {"cmd": "dir", "salida": listado},
            {"cmd": "python manage.py check", "salida": comprobar},
        ],
    })

    # 4) Crear las cuatro aplicaciones
    lineas_app = []
    for app in ("nucleo", "socios", "flota", "eventos"):
        ejecutar(f'"{PYTHON}" manage.py startapp {app}', cwd=proyecto)
    listado_apps = ejecutar("dir", cwd=proyecto)
    bloques.append({
        "id": "startapp",
        "titulo": "Crear las cuatro aplicaciones",
        "consola": [
            {"cmd": "python manage.py startapp nucleo", "salida": []},
            {"cmd": "python manage.py startapp socios", "salida": []},
            {"cmd": "python manage.py startapp flota", "salida": []},
            {"cmd": "python manage.py startapp eventos", "salida": []},
            {"cmd": "dir", "salida": listado_apps},
        ],
    })

    shutil.rmtree(temporal, ignore_errors=True)

    # 4) Comprobacion del proyecto real
    bloques.append({
        "id": "check",
        "titulo": "Comprobar el proyecto",
        "consola": [
            {"cmd": "python manage.py check", "salida": ejecutar(f'"{PYTHON}" manage.py check')},
            {"cmd": "python manage.py showmigrations", "salida": ejecutar(f'"{PYTHON}" manage.py showmigrations')},
        ],
    })

    # 5) Migraciones
    lineas_makemigrations = ejecutar(f'"{PYTHON}" manage.py makemigrations socios flota eventos')
    for app in ("socios", "flota", "eventos"):
        carpeta = RAIZ / app / "migrations"
        if carpeta.exists():
            shutil.rmtree(carpeta, ignore_errors=True)
    bloques.append({
        "id": "migraciones",
        "titulo": "Migraciones",
        "consola": [
            {"cmd": "python manage.py makemigrations socios flota eventos", "salida": lineas_makemigrations},
            {"cmd": "python manage.py migrate", "salida": ejecutar(f'"{PYTHON}" manage.py migrate')},
        ],
    })

    # 6) Datos de prueba (salida real completa)
    bloques.append({
        "id": "seed",
        "titulo": "Cargar los datos de prueba",
        "consola": [
            {"cmd": "python manage.py seed_data --flush", "salida": ejecutar(f'"{PYTHON}" manage.py seed_data --flush')},
        ],
    })

    # 7) Validacion de esquemas (salida real)
    bloques.append({
        "id": "esquemas",
        "titulo": "Validar los datos contra los JSON Schemas",
        "consola": [
            {"cmd": "python manage.py validar_esquemas", "salida": ejecutar(f'"{PYTHON}" manage.py validar_esquemas')},
        ],
    })

    # 8) Contenedor en marcha
    ps = ejecutar("docker compose ps")
    logs = ejecutar('docker compose logs web 2>&1 | findstr /C:"entrypoint" /C:"gunicorn"')
    bloques.append({
        "id": "docker",
        "titulo": "Levantar la aplicacion con Docker",
        "consola": [
            {"cmd": "docker compose up -d --build", "salida": ultimas(ejecutar("docker compose up -d --build"), 6)},
            {"cmd": "docker compose ps", "salida": ps},
            {"cmd": "docker compose logs web", "salida": ultimas(logs, 8)},
        ],
    })

    # 9) Git
    bloques.append({
        "id": "git",
        "titulo": "Publicar los cambios",
        "consola": [
            {"cmd": "git status", "salida": ultimas(ejecutar("git status --short"), 8)},
            {"cmd": "git add .", "salida": []},
            {"cmd": 'git commit -m "feat(app): proyecto inicial del Club de Motociclistas"', "salida": []},
            {"cmd": "git push origin main", "salida": ejecutar("git push origin main 2>&1")},
        ],
    })

    SALIDA.write_text(json.dumps(bloques, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{SALIDA} generado con {len(bloques)} bloques")


if __name__ == "__main__":
    main()
