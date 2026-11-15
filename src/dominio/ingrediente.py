"""Clase Ingrediente: un renglón de la lista de ingredientes de una receta."""


class Ingrediente:
    """Ingrediente de una receta: nombre, cantidad y unidad (ej. 50 g de perejil)."""

    def __init__(self, nombre, cantidad, unidad):
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad = unidad

    def __str__(self):
        return f"{self.cantidad:g} {self.unidad} de {self.nombre}"
