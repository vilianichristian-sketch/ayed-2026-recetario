"""Clase Recetario: el libro de recetas (catálogo)."""

from src.dominio.datos_iniciales import INGREDIENTES, RECETAS, SUBRECETAS
from src.dominio.ingrediente import Ingrediente
from src.dominio.receta import Receta
from src.excepciones import ItemNoEncontradoError


class Recetario:
    """Catálogo de recetas + relación "receta usa sub-receta".

    E2: las recetas viven en una list de Python (en E3 pasa a ListaEnlazada).
    subrecetas es un dict: id de receta -> lista de ids de sus sub-recetas.
    """

    def __init__(self):
        self.recetas = []
        self.subrecetas = {}

    def cargar_datos_iniciales(self):
        """Arma el catálogo desde las tuplas de datos_iniciales.py (los .txt se leen en E5)."""
        for id_receta, nombre, tiempo, dificultad, categoria in RECETAS:
            self.agregar(Receta(id_receta, nombre, tiempo, dificultad, categoria))
        for id_receta, nombre, cantidad, unidad in INGREDIENTES:
            self.obtener(id_receta).agregar_ingrediente(Ingrediente(nombre, cantidad, unidad))
        for id_receta, id_sub in SUBRECETAS:
            self.agregar_subreceta(id_receta, id_sub)

    def agregar(self, receta):
        self.recetas.append(receta)

    def agregar_subreceta(self, id_receta, id_subreceta):
        """Registra que la receta id_receta usa a la receta id_subreceta."""
        if id_receta not in self.subrecetas:
            self.subrecetas[id_receta] = []
        self.subrecetas[id_receta].append(id_subreceta)

    def obtener(self, id_receta):
        """Devuelve la receta con ese id. Si no existe lanza ItemNoEncontradoError."""
        for receta in self.recetas:
            if receta.id == id_receta:
                return receta
        raise ItemNoEncontradoError(f"No existe una receta con id {id_receta}.")

    def subrecetas_de(self, id_receta):
        """Ids de las sub-recetas directas (lista vacía si no usa ninguna)."""
        return self.subrecetas.get(id_receta, [])

    def cantidad(self):
        return len(self.recetas)

    def __iter__(self):
        return iter(self.recetas)
