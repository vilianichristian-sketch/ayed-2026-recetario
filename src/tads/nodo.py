class Nodo:
    """Eslabón de la lista enlazada: un dato y la referencia al nodo siguiente.

    siguiente es None cuando el nodo es el último de la cadena.
    Solo lo usan ListaEnlazada (y su iterador); el resto del programa no ve nodos.
    """

    def __init__(self, dato, siguiente=None):
        self.dato = dato
        self.siguiente = siguiente
