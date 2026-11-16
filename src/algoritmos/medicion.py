"""Mediciones de tiempo con time.perf_counter para el informe (§5).

Ejecutar desde la raíz del repo:   python -m src.algoritmos.medicion

Mide sobre el dataset original (n = 30) y sobre copias agrandadas repitiendo
las filas (x10 y x100). En las copias se cambia el id y se agrega un sufijo al
nombre para que no haya claves repetidas.
"""

import time

from src.algoritmos.busqueda import busqueda_binaria, busqueda_lineal
from src.algoritmos.ordenamiento import ordenar_insercion, ordenar_seleccion, ordenar_shell
from src.config import CARPETA_DATOS
from src.dominio.receta import Receta
from src.dominio.recetario import CRITERIOS, Recetario
from src.persistencia.repositorio import cargar_recetario

FACTORES = (1, 10, 100)
CLAVE_NOMBRE = CRITERIOS["nombre"]


def recetario_base():
    """El dataset original, leído de data/*.txt."""
    return cargar_recetario(CARPETA_DATOS)


def recetario_agrandado(base, factor):
    """Repite las recetas del catálogo `factor` veces (con id y nombre distintos)."""
    if factor == 1:
        return base
    grande = Recetario()
    desplazamiento = 0
    for copia in range(factor):
        for receta in base:
            sufijo = "" if copia == 0 else f" {copia}"
            grande.agregar(Receta(receta.id + desplazamiento, receta.nombre + sufijo,
                                  receta.tiempo_min, receta.dificultad, receta.categoria))
        desplazamiento += 1000
    return grande


def medir(funcion, repeticiones):
    """Tiempo promedio (segundos) de una llamada a funcion(), repitiéndola varias veces."""
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        funcion()
    fin = time.perf_counter()
    return (fin - inicio) / repeticiones


def recorrer(recetario):
    contador = 0
    for _receta in recetario:
        contador += 1
    return contador


def main():
    base = recetario_base()
    filas = []
    for factor in FACTORES:
        rec = recetario_agrandado(base, factor)
        n = rec.cantidad()
        lista = rec.a_lista()
        ordenada_por_nombre = ordenar_shell(lista, CLAVE_NOMBRE)
        ultimo_id = lista[-1].id
        rep_rapidas = 2000 if n <= 300 else 300
        rep_orden = 20 if n <= 30 else (3 if n <= 300 else 1)

        filas.append(("listar catálogo (iterador ListaEnlazada)", n, medir(lambda: recorrer(rec), rep_rapidas)))
        filas.append(("búsqueda lineal por nombre (peor caso: no existe)", n,
                      medir(lambda: busqueda_lineal(rec, "zzz no existe", CLAVE_NOMBRE), rep_rapidas)))
        filas.append(("búsqueda binaria por nombre (no existe; lista ya ordenada)", n,
                      medir(lambda: busqueda_binaria(ordenada_por_nombre, "zzz no existe", CLAVE_NOMBRE), rep_rapidas)))
        filas.append(("copiar ListaEnlazada a list (a_lista, previo a la binaria)", n,
                      medir(lambda: rec.a_lista(), rep_rapidas)))
        filas.append(("obtener por id con índice dict (último id)", n,
                      medir(lambda: rec.obtener(ultimo_id), rep_rapidas)))
        filas.append(("obtener por id recorriendo la lista (último id)", n,
                      medir(lambda: rec.obtener_sin_indice(ultimo_id), rep_rapidas)))
        filas.append(("ordenar por nombre: selección", n,
                      medir(lambda: ordenar_seleccion(lista, CLAVE_NOMBRE), rep_orden)))
        filas.append(("ordenar por nombre: inserción (entrada desordenada)", n,
                      medir(lambda: ordenar_insercion(lista, CLAVE_NOMBRE), rep_orden)))
        filas.append(("ordenar por nombre: inserción (entrada ya ordenada, mejor caso)", n,
                      medir(lambda: ordenar_insercion(ordenada_por_nombre, CLAVE_NOMBRE), rep_orden)))
        filas.append(("ordenar por nombre: shell", n,
                      medir(lambda: ordenar_shell(lista, CLAVE_NOMBRE), rep_orden)))
        # Apéndice comparativo (no se usa para cumplir el requisito):
        filas.append(("[apéndice] sorted() de Python por nombre", n,
                      medir(lambda: sorted(lista, key=CLAVE_NOMBRE), rep_orden)))

    print("| Operación | n | segundos |")
    print("| --- | --- | --- |")
    for operacion in _operaciones_en_orden(filas):
        for nombre, n, segundos in filas:
            if nombre == operacion:
                print(f"| {nombre} | {n} | {segundos:.8f} |")


def _operaciones_en_orden(filas):
    vistas = []
    for nombre, _n, _s in filas:
        if busqueda_lineal(vistas, nombre) is None:
            vistas.append(nombre)
    return vistas


if __name__ == "__main__":
    main()
