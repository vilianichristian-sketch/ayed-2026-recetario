"""Clase Recetario: el libro de recetas (catálogo)."""

from src.dominio.datos_iniciales import INGREDIENTES, RECETAS, SUBRECETAS
from src.dominio.ingrediente import Ingrediente
from src.dominio.receta import Receta
from src.excepciones import DatoInvalidoError, ItemNoEncontradoError
from src.tads.lista_enlazada import ListaEnlazada


class Recetario:
    """Catálogo de recetas + relación "receta usa sub-receta".

    - _recetas: ListaEnlazada con todas las recetas (el listado usa su iterador).
    - _subrecetas: dict id de receta -> lista de ids de sus sub-recetas.
    """

    def __init__(self):
        self._recetas = ListaEnlazada()
        self._subrecetas = {}

    def cargar_datos_iniciales(self):
        """Arma el catálogo desde las tuplas de datos_iniciales.py (los .txt se leen en E5)."""
        for id_receta, nombre, tiempo, dificultad, categoria in RECETAS:
            self.agregar(Receta(id_receta, nombre, tiempo, dificultad, categoria))
        for id_receta, nombre, cantidad, unidad in INGREDIENTES:
            self.obtener(id_receta).agregar_ingrediente(Ingrediente(nombre, cantidad, unidad))
        for id_receta, id_sub in SUBRECETAS:
            self.agregar_subreceta(id_receta, id_sub)

    # ------------------------------------------------------------ consultas
    def obtener(self, id_receta):
        """Devuelve la receta con ese id. Si no existe lanza ItemNoEncontradoError."""
        receta = self._recetas.buscar_por(lambda r: r.id == id_receta)
        if receta is None:
            raise ItemNoEncontradoError(f"No existe una receta con id {id_receta}.")
        return receta

    def existe(self, id_receta):
        return self._recetas.buscar_por(lambda r: r.id == id_receta) is not None

    def subrecetas_de(self, id_receta):
        """Ids de las sub-recetas directas (tupla vacía si no usa ninguna)."""
        return tuple(self._subrecetas.get(id_receta, ()))

    def cantidad(self):
        return self._recetas.tamanio()

    def esta_vacio(self):
        return self._recetas.esta_vacia()

    def __iter__(self):
        """Permite `for receta in recetario`: usa el iterador de la ListaEnlazada."""
        return iter(self._recetas)

    # ------------------------------------------------------------ altas
    def agregar(self, receta):
        if self.existe(receta.id):
            raise DatoInvalidoError(f"Ya existe una receta con id {receta.id}.")
        self._recetas.insertar_al_final(receta)

    def agregar_subreceta(self, id_receta, id_subreceta):
        """Registra que la receta id_receta usa a la receta id_subreceta."""
        self.obtener(id_receta)      # validan que existan las dos
        self.obtener(id_subreceta)
        if id_receta not in self._subrecetas:
            self._subrecetas[id_receta] = []
        self._subrecetas[id_receta].append(id_subreceta)
