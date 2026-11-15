"""Una función por opción del menú. Piden datos, llaman al dominio y muestran el resultado.

Acá no hay lógica del negocio: solo entrada/salida y captura de excepciones propias.
"""

from src.cli.entrada import ejecutar_submenu, pedir_entero
from src.dominio.desglose import arbol_subrecetas, ingredientes_totales
from src.excepciones import (
    CicloSubrecetasError,
    ColeccionLlenaError,
    ColeccionVaciaError,
    ItemNoEncontradoError,
    SubrecetaFaltanteError,
)

ENCABEZADO = f"{'ID':>3}  {'Nombre':<30} {'Tiempo':>8}  {'Dific.':<6} Categoría"


def _pedir_receta(sistema, mensaje="Id de la receta (Enter para cancelar): "):
    """Pide un id y devuelve la receta, o None si cancela o no existe (avisando)."""
    id_receta = pedir_entero(mensaje)
    if id_receta is None:
        print("Cancelado.")
        return None
    try:
        return sistema.recetario.obtener(id_receta)
    except ItemNoEncontradoError as error:
        print(f"Error: {error}")
        return None


# ---------------------------------------------------------------- 1. Listar
def listar_catalogo(sistema):
    print(ENCABEZADO)
    for receta in sistema.recetario:
        print(receta.resumen())
    print(f"Total: {sistema.recetario.cantidad()} recetas.")


# ---------------------------------------------------------------- 2. Detalle
def ver_detalle(sistema):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    print(receta.detalle())
    ids_sub = sistema.recetario.subrecetas_de(receta.id)
    if ids_sub:
        nombres = []
        for id_sub in ids_sub:
            try:
                nombres.append(f"{sistema.recetario.obtener(id_sub).nombre} (#{id_sub})")
            except ItemNoEncontradoError:
                nombres.append(f"#{id_sub} (no está en el catálogo)")
        print("  Usa las sub-recetas: " + ", ".join(nombres))


# ---------------------------------------------------------------- 5. Recursión
def _mostrar_arbol(sistema):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    try:
        arbol = arbol_subrecetas(sistema.recetario, receta.id)
    except (SubrecetaFaltanteError, CicloSubrecetasError) as error:
        print(f"Error: {error}")
        return
    for nivel, sub in arbol:
        prefijo = "    " * nivel + ("+-- " if nivel > 0 else "")
        print(f"{prefijo}{sub.nombre} (#{sub.id}, {sub.tiempo_min} min)")
    if len(arbol) == 1:
        print("(No usa sub-recetas: es una receta hoja, caso base de la recursión.)")


def _mostrar_ingredientes_totales(sistema, con_traza=False):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    traza = [] if con_traza else None
    try:
        totales = ingredientes_totales(sistema.recetario, receta.id, traza=traza)
    except (SubrecetaFaltanteError, CicloSubrecetasError) as error:
        print(f"Error: {error}")
        return
    if con_traza:
        print("Traza de llamadas (cada sangría es un nivel más de recursión):")
        for linea in traza:
            print("  " + linea)
        print()
    print(f"Ingredientes totales de {receta.nombre} (incluye sub-recetas):")
    for (nombre, unidad), cantidad in totales.items():
        print(f"  - {cantidad:g} {unidad} de {nombre}")


def operacion_recursiva(sistema):
    ejecutar_submenu(
        "Operación recursiva: desglose de sub-recetas",
        {
            "1": ("Ver árbol de sub-recetas", _mostrar_arbol),
            "2": ("Ingredientes totales (explota sub-recetas)", _mostrar_ingredientes_totales),
            "3": ("Ingredientes totales con traza de la recursión",
                  lambda s: _mostrar_ingredientes_totales(s, con_traza=True)),
        },
        sistema,
    )


# ---------------------------------------------------------------- 6. Menú semanal
def _ver_menu(sistema):
    if sistema.menu.esta_vacio():
        print("El menú semanal está vacío.")
        return
    for dia, receta in sistema.menu.dias_y_recetas():
        print(f"  {dia:<10} {receta.nombre} (#{receta.id})")


def _agregar_al_menu(sistema):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    try:
        sistema.menu.agregar(receta)
        print(f"Agregada al menú: {receta.nombre}")
    except ColeccionLlenaError as error:
        print(f"Error: {error}")


def _quitar_del_menu(sistema):
    id_receta = pedir_entero("Id de la receta a quitar (Enter para cancelar): ")
    if id_receta is None:
        print("Cancelado.")
        return
    try:
        receta = sistema.menu.quitar(id_receta)
        print(f"Quitada del menú: {receta.nombre}")
    except (ColeccionVaciaError, ItemNoEncontradoError) as error:
        print(f"Error: {error}")


def menu_semanal(sistema):
    ejecutar_submenu(
        "Menú semanal (colección principal)",
        {
            "1": ("Ver menú de la semana", _ver_menu),
            "2": ("Agregar receta al menú", _agregar_al_menu),
            "3": ("Quitar receta del menú", _quitar_del_menu),
        },
        sistema,
    )
