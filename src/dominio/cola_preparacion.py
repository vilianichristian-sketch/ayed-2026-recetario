"""Clase ColaPreparacion: recetas esperando a ser cocinadas (usa una Cola)."""

from src.excepciones import ColaVaciaError
from src.tads.cola import Cola


class ColaPreparacion:
    """La primera receta que entra a la cola es la primera que se prepara (FIFO)."""

    def __init__(self):
        self._cola = Cola()

    def agregar(self, receta):
        """Encolar."""
        self._cola.encolar(receta)

    def siguiente(self):
        """Desencolar: saca y devuelve la próxima receta a preparar."""
        if self._cola.esta_vacia():
            raise ColaVaciaError("No hay recetas en la cola de preparación.")
        return self._cola.desencolar()

    def proxima(self):
        """Ver frente: la próxima receta, sin sacarla."""
        if self._cola.esta_vacia():
            raise ColaVaciaError("No hay recetas en la cola de preparación.")
        return self._cola.ver_frente()

    def vaciar(self):
        self._cola = Cola()

    def esta_vacia(self):
        return self._cola.esta_vacia()

    def cantidad(self):
        return self._cola.tamanio()

    def __iter__(self):
        """Del frente (próxima a preparar) al final."""
        return iter(self._cola)
