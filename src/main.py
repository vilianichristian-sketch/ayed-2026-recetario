"""Punto de entrada del programa: solo menú y despacho de opciones.

Ejecutar desde la raíz del repo con:  python -m src.main
"""

from src.cli import pantallas
from src.config import CARPETA_DATOS, RUTA_BINARIO, TEMA
from src.dominio.sistema import SistemaRecetario
from src.excepciones import ArchivoInvalidoError, RecetarioError
from src.persistencia.binario import guardar_binario
from src.persistencia.repositorio import cargar_menu, cargar_recetario

TEMAS = {
    "pokedex": "Pokédex",
    "recetario": "Recetario",
    "musica": "Biblioteca musical",
}

# Despacho: cada opción del menú es una función que recibe el sistema.
OPCIONES = {
    "1": ("Listar catálogo", pantallas.listar_catalogo),
    "2": ("Ver detalle", pantallas.ver_detalle),
    "3": ("Buscar (lineal / binaria)", pantallas.buscar),
    "4": ("Ordenar (selección / inserción / shell)", pantallas.ordenar),
    "5": ("Operación recursiva (desglose de sub-recetas)", pantallas.operacion_recursiva),
    "6": ("ABM: menú semanal (colección principal) y catálogo", pantallas.menu_semanal),
    "7": ("Historial de recetas cocinadas (pila)", pantallas.historial),
    "8": ("Cola de preparación (cola)", pantallas.cola_preparacion),
    "9": ("Archivos: guardar / cargar en .txt y binario", pantallas.archivos),
}


def mostrar_menu():
    nombre = TEMAS.get(TEMA, TEMA or "(sin tema)")
    print()
    print(f"=== {nombre} — AyED C2 2026 ===")
    for clave, (texto, _funcion) in OPCIONES.items():
        print(f"{clave}. {texto}")
    print("0. Salir")


def crear_sistema():
    """Arma el sistema desde los archivos de data/.

    1. Catálogo desde recetas.txt + ingredientes.txt + subrecetas.txt.
       Si están mal, avisa y arranca con el catálogo vacío.
    2. Binario: se guarda recetas.bin con el catálogo cargado, así el .bin queda
       en el mismo orden que la memoria (regla de oro del acceso directo).
    3. Menú semanal: si hay uno guardado (menu_semanal.txt), se recupera.
    """
    try:
        recetario = cargar_recetario(CARPETA_DATOS)
    except ArchivoInvalidoError as error:
        print(f"Aviso: no se pudo cargar el catálogo ({error}). Se arranca con el catálogo vacío.")
        return SistemaRecetario()
    print(f"Catálogo cargado desde {CARPETA_DATOS.name}/: {recetario.cantidad()} recetas.")
    sistema = SistemaRecetario(recetario)
    try:
        guardar_binario(RUTA_BINARIO, recetario)
    except ArchivoInvalidoError as error:
        print(f"Aviso: no se pudo generar el binario ({error}).")
    try:
        recetas_menu, faltantes = cargar_menu(recetario, CARPETA_DATOS)
        if recetas_menu:
            cantidad = sistema.restaurar_menu(recetas_menu)
            print(f"Menú semanal recuperado: {cantidad} recetas.")
        if faltantes:
            print(f"Aviso: el menú guardado nombraba recetas que ya no existen: {faltantes}.")
    except ArchivoInvalidoError as error:
        print(f"Aviso: no se pudo leer el menú semanal guardado ({error}). Se arranca con el menú vacío.")
    return sistema


def main():
    if TEMA not in TEMAS:
        print("Seteá TEMA en src/config.py: 'pokedex', 'recetario' o 'musica'.")
        return

    try:
        sistema = crear_sistema()
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
