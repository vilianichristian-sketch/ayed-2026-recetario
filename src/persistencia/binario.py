"""Persistencia binaria: registros de longitud fija con struct.

Layout del archivo (todo little-endian, '<', sin relleno entre campos):

  Header (9 bytes), formato '<4s1sI':
    magia      4s  b'AYED'
    tema       1s  b'R' (recetario)
    cantidad   I   unsigned int de 4 bytes: cuántos registros hay

  Registro de receta (74 bytes), formato '<I40sH8s20s':
    id          I    4 bytes, unsigned int
    nombre     40s   40 bytes, UTF-8, recortado o rellenado con \\0
    tiempo_min  H    2 bytes, unsigned short (0 a 65535)
    dificultad  8s   8 bytes, UTF-8 ('baja', 'media', 'alta')
    categoria  20s   20 bytes, UTF-8

Como todos los registros miden lo mismo, el registro de la posición p
(0-based) empieza en el byte  TAM_HEADER + p * TAM_REGISTRO.  Eso permite el
acceso directo: seek() a ese byte y leer o escribir solo ese registro.

Alta: append al final (seek(0, 2)) + header con cantidad + 1.
Baja: se reescribe el archivo sin ese registro (si no, quedaría un hueco).

En el binario se guarda el registro principal del catálogo. Las tablas
auxiliares (ingredientes y sub-recetas) siguen en .txt.
"""

import os
import struct

from src.dominio.receta import Receta
from src.excepciones import ArchivoInvalidoError, DatoInvalidoError, ItemNoEncontradoError

MAGIA = b"AYED"
TEMA = b"R"
FORMATO_HEADER = "<4s1sI"
FORMATO_REGISTRO = "<I40sH8s20s"
TAM_HEADER = struct.calcsize(FORMATO_HEADER)        # 9
TAM_REGISTRO = struct.calcsize(FORMATO_REGISTRO)    # 74
ANCHO_NOMBRE = 40
ANCHO_DIFICULTAD = 8
ANCHO_CATEGORIA = 20


# ------------------------------------------------------------------ conversión de textos
def _a_bytes(texto, ancho):
    """str -> bytes UTF-8 de como máximo `ancho` bytes.

    Si no entra se recorta, sin partir una letra de 2 bytes (á, ñ) por la mitad.
    El relleno con \\0 hasta el ancho lo hace struct.pack con el formato 's'.
    """
    datos = texto.encode("utf-8")
    if len(datos) > ancho:
        datos = datos[:ancho].decode("utf-8", errors="ignore").encode("utf-8")
    return datos


def _de_bytes(datos, posicion):
    try:
        return datos.rstrip(b"\0").decode("utf-8")
    except UnicodeDecodeError:
        raise ArchivoInvalidoError(f"El registro {posicion} tiene texto que no es UTF-8.") from None


def _empaquetar(receta):
    if receta.tiempo_min > 65535:
        raise DatoInvalidoError(f"El tiempo de '{receta.nombre}' no entra en 2 bytes (máximo 65535).")
    return struct.pack(
        FORMATO_REGISTRO,
        receta.id,
        _a_bytes(receta.nombre, ANCHO_NOMBRE),
        receta.tiempo_min,
        _a_bytes(receta.dificultad, ANCHO_DIFICULTAD),
        _a_bytes(receta.categoria, ANCHO_CATEGORIA),
    )


def _desempaquetar(datos, posicion):
    id_receta, nombre, tiempo, dificultad, categoria = struct.unpack(FORMATO_REGISTRO, datos)
    try:
        return Receta(id_receta, _de_bytes(nombre, posicion), tiempo,
                      _de_bytes(dificultad, posicion), _de_bytes(categoria, posicion))
    except DatoInvalidoError as error:
        raise ArchivoInvalidoError(f"El registro {posicion} no es una receta válida: {error}") from None


# ------------------------------------------------------------------ header
def _leer_header(archivo, ruta):
    """Lee y valida el header. Devuelve la cantidad de registros."""
    datos = archivo.read(TAM_HEADER)
    if len(datos) < TAM_HEADER:
        raise ArchivoInvalidoError(f"{ruta} está truncado: no alcanza ni para el header ({TAM_HEADER} bytes).")
    magia, tema, cantidad = struct.unpack(FORMATO_HEADER, datos)
    if magia != MAGIA:
        raise ArchivoInvalidoError(f"{ruta} no empieza con la magia {MAGIA!r} (tiene {magia!r}): no es un binario del TP.")
    if tema != TEMA:
        raise ArchivoInvalidoError(f"{ruta} es de otro tema ({tema!r}); se esperaba {TEMA!r} (recetario).")
    tamanio_real = os.fstat(archivo.fileno()).st_size
    tamanio_esperado = TAM_HEADER + cantidad * TAM_REGISTRO
    if tamanio_real != tamanio_esperado:
        raise ArchivoInvalidoError(
            f"{ruta} está truncado o dañado: el header dice {cantidad} registros "
            f"({tamanio_esperado} bytes) pero el archivo tiene {tamanio_real} bytes."
        )
    return cantidad


