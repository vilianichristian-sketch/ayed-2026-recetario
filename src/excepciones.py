"""Excepciones propias del sistema."""


class ItemNoEncontradoError(Exception):
    """No existe una receta (o un elemento de una colección) con ese id."""


class ColeccionLlenaError(Exception):
    """Se quiso agregar a una colección que llegó a su tope."""


class ColeccionVaciaError(Exception):
    """Se quiso sacar algo de una colección vacía."""


class PilaVaciaError(Exception):
    """Se quiso desapilar / ver el tope de una pila vacía."""


class ColaVaciaError(Exception):
    """Se quiso desencolar / ver el frente de una cola vacía."""


class ArchivoInvalidoError(Exception):
    """El archivo no existe, está truncado o no tiene el formato esperado."""


class SubrecetaFaltanteError(Exception):
    """Una receta referencia como sub-receta a un id que no está en el catálogo."""


class CicloSubrecetasError(Exception):
    """Una receta termina usándose a sí misma (A usa B, B usa A): la recursión no terminaría."""
