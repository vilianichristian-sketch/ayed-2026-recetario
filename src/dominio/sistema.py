"""Clase SistemaRecetario: agrupa el catálogo y las colecciones del dominio.

El CLI solo habla con esta clase (y a través de ella con el recetario y el
menú semanal); no conoce cómo están guardados los datos por dentro.
"""

from src.dominio.menu_semanal import MenuSemanal
from src.dominio.recetario import Recetario


class SistemaRecetario:
    def __init__(self):
        self.recetario = Recetario()
        self.recetario.cargar_datos_iniciales()
        self.menu = MenuSemanal()
