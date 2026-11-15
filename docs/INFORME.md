# Informe del TP

Completar y hacer crecer en cada entrega. No hace falta prosa larga: oraciones claras y tablas.

## 1. Grupo y tema

- Integrante: Viliani Christian (viliani.christian@gmail.com), comisión 1 (trabajo individual).

- Tema: **Recetario** (libro de recetas con sub-recetas, menú semanal y cola de preparación).
- Por qué se eligió:
  - Es un dominio que todos conocemos: no hace falta estudiar reglas de un juego para entender los datos.
  - La relación recursiva es natural y fácil de explicar: una receta usa otras recetas (el asado usa chimichurri y salsa criolla; las empanadas usan sofrito y masa).
  - Permite una operación recursiva "de verdad": juntar los ingredientes totales de una receta explotando sus sub-recetas y sumando cantidades repetidas.
  - Las estructuras lineales tienen un uso claro: el menú de la semana (lista con tope de 7 días), las recetas cocinadas (pila, para deshacer la última) y la cola de preparación (la primera receta que entra es la primera que se cocina).
  - El dataset de la cátedra (30 recetas, ~110 ingredientes, 14 relaciones de sub-receta) alcanza para medir y probar.

## 2. Modelo

**Ítem del catálogo:** una receta, con `id`, `nombre`, `tiempo_min`, `dificultad` y `categoria`.

En E1 el catálogo es una **lista de Python** (`CATALOGO` en `src/dominio/receta.py`) y cada receta es un **diccionario**.

Qué es mutable y qué no (y por qué lo elegimos así):

| Elemento | Tipo | ¿Mutable? | Por qué |
| --- | --- | --- | --- |
| `CATALOGO` | `list` | Sí | El catálogo va a crecer y achicarse (altas y bajas). |
| Cada receta | `dict` | Sí | Se pueden modificar campos (por ejemplo el tiempo) sin crear otra receta. |
| Claves del dict (`"id"`, `"nombre"`, ...) | `str` | No | Las claves de un dict tienen que ser inmutables (hashables). |
| `id`, `tiempo_min` | `int` | No | Un número no se modifica: si cambia el tiempo, se reemplaza el valor de la clave. |
| `nombre`, `dificultad`, `categoria` | `str` | No | Los strings son inmutables: "modificar" un nombre es asignar un string nuevo. |
| `DIFICULTADES` | `tuple` | No | Los valores válidos (`baja`, `media`, `alta`) son fijos; con una tupla nadie los puede alterar por error. |
| `TEMA` (en `config.py`) | `str` | No | Se elige una vez y no cambia entre entregas. |

Consecuencia práctica: como `CATALOGO` y los dicts son mutables, si una función recibe una receta y le cambia un valor, el cambio se ve en el catálogo (se pasa la referencia, no una copia).

```text
CATALOGO (list)
 ├── {"id": 1, "nombre": "Chimichurri", "tiempo_min": 15, "dificultad": "baja", "categoria": "salsa"}
 ├── {"id": 2, "nombre": "Salsa criolla", ...}
 └── ...
```

Funciones (cada acción del menú es una función; `main` solo despacha):

- `listar_catalogo()` — imprime todas las recetas.
- `buscar_por_id(id)` — devuelve el dict de la receta o `None`.
- `formatear_resumen(item)` / `formatear_detalle(item)` — arman el texto a mostrar.

## 3. Recursión (E2)

- Función:
- Caso base:
- Caso recursivo:
- Traza de un ejemplo real del dataset:

## 4. TADs (E3)

| TAD | Operaciones | Invariante |
| --- | --- | --- |
| ListaEnlazada |  |  |
| Pila |  |  |
| Cola |  |  |

Dónde se usa cada uno en el dominio.

## 5. Complejidad (E4)

| Operación | Tiempo | Espacio | Por qué |
| --- | --- | --- | --- |
|  |  |  |  |

Mediciones (`time.perf_counter`):

| Operación | n | segundos |
| --- | --- | --- |
|  |  |  |

## 6. Persistencia (E5)

- Layout del registro binario (campos, `struct`, anchos):
- Header:
- Cómo se actualiza un registro por posición:

## 7. Reparto de trabajo (E6)

| Integrante | Qué hizo | Qué puede defender |
| --- | --- | --- |
| Viliani Christian | Todo el trabajo (trabajo individual) | Todo el repo |
