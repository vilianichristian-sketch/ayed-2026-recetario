"""Clase Recetario: el libro de recetas (catálogo)."""

from src.algoritmos.busqueda import busqueda_binaria, busqueda_lineal, busqueda_lineal_todos
from src.algoritmos.ordenamiento import ALGORITMOS
from src.dominio.datos_iniciales import INGREDIENTES, RECETAS, SUBRECETAS
from src.dominio.ingrediente import Ingrediente
from src.dominio.normalizar import normalizar
from src.dominio.receta import Receta
from src.excepciones import DatoInvalidoError, ItemNoEncontradoError
from src.tads.lista_enlazada import ListaEnlazada

# Criterios de ordenamiento: nombre que ve el usuario -> función clave.
CRITERIOS = {
    "id": lambda receta: receta.id,
    "nombre": lambda receta: receta.nombre_normalizado,
    "tiempo": lambda receta: receta.tiempo_min,
    "dificultad": lambda receta: receta.nivel_dificultad(),
}


class Recetario:
    """Catálogo de recetas + relación "receta usa sub-receta".

    - _recetas: ListaEnlazada con todas las recetas, en el orden actual
      (el listado usa su iterador).
    - _indice: dict id -> Receta. Estructura auxiliar para encontrar una receta
      por id en O(1) en lugar de recorrer la lista (ver informe §5).
    - _subrecetas: dict id de receta -> lista de ids de sus sub-recetas.
    - _orden: criterio por el que está ordenada _recetas ("id" al cargar).
      La búsqueda binaria por nombre solo se usa si _orden == "nombre".
    """

    def __init__(self):
        self._recetas = ListaEnlazada()
        self._indice = {}
        self._subrecetas = {}
        self._orden = "id"

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
        """Receta con ese id usando el índice dict: O(1). Si no existe: ItemNoEncontradoError."""
        receta = self._indice.get(id_receta)
        if receta is None:
            raise ItemNoEncontradoError(f"No existe una receta con id {id_receta}.")
        return receta

    def obtener_sin_indice(self, id_receta):
        """Lo mismo que obtener() pero recorriendo la lista (búsqueda lineal): O(n).

        Se deja para comparar en el informe qué se gana con el índice.
        """
        receta = busqueda_lineal(self._recetas, id_receta, lambda r: r.id)
        if receta is None:
            raise ItemNoEncontradoError(f"No existe una receta con id {id_receta}.")
        return receta

    def existe(self, id_receta):
        return id_receta in self._indice

    def subrecetas_de(self, id_receta):
        """Ids de las sub-recetas directas (tupla vacía si no usa ninguna)."""
        return tuple(self._subrecetas.get(id_receta, ()))

    def cantidad(self):
        return self._recetas.tamanio()

    def esta_vacio(self):
        return self._recetas.esta_vacia()

    def a_lista(self):
        """Copia de las recetas en el orden actual, como list de Python. O(n)."""
        return self._recetas.a_lista()

    @property
    def orden_actual(self):
        return self._orden

    def __iter__(self):
        """Permite `for receta in recetario`: usa el iterador de la ListaEnlazada."""
        return iter(self._recetas)

    # ------------------------------------------------------------ altas
    def agregar(self, receta):
        """Alta al final del catálogo (O(1)) y en el índice (O(1))."""
        if self.existe(receta.id):
            raise DatoInvalidoError(f"Ya existe una receta con id {receta.id}.")
        if self._orden is not None and not self._recetas.esta_vacia():
            clave = CRITERIOS[self._orden]
            if clave(receta) < clave(self._recetas.ultimo()):
                self._orden = None  # quedó una receta "fuera de lugar": ya no está ordenado
        self._recetas.insertar_al_final(receta)
        self._indice[receta.id] = receta

    def agregar_subreceta(self, id_receta, id_subreceta):
        """Registra que la receta id_receta usa a la receta id_subreceta."""
        self.obtener(id_receta)      # validan que existan las dos
        self.obtener(id_subreceta)
        if id_receta not in self._subrecetas:
            self._subrecetas[id_receta] = []
        self._subrecetas[id_receta].append(id_subreceta)

    # ------------------------------------------------------------ búsquedas (E4)
    def buscar_lineal_por_nombre(self, nombre):
        """Recorre el catálogo de a uno comparando nombres normalizados. O(n)."""
        return busqueda_lineal(self._recetas, normalizar(nombre), CRITERIOS["nombre"])

    def buscar_binaria_por_nombre(self, nombre):
        """Búsqueda binaria por nombre. Devuelve (receta o None, se_reordeno).

        Si el catálogo no está ordenado por nombre, primero lo ordena (inserción)
        y lo avisa con se_reordeno=True: nunca corre la binaria sobre datos
        desordenados (daría falsos "no encontrado").
        """
        se_reordeno = False
        if self._orden != "nombre":
            self.ordenar("nombre", "insercion")
            se_reordeno = True
        # La binaria necesita índices: se copia la lista enlazada a una list (O(n)).
        ordenadas = self._recetas.a_lista()
        receta = busqueda_binaria(ordenadas, normalizar(nombre), CRITERIOS["nombre"])
        return receta, se_reordeno

    def buscar_por_texto_en_nombre(self, texto):
        """Todas las recetas cuyo nombre contiene el texto (para sugerencias). O(n)."""
        buscado = normalizar(texto)
        return busqueda_lineal_todos(self._recetas, lambda r: buscado in r.nombre_normalizado)

    def filtrar_por_categoria(self, categoria):
        """Búsqueda lineal de todas las recetas de una categoría. O(n)."""
        buscada = normalizar(categoria)
        return busqueda_lineal_todos(self._recetas, lambda r: normalizar(r.categoria) == buscada)

    def filtrar_por_ingrediente(self, ingrediente):
        """Búsqueda lineal de todas las recetas que usan un ingrediente (propio). O(n · ingredientes)."""
        return busqueda_lineal_todos(self._recetas, lambda r: r.usa_ingrediente(ingrediente))

    def categorias(self):
        """Categorías distintas, en el orden en que aparecen."""
        vistas = []
        for receta in self._recetas:
            if busqueda_lineal(vistas, receta.categoria) is None:
                vistas.append(receta.categoria)
        return vistas

    # ------------------------------------------------------------ ordenamiento (E4)
    def ordenar(self, criterio, algoritmo):
        """Reordena el catálogo con un algoritmo propio según un criterio.

        La lista enlazada no tiene índices: se copia a una list (O(n)), se ordena
        con el algoritmo elegido y se vuelve a armar la lista enlazada (O(n)).
        """
        if criterio not in CRITERIOS:
            raise DatoInvalidoError(f"Criterio de orden desconocido: {criterio}.")
        if algoritmo not in ALGORITMOS:
            raise DatoInvalidoError(f"Algoritmo de orden desconocido: {algoritmo}.")
        _nombre, funcion = ALGORITMOS[algoritmo]
        ordenadas = funcion(self._recetas.a_lista(), CRITERIOS[criterio])
        nueva = ListaEnlazada()
        for receta in ordenadas:
            nueva.insertar_al_final(receta)
        self._recetas = nueva
        self._orden = criterio
