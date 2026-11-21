"""Pobla MongoDB con datos de prueba coherentes para el club.

Uso:
    python manage.py seed_data
    python manage.py seed_data --flush      # limpia antes de poblar
    python manage.py seed_data --sin-fotos   # no usa imagenes remotas

Las referencias entre documentos son planas: se guarda el ObjectId del
documento apuntado en texto, sin relaciones en la base de datos.
"""

from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand

from eventos.models import Galeria, Inscripcion, Rodada
from flota.models import Accidente, Mantenimiento, Moto
from socios.models import DocumentoSocio, Motociclista


class Command(BaseCommand):
    help = "Pobla la base de datos con socios, motos, rodadas, inscripciones y galeria."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Elimina todos los registros antes de poblar.",
        )
        parser.add_argument(
            "--sin-fotos",
            action="store_true",
            help="No asigna imagenes remotas a socios y motos.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Vaciando colecciones..."))
            Galeria.objects.all().delete()
            Inscripcion.objects.all().delete()
            Rodada.objects.all().delete()
            Accidente.objects.all().delete()
            Mantenimiento.objects.all().delete()
            Moto.objects.all().delete()
            DocumentoSocio.objects.all().delete()
            Motociclista.objects.all().delete()

        if Motociclista.objects.exists() and not options["flush"]:
            self.stdout.write(
                self.style.WARNING(
                    "La base ya tiene datos. Usa --flush para reemplazarlos."
                )
            )
            return

        ahora = datetime.now(timezone.utc).replace(microsecond=0)
        usar_fotos = not options["sin_fotos"]

        self.stdout.write("Creando motociclistas...")
        socios = self._crear_motociclistas(usar_fotos)

        self.stdout.write("Creando documentos...")
        self._crear_documentos(socios)

        self.stdout.write("Creando motos...")
        motos = self._crear_motos(socios, usar_fotos)

        self.stdout.write("Creando mantenimientos...")
        self._crear_mantenimientos(motos, ahora)

        self.stdout.write("Creando accidentes...")
        self._crear_accidentes(motos, ahora)

        self.stdout.write("Creando rodadas...")
        rodadas = self._crear_rodadas(ahora)

        self.stdout.write("Creando inscripciones...")
        self._crear_inscripciones(socios, rodadas, ahora)

        self.stdout.write("Creando galeria...")
        self._crear_galeria(rodadas, ahora, usar_fotos)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seed completado correctamente."))
        self._resumen()

    # ------------------------------------------------------------------
    # Socos
    # ------------------------------------------------------------------

    def _crear_motociclistas(self, usar_fotos):
        datos = [
            ("Octavio", "Velasco", "octavio.velasco@club-moto.co", "+57 311 456 7821",
             (2005, 4, 20), "A2", "Triumph"),
            ("Jaime", "Calderon", "jaime.calderon@club-moto.co", "+57 320 874 1193",
             (2004, 5, 15), "A2", "ducati"),
            ("Santiago", "Ramirez", "santiago.ramirez@club-moto.co", "+57 315 220 4987",
             (2001, 8, 3), "A2", "yamaha"),
            ("Valentina", "Ortiz", "valentina.ortiz@club-moto.co", "+57 318 663 2015",
             (2003, 1, 28), "A1", "honda"),
            ("Andres", "Moreno", "andres.moreno@club-moto.co", "+57 312 991 4408",
             (1998, 11, 9), "A2", "bmw"),
            ("Camila", "Perez", "camila.perez@club-moto.co", "+57 316 557 3260",
             (2000, 6, 17), "A2", "kawasaki"),
            ("Daniel", "Restrepo", "daniel.restrepo@club-moto.co", "+57 321 778 9120",
             (1996, 3, 5), "A2", "ktm"),
        ]

        socios = {}
        for indice, (nombre, apellido, correo, telefono, nacimiento, licencia, semilla) in enumerate(
            datos, start=1
        ):
            socio = Motociclista.objects.create(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                fechaNacimiento=datetime(*nacimiento, tzinfo=timezone.utc).date(),
                activo=True,
                tipoLicencia=licencia,
                fotoUrl=_foto(f"socio-{semilla}", 640, 640) if usar_fotos else None,
            )
            socios[apellido] = socio
            self.stdout.write(f"  + {socio} ({len(socios)})")
        return socios

    # ------------------------------------------------------------------
    # Documentos
    # ------------------------------------------------------------------

    def _crear_documentos(self, socios):
        for indice, (apellido, socio) in enumerate(socios.items(), start=1):
            anio_licencia = 2023 if socio.tipoLicencia == "A2" else 2024
            documentos = [
                (
                    "Cedula de Ciudadania",
                    f"{1000000000 + indice}",
                    (2019, 7, 10),
                    (2031, 7, 10),
                    "cedulas",
                ),
                (
                    f"Licencia de Conduccion {socio.tipoLicencia}",
                    f"{socio.tipoLicencia}-2023-{indice:04d}",
                    (anio_licencia, 6, 1),
                    (2033, 6, 1),
                    "licencias",
                ),
                (
                    "SOAT",
                    f"SOAT-2026-{indice:04d}",
                    (2026, 1, 15),
                    (2027, 1, 15),
                    "soat",
                ),
                (
                    "Tecnomecanica",
                    f"RTM-2026-{indice:04d}",
                    (2026, 4, 20),
                    (2027, 4, 20),
                    "tecnomecanica",
                ),
            ]
            for nombre, numero, emision, vencimiento, carpeta in documentos:
                DocumentoSocio.objects.create(
                    nombreDocumento=nombre,
                    numeroDocumento=numero,
                    fechaEmision=datetime(*emision, tzinfo=timezone.utc).date(),
                    fechaVencimiento=datetime(*vencimiento, tzinfo=timezone.utc).date(),
                    archivoUrl=f"https://docs.club-moto.co/{carpeta}/{apellido.lower()}.pdf",
                    idMotociclista=str(socio.pk),
                )

    # ------------------------------------------------------------------
    # Motos
    # ------------------------------------------------------------------

    def _crear_motos(self, socios, usar_fotos):
        catalogo = {
            "Velasco": ("Triumph", "Tiger 1200 GT Explorer", 2024, "Adventure", 1200, "Verde Mate", "OVL"),
            "Calderon": ("Ducati", "Hypermotard 939 SP", 2019, "Supermotard", 937, "Rojo Ducati", "JCL"),
            "Ramirez": ("Yamaha", "MT-09 SP", 2023, "Naked", 890, "Azul Team", "SRM"),
            "Ortiz": ("Honda", "CB650R", 2022, "Naked", 649, "Negro Mate", "VOR"),
            "Moreno": ("BMW", "R 1250 GS Adventure", 2023, "Adventure", 1254, "Blanco", "AMR"),
            "Perez": ("Kawasaki", "Ninja 650", 2021, "Deportiva", 649, "Verde KRT", "CPR"),
            "Restrepo": ("KTM", "390 Duke", 2024, "Naked", 373, "Naranja", "DRS"),
        }
        motos = {}
        for indice, (apellido, socio) in enumerate(socios.items(), start=1):
            marca, modelo, anio, tipo, cilindrada, color, prefijo = catalogo[apellido]
            moto = Moto.objects.create(
                placa=f"{prefijo}{10 + indice:02d}",
                marca=marca,
                modelo=modelo,
                anio=anio,
                tipoMoto=tipo,
                cilindrada=cilindrada,
                color=color,
                fotoUrl=_foto(f"moto-{marca.lower()}", 800, 600) if usar_fotos else None,
                idMotociclista=str(socio.pk),
            )
            motos[apellido] = moto
        return motos

    # ------------------------------------------------------------------
    # Mantenimientos
    # ------------------------------------------------------------------

    def _crear_mantenimientos(self, motos, ahora):
        planes = {
            "Tiger 1200 GT Explorer": [
                ("Cambio de aceite y filtro", 380000, 5200,
                 "Aceite Motul 7100 20W-50 y filtro OEM. Moto en optimas condiciones.", 300),
                ("Cambio de neumatico trasero", 720000, 7900,
                 "Pirelli Scorpion Trail III 170/60 R17. Desgaste normal por rodada a Girardot.", 210),
                ("Revision de frenos y pastillas", 280000, 9450,
                 "Pastillas Brembo delante en buen estado. Liquido DOT 5.1 reemplazado.", 120),
            ],
            "Hypermotard 939 SP": [
                ("Cambio de aceite y filtro", 320000, 11200,
                 "Shell Advance Ultra 10W-40. Filtro K&N limpiado.", 280),
                ("Ajuste de cadena y engrase", 90000, 12100,
                 "Cadena DID VX. Tensado segun manual. Engrase Motul Chain Lube.", 190),
                ("Cambio de neumaticos", 980000, 13450,
                 "Pirelli Diablo Rosso IV adelante y atras. Primer juego cumplido.", 95),
            ],
            "MT-09 SP": [
                ("Cambio de aceite", 250000, 14800, "Yamalube 10W-40 y filtro OEM.", 240),
                ("Cambio de pastillas freno delantero", 220000, 16100,
                 "Pastillas Brembo SA. Buen estado del disco.", 160),
            ],
            "CB650R": [
                ("Primer servicio 6000 km", 180000, 6100,
                 "Aceite Honda HP4 10W-30. Ajuste de valvulas dentro de tolerancia.", 330),
                ("Cambio de filtro de aire", 140000, 12400,
                 "Filtro K&N. Limpieza y aceitado.", 170),
            ],
            "R 1250 GS Adventure": [
                ("Cambio de aceite y filtros", 520000, 28800,
                 "Motul 5100 15W-50. Filtro de aceite y filtro de aire OEM.", 310),
                ("Cambio de neumaticos", 1450000, 34200,
                 "Metzeler Karoo 4. Para uso mixto on/off.", 200),
                ("Mantenimiento 30000 km", 1100000, 38150,
                 "Bujias, aceite, filtro aire, valvulas, refrigerante. Servicio completo.", 45),
            ],
            "Ninja 650": [
                ("Cambio de aceite", 200000, 16700,
                 "Kawasaki 10W-40 semi-sintetico. Filtro OEM.", 220),
                ("Cambio de cadena y sprocket", 480000, 18900,
                 "Kit D.I.D VX + JT Sprockets. Relacion original 15/46.", 140),
            ],
            "390 Duke": [
                ("Primer service 1000 km", 95000, 1200,
                 "Aceite Motorex 10W-40. Filtro OEM. Sin observaciones.", 280),
                ("Cambio de neumatico delantero", 320000, 5400,
                 "Metzeler Sportec M9. Desgaste por uso urbano.", 180),
            ],
        }

        for moto in motos.values():
            for tipo, costo, km, descripcion, dias in planes.get(moto.modelo, []):
                Mantenimiento.objects.create(
                    idMoto=str(moto.pk),
                    fecha=ahora - timedelta(days=dias),
                    tipo=tipo,
                    descripcion=descripcion,
                    costo=costo,
                    kilometraje=km,
                    realizado=True,
                )

    # ------------------------------------------------------------------
    # Accidentes
    # ------------------------------------------------------------------

    def _crear_accidentes(self, motos, ahora):
        Accidente.objects.create(
            idMoto=str(motos["Perez"].pk),
            fecha=ahora - timedelta(days=280),
            descripcion=(
                "Caida a baja velocidad en lluvia sobre la Av. Boyaca con calle 53. "
                "Piso mojado, la moto derrapo al frenar en el semaforo. Sin lesionados. "
                "Danos menores: guardabarros delantero rayado, palanca de freno torcida."
            ),
            ubicacion="Avenida Boyaca con Calle 53, Bogota",
            gravedad="leve",
            costoEstimado=420000,
        )
        Accidente.objects.create(
            idMoto=str(motos["Restrepo"].pk),
            fecha=ahora - timedelta(days=95),
            descripcion=(
                "Colision lateral contra un vehiculo particular en la via Villavicencio. "
                "El conductor cambio de carril sin senalizar. Lesiones leves en el "
                "hombro, atendido en el hospital."
            ),
            ubicacion="Via Villavicencio km 12, Tocancipa",
            gravedad="moderado",
            costoEstimado=1850000,
        )

    # ------------------------------------------------------------------
    # Rodadas
    # ------------------------------------------------------------------

    def _crear_rodadas(self, ahora):
        datos = [
            {
                "nombre": "Rodada al Embalse del Neusa",
                "fechaSalida": ahora + timedelta(days=12, hours=6),
                "puntoEncuentro": "Centro Comercial Andino, Carrera 11 #82-71",
                "destino": "Embalse del Neusa, Cogua, Cundinamarca",
                "estado": "programada",
                "cupoMaximo": 20,
                "distanciaKm": 95,
                "costo": 45000,
            },
            {
                "nombre": "Rodada Parque Nacional Chingaza",
                "fechaSalida": ahora + timedelta(days=21, hours=6),
                "puntoEncuentro": "Parqueadero CC Unicentro, Calle 127 #15-30",
                "destino": "Parque Nacional Natural Chingaza, La Calera",
                "estado": "programada",
                "cupoMaximo": 12,
                "distanciaKm": 65,
                "costo": 60000,
            },
            {
                "nombre": "Rodada Nocturna Girardot",
                "fechaSalida": ahora + timedelta(days=35, hours=5),
                "puntoEncuentro": "Peaje de Chinauta, Via Bogota - Girardot",
                "destino": "Plaza Principal de Girardot",
                "estado": "programada",
                "cupoMaximo": 25,
                "distanciaKm": 130,
                "costo": 80000,
            },
            {
                "nombre": "Rodada Villa de Leyva",
                "fechaSalida": ahora - timedelta(days=28),
                "puntoEncuentro": "Estacion de Servicio Terpel Norte, Calle 220",
                "destino": "Villa de Leyva, Boyaca",
                "estado": "finalizada",
                "cupoMaximo": 18,
                "distanciaKm": 195,
                "costo": 95000,
            },
            {
                "nombre": "Rodada Desayuno Sutamarchan",
                "fechaSalida": ahora - timedelta(days=55),
                "puntoEncuentro": "Parqueadero CC Plaza Imperial, Suba",
                "destino": "Sutamarchan, Boyaca",
                "estado": "finalizada",
                "cupoMaximo": 15,
                "distanciaKm": 170,
                "costo": 70000,
            },
        ]
        return {datos["nombre"]: Rodada.objects.create(**datos) for datos in datos}

    # ------------------------------------------------------------------
    # Inscripciones
    # ------------------------------------------------------------------

    def _crear_inscripciones(self, socios, rodadas, ahora):
        futuras = [
            ("Rodada al Embalse del Neusa",
             ["Velasco", "Calderon", "Ramirez", "Ortiz", "Moreno", "Restrepo"]),
            ("Rodada Parque Nacional Chingaza",
             ["Velasco", "Calderon", "Moreno", "Restrepo"]),
            ("Rodada Nocturna Girardot",
             ["Velasco", "Calderon", "Ramirez", "Perez", "Ortiz", "Moreno", "Restrepo"]),
        ]
        pasadas = [
            ("Rodada Villa de Leyva",
             ["Velasco", "Calderon", "Ramirez", "Moreno", "Perez"], True),
            ("Rodada Desayuno Sutamarchan",
             ["Calderon", "Ortiz", "Moreno", "Restrepo"], True),
        ]

        for nombre_rodada, apellidos in futuras:
            for apellido in apellidos:
                Inscripcion.objects.create(
                    idMotociclista=str(socios[apellido].pk),
                    idRodada=str(rodadas[nombre_rodada].pk),
                    fechaInscripcion=ahora - timedelta(days=3),
                    asistio=False,
                    observaciones=None,
                )

        for nombre_rodada, apellidos, asistio in pasadas:
            for apellido in apellidos:
                Inscripcion.objects.create(
                    idMotociclista=str(socios[apellido].pk),
                    idRodada=str(rodadas[nombre_rodada].pk),
                    fechaInscripcion=ahora - timedelta(days=35),
                    asistio=asistio,
                    observaciones="Asistencia completa, sin novedades." if asistio else None,
                )

    # ------------------------------------------------------------------
    # Galeria
    # ------------------------------------------------------------------

    def _crear_galeria(self, rodadas, ahora, usar_fotos):
        fotos = [
            ("Rodada Villa de Leyva", "Salida grupal Km 0",
             "Foto del grupo antes de partir desde el punto de encuentro.", "galeria-salida", 26),
            ("Rodada Villa de Leyva", "Llegada a Plaza Mayor",
             "Grupo completo frente a la Plaza Mayor de Villa de Leyva.", "galeria-plaza", 26),
            ("Rodada Villa de Leyva", "Curva de Sutamarchan",
             "Caravana tomando la curva antes de Sutamarchan.", "galeria-curva", 26),
            ("Rodada Desayuno Sutamarchan", "Desayuno campesino",
             "Socios disfrutando del desayuno tipico en Sutamarchan.", "galeria-desayuno", 53),
            ("Rodada Desayuno Sutamarchan", "Aparcamiento de las motos",
             "Fila de motos aparcadas antes de arrancar.", "galeria-motos", 53),
        ]
        for nombre, titulo, descripcion, semilla, dias in fotos:
            Galeria.objects.create(
                idRodada=str(rodadas[nombre].pk),
                titulo=titulo,
                descripcion=descripcion,
                urlFoto=_foto(semilla, 1200, 800) if usar_fotos else "https://picsum.photos/1200/800",
                fechaSubida=ahora - timedelta(days=dias),
            )

    # ------------------------------------------------------------------
    # Resumen
    # ------------------------------------------------------------------

    def _resumen(self):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== RESUMEN ==="))
        self.stdout.write(f"Motociclistas:  {Motociclista.objects.count()}")
        self.stdout.write(f"Documentos:     {DocumentoSocio.objects.count()}")
        self.stdout.write(f"Motos:          {Moto.objects.count()}")
        self.stdout.write(f"Mantenimientos: {Mantenimiento.objects.count()}")
        self.stdout.write(f"Accidentes:     {Accidente.objects.count()}")
        self.stdout.write(f"Rodadas:        {Rodada.objects.count()}")
        self.stdout.write(f"Inscripciones:  {Inscripcion.objects.count()}")
        self.stdout.write(f"Galeria:        {Galeria.objects.count()}")


def _foto(semilla, ancho, alto):
    """URL de imagen estable (misma semilla, misma foto)."""
    return f"https://picsum.photos/seed/{semilla}/{ancho}/{alto}"
