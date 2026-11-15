"""Punto de entrada del programa: solo menú y despacho de opciones.

Ejecutar desde la raíz del repo con:  python -m src.main
"""

from src.config import TEMA
from src.dominio.receta import buscar_por_id, formatear_detalle, listar_catalogo

TEMAS = {
    "pokedex": "Pokédex",
    "recetario": "Recetario",
    "musica": "Biblioteca musical",
}


def pendiente():
    print("Todavía no está implementado. Completar en la entrega que corresponde.")


def mostrar_menu():
    nombre = TEMAS.get(TEMA, TEMA or "(sin tema)")
    print()
    print(f"=== {nombre} — AyED C2 2026 ===")
    print("1. Listar catálogo")
    print("2. Ver detalle")
    print("3. Buscar")
    print("4. Ordenar")
    print("5. Operación recursiva")
    print("6. Colección principal (menú semanal)")
    print("7. Historial (pila)")
    print("8. Cola de preparación")
    print("9. Guardar / cargar archivos")
    print("0. Salir")


def pedir_id():
    """Pide un id entero. Devuelve None si queda vacío o no es un número."""
    texto = input("Id de la receta: ").strip()
    if texto == "":
        print("No ingresaste ningún id.")
        return None
    try:
        return int(texto)
    except ValueError:
        print(f"'{texto}' no es un número entero.")
        return None


def ver_detalle():
    id_receta = pedir_id()
    if id_receta is None:
        return
    item = buscar_por_id(id_receta)
    if item is None:
        print(f"No existe una receta con id {id_receta}.")
    else:
        print(formatear_detalle(item))


def main():
    if TEMA not in TEMAS:
        print("Seteá TEMA en src/config.py: 'pokedex', 'recetario' o 'musica'.")
        return

    opcion = None
    try:
        while opcion != "0":
            mostrar_menu()
            opcion = input("> ").strip()
            if opcion == "0":
                print("Chau.")
            elif opcion == "1":
                listar_catalogo()
            elif opcion == "2":
                ver_detalle()
            elif opcion in {"3", "4", "5", "6", "7", "8", "9"}:
                pendiente()
            else:
                print("Opción inválida. Elegí un número del 0 al 9.")
    except (EOFError, KeyboardInterrupt):
        # Fin de la entrada (Ctrl+Z / Ctrl+D) o Ctrl+C: salimos sin traceback.
        print("\nChau.")


if __name__ == "__main__":
    main()
