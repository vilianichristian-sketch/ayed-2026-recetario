from src.excepciones import ColaVaciaError
from src.tads.lista_enlazada import ListaEnlazada


class Cola:
    """TAD cola (FIFO) implementado sobre ListaEnlazada.

    Se encola al final de la lista (O(1) porque la lista guarda _ultimo) y se
    desencola desde la cabeza (O(1)).

    Invariante: el frente es el dato más antiguo que todavía no se desencoló.
    """

    def __init__(self):
        self._items = ListaEnlazada()

    def encolar(self, dato):
        self._items.insertar_al_final(dato)

    def desencolar(self):
        if self.esta_vacia():
            raise ColaVaciaError("La cola está vacía.")
        return self._items.eliminar_primero()

    def ver_frente(self):
        if self.esta_vacia():
            raise ColaVaciaError("La cola está vacía.")
        return self._items.primero()

    def esta_vacia(self):
        return self._items.esta_vacia()

    def tamanio(self):
        return self._items.tamanio()

    def __len__(self):
        return self._items.tamanio()

    def __iter__(self):
        """Recorre del frente al final, sin modificar la cola."""
        return iter(self._items)
