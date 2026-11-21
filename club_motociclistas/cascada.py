"""Eliminacion en cascada de los documentos que dependen de otros.

El proyecto funciona **sin relaciones en la base de datos**: cada
dependencia se guarda como el identificador (``ObjectId`` en texto) dentro
de un campo ``CharField`` indexado. Por eso no se puede usar
``on_delete=CASCADE`` de Django y el borrado en cascada se resuelve aqui
de forma explicita y controlada.

Este modulo ofrece dos operaciones:

- :func:`plan_para` calcula que documentos se van a borrar junto al objeto
  **sin tocar la base de datos**. Sirve para mostrar la advertencia en la
  pantalla de confirmacion y para rotular el boton de eliminacion.
- :func:`aplicar` borra el plan completo: primero los documentos hijos y
  despues el padre, y devuelve cuantos se eliminaron de cada tipo.

Orden de borrado
----------------
Los grupos de un :class:`Plan` se borran en el orden en que aparecen, de
modo que siempre se borra un hijo antes que su padre: los mantenimientos
y los accidentes antes que la moto, y las motos antes que el socio.

Convencion de nombres
---------------------
- ``idMotociclista`` -> referencia a :class:`socios.models.Motociclista`
- ``idMoto``         -> referencia a :class:`flota.models.Moto`
- ``idRodada``       -> referencia a :class:`eventos.models.Rodada`
"""

from dataclasses import dataclass, field
from datetime import date

from .referencias import a_texto, ids_de, mapa_por_id


@dataclass
class Grupo:
    """Documentos del mismo tipo que se borran junto con su padre."""

    etiqueta: str
    singular: str
    modelo: object = None
    elementos: list = field(default_factory=list)
    detalle: str = ""
    describir: object = None

    @property
    def cantidad(self):
        """Cuantos documentos contiene el grupo."""
        return len(self.elementos)

    def nombre(self):
        """Como se nombra el grupo segun la cantidad: ``1 moto`` / ``2 motos``."""
        return self.singular if self.cantidad == 1 else self.etiqueta

    def lineas(self):
        """Descripcion corta de cada documento del grupo."""
        if self.describir is None:
            return [str(elemento) for elemento in self.elementos]
        return [self.describir(elemento) for elemento in self.elementos]


@dataclass
class Plan:
    """Resumen de una eliminacion en cascada."""

    clave: str
    etiqueta_padre: str
    padre: object
    mensaje_base: str = ""
    grupos: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)

    @property
    def total(self):
        """Cuantos registros asociados se van a borrar en cascada."""
        return sum(grupo.cantidad for grupo in self.grupos)

    @property
    def vacio(self):
        """``True`` cuando el objeto no tiene nada asociado."""
        return self.total == 0

    def resumen(self):
        """Texto corto con el detalle: ``"2 motos, 1 inscripcion"``."""
        partes = [
            f"{grupo.cantidad} {grupo.nombre()}"
            for grupo in self.grupos
            if grupo.cantidad
        ]
        return ", ".join(partes)

    def mensaje_exito(self):
        """Mensaje de confirmacion que se muestra tras aplicar la cascada."""
        if self.vacio:
            return self.mensaje_base
        return (
            f"{self.mensaje_base} Tambien se eliminaron {self.total} registros "
            f"asociados en cascada ({self.resumen()})."
        )


# ---------------------------------------------------------------------------
# Descripciones cortas de cada tipo de documento
# ---------------------------------------------------------------------------

def _describir_moto(moto):
    return f"{moto.marca} {moto.modelo} ({moto.placa})"


def _describir_mantenimiento(mantenimiento):
    return f"{mantenimiento.tipo} - {mantenimiento.fecha:%d/%m/%Y}"


def _describir_accidente(accidente):
    return f"{accidente.get_gravedad_display()} - {accidente.fecha:%d/%m/%Y}"


def _describir_documento(documento):
    return f"{documento.nombreDocumento} - {documento.numeroDocumento}"


def _describir_galeria(foto):
    return foto.titulo


def _describir_inscripciones(inscripciones):
    """Devuelve un descriptor que nombra la rodada de cada inscripcion."""
    from eventos.models import Rodada

    rodadas = mapa_por_id(Rodada, ids_de(inscripciones, "idRodada"))

    def describir(inscripcion):
        rodada = rodadas.get(a_texto(inscripcion.idRodada))
        nombre = rodada.nombre if rodada is not None else "rodada desconocida"
        return f"{nombre} - {inscripcion.fechaInscripcion:%d/%m/%Y}"

    return describir


# ---------------------------------------------------------------------------
# Planes por tipo de documento
# ---------------------------------------------------------------------------

