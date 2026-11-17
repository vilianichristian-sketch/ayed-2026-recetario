# AyED C2 2026 — Recetario

Gestor de un **libro de recetas** en consola (CLI), hecho en Python 3 con biblioteca estándar.

## Integrante

| Nombre | Mail | GitHub |
| --- | --- | --- |
| Viliani Christian | viliani.christian@gmail.com | @vilianichristian-sketch |

**Comisión:** 1 (trabajo individual grupo 69)

**Tema elegido:** Recetario (`TEMA = "recetario"` en `src/config.py`): un libro de 30 recetas donde una receta puede usar otras como sub-recetas (el asado usa chimichurri y salsa criolla), con menú semanal, historial de recetas cocinadas y cola de preparación.

## Cómo ejecutar

Desde la raíz del repo, con Python 3.10 o superior:

```text
python -m src.main
```

En Windows, si `python` no anda: `py -3 -m src.main`.

Solo biblioteca estándar. No hay `requirements.txt` a propósito.

## Qué hace (producto final: E6)

Gestor de catálogo por consola con las 10 operaciones de la consigna: listar, ver detalle, buscar (lineal y binaria), ordenar (selección, inserción y shell), recursión de sub-recetas, ABM del menú semanal con tope de 7 y de las recetas, historial (pila), cola de preparación y persistencia en `.txt` y en binario con `struct`.

| Opción | Estado |
| --- | --- |
| 1. Listar catálogo | ✅ recorre la `ListaEnlazada` con su iterador |
| 2. Ver detalle | ✅ por id, con índice `dict` O(1) |
| 3. Buscar | ✅ lineal por nombre / categoría / ingrediente; binaria por nombre (ordena y avisa si hace falta) |
| 4. Ordenar | ✅ por nombre, tiempo, dificultad o id con selección, inserción o shell (propios) |
| 5. Operación recursiva | ✅ árbol de sub-recetas e ingredientes totales (con traza) |
| 6. ABM | ✅ menú semanal (alta / baja / modificación sobre `ListaEnlazada`, tope 7) y recetas del catálogo; todo persistente |
| 7. Historial (pila) | ✅ registrar (apilar), deshacer (desapilar), ver última (tope) |
| 8. Cola de preparación | ✅ encolar, preparar siguiente (desencolar → historial), ver próxima, encolar el menú |
| 9. Archivos | ✅ cargar/guardar en `.txt` y en binario (`struct`, registros de longitud fija) y leer un registro por posición |

Al arrancar, el catálogo se lee de `data/recetas.txt`, `data/ingredientes.txt` y `data/subrecetas.txt`, se genera `data/recetas.bin` y se recupera el menú semanal de `data/menu_semanal.txt` (si existe). Los dos últimos los crea el programa y están en `.gitignore`.

Cada alta, baja o modificación (opción 6) queda guardada enseguida: en el binario el alta es un *append*, la modificación pisa solo ese registro con `seek` y la baja reescribe el archivo.

Mediciones de tiempo: `python -m src.algoritmos.medicion` (resultados en `docs/INFORME.md` §5).

## Cómo probarlo

- **Protocolo de pruebas manual:** `docs/PROTOCOLO_PRUEBAS.md` (27 casos con pasos, datos y resultado esperado; todos ejecutados en E6).
- **Mediciones de tiempo:** `python -m src.algoritmos.medicion` (tabla en `docs/INFORME.md` §5).
- **Recorrido rápido para mostrar en la defensa:**
  1. `1` listar → `2` detalle del id `9` (Asado).
  2. `5` → `3` con id `9`: traza de la recursión.
  3. `6` → `2` agregar `10`, `3`; `8` → `5` encolar el menú → `3` preparar; `7` → `1` ver historial → `3` deshacer.
  4. `3` → `2` buscar `Pesto` con binaria (avisa que ordena) → `4` ordenar por tiempo con inserción.
  5. `9` → `5` ver el registro en la posición `8` del binario; `6` → `7` modificar el id `9` (pisa solo ese registro con `seek`); `9` → `4` cargar desde binario y `2` detalle del `9`.

## Limitaciones conocidas

- Los nombres no pueden tener comas (se usan como separador en los `.txt`).
- En el binario el nombre ocupa 40 bytes (se recorta si es más largo) y solo se guarda el registro principal; ingredientes y sub-recetas quedan en los `.txt`.
- El historial y la cola de preparación no se guardan entre ejecuciones (el catálogo y el menú semanal sí).
- No se pueden agregar sub-recetas a una receta existente ni borrar una receta que otra usa como sub-receta.

## Documentación

- `docs/INFORME.md`: tema, modelo y mutabilidad, recursión con traza, TADs e invariantes, complejidad y mediciones, formato del binario, reparto, mapa de requisitos y limitaciones.
- `docs/PROTOCOLO_PRUEBAS.md`: casos de prueba y resultados.
- `docs/DECLARACION_IA.md`: uso de IA por entrega.

## Estructura

```text
src/
  config.py        TEMA elegido
  main.py          menú + despacho de opciones (sin lógica del negocio)
  excepciones.py   excepciones propias
  cli/             entrada.py (lectura segura de datos) y pantallas.py (una función por opción)
  dominio/         Receta, Ingrediente, Recetario, MenuSemanal, Historial, ColaPreparacion,
                   SistemaRecetario,
                   desglose.py (recursión), normalizar.py
  tads/            Nodo, ListaEnlazada (con iterador), Pila y Cola
  algoritmos/      busqueda.py, ordenamiento.py, medicion.py
  persistencia/    texto.py (.txt), binario.py (struct), repositorio.py (archivos <-> dominio)
data/              recetas.txt, ingredientes.txt, subrecetas.txt (+ recetas.bin generado)
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
