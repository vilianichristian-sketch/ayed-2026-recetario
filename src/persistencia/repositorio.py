"""Traducción entre los archivos de data/ y los objetos del dominio.

- recetas.txt       id,nombre,tiempo_min,dificultad,categoria   (catálogo)
- ingredientes.txt  receta_id,nombre,cantidad,unidad           (tabla auxiliar)
- subrecetas.txt    receta_id,subreceta_id                     (tabla auxiliar, relación recursiva)
- recetas.bin       catálogo en binario (ver binario.py); ingredientes y sub-recetas se toman de los .txt
- menu_semanal.txt dia,receta_id                               (colección principal)
"""

from pathlib import Path

from src.algoritmos.ordenamiento import ordenar_insercion
from src.dominio.ingrediente import Ingrediente
from src.dominio.receta import Receta
from src.dominio.recetario import CRITERIOS, Recetario
from src.excepciones import ArchivoInvalidoError, DatoInvalidoError, ItemNoEncontradoError
from src.persistencia.binario import (
    actualizar_registro,
    alta_binario,
    baja_binario,
    cantidad_registros,
    cargar_binario,
    guardar_binario,
)
from src.persistencia.texto import cargar_texto, guardar_texto

ARCHIVO_RECETAS = "recetas.txt"
ARCHIVO_INGREDIENTES = "ingredientes.txt"
ARCHIVO_SUBRECETAS = "subrecetas.txt"
CAMPOS_RECETAS = ("id", "nombre", "tiempo_min", "dificultad", "categoria")
CAMPOS_INGREDIENTES = ("receta_id", "nombre", "cantidad", "unidad")
CAMPOS_SUBRECETAS = ("receta_id", "subreceta_id")


# ------------------------------------------------------------------ conversiones con validación
def _entero(valor, ruta, campo):
    try:
        return int(valor)
    except ValueError:
        raise ArchivoInvalidoError(f"{ruta}: '{valor}' no es un número entero válido para '{campo}'.") from None


def _numero(valor, ruta, campo):
    try:
        return int(valor)
    except ValueError:
        try:
            return float(valor)
        except ValueError:
            raise ArchivoInvalidoError(f"{ruta}: '{valor}' no es un número válido para '{campo}'.") from None


def _receta_desde_fila(fila, ruta):
    try:
        return Receta(_entero(fila["id"], ruta, "id"), fila["nombre"],
                      _entero(fila["tiempo_min"], ruta, "tiempo_min"), fila["dificultad"], fila["categoria"])
    except DatoInvalidoError as error:
        raise ArchivoInvalidoError(f"{ruta}: la receta {fila['id']} tiene datos inválidos: {error}") from None


# ------------------------------------------------------------------ carga
def _cargar_tablas_auxiliares(recetario, carpeta, estricto=True):
    """Agrega ingredientes y sub-recetas. Devuelve cuántas filas se omitieron.

    estricto=True: una fila que nombra una receta inexistente es un error de archivo.
    estricto=False (al cargar desde binario): esas filas se omiten.
    """
    omitidas = 0
    ruta = Path(carpeta) / ARCHIVO_INGREDIENTES
    for fila in cargar_texto(ruta, CAMPOS_INGREDIENTES):
        id_receta = _entero(fila["receta_id"], ruta, "receta_id")
        if not recetario.existe(id_receta):
            if estricto:
                raise ArchivoInvalidoError(f"{ruta}: hay ingredientes de la receta {id_receta}, que no existe.")
            omitidas += 1
            continue
        try:
            ingrediente = Ingrediente(fila["nombre"], _numero(fila["cantidad"], ruta, "cantidad"), fila["unidad"])
        except DatoInvalidoError as error:
            raise ArchivoInvalidoError(f"{ruta}: ingrediente inválido de la receta {id_receta}: {error}") from None
        recetario.obtener(id_receta).agregar_ingrediente(ingrediente)

    ruta = Path(carpeta) / ARCHIVO_SUBRECETAS
    for fila in cargar_texto(ruta, CAMPOS_SUBRECETAS):
        id_receta = _entero(fila["receta_id"], ruta, "receta_id")
        id_sub = _entero(fila["subreceta_id"], ruta, "subreceta_id")
        try:
            recetario.agregar_subreceta(id_receta, id_sub)
        except ItemNoEncontradoError:
            if estricto:
                raise ArchivoInvalidoError(
                    f"{ruta}: la relación {id_receta} -> {id_sub} nombra una receta o sub-receta faltante."
                ) from None
            omitidas += 1
    return omitidas


def cargar_recetario(carpeta, ruta_recetas=None):
    """Lee recetas.txt + ingredientes.txt + subrecetas.txt y arma un Recetario.

    ruta_recetas permite cargar el catálogo desde otro .txt (las tablas
    auxiliares se leen siempre de `carpeta`).
    """
    recetario = Recetario()
    ruta = Path(carpeta) / ARCHIVO_RECETAS if ruta_recetas is None else Path(ruta_recetas)
    for fila in cargar_texto(ruta, CAMPOS_RECETAS):
        receta = _receta_desde_fila(fila, ruta)
        try:
            recetario.agregar(receta)
        except DatoInvalidoError as error:  # id repetido
            raise ArchivoInvalidoError(f"{ruta}: {error}") from None
    _cargar_tablas_auxiliares(recetario, carpeta, estricto=ruta_recetas is None)
    return recetario


