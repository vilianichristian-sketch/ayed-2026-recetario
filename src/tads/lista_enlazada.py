from src.excepciones import ColeccionVaciaError
from src.tads.nodo import Nodo


class IteradorLista:
    """Recorre la lista nodo por nodo. Python lo usa en cada `for x in lista`."""

    def __init__(self, primer_nodo):
        self._actual = primer_nodo

    def __iter__(self):
        return self

    def __next__(self):
        if self._actual is None:
            raise StopIteration  # se terminó la lista: el for corta solo
        dato = self._actual.dato
        self._actual = self._actual.siguiente
        return dato


class ListaEnlazada:
    """TAD lista simplemente enlazada. No usa list de Python por debajo.

    Guarda referencia al primer nodo (_cabeza) y al último (_ultimo) para que
    insertar al final sea O(1).

    Invariante:
      - _tamanio == 0  <=>  _cabeza is None  <=>  _ultimo is None
      - partiendo de _cabeza y siguiendo .siguiente se visitan exactamente
        _tamanio nodos; el último visitado es _ultimo y su .siguiente es None.
    """

    def __init__(self):
        self._cabeza = None
        self._ultimo = None
        self._tamanio = 0

    # ------------------------------------------------------------ consultas
    def esta_vacia(self):
        return self._tamanio == 0

    def tamanio(self):
        return self._tamanio

    def __len__(self):
        return self._tamanio

    def __iter__(self):
        return IteradorLista(self._cabeza)

    def primero(self):
        """Dato del primer nodo, sin sacarlo. O(1)."""
        if self.esta_vacia():
            raise ColeccionVaciaError("La lista está vacía.")
        return self._cabeza.dato

    def buscar(self, dato):
        """Devuelve el dato guardado que sea igual (==) a `dato`, o None. O(n)."""
        return self.buscar_por(lambda elemento: elemento == dato)

    def buscar_por(self, condicion):
        """Devuelve el primer dato para el que condicion(dato) es True, o None. O(n)."""
        actual = self._cabeza
        while actual is not None:
            if condicion(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None

    def obtener_en(self, posicion):
        """Dato en la posición indicada (0 = primero). O(n): hay que recorrer."""
        return self._nodo_en(posicion).dato

    # ------------------------------------------------------------ inserción
    def insertar_al_inicio(self, dato):
        """O(1): el nodo nuevo pasa a ser la cabeza."""
        nuevo = Nodo(dato, self._cabeza)
        self._cabeza = nuevo
        if self._ultimo is None:  # la lista estaba vacía
            self._ultimo = nuevo
        self._tamanio += 1

    def insertar_al_final(self, dato):
        """O(1) gracias a la referencia _ultimo."""
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self._cabeza = nuevo
        else:
            self._ultimo.siguiente = nuevo
        self._ultimo = nuevo
        self._tamanio += 1

    def insertar_ordenado(self, dato, clave=lambda x: x):
        """Inserta dejando la lista ordenada en forma ascendente según clave(dato).

        Si hay claves iguales, el nuevo queda después de los existentes (estable). O(n).
        """
        valor = clave(dato)
        if self.esta_vacia() or valor < clave(self._cabeza.dato):
            self.insertar_al_inicio(dato)
            return
        actual = self._cabeza
        while actual.siguiente is not None and clave(actual.siguiente.dato) <= valor:
            actual = actual.siguiente
        nuevo = Nodo(dato, actual.siguiente)
        actual.siguiente = nuevo
        if nuevo.siguiente is None:
            self._ultimo = nuevo
        self._tamanio += 1

    # ------------------------------------------------------------ eliminación / modificación
    def eliminar_primero(self):
        """Saca el primer nodo y devuelve su dato. O(1)."""
        if self.esta_vacia():
            raise ColeccionVaciaError("La lista está vacía.")
        dato = self._cabeza.dato
        self._cabeza = self._cabeza.siguiente
        if self._cabeza is None:
            self._ultimo = None
        self._tamanio -= 1
        return dato

    def eliminar(self, dato):
        """Elimina la primera aparición de `dato` (comparando con ==).

        Devuelve True si lo encontró y lo sacó, False si no estaba. O(n).
        """
        anterior = None
        actual = self._cabeza
        while actual is not None:
            if actual.dato == dato:
                if anterior is None:          # caso 1: es la cabeza
                    self._cabeza = actual.siguiente
                else:                         # caso 2: está en el medio o al final
                    anterior.siguiente = actual.siguiente
                if actual is self._ultimo:
                    self._ultimo = anterior
                self._tamanio -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False                          # caso 3: no estaba

    def reemplazar_en(self, posicion, dato):
        """Cambia el dato de la posición indicada (0 = primero). O(n)."""
        self._nodo_en(posicion).dato = dato

    def vaciar(self):
        self._cabeza = None
        self._ultimo = None
        self._tamanio = 0

    # ------------------------------------------------------------ conversión
    def a_lista(self):
        """Copia los datos a una list de Python (para los algoritmos que usan índices). O(n)."""
        copia = []
        for dato in self:
            copia.append(dato)
        return copia

    # ------------------------------------------------------------ auxiliar
    def _nodo_en(self, posicion):
        if posicion < 0 or posicion >= self._tamanio:
            raise IndexError(f"Posición {posicion} fuera de rango (tamaño {self._tamanio}).")
        actual = self._cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        return actual

    def __str__(self):
        partes = []
        for dato in self:
            partes.append(str(dato))
        return "[" + " -> ".join(partes) + "]"
