"""Excepciones propias del sistema.

Todas heredan de RecetarioError, así el menú principal puede tener una red de
seguridad (`except RecetarioError`) sin usar nunca un `except:` pelado.
"""


class RecetarioError(Exception):
    """Base de todas las excepciones propias del TP."""


class ItemNoEncontradoError(RecetarioError):
    """No existe una receta (o un elemento de una colección) con ese id."""


class ColeccionLlenaError(RecetarioError):
    """Se quiso agregar a una colección que llegó a su tope."""


class ColeccionVaciaError(RecetarioError):
    """Se quiso sacar algo de una colección vacía."""


class PilaVaciaError(RecetarioError):
    """Se quiso desapilar / ver el tope de una pila vacía."""


class ColaVaciaError(RecetarioError):
    """Se quiso desencolar / ver el frente de una cola vacía."""


class ArchivoInvalidoError(RecetarioError):
    """El archivo no existe, está truncado o no tiene el formato esperado."""


class SubrecetaFaltanteError(RecetarioError):
    """Una receta referencia como sub-receta a un id que no está en el catálogo."""


class CicloSubrecetasError(RecetarioError):
    """Una receta termina usándose a sí misma (A usa B, B usa A): la recursión no terminaría."""


class DatoInvalidoError(RecetarioError):
    """Un valor no es válido para una receta (vacío, con comas, tiempo negativo, etc.)."""
