"""Clase SistemaRecetario: agrupa el catálogo y las colecciones del dominio.

El CLI solo habla con esta clase y con los métodos públicos de los objetos que
expone; nunca toca atributos internos (los que empiezan con _).
"""

from src.dominio.cola_preparacion import ColaPreparacion
from src.dominio.historial import Historial
from src.dominio.ingrediente import Ingrediente
from src.dominio.menu_semanal import MenuSemanal
from src.dominio.receta import Receta
from src.dominio.recetario import Recetario
from src.excepciones import ColeccionVaciaError


class SistemaRecetario:
    def __init__(self, recetario=None):
        self._recetario = recetario if recetario is not None else Recetario()
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

    # ------------------------------------------------------------ ABM del catálogo (E5)
    def alta_receta(self, nombre, tiempo_min, dificultad, categoria, ingredientes=(), ids_subrecetas=()):
        """Crea una receta con el próximo id libre.

        ingredientes: tuplas (nombre, cantidad, unidad). Todo se valida antes de
        tocar el catálogo, así un dato inválido no deja una receta a medias.
        """
        receta = Receta(self._recetario.siguiente_id(), nombre, tiempo_min, dificultad, categoria)
        for nombre_ing, cantidad, unidad in ingredientes:
            receta.agregar_ingrediente(Ingrediente(nombre_ing, cantidad, unidad))
        for id_sub in ids_subrecetas:
            self._recetario.obtener(id_sub)  # valida que exista antes de dar el alta
        self._recetario.agregar(receta)
        for id_sub in ids_subrecetas:
            self._recetario.agregar_subreceta(receta.id, id_sub)
        return receta

    def baja_receta(self, id_receta):
        """Borra la receta del catálogo y del menú semanal (la cola y el historial son registro de lo hecho)."""
        receta = self._recetario.eliminar(id_receta)
        self._menu.quitar_todas(id_receta)
        return receta

    def modificar_receta(self, id_receta, **cambios):
        return self._recetario.modificar(id_receta, **cambios)

    def reemplazar_recetario(self, recetario):
        """Cambia el catálogo por uno recién cargado de un archivo.

        El menú y la cola apuntan a objetos Receta del catálogo anterior: el
        menú se vuelve a armar con las recetas del catálogo nuevo que tengan el
        mismo id, y la cola se vacía. Devuelve True si se vació algo de la cola.
        """
        ids_menu = []
        for receta in self._menu:
            ids_menu.append(receta.id)
        habia_cola = not self._cola.esta_vacia()
        self._recetario = recetario
        recetas = []
        for id_receta in ids_menu:
            if recetario.existe(id_receta):
                recetas.append(recetario.obtener(id_receta))
        self.restaurar_menu(recetas)
        self._cola.vaciar()
        return habia_cola

    def restaurar_menu(self, recetas):
        """Arma el menú semanal con estas recetas (por ejemplo, las leídas del archivo).

        Si vinieran más que el tope, las que sobran se ignoran. Devuelve cuántas se cargaron.
        """
        self._menu.vaciar()
        for receta in recetas:
            if self._menu.esta_lleno():
                break
            self._menu.agregar(receta)
        return self._menu.cantidad()
