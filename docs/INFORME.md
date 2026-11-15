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

Funciones de E1 (cada acción del menú es una función; `main` solo despacha). En E2 pasan a ser métodos de las clases de abajo:

- `listar_catalogo()` — imprime todas las recetas.
- `buscar_por_id(id)` — devuelve el dict de la receta o `None`.
- `formatear_resumen(item)` / `formatear_detalle(item)` — arman el texto a mostrar.

### Clases del dominio (E2)

Desde E2 el código está partido en módulos y cada concepto es una clase:

| Clase | Archivo | Responsabilidad |
| --- | --- | --- |
| `Ingrediente` | `src/dominio/ingrediente.py` | nombre, cantidad y unidad de un ingrediente |
| `Receta` | `src/dominio/receta.py` | ítem del catálogo + sus ingredientes propios |
| `Recetario` | `src/dominio/recetario.py` | catálogo (libro de recetas) y relación receta → sub-recetas |
| `MenuSemanal` | `src/dominio/menu_semanal.py` | colección principal: hasta 7 recetas, una por día |
| `SistemaRecetario` | `src/dominio/sistema.py` | agrupa catálogo y colecciones; es lo único que ve el CLI |
| (funciones) | `src/dominio/desglose.py` | operación recursiva del dominio |
| (funciones) | `src/cli/pantallas.py`, `src/cli/entrada.py` | entrada/salida de cada opción del menú |

`src/main.py` solo arma el menú y despacha cada opción a una función de `src/cli/pantallas.py`.

Los datos iniciales siguen armados en el código (`src/dominio/datos_iniciales.py`, tuplas inmutables copiadas del dataset); los `.txt` se leen en E5.

```text
SistemaRecetario
 ├── recetario: Recetario
 │     ├── recetas: [Receta, Receta, ...]          (cada Receta tiene [Ingrediente, ...])
 │     └── subrecetas: {9: [1, 2], 10: [3, 5], ...}  (receta -> recetas que usa)
 └── menu: MenuSemanal  (hasta 7 Receta, una por día)
```

### Encapsulamiento y TADs en el modelo (E3)

```text
SistemaRecetario                      (el CLI solo usa sus métodos/properties públicos)
 ├── recetario: Recetario
 │     ├── _recetas: ListaEnlazada[Receta]        catálogo completo (bonus: el catálogo también es lista enlazada)
 │     └── _subrecetas: dict {id: [ids]}          relación receta -> sub-recetas
 ├── menu: MenuSemanal
 │     └── _recetas: ListaEnlazada[Receta]        colección principal, tope 7 (un día por posición)
 ├── historial: Historial
 │     └── _pila: Pila  (sobre ListaEnlazada)     recetas cocinadas, la última arriba
 └── cola: ColaPreparacion
       └── _cola: Cola  (sobre ListaEnlazada)     recetas esperando para cocinarse
```

Flujo entre colecciones: **menú semanal** → (opción 8.5) se encolan todas en la **cola de preparación** → (8.3) "preparar la siguiente" desencola la primera y la **apila en el historial** → (7.3) "deshacer" desapila la última cocinada.

Encapsulamiento:

- Todos los atributos internos empiezan con `_` (`_cabeza`, `_items`, `_recetas`, `_pila`, ...). Desde `src/cli/` y `src/main.py` **nunca** se accede a ellos: solo se llaman métodos (`agregar`, `quitar`, `apilar`, `desencolar`, ...).
- `Receta` expone sus datos con `@property`. Los setters validan (nombre sin comas ni vacío, tiempo entero > 0, dificultad `baja|media|alta`) y lanzan `DatoInvalidoError`. El `id` no tiene setter: es la identidad de la receta.
- `Receta.ingredientes` devuelve una **tupla** (copia inmutable): desde afuera no se puede modificar la lista interna.
- `Ingrediente` es inmutable (solo properties de lectura).

Excepciones propias (`src/excepciones.py`, todas heredan de `RecetarioError`):

