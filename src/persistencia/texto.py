"""Persistencia en texto simple (.txt).

Formato: UTF-8, un registro por línea, campos separados por coma y la primera
línea con los nombres de los campos (encabezados). Ejemplo:

    id,nombre,tiempo_min,dificultad,categoria
    1,Chimichurri,15,baja,salsa

Estas funciones no saben nada de recetas: leen y escriben filas genéricas.
La traducción fila <-> Receta está en persistencia/repositorio.py.
"""

import os
from pathlib import Path

from src.excepciones import ArchivoInvalidoError, DatoInvalidoError

SEPARADOR = ","


def cargar_texto(ruta, encabezados_esperados=None):
    """Lee el archivo en forma secuencial (línea por línea).

    Devuelve una list de dicts {encabezado: valor (str)}. Las líneas en blanco
    se ignoran. Si el archivo no existe, no es UTF-8, no tiene encabezados, los
    encabezados no son los esperados o una línea tiene otra cantidad de campos,
    lanza ArchivoInvalidoError indicando el número de línea.
    """
    filas = []
    try:
        with open(ruta, encoding="utf-8") as archivo:
            encabezados = None
            for numero, linea in enumerate(archivo, start=1):
                linea = linea.rstrip("\n").rstrip("\r")
                if linea.strip() == "":
                    continue
                valores = []
                for valor in linea.split(SEPARADOR):
                    valores.append(valor.strip())
                if encabezados is None:  # primera línea con contenido
                    encabezados = valores
                    if encabezados_esperados is not None and encabezados != list(encabezados_esperados):
                        raise ArchivoInvalidoError(
                            f"{ruta}: los encabezados son {','.join(encabezados)} "
                            f"y se esperaban {','.join(encabezados_esperados)}."
                        )
                    continue
                if len(valores) != len(encabezados):
                    raise ArchivoInvalidoError(
                        f"{ruta}, línea {numero}: tiene {len(valores)} campos y se esperaban {len(encabezados)}."
                    )
                fila = {}
                for campo, valor in zip(encabezados, valores):
                    fila[campo] = valor
                filas.append(fila)
    except FileNotFoundError:
        raise ArchivoInvalidoError(f"No existe el archivo {ruta}.") from None
    except UnicodeDecodeError:
        raise ArchivoInvalidoError(f"{ruta} no es un archivo de texto UTF-8.") from None
    except OSError as error:
        raise ArchivoInvalidoError(f"No se pudo leer {ruta}: {error}") from None
    if encabezados is None:
        raise ArchivoInvalidoError(f"{ruta} está vacío (falta la línea de encabezados).")
    return filas


def guardar_texto(ruta, filas, encabezados):
    """Escribe el archivo completo: encabezados + una línea por fila.

    filas: secuencia de secuencias de valores, en el mismo orden que encabezados.
    Se escribe primero un archivo temporal y después se reemplaza el original
    (os.replace): si algo falla a mitad de camino, el archivo anterior no se pierde.
    """
    ruta = Path(ruta)
    lineas = [SEPARADOR.join(encabezados)]
    for fila in filas:
        textos = []
        for valor in fila:
            texto = str(valor)
            if SEPARADOR in texto or "\n" in texto:
                raise DatoInvalidoError(f"El valor '{texto}' no puede tener comas ni saltos de línea.")
            textos.append(texto)
        if len(textos) != len(encabezados):
            raise DatoInvalidoError(f"Una fila tiene {len(textos)} valores y hay {len(encabezados)} encabezados.")
        lineas.append(SEPARADOR.join(textos))
    temporal = ruta.with_name(ruta.name + ".tmp")
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        # newline="\r\n": mismo fin de línea que el dataset de la cátedra (así git no ve cambios falsos).
        with open(temporal, "w", encoding="utf-8", newline="\r\n") as archivo:
            archivo.write("\n".join(lineas) + "\n")
        os.replace(temporal, ruta)
    except OSError as error:
        raise ArchivoInvalidoError(f"No se pudo escribir {ruta}: {error}") from None
