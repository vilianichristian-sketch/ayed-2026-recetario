"""Clase SistemaRecetario: agrupa el catálogo y las colecciones del dominio.

El CLI solo habla con esta clase y con los métodos públicos de los objetos que
expone; nunca toca atributos internos (los que empiezan con _).
"""

from src.dominio.cola_preparacion import ColaPreparacion
from src.dominio.historial import Historial
from src.dominio.menu_semanal import MenuSemanal
from src.dominio.recetario import Recetario
from src.excepciones import ColeccionVaciaError


class SistemaRecetario:
    def __init__(self, recetario=None):
        if recetario is None:
            recetario = Recetario()
            recetario.cargar_datos_iniciales()
        self._recetario = recetario
        self._menu = MenuSemanal()
        self._historial = Historial()
        self._cola = ColaPreparacion()

    # ------------------------------------------------------------ acceso de solo lectura
    @property
    def recetario(self):
        return self._recetario

    @property
    def menu(self):
        return self._menu

    @property
    def historial(self):
        return self._historial

    @property
    def cola(self):
        return self._cola

    # ------------------------------------------------------------ operaciones que cruzan colecciones
    def preparar_siguiente(self):
        """Desencola la próxima receta de la cola y la registra en el historial (la apila)."""
        receta = self._cola.siguiente()
        self._historial.registrar(receta)
        return receta

    def encolar_menu(self):
        """Manda todas las recetas del menú semanal a la cola de preparación, en orden."""
        if self._menu.esta_vacio():
            raise ColeccionVaciaError("El menú semanal está vacío: no hay nada para encolar.")
        cantidad = 0
        for receta in self._menu:
            self._cola.agregar(receta)
            cantidad += 1
        return cantidad