| Excepción | Cuándo se lanza | Dónde se captura |
| --- | --- | --- |
| `ItemNoEncontradoError` | id de receta inexistente; receta que no está en el menú; día sin receta | pantallas 2, 5, 6, 7, 8 |
| `ColeccionLlenaError` | agregar una 8.ª receta al menú semanal | pantalla 6 |
| `ColeccionVaciaError` | quitar/cambiar en el menú vacío; encolar el menú vacío | pantallas 6 y 8 |
| `PilaVaciaError` | deshacer / ver la última con el historial vacío | pantalla 7 |
| `ColaVaciaError` | preparar / ver la próxima con la cola vacía | pantalla 8 |
| `SubrecetaFaltanteError`, `CicloSubrecetasError` | datos inconsistentes en la recursión | pantalla 5 |
| `DatoInvalidoError` | valor inválido para una receta | altas/modificaciones (E5) |
| `ArchivoInvalidoError` | archivo inexistente, truncado o con formato malo | archivos (E5) |

Además `main.py` tiene una red de seguridad `except RecetarioError` alrededor de cada opción. No hay ningún `except:` pelado.

## 3. Recursión (E2)

Archivo: `src/dominio/desglose.py`. Datos: `subrecetas.txt` + `ingredientes.txt` (en E2 cargados desde `datos_iniciales.py`).

Hay dos funciones recursivas con la misma estructura:

- `arbol_subrecetas(recetario, id_receta, camino=())` → lista de `(nivel, receta)` con la receta y todas sus sub-recetas (directas e indirectas).
- `ingredientes_totales(recetario, id_receta, camino=(), traza=None)` → dict `{(nombre, unidad): cantidad}` con los ingredientes propios **más** los de todas las sub-recetas, sumando los repetidos.

- **Caso base:** la receta no tiene sub-recetas (`recetario.subrecetas_de(id)` devuelve vacío) → es una receta "hoja": se devuelven solo sus propios ingredientes (o solo ella misma en el árbol).
- **Caso recursivo:** la receta usa sub-recetas → se llama a la misma función para cada sub-receta (un problema más chico: está un nivel más abajo en el árbol) y se suman/concatenan los resultados.
- **Por qué termina:** cada llamada baja un nivel en el árbol de sub-recetas, y el árbol es finito. `camino` guarda los ids que se están desglosando; si un id aparece dos veces hay un ciclo y se lanza `CicloSubrecetasError` en lugar de recursión infinita.
- Si una sub-receta referenciada no existe en el catálogo se lanza `SubrecetaFaltanteError`.

### Traza de un ejemplo real del dataset: `ingredientes_totales(recetario, 9)` (Asado)

Según `subrecetas.txt`: `9,1` y `9,2` → el Asado (9) usa Chimichurri (1) y Salsa criolla (2). Ninguna de esas dos usa otra receta.

```text
Llamada 1: ingredientes_totales(9)  [Asado]           camino = ()
           propios: vacio 1200 g, chorizo 4 u, sal gruesa 20 g          -> 3 ingredientes
           subrecetas_de(9) = [1, 2]  -> NO es caso base, llama por cada sub-receta

    Llamada 2: ingredientes_totales(1)  [Chimichurri]  camino = (9,)
               propios: perejil 50 g, ajo 4 dientes, oregano 5 g,
                        aceite de oliva 80 ml, vinagre 30 ml, aji molido 5 g
               subrecetas_de(1) = []  -> CASO BASE: devuelve sus 6 ingredientes
    (se desapila la llamada 2; la llamada 1 suma esos 6 a sus 3 -> 9 claves)

    Llamada 3: ingredientes_totales(2)  [Salsa criolla] camino = (9,)
               propios: tomate 3 u, cebolla 1 u, morron 1 u,
                        aceite de oliva 40 ml, vinagre 20 ml
               subrecetas_de(2) = []  -> CASO BASE: devuelve sus 5 ingredientes
    (se desapila la llamada 3; la llamada 1 suma: aceite de oliva 80+40 = 120 ml,
     vinagre 30+20 = 50 ml, y agrega tomate, cebolla y morron -> 12 claves)

Llamada 1 devuelve 12 ingredientes:
  vacio 1200 g, chorizo 4 u, sal gruesa 20 g, perejil 50 g, ajo 4 dientes,
  oregano 5 g, aceite de oliva 120 ml, vinagre 50 ml, aji molido 5 g,
  tomate 3 u, cebolla 1 u, morron 1 u
```

