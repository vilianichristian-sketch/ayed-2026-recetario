"""Clase Ingrediente: un renglón de la lista de ingredientes de una receta."""

from src.excepciones import DatoInvalidoError


def _validar_texto(valor, campo):
    if not isinstance(valor, str) or valor.strip() == "":
        raise DatoInvalidoError(f"El {campo} del ingrediente no puede quedar vacío.")
    if "," in valor:
        raise DatoInvalidoError(f"El {campo} del ingrediente no puede tener comas.")
    return valor.strip()


class Ingrediente:
    """Ingrediente de una receta: nombre, cantidad y unidad (ej. 50 g de perejil).

    Es inmutable: los atributos son "privados" (_) y solo tienen property de
    lectura. Para cambiar una cantidad se crea otro Ingrediente.
    """

    def __init__(self, nombre, cantidad, unidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, (int, float)) or cantidad <= 0:
            raise DatoInvalidoError("La cantidad del ingrediente tiene que ser un número mayor a 0.")
        self._nombre = _validar_texto(nombre, "nombre")
        self._cantidad = cantidad
        self._unidad = _validar_texto(unidad, "unidad")

    @property
    def nombre(self):
        return self._nombre

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def unidad(self):
        return self._unidad

    def __str__(self):
        return f"{self._cantidad:g} {self._unidad} de {self._nombre}"

    def __repr__(self):
        return f"Ingrediente({self._nombre!r}, {self._cantidad!r}, {self._unidad!r})"
