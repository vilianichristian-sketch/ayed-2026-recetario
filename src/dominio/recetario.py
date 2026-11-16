"""Clase Recetario: el libro de recetas (catálogo)."""

from src.algoritmos.busqueda import busqueda_binaria, busqueda_lineal, busqueda_lineal_todos
from src.algoritmos.ordenamiento import ALGORITMOS
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

    def posicion_de(self, id_receta):
        """Posición (0-based) de la receta en el orden actual, recorriendo con el iterador. O(n).

        Como el .bin se guarda en el mismo orden que la lista, es también la
        posición de su registro en el binario (acceso directo).
        """
        posicion = 0
        for receta in self._recetas:
            if receta.id == id_receta:
                return posicion
            posicion += 1
        raise ItemNoEncontradoError(f"No existe una receta con id {id_receta}.")

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
        if id_receta == id_subreceta:
            raise DatoInvalidoError("Una receta no puede ser sub-receta de sí misma.")
        if id_receta not in self._subrecetas:
            self._subrecetas[id_receta] = []
        if busqueda_lineal(self._subrecetas[id_receta], id_subreceta) is None:  # sin repetidos
            self._subrecetas[id_receta].append(id_subreceta)

    def siguiente_id(self):
        """Id libre para una receta nueva: el mayor id + 1. O(n)."""
        mayor = 0
        for receta in self._recetas:
            if receta.id > mayor:
                mayor = receta.id
        return mayor + 1

    def relaciones_subrecetas(self):
        """Pares (id_receta, id_subreceta), para guardarlos en subrecetas.txt."""
        pares = []
        for id_receta, ids_sub in self._subrecetas.items():
            for id_sub in ids_sub:
                pares.append((id_receta, id_sub))
        return pares

    def recetas_que_usan(self, id_subreceta):
        """Recetas que tienen a id_subreceta como sub-receta directa. O(relaciones)."""
        usan = []
        for id_receta, ids_sub in self._subrecetas.items():
            if busqueda_lineal(ids_sub, id_subreceta) is not None:
                usan.append(self.obtener(id_receta))
        return usan

    # ------------------------------------------------------------ bajas y modificaciones (E5)
    def eliminar(self, id_receta):
        """Baja: saca la receta de la lista, del índice y sus relaciones. Devuelve la receta.

        No se permite borrar una receta que otra usa como sub-receta (quedaría
        una sub-receta faltante y la recursión fallaría).
        """
        receta = self.obtener(id_receta)
        usan = self.recetas_que_usan(id_receta)
        if usan:
            nombres = []
            for otra in usan:
                nombres.append(otra.nombre)
            raise DatoInvalidoError(
                f"No se puede borrar '{receta.nombre}': es sub-receta de {', '.join(nombres)}."
            )
        self._recetas.eliminar(receta)
        del self._indice[id_receta]
        self._subrecetas.pop(id_receta, None)
        return receta

    def modificar(self, id_receta, nombre=None, tiempo_min=None, dificultad=None, categoria=None):
        """Modificación: cambia los campos que no son None. Devuelve la receta.

        Primero se validan todos los valores nuevos armando una Receta de prueba:
        si alguno es inválido no se cambia nada (no queda a medio modificar).
        """
        receta = self.obtener(id_receta)
        nuevo_nombre = receta.nombre if nombre is None else nombre
        nuevo_tiempo = receta.tiempo_min if tiempo_min is None else tiempo_min
        nueva_dificultad = receta.dificultad if dificultad is None else dificultad
        nueva_categoria = receta.categoria if categoria is None else categoria
        Receta(id_receta, nuevo_nombre, nuevo_tiempo, nueva_dificultad, nueva_categoria)  # valida
        receta.nombre = nuevo_nombre
        receta.tiempo_min = nuevo_tiempo
        receta.dificultad = nueva_dificultad
        receta.categoria = nueva_categoria
        if self._orden != "id":
            self._orden = None  # el campo cambiado puede haber roto el orden actual
        return receta

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
