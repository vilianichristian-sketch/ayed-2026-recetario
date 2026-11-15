"""Normalización de textos para comparar nombres sin importar mayúsculas ni tildes."""

import unicodedata


def normalizar(texto):
    """'  Puré de Papas ' -> 'pure de papas'.

    Separa cada letra de su tilde (forma NFD) y descarta las marcas de tilde.
    """
    descompuesto = unicodedata.normalize("NFD", texto.strip().lower())
    sin_tildes = []
    for caracter in descompuesto:
        if unicodedata.category(caracter) != "Mn":  # Mn = marca diacrítica (tilde)
            sin_tildes.append(caracter)
    return "".join(sin_tildes)
