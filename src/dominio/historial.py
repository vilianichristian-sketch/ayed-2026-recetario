"""Clase Historial: recetas cocinadas, la más reciente arriba (usa una Pila)."""

from src.excepciones import PilaVaciaError
from src.tads.pila import Pila


class Historial:
    """Historial de recetas cocinadas. Deshacer saca la última registrada (LIFO)."""

    def __init__(self):
        self._pila = Pila()

    def registrar(self, receta):
        """Push: anota que se cocinó la receta."""
        self._pila.apilar(receta)

    def deshacer(self):
        """Pop: borra del historial la última receta cocinada y la devuelve."""
        if self._pila.esta_vacia():
            raise PilaVaciaError("No hay recetas cocinadas en el historial para deshacer.")
        return self._pila.desapilar()

    def ultima(self):
        """Peek: la última receta cocinada, sin sacarla."""
        if self._pila.esta_vacia():
            raise PilaVaciaError("Todavía no se cocinó ninguna receta.")
        return self._pila.ver_tope()

    def esta_vacio(self):
        return self._pila.esta_vacia()

    def cantidad(self):
        return self._pila.tamanio()

    def __iter__(self):
        """De la más reciente a la más vieja."""
        return iter(self._pila)
