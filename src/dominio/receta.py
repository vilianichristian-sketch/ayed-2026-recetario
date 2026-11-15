"""Clase Receta: el ítem del catálogo."""

# Tupla: inmutable a propósito, las dificultades válidas no cambian.
DIFICULTADES = ("baja", "media", "alta")


class Receta:
    """Una receta del libro: datos básicos + su lista de ingredientes propios.

    Las sub-recetas (qué otras recetas usa) no se guardan acá sino en el
    Recetario, porque es una relación entre recetas del catálogo.
    """

    def __init__(self, id_receta, nombre, tiempo_min, dificultad, categoria):
        self.id = id_receta
        self.nombre = nombre
        self.tiempo_min = tiempo_min
        self.dificultad = dificultad
        self.categoria = categoria
        self.ingredientes = []  # lista de Ingrediente (mutable: se van agregando)

    def agregar_ingrediente(self, ingrediente):
        self.ingredientes.append(ingrediente)

    def resumen(self):
        """Una línea con los datos principales (para listados)."""
        return (
            f"{self.id:>3}  {self.nombre:<30} {self.tiempo_min:>4} min  "
            f"{self.dificultad:<6} {self.categoria}"
        )

    def detalle(self):
        """Varias líneas con todos los datos y los ingredientes propios."""
        lineas = [
            f"Receta #{self.id}: {self.nombre}",
            f"  Tiempo de preparación: {self.tiempo_min} minutos",
            f"  Dificultad: {self.dificultad}",
            f"  Categoría: {self.categoria}",
            "  Ingredientes propios:",
        ]
        if not self.ingredientes:
            lineas.append("    (ninguno)")
        for ingrediente in self.ingredientes:
            lineas.append(f"    - {ingrediente}")
        return "\n".join(lineas)

    def __str__(self):
        return self.nombre
