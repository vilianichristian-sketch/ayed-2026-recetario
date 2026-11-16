"""Clase MenuSemanal: la colección principal del dominio (una receta por día)."""

from src.excepciones import ColeccionLlenaError, ColeccionVaciaError, ItemNoEncontradoError
from src.tads.lista_enlazada import ListaEnlazada

DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")


class MenuSemanal:
    """Menú de la semana: hasta 7 recetas sobre una ListaEnlazada; la posición es el día.

    Invariante: 0 <= cantidad() <= tope.
    """

    def __init__(self, tope=len(DIAS)):
        self._recetas = ListaEnlazada()
        self._tope = tope

    @property
    def tope(self):
        return self._tope

    # ------------------------------------------------------------ ABM
    def agregar(self, receta):
        """Alta: agrega la receta en el próximo día libre."""
        if self.esta_lleno():
            raise ColeccionLlenaError(
                f"El menú semanal está completo (máximo {self._tope} recetas, una por día)."
            )
        self._recetas.insertar_al_final(receta)

    def quitar(self, id_receta):
        """Baja: quita la primera aparición de la receta con ese id y la devuelve."""
        if self.esta_vacio():
            raise ColeccionVaciaError("El menú semanal está vacío.")
        receta = self._recetas.buscar_por(lambda r: r.id == id_receta)
        if receta is None:
            raise ItemNoEncontradoError(f"La receta {id_receta} no está en el menú semanal.")
        self._recetas.eliminar(receta)
        return receta

    def reemplazar_dia(self, numero_dia, receta):
        """Modificación: cambia la receta del día numero_dia (1 = Lunes). Devuelve la anterior."""
        if self.esta_vacio():
            raise ColeccionVaciaError("El menú semanal está vacío.")
        if numero_dia < 1 or numero_dia > self.cantidad():
            raise ItemNoEncontradoError(
                f"No hay receta cargada para el día {numero_dia} (hay {self.cantidad()} días cargados)."
            )
        anterior = self._recetas.obtener_en(numero_dia - 1)
        self._recetas.reemplazar_en(numero_dia - 1, receta)
        return anterior

    def quitar_todas(self, id_receta):
        """Quita todas las apariciones de una receta (se usa si la receta se borra del catálogo)."""
        while self._recetas.buscar_por(lambda r: r.id == id_receta) is not None:
            self.quitar(id_receta)

    def vaciar(self):
        self._recetas.vaciar()

    # ------------------------------------------------------------ consultas
    def __iter__(self):
        return iter(self._recetas)

    def dias_y_recetas(self):
        """Genera pares (día, receta) en el orden en que se agregaron."""
        numero = 0
        for receta in self._recetas:
            yield DIAS[numero], receta
            numero += 1

    def tiempo_total(self):
        total = 0
        for receta in self._recetas:
            total += receta.tiempo_min
        return total

    def cantidad(self):
        return self._recetas.tamanio()

    def esta_vacio(self):
        return self._recetas.esta_vacia()

    def esta_lleno(self):
        return self._recetas.tamanio() >= self._tope
