"""Clase MenuSemanal: la colección principal del dominio (una receta por día)."""

from src.excepciones import ColeccionLlenaError, ColeccionVaciaError, ItemNoEncontradoError

DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")


class MenuSemanal:
    """Menú de la semana: hasta 7 recetas, la posición indica el día.

    E2: usa una list de Python por dentro (en E3 pasa a ListaEnlazada).
    """

    def __init__(self, tope=len(DIAS)):
        self.recetas = []
        self.tope = tope

    def agregar(self, receta):
        if len(self.recetas) >= self.tope:
            raise ColeccionLlenaError(
                f"El menú semanal está completo (máximo {self.tope} recetas, una por día)."
            )
        self.recetas.append(receta)

    def quitar(self, id_receta):
        """Quita la primera aparición de la receta con ese id y la devuelve."""
        if not self.recetas:
            raise ColeccionVaciaError("El menú semanal está vacío.")
        for receta in self.recetas:
            if receta.id == id_receta:
                self.recetas.remove(receta)
                return receta
        raise ItemNoEncontradoError(f"La receta {id_receta} no está en el menú semanal.")

    def dias_y_recetas(self):
        """Pares (día, receta) en el orden en que se agregaron."""
        return list(zip(DIAS, self.recetas))

    def cantidad(self):
        return len(self.recetas)

    def esta_vacio(self):
        return len(self.recetas) == 0