Pila de llamadas en el momento más profundo: `[ingredientes_totales(9), ingredientes_totales(1)]` → profundidad 2.

La misma traza la imprime el programa: menú **5 → 3** con id `9`.

### Traza de `arbol_subrecetas(recetario, 10)` (Empanadas de carne)

`subrecetas.txt`: `10,3` y `10,5`.

```text
Llamada 1: arbol(10) -> subrecetas [3, 5] -> resultado = [(0, Empanadas de carne)]
    Llamada 2: arbol(3)  -> subrecetas []  -> CASO BASE -> [(1, Sofrito)]
    Llamada 3: arbol(5)  -> subrecetas []  -> CASO BASE -> [(1, Masa de empanadas)]
Resultado: [(0, Empanadas de carne)] + [(1, Sofrito)] + [(1, Masa de empanadas)]
```

Ejemplo **sin** cadena (caso base directo): `arbol_subrecetas(recetario, 3)` → `[(0, Sofrito)]`; `ingredientes_totales(recetario, 3)` → solo los 4 ingredientes del sofrito.

## 4. TADs (E3)

Implementados en `src/tads/`, sin `list` de Python por debajo: cada dato vive en un `Nodo` con referencia `siguiente`.

| TAD | Operaciones | Invariante |
| --- | --- | --- |
| `Nodo` | `dato`, `siguiente` | `siguiente` es otro `Nodo` o `None` (último) |
| `ListaEnlazada` | `esta_vacia`, `tamanio`/`len`, `insertar_al_inicio` O(1), `insertar_al_final` O(1), `insertar_ordenado` O(n), `eliminar(dato)` O(n), `eliminar_primero` O(1), `primero` O(1), `buscar` / `buscar_por(condicion)` O(n), `obtener_en` / `reemplazar_en` O(n), `a_lista` O(n), `__iter__` (iterador propio con `__next__`) | `_tamanio == 0` ⇔ `_cabeza is None` ⇔ `_ultimo is None`; desde `_cabeza` siguiendo `.siguiente` se visitan exactamente `_tamanio` nodos y el último es `_ultimo` (con `.siguiente is None`) |
| `Pila` | `apilar` O(1), `desapilar` O(1), `ver_tope` O(1), `esta_vacia`, `tamanio`, `__iter__` (tope → base) | el tope es la cabeza de la lista = el último dato apilado que no se desapiló; `desapilar`/`ver_tope` en vacía lanzan `PilaVaciaError` |
| `Cola` | `encolar` O(1), `desencolar` O(1), `ver_frente` O(1), `esta_vacia`, `tamanio`, `__iter__` (frente → final) | el frente es la cabeza = el dato más antiguo sin desencolar; se encola por `_ultimo`; en vacía lanzan `ColaVaciaError` |

Decisiones:

- La lista guarda `_ultimo` además de `_cabeza` para que `insertar_al_final` (y por lo tanto `encolar`) sea O(1) en lugar de recorrer toda la lista.
- `Pila` y `Cola` usan `primero()` / `eliminar_primero()` de la lista, así no tocan `_cabeza` de otra clase.
- El iterador es una clase propia (`IteradorLista`) con `__iter__` y `__next__`; cuando llega a `None` lanza `StopIteration` y el `for` termina.

Dónde se usa cada uno en el dominio:

| Estructura | Clase del dominio | Uso |
| --- | --- | --- |
| `ListaEnlazada` | `Recetario._recetas` | catálogo completo; la opción 1 lo lista con `for receta in recetario` (iterador) |
| `ListaEnlazada` con tope | `MenuSemanal._recetas` | colección principal: alta / baja / modificación, máximo 7 (`ColeccionLlenaError`) |
| `Pila` | `Historial._pila` | recetas cocinadas; deshacer = desapilar la última |
| `Cola` | `ColaPreparacion._cola` | la primera receta encolada es la primera que se prepara |

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
