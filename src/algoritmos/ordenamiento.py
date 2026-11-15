"""Ordenamientos propios (sin sorted ni list.sort).

Todos reciben una colección iterable y una función `clave(elemento)`, y
devuelven una NUEVA list ordenada en forma ascendente (no modifican la original).
"""


def _copiar(coleccion):
    copia = []
    for elemento in coleccion:
        copia.append(elemento)
    return copia


def ordenar_seleccion(coleccion, clave):
    """Selección: para cada posición i busca el mínimo de lo que falta y lo intercambia.

    O(n²) comparaciones siempre (aunque ya esté ordenado). NO es estable: el
    intercambio puede pasar un elemento por encima de otro con la misma clave.
    """
    datos = _copiar(coleccion)
    n = len(datos)
    for i in range(n - 1):
        pos_min = i
        for j in range(i + 1, n):
            if clave(datos[j]) < clave(datos[pos_min]):
                pos_min = j
        if pos_min != i:
            datos[i], datos[pos_min] = datos[pos_min], datos[i]
    return datos


def ordenar_insercion(coleccion, clave):
    """Inserción: toma cada elemento y lo inserta en su lugar entre los ya ordenados.

    Mejor caso O(n) (ya ordenado), peor y promedio O(n²). ES estable: solo se
    desplazan los elementos estrictamente mayores, los iguales no se saltean.
    """
    datos = _copiar(coleccion)
    for i in range(1, len(datos)):
        actual = datos[i]
        clave_actual = clave(actual)
        j = i - 1
        while j >= 0 and clave(datos[j]) > clave_actual:
            datos[j + 1] = datos[j]   # desplaza el mayor un lugar a la derecha
            j -= 1
        datos[j + 1] = actual         # deja el elemento en su hueco
    return datos


def ordenar_shell(coleccion, clave):
    """Shell sort: inserción con saltos (gap) que se van achicando: n/2, n/4, ..., 1.

    Mueve los elementos lejanos de entrada y termina con una inserción común
    sobre una lista casi ordenada. Con esta secuencia de gaps el peor caso es
    O(n²) pero en la práctica anda mucho mejor (~n^1.3). NO es estable.
    """
    datos = _copiar(coleccion)
    gap = len(datos) // 2
    while gap > 0:
        for i in range(gap, len(datos)):
            actual = datos[i]
            clave_actual = clave(actual)
            j = i
            while j >= gap and clave(datos[j - gap]) > clave_actual:
                datos[j] = datos[j - gap]
                j -= gap
            datos[j] = actual
        gap //= 2
    return datos


# Nombre que se muestra en el menú -> función
ALGORITMOS = {
    "seleccion": ("selección", ordenar_seleccion),
    "insercion": ("inserción", ordenar_insercion),
    "shell": ("shell", ordenar_shell),
}
