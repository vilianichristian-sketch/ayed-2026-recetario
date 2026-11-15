"""Operación recursiva del dominio: desglosar una receta explotando sus sub-recetas.

Datos reales: data/subrecetas.txt dice, por ejemplo, que el Asado (9) usa el
Chimichurri (1) y la Salsa criolla (2), y que las Empanadas de carne (10) usan
el Sofrito (3) y la Masa de empanadas (5). Esas sub-recetas no usan otras: son
recetas "hoja" y ahí se corta la recursión (caso base).

Las dos funciones reciben `camino`: una tupla con los ids que se están
desglosando desde la receta original hasta la actual. Su largo es el nivel de
profundidad y además permite detectar un ciclo (A usa B y B usa A), que haría
que la recursión no termine nunca.
"""

from src.excepciones import CicloSubrecetasError, ItemNoEncontradoError, SubrecetaFaltanteError


def _obtener_receta(recetario, id_receta, camino):
    """Busca la receta validando que no haya ciclo y que la sub-receta exista."""
    if id_receta in camino:
        raise CicloSubrecetasError(
            f"Ciclo de sub-recetas: la receta {id_receta} termina usándose a sí misma."
        )
    try:
        return recetario.obtener(id_receta)
    except ItemNoEncontradoError:
        if not camino:  # es la receta que pidió el usuario: el error original alcanza
            raise
        raise SubrecetaFaltanteError(
            f"La receta {camino[-1]} usa la sub-receta {id_receta}, que no está en el catálogo."
        ) from None


def arbol_subrecetas(recetario, id_receta, camino=()):
    """Devuelve la receta y todas sus sub-recetas (directas e indirectas).

    Resultado: lista de pares (nivel, receta) en preorden. Nivel 0 es la receta
    pedida, nivel 1 sus sub-recetas, nivel 2 las sub-recetas de esas, etc.
    """
    receta = _obtener_receta(recetario, id_receta, camino)
    nivel = len(camino)
    subrecetas = recetario.subrecetas_de(id_receta)

    if not subrecetas:  # CASO BASE: receta hoja, no usa otras recetas
        return [(nivel, receta)]

    resultado = [(nivel, receta)]
    for id_sub in subrecetas:  # CASO RECURSIVO: mismo problema, una receta más chica
        resultado += arbol_subrecetas(recetario, id_sub, camino + (id_receta,))
    return resultado


def _sumar_ingredientes(totales, ingredientes):
    """Acumula (nombre, unidad) -> cantidad en el dict totales."""
    for ingrediente in ingredientes:
        clave = (ingrediente.nombre, ingrediente.unidad)  # tupla: puede ser clave de dict
        totales[clave] = totales.get(clave, 0) + ingrediente.cantidad


def ingredientes_totales(recetario, id_receta, camino=(), traza=None):
    """Ingredientes propios de la receta + los de todas sus sub-recetas, sumados.

    Devuelve un dict {(nombre, unidad): cantidad_total}.
    Si `traza` es una lista, se le agrega una línea por cada llamada y por cada
    vuelta, para poder mostrar cómo se apilan y desapilan las llamadas.
    """
    receta = _obtener_receta(recetario, id_receta, camino)
    sangria = "    " * len(camino)
    if traza is not None:
        traza.append(f"{sangria}-> ingredientes_totales({id_receta})  [{receta.nombre}]")

    totales = {}
    _sumar_ingredientes(totales, receta.ingredientes)
    subrecetas = recetario.subrecetas_de(id_receta)

    if not subrecetas:  # CASO BASE: receta hoja, solo sus ingredientes propios
        if traza is not None:
            traza.append(f"{sangria}<- caso base: devuelve {len(totales)} ingredientes de {receta.nombre}")
        return totales

    for id_sub in subrecetas:  # CASO RECURSIVO: se resuelve cada sub-receta y se suma
        parciales = ingredientes_totales(recetario, id_sub, camino + (id_receta,), traza)
        for clave, cantidad in parciales.items():
            totales[clave] = totales.get(clave, 0) + cantidad

    if traza is not None:
        traza.append(f"{sangria}<- devuelve {len(totales)} ingredientes acumulados de {receta.nombre}")
    return totales
