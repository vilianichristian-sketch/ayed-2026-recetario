"""Búsqueda lineal y binaria, implementación propia (sin `in`, index() ni bisect).

`obtener_clave` es una función que, dado un elemento, devuelve el valor a
comparar (por ejemplo `lambda r: r.nombre_normalizado`). Así el mismo algoritmo
sirve para buscar por nombre, por id, por tiempo, etc.
"""


def busqueda_lineal(coleccion, clave, obtener_clave=None):
    """Devuelve el primer elemento cuya clave es igual a `clave`, o None.

    Recorre de a uno: sirve para cualquier colección iterable (también la
    ListaEnlazada) y no necesita que esté ordenada. O(n) en el peor caso.
    """
    for elemento in coleccion:
        valor = elemento if obtener_clave is None else obtener_clave(elemento)
        if valor == clave:
            return elemento
    return None


def busqueda_lineal_todos(coleccion, condicion):
    """Devuelve una list con TODOS los elementos para los que condicion(elemento) es True. O(n)."""
    encontrados = []
    for elemento in coleccion:
        if condicion(elemento):
            encontrados.append(elemento)
    return encontrados


def busqueda_binaria(coleccion_ordenada, clave, obtener_clave=None):
    """Búsqueda binaria. La colección tiene que estar ordenada por obtener_clave.

    Necesita acceso por índice (una list de Python): en una lista enlazada
    llegar al medio cuesta O(n). Cada vuelta descarta la mitad del rango:
    O(log n) comparaciones. Devuelve el elemento o None.
    """
    izquierda = 0
    derecha = len(coleccion_ordenada) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        elemento = coleccion_ordenada[medio]
        valor = elemento if obtener_clave is None else obtener_clave(elemento)
        if valor == clave:
            return elemento
        if valor < clave:
            izquierda = medio + 1   # la clave solo puede estar en la mitad derecha
        else:
            derecha = medio - 1     # la clave solo puede estar en la mitad izquierda
    return None
