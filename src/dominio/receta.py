"""Clase Receta: el ítem del catálogo."""

from src.excepciones import DatoInvalidoError

# Tupla: inmutable a propósito, las dificultades válidas no cambian.
# El orden importa: se usa para ordenar por dificultad (baja < media < alta).
DIFICULTADES = ("baja", "media", "alta")


def _validar_texto(valor, campo):
    """Texto no vacío y sin comas (la coma separa campos en los .txt)."""
    if not isinstance(valor, str) or valor.strip() == "":
        raise DatoInvalidoError(f"El campo '{campo}' no puede quedar vacío.")
    if "," in valor:
        raise DatoInvalidoError(f"El campo '{campo}' no puede tener comas.")
    return valor.strip()


class Receta:
    """Una receta del libro: datos básicos + su lista de ingredientes propios.

    Encapsulamiento: los atributos son "privados" (_nombre, _tiempo_min, ...) y
    se acceden con properties. Los setters validan, así una Receta nunca queda
    en un estado inválido. El id no tiene setter: es la identidad de la receta.

    Las sub-recetas (qué otras recetas usa) no se guardan acá sino en el
    Recetario, porque es una relación entre recetas del catálogo.
    """

    def __init__(self, id_receta, nombre, tiempo_min, dificultad, categoria):
        if not isinstance(id_receta, int) or id_receta <= 0:
            raise DatoInvalidoError("El id tiene que ser un entero positivo.")
        self._id = id_receta
        # Estas asignaciones pasan por los setters de abajo (que validan).
        self.nombre = nombre
        self.tiempo_min = tiempo_min
        self.dificultad = dificultad
        self.categoria = categoria
        self._ingredientes = []

    # ------------------------------------------------------------ properties
    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = _validar_texto(valor, "nombre")

    @property
    def tiempo_min(self):
        return self._tiempo_min

    @tiempo_min.setter
    def tiempo_min(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise DatoInvalidoError("El tiempo tiene que ser un entero mayor a 0 (minutos).")
        self._tiempo_min = valor

    @property
    def dificultad(self):
        return self._dificultad

    @dificultad.setter
    def dificultad(self, valor):
        valor = str(valor).strip().lower()
        if valor not in DIFICULTADES:
            raise DatoInvalidoError(f"La dificultad tiene que ser una de: {', '.join(DIFICULTADES)}.")
        self._dificultad = valor

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, valor):
        self._categoria = _validar_texto(valor, "categoria").lower()

    @property
    def ingredientes(self):
        """Copia inmutable (tupla): desde afuera no se puede alterar la lista interna."""
        return tuple(self._ingredientes)

    # ------------------------------------------------------------ comportamiento
    def agregar_ingrediente(self, ingrediente):
        self._ingredientes.append(ingrediente)

    def nivel_dificultad(self):
        """0 = baja, 1 = media, 2 = alta (para ordenar por dificultad)."""
        return DIFICULTADES.index(self._dificultad)

    def resumen(self):
        """Una línea con los datos principales (para listados)."""
        return (
            f"{self._id:>3}  {self._nombre:<30} {self._tiempo_min:>4} min  "
            f"{self._dificultad:<6} {self._categoria}"
        )

    def detalle(self):
        """Varias líneas con todos los datos y los ingredientes propios."""
        lineas = [
            f"Receta #{self._id}: {self._nombre}",
            f"  Tiempo de preparación: {self._tiempo_min} minutos",
            f"  Dificultad: {self._dificultad}",
            f"  Categoría: {self._categoria}",
            "  Ingredientes propios:",
        ]
        if not self._ingredientes:
            lineas.append("    (ninguno)")
        for ingrediente in self._ingredientes:
            lineas.append(f"    - {ingrediente}")
        return "\n".join(lineas)

    def __str__(self):
        return self._nombre

    def __repr__(self):
        return f"Receta({self._id}, {self._nombre!r})"