def _plan_motociclista(socio):
    """Plan de un socio: motos (y sus mantenimientos/accidentes), documentos
    e inscripciones."""
    from eventos.models import Inscripcion
    from flota.models import Accidente, Mantenimiento, Moto
    from socios.models import DocumentoSocio

    motos = list(
        Moto.objects.filter(idMotociclista=a_texto(socio.pk)).order_by("placa")
    )
    ids_motos = [a_texto(moto.pk) for moto in motos]

    grupos = []
    if ids_motos:
        grupos.append(
            Grupo(
                etiqueta="mantenimientos",
                singular="mantenimiento",
                modelo=Mantenimiento,
                elementos=list(
                    Mantenimiento.objects.filter(idMoto__in=ids_motos).order_by("-fecha")
                ),
                detalle="de sus motos",
                describir=_describir_mantenimiento,
            )
        )
        grupos.append(
            Grupo(
                etiqueta="accidentes",
                singular="accidente",
                modelo=Accidente,
                elementos=list(
                    Accidente.objects.filter(idMoto__in=ids_motos).order_by("-fecha")
                ),
                detalle="de sus motos",
                describir=_describir_accidente,
            )
        )

    grupos.append(
        Grupo(
            etiqueta="motos",
            singular="moto",
            modelo=Moto,
            elementos=motos,
            describir=_describir_moto,
        )
    )
    grupos.append(
        Grupo(
            etiqueta="documentos",
            singular="documento",
            modelo=DocumentoSocio,
            elementos=list(
                DocumentoSocio.objects.filter(idMotociclista=a_texto(socio.pk)).order_by(
                    "-fechaEmision"
                )
            ),
            describir=_describir_documento,
        )
    )

    inscripciones = list(
        Inscripcion.objects.filter(idMotociclista=a_texto(socio.pk)).order_by(
            "-fechaInscripcion"
        )
    )
    grupos.append(
        Grupo(
            etiqueta="inscripciones",
            singular="inscripcion",
            modelo=Inscripcion,
            elementos=inscripciones,
            describir=_describir_inscripciones(inscripciones),
        )
    )

    return Plan(
        clave="motociclista",
        etiqueta_padre="Motociclista",
        padre=socio,
        mensaje_base="Motociclista eliminado correctamente.",
        grupos=grupos,
    )


def _plan_moto(moto):
    """Plan de una moto: mantenimientos y accidentes registrados."""
    from flota.models import Accidente, Mantenimiento

    grupos = [
        Grupo(
            etiqueta="mantenimientos",
            singular="mantenimiento",
            modelo=Mantenimiento,
            elementos=list(
                Mantenimiento.objects.filter(idMoto=a_texto(moto.pk)).order_by("-fecha")
            ),
            describir=_describir_mantenimiento,
        ),
        Grupo(
            etiqueta="accidentes",
            singular="accidente",
            modelo=Accidente,
            elementos=list(
                Accidente.objects.filter(idMoto=a_texto(moto.pk)).order_by("-fecha")
            ),
            describir=_describir_accidente,
        ),
    ]

    return Plan(
        clave="moto",
        etiqueta_padre="Moto",
        padre=moto,
        mensaje_base="Moto eliminada correctamente.",
        grupos=grupos,
    )


def _plan_rodada(rodada):
    """Plan de una rodada: inscripciones y fotos de la galeria."""
    from eventos.models import Galeria, Inscripcion

    inscripciones = list(
        Inscripcion.objects.filter(idRodada=a_texto(rodada.pk)).order_by(
            "fechaInscripcion"
        )
    )
    grupos = [
        Grupo(
            etiqueta="inscripciones",
            singular="inscripcion",
            modelo=Inscripcion,
            elementos=inscripciones,
            describir=_describir_inscripciones(inscripciones),
        ),
        Grupo(
            etiqueta="fotos",
            singular="foto",
            modelo=Galeria,
            elementos=list(
                Galeria.objects.filter(idRodada=a_texto(rodada.pk)).order_by(
                    "-fechaSubida"
                )
            ),
            describir=_describir_galeria,
        ),
    ]

    return Plan(
        clave="rodada",
        etiqueta_padre="Rodada",
        padre=rodada,
        mensaje_base="Rodada eliminada correctamente.",
        grupos=grupos,
    )


def _plan_documento(documento):
    """Plan de un documento de socio: no tiene dependencias, pero avisa si
    el documento sigue vigente."""
    advertencias = []
    if documento.fechaVencimiento and documento.fechaVencimiento >= date.today():
        advertencias.append(
            "Este documento sigue vigente hasta el "
            f"{documento.fechaVencimiento:%d/%m/%Y}; al eliminarlo el socio "
            "quedara sin esa acreditacion."
        )

    return Plan(
        clave="documento",
        etiqueta_padre="Documento",
        padre=documento,
        mensaje_base="Documento eliminado correctamente.",
        grupos=[],
        advertencias=advertencias,
    )


CONSTRUCTORES = {
    "motociclista": _plan_motociclista,
    "moto": _plan_moto,
    "rodada": _plan_rodada,
    "documento": _plan_documento,
}


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------

def plan_para(clave, objeto):
    """Calcula el plan de cascada de ``objeto`` sin modificar la base."""
    constructor = CONSTRUCTORES.get(clave)
    if constructor is None:
        raise KeyError(f"No hay plan de cascada definido para '{clave}'")
    return constructor(objeto)


def aplicar(plan):
    """Ejecuta el plan: borra los grupos en orden y despues el padre.

    Devuelve un diccionario con la cantidad de documentos eliminados por
    tipo, incluyendo el propio padre bajo su ``clave``.
    """
    eliminados = {}
    for grupo in plan.grupos:
        if not grupo.elementos:
            continue
        ids = [a_texto(elemento.pk) for elemento in grupo.elementos]
        grupo.modelo.objects.filter(pk__in=ids).delete()
        eliminados[grupo.singular] = eliminados.get(grupo.singular, 0) + grupo.cantidad

    plan.padre.delete()
    eliminados[plan.clave] = eliminados.get(plan.clave, 0) + 1
    return eliminados