def _abrir(ruta, modo):
    try:
        return open(ruta, modo)
    except FileNotFoundError:
        raise ArchivoInvalidoError(f"No existe el archivo {ruta}. Guardá primero el binario.") from None
    except OSError as error:
        raise ArchivoInvalidoError(f"No se pudo abrir {ruta}: {error}") from None


def _validar_posicion(posicion, cantidad):
    if posicion < 0 or posicion >= cantidad:
        raise ItemNoEncontradoError(
            f"Posición {posicion} fuera de rango: el binario tiene {cantidad} registros (0 a {cantidad - 1})."
        )


# ------------------------------------------------------------------ operaciones públicas
def guardar_binario(ruta, recetas):
    """Escribe el archivo completo: header + un registro por receta. Devuelve la cantidad."""
    registros = []
    for receta in recetas:
        registros.append(_empaquetar(receta))
    try:
        with open(ruta, "wb") as archivo:
            archivo.write(struct.pack(FORMATO_HEADER, MAGIA, TEMA, len(registros)))
            for registro in registros:
                archivo.write(registro)
    except OSError as error:
        raise ArchivoInvalidoError(f"No se pudo escribir {ruta}: {error}") from None
    return len(registros)


def cargar_binario(ruta):
    """Lee todos los registros en orden. Devuelve una list de Receta (sin ingredientes)."""
    recetas = []
    with _abrir(ruta, "rb") as archivo:
        cantidad = _leer_header(archivo, ruta)
        for posicion in range(cantidad):
            recetas.append(_desempaquetar(archivo.read(TAM_REGISTRO), posicion))
    return recetas


def cantidad_registros(ruta):
    with _abrir(ruta, "rb") as archivo:
        return _leer_header(archivo, ruta)


def leer_registro(ruta, posicion):
    """Acceso directo: lee SOLO el registro de esa posición (0-based) con seek()."""
    with _abrir(ruta, "rb") as archivo:
        cantidad = _leer_header(archivo, ruta)
        _validar_posicion(posicion, cantidad)
        archivo.seek(TAM_HEADER + posicion * TAM_REGISTRO)
        return _desempaquetar(archivo.read(TAM_REGISTRO), posicion)


def actualizar_registro(ruta, posicion, receta):
    """Acceso directo: pisa SOLO el registro de esa posición (0-based), sin reescribir el archivo."""
    registro = _empaquetar(receta)
    with _abrir(ruta, "r+b") as archivo:
        cantidad = _leer_header(archivo, ruta)
        _validar_posicion(posicion, cantidad)
        archivo.seek(TAM_HEADER + posicion * TAM_REGISTRO)
        archivo.write(registro)


def alta_binario(ruta, receta):
    """Alta: agrega UN registro al final (append) y corrige la cantidad del header.

    No reescribe los registros existentes: seek(0, 2) va al final del archivo,
    se escribe el registro nuevo y después seek(0) vuelve al header.
    """
    registro = _empaquetar(receta)
    with _abrir(ruta, "r+b") as archivo:
        cantidad = _leer_header(archivo, ruta)
        archivo.seek(0, 2)              # 2 = desde el final del archivo
        archivo.write(registro)
        archivo.seek(0)                 # volver al principio para arreglar el header
        archivo.write(struct.pack(FORMATO_HEADER, MAGIA, TEMA, cantidad + 1))
    return cantidad + 1


def baja_binario(ruta, posicion):
    """Baja: quita el registro de esa posición.

    Al sacar un registro del medio quedaría un hueco y los siguientes se
    correrían, así que se leen los registros, se saca ese y se reescribe el
    archivo (truncate + header con la cantidad nueva). Devuelve la cantidad nueva.
    """
    with _abrir(ruta, "r+b") as archivo:
        cantidad = _leer_header(archivo, ruta)
        _validar_posicion(posicion, cantidad)
        registros = []
        for _ in range(cantidad):
            registros.append(archivo.read(TAM_REGISTRO))
        del registros[posicion]
        archivo.seek(0)
        archivo.truncate()              # borra el contenido viejo
        archivo.write(struct.pack(FORMATO_HEADER, MAGIA, TEMA, len(registros)))
        for registro in registros:
            archivo.write(registro)
    return len(registros)
