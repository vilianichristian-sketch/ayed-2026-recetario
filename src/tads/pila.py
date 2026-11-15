from src.excepciones import PilaVaciaError
from src.tads.lista_enlazada import ListaEnlazada


class Pila:
    """TAD pila (LIFO) implementado sobre ListaEnlazada.

    El tope de la pila es la cabeza de la lista: apilar = insertar_al_inicio y
    desapilar = eliminar_primero, las dos O(1).

    Invariante: el último dato apilado que todavía no se desapiló es el tope.
    """

    def __init__(self):
        self._items = ListaEnlazada()

    def apilar(self, dato):
        self._items.insertar_al_inicio(dato)

    def desapilar(self):
        if self.esta_vacia():
            raise PilaVaciaError("La pila está vacía.")
        return self._items.eliminar_primero()

    def ver_tope(self):
        if self.esta_vacia():
            raise PilaVaciaError("La pila está vacía.")
        return self._items.primero()

    def esta_vacia(self):
        return self._items.esta_vacia()

    def tamanio(self):
        return self._items.tamanio()

    def __len__(self):
        return self._items.tamanio()

    def __iter__(self):
        """Recorre del tope a la base, sin modificar la pila."""
        return iter(self._items)
