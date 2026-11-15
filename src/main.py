"""Punto de entrada del programa: solo menú y despacho de opciones.

Ejecutar desde la raíz del repo con:  python -m src.main
"""

from src.cli import pantallas
from src.config import TEMA
from src.dominio.sistema import SistemaRecetario
from src.excepciones import RecetarioError

TEMAS = {
    "pokedex": "Pokédex",
    "recetario": "Recetario",
    "musica": "Biblioteca musical",
}


def pendiente(_sistema):
    print("Todavía no está implementado. Completar en la entrega que corresponde.")


# Despacho: cada opción del menú es una función que recibe el sistema.
OPCIONES = {
    "1": ("Listar catálogo", pantallas.listar_catalogo),
    "2": ("Ver detalle", pantallas.ver_detalle),
    "3": ("Buscar", pendiente),
    "4": ("Ordenar", pendiente),
    "5": ("Operación recursiva (desglose de sub-recetas)", pantallas.operacion_recursiva),
    "6": ("Colección principal (menú semanal)", pantallas.menu_semanal),
    "7": ("Historial de recetas cocinadas (pila)", pantallas.historial),
    "8": ("Cola de preparación (cola)", pantallas.cola_preparacion),
    "9": ("Guardar / cargar archivos", pendiente),
}


def mostrar_menu():
    nombre = TEMAS.get(TEMA, TEMA or "(sin tema)")
    print()
    print(f"=== {nombre} — AyED C2 2026 ===")
    for clave, (texto, _funcion) in OPCIONES.items():
        print(f"{clave}. {texto}")
    print("0. Salir")


def main():
    if TEMA not in TEMAS:
        print("Seteá TEMA en src/config.py: 'pokedex', 'recetario' o 'musica'.")
        return

    sistema = SistemaRecetario()
    try:
        while True:
            mostrar_menu()
            opcion = input("> ").strip()
            if opcion == "0":
                print("Chau.")
                break
            if opcion not in OPCIONES:
                print("Opción inválida. Elegí un número del 0 al 9.")
                continue
            _texto, accion = OPCIONES[opcion]
            try:
                accion(sistema)
            except RecetarioError as error:
                # Red de seguridad: una excepción propia que no se capturó en la
                # pantalla se muestra con un mensaje y el menú sigue.
                print(f"Error: {error}")
    except (EOFError, KeyboardInterrupt):
        # Fin de la entrada (Ctrl+Z / Ctrl+D) o Ctrl+C: salimos sin traceback.
        print("\nChau.")


if __name__ == "__main__":
    main()
