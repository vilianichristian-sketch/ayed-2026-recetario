"""Lectura de datos del usuario sin que el programa se rompa con input vacío o basura."""


def pedir_texto(mensaje):
    """Devuelve lo que escribió el usuario, sin espacios a los costados (puede ser '')."""
    return input(mensaje).strip()


def pedir_entero(mensaje):
    """Pide un número entero.

    - Enter vacío: devuelve None (el usuario cancela).
    - Algo que no es número: avisa y vuelve a preguntar.
    """
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            return None
        try:
            return int(texto)
        except ValueError:
            print(f"  '{texto}' no es un número entero. Probá de nuevo (Enter vacío para cancelar).")


def ejecutar_submenu(titulo, opciones, sistema):
    """Muestra un submenú hasta que el usuario elige 0.

    opciones: dict {"1": ("Texto de la opción", funcion), ...}; cada función recibe el sistema.
    """
    while True:
        print()
        print(f"--- {titulo} ---")
        for clave, (texto, _funcion) in opciones.items():
            print(f"{clave}. {texto}")
        print("0. Volver")
        eleccion = input("> ").strip()
        if eleccion == "0":
            return
        if eleccion not in opciones:
            print("Opción inválida.")
            continue
        _texto, funcion = opciones[eleccion]
        funcion(sistema)
