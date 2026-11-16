"""Elegir un tema y no cambiarlo entre entregas."""

from pathlib import Path

# "pokedex" | "recetario" | "musica"
TEMA = "recetario"

# Rutas de los archivos (relativas a la raíz del repo, así anda desde cualquier carpeta).
RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ / "data"
RUTA_BINARIO = CARPETA_DATOS / "recetas.bin"
