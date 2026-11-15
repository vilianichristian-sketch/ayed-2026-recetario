# TP integrador — AyED C2 2026 · Recetario

Repositorio del grupo. Gestor de un **libro de recetas** en consola (CLI), hecho en Python 3 con biblioteca estándar.

## Integrante

| Nombre | Mail | GitHub |
| --- | --- | --- |
| Viliani Christian | viliani.christian@gmail.com | @vilianichristian-sketch |

**Comisión:** 1 (trabajo individual)

**Tema elegido:** Recetario (`TEMA = "recetario"` en `src/config.py`).

## Cómo ejecutar

Desde la raíz del repo, con Python 3.10 o superior:

```text
python -m src.main
```

En Windows, si `python` no anda: `py -3 -m src.main`.

Solo biblioteca estándar. No hay `requirements.txt` a propósito.

## Qué hace (estado en esta entrega: E1)

| Opción | Estado |
| --- | --- |
| 1. Listar catálogo | ✅ catálogo armado a mano en `src/dominio/receta.py` |
| 2. Ver detalle | ✅ por id |
| 3 a 9 | se completan en las próximas entregas |

## Estructura

```text
src/
  config.py        TEMA elegido
  main.py          menú + despacho de opciones
  excepciones.py   excepciones propias
  dominio/         receta.py: catálogo (lista de dicts) y funciones de listado/detalle
  tads/            (E3)
  algoritmos/      (E4)
  persistencia/    (E5)
data/              datasets .txt (se leen recién en E5)
docs/              INFORME.md, PROTOCOLO_PRUEBAS.md, DECLARACION_IA.md
```

## Entregas

Cada vencimiento se marca con un tag. Ver `GIT.md`.

| Tag | Vence |
| --- | --- |
| `preentrega` (opcional, solo repo) | domingo 30-ago-2026 23:59 |
| `entrega-1` | domingo 06-sep-2026 23:59 |
| `entrega-2` | domingo 20-sep-2026 23:59 |
| `entrega-3` | domingo 04-oct-2026 23:59 |
| `entrega-4` | domingo 01-nov-2026 23:59 |
| `entrega-5` | domingo 15-nov-2026 23:59 |
| `entrega-6` | domingo 22-nov-2026 23:59 |

Defensa oral (reemplaza el 2do parcial): 25 y 27-nov-2026.

La cátedra corrige el **tag**, no el último commit suelto de `main`.
