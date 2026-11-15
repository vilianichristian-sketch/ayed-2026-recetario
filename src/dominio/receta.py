"""Catálogo del recetario (Entrega 1).

En E1 el catálogo se arma a mano en el código: es una lista de Python
(mutable) donde cada receta es un diccionario (mutable) con claves de tipo
str (inmutables) y valores int / str (inmutables).
Los archivos .txt de data/ se empiezan a leer recién en la Entrega 5.
"""

CATALOGO = [
    {"id": 1, "nombre": "Chimichurri", "tiempo_min": 15, "dificultad": "baja", "categoria": "salsa"},
    {"id": 2, "nombre": "Salsa criolla", "tiempo_min": 20, "dificultad": "baja", "categoria": "salsa"},
    {"id": 3, "nombre": "Sofrito", "tiempo_min": 25, "dificultad": "baja", "categoria": "base"},
    {"id": 4, "nombre": "Pure de papas", "tiempo_min": 30, "dificultad": "baja", "categoria": "acompanamiento"},
    {"id": 5, "nombre": "Masa de empanadas", "tiempo_min": 90, "dificultad": "media", "categoria": "base"},
    {"id": 6, "nombre": "Masa de pizza", "tiempo_min": 120, "dificultad": "media", "categoria": "base"},
    {"id": 7, "nombre": "Pesto", "tiempo_min": 15, "dificultad": "baja", "categoria": "salsa"},
    {"id": 8, "nombre": "Pico de gallo", "tiempo_min": 15, "dificultad": "baja", "categoria": "salsa"},
    {"id": 9, "nombre": "Asado", "tiempo_min": 180, "dificultad": "media", "categoria": "principal"},
    {"id": 10, "nombre": "Empanadas de carne", "tiempo_min": 150, "dificultad": "media", "categoria": "principal"},
    {"id": 11, "nombre": "Milanesa napolitana", "tiempo_min": 50, "dificultad": "media", "categoria": "principal"},
    {"id": 12, "nombre": "Locro", "tiempo_min": 150, "dificultad": "alta", "categoria": "principal"},
    {"id": 13, "nombre": "Pizza muzzarella", "tiempo_min": 140, "dificultad": "media", "categoria": "principal"},
    {"id": 14, "nombre": "Choripan", "tiempo_min": 25, "dificultad": "baja", "categoria": "principal"},
    {"id": 15, "nombre": "Flan casero", "tiempo_min": 70, "dificultad": "media", "categoria": "postre"},
    {"id": 16, "nombre": "Panqueques con dulce de leche", "tiempo_min": 40, "dificultad": "baja", "categoria": "postre"},
    {"id": 17, "nombre": "Tacos de carne", "tiempo_min": 40, "dificultad": "baja", "categoria": "principal"},
    {"id": 18, "nombre": "Guacamole", "tiempo_min": 15, "dificultad": "baja", "categoria": "entrada"},
    {"id": 19, "nombre": "Pasta con salsa fileto", "tiempo_min": 45, "dificultad": "baja", "categoria": "principal"},
    {"id": 20, "nombre": "Noquis con pesto", "tiempo_min": 50, "dificultad": "media", "categoria": "principal"},
    {"id": 21, "nombre": "Tortilla de papas", "tiempo_min": 40, "dificultad": "media", "categoria": "principal"},
    {"id": 22, "nombre": "Pollo al horno con papas", "tiempo_min": 70, "dificultad": "baja", "categoria": "principal"},
    {"id": 23, "nombre": "Sopa de calabaza", "tiempo_min": 40, "dificultad": "baja", "categoria": "entrada"},
    {"id": 24, "nombre": "Arroz con leche", "tiempo_min": 45, "dificultad": "baja", "categoria": "postre"},
    {"id": 25, "nombre": "Brownies", "tiempo_min": 50, "dificultad": "media", "categoria": "postre"},
    {"id": 26, "nombre": "Humita", "tiempo_min": 60, "dificultad": "media", "categoria": "principal"},
    {"id": 27, "nombre": "Hamburguesa casera", "tiempo_min": 35, "dificultad": "baja", "categoria": "principal"},
    {"id": 28, "nombre": "Ensalada rusa", "tiempo_min": 35, "dificultad": "baja", "categoria": "entrada"},
    {"id": 29, "nombre": "Curry de garbanzos", "tiempo_min": 40, "dificultad": "baja", "categoria": "principal"},
    {"id": 30, "nombre": "Risotto de hongos", "tiempo_min": 45, "dificultad": "alta", "categoria": "principal"},
]

# Tupla: inmutable a propósito, las dificultades válidas no cambian.
DIFICULTADES = ("baja", "media", "alta")


def formatear_resumen(item):
    """Devuelve una línea de texto con los datos principales de una receta."""
    return (
        f"{item['id']:>3}  {item['nombre']:<30} {item['tiempo_min']:>4} min  "
        f"{item['dificultad']:<6} {item['categoria']}"
    )


def listar_catalogo():
    """Imprime el catálogo completo, una receta por línea."""
    print(f"{'ID':>3}  {'Nombre':<30} {'Tiempo':>8}  {'Dific.':<6} Categoría")
    for item in CATALOGO:
        print(formatear_resumen(item))
    print(f"Total: {len(CATALOGO)} recetas.")


def buscar_por_id(id_receta):
    """Devuelve el diccionario de la receta con ese id, o None si no existe."""
    for item in CATALOGO:
        if item["id"] == id_receta:
            return item
    return None


def formatear_detalle(item):
    """Devuelve el detalle completo de una receta en varias líneas."""
    return (
        f"Receta #{item['id']}: {item['nombre']}\n"
        f"  Tiempo de preparación: {item['tiempo_min']} minutos\n"
        f"  Dificultad: {item['dificultad']}\n"
        f"  Categoría: {item['categoria']}"
    )