def cargar_recetario_binario(ruta_binario, carpeta):
    """Catálogo desde el binario + ingredientes y sub-recetas desde los .txt.

    Devuelve (recetario, filas_auxiliares_omitidas).
    """
    recetario = Recetario()
    for receta in cargar_binario(ruta_binario):
        try:
            recetario.agregar(receta)
        except DatoInvalidoError as error:
            raise ArchivoInvalidoError(f"{ruta_binario}: {error}") from None
    omitidas = _cargar_tablas_auxiliares(recetario, carpeta, estricto=False)
    return recetario, omitidas


# ------------------------------------------------------------------ guardado
def guardar_recetario(recetario, carpeta):
    """Reescribe los tres .txt con el contenido actual del recetario (ordenado por id)."""
    por_id = ordenar_insercion(recetario.a_lista(), CRITERIOS["id"])
    filas_recetas = []
    filas_ingredientes = []
    for receta in por_id:
        filas_recetas.append((receta.id, receta.nombre, receta.tiempo_min, receta.dificultad, receta.categoria))
        for ingrediente in receta.ingredientes:
            filas_ingredientes.append((receta.id, ingrediente.nombre, f"{ingrediente.cantidad:g}", ingrediente.unidad))
    filas_subrecetas = []
    for id_receta, id_sub in recetario.relaciones_subrecetas():
        filas_subrecetas.append((id_receta, id_sub))

    guardar_texto(Path(carpeta) / ARCHIVO_RECETAS, filas_recetas, CAMPOS_RECETAS)
    guardar_texto(Path(carpeta) / ARCHIVO_INGREDIENTES, filas_ingredientes, CAMPOS_INGREDIENTES)
    guardar_texto(Path(carpeta) / ARCHIVO_SUBRECETAS, filas_subrecetas, CAMPOS_SUBRECETAS)
    return len(filas_recetas)


# ------------------------------------------------------------------ regla de oro: memoria = archivos
# Después de cada cambio del catálogo (cargar, ordenar, alta, baja, modificación)
# se actualizan los archivos. El .bin queda SIEMPRE en el mismo orden que la
# lista enlazada en memoria, así la posición de una receta es la misma en los
# dos lados y se puede usar para el acceso directo.

def guardar_todo(recetario, carpeta, ruta_binario):
    """Guarda el catálogo en los dos formatos: .txt (por id) y .bin (en el orden de la memoria)."""
    guardar_recetario(recetario, carpeta)
    return guardar_binario(ruta_binario, recetario)


def _binario_sincronizado(ruta_binario, cantidad_esperada):
    """True si el .bin existe, es válido y tiene la cantidad de registros esperada."""
    try:
        return cantidad_registros(ruta_binario) == cantidad_esperada
    except ArchivoInvalidoError:
        return False


def persistir_alta(recetario, receta, carpeta, ruta_binario):
    """Después de agregar `receta` al final del catálogo: .txt completo + append en el .bin."""
    guardar_recetario(recetario, carpeta)
    if _binario_sincronizado(ruta_binario, recetario.cantidad() - 1):
        alta_binario(ruta_binario, receta)
        return "append"
    guardar_binario(ruta_binario, recetario)  # el .bin no estaba al día: se rehace entero
    return "completo"


def persistir_baja(recetario, posicion, carpeta, ruta_binario):
    """Después de sacar del catálogo la receta que estaba en `posicion`: .txt completo + baja en el .bin."""
    guardar_recetario(recetario, carpeta)
    if _binario_sincronizado(ruta_binario, recetario.cantidad() + 1):
        baja_binario(ruta_binario, posicion)
        return "baja"
    guardar_binario(ruta_binario, recetario)
    return "completo"


def persistir_modificacion(recetario, receta, posicion, carpeta, ruta_binario):
    """Después de modificar `receta` (que está en `posicion`): .txt completo + acceso directo al .bin."""
    guardar_recetario(recetario, carpeta)
    if _binario_sincronizado(ruta_binario, recetario.cantidad()):
        actualizar_registro(ruta_binario, posicion, receta)
        return "acceso directo"
    guardar_binario(ruta_binario, recetario)
    return "completo"


# ------------------------------------------------------------------ menú semanal (colección principal)
ARCHIVO_MENU = "menu_semanal.txt"
CAMPOS_MENU = ("dia", "receta_id")


def guardar_menu(menu, carpeta):
    """Guarda el menú semanal: una línea por día con el id de la receta."""
    filas = []
    numero = 1
    for receta in menu:
        filas.append((numero, receta.id))
        numero += 1
    guardar_texto(Path(carpeta) / ARCHIVO_MENU, filas, CAMPOS_MENU)


def cargar_menu(recetario, carpeta):
    """Lee el menú semanal guardado. Devuelve (recetas en orden, ids que ya no existen).

    Si el archivo todavía no existe (nunca se guardó un menú) devuelve listas vacías.
    """
    ruta = Path(carpeta) / ARCHIVO_MENU
    if not ruta.exists():
        return [], []
    recetas = []
    faltantes = []
    for fila in cargar_texto(ruta, CAMPOS_MENU):
        id_receta = _entero(fila["receta_id"], ruta, "receta_id")
        if recetario.existe(id_receta):
            recetas.append(recetario.obtener(id_receta))
        else:
            faltantes.append(id_receta)
    return recetas, faltantes
