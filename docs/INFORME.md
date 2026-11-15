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

Código: `src/algoritmos/busqueda.py` (lineal y binaria), `src/algoritmos/ordenamiento.py` (selección, inserción y shell), usados desde `Recetario` (`src/dominio/recetario.py`) y las opciones 3 y 4 del menú. No se usa `sorted`, `list.sort` ni `bisect` para cumplir los requisitos (solo aparece `sorted` en el apéndice comparativo de las mediciones).

### Cómo se conecta con el CLI

- **3 → 1** búsqueda lineal por nombre (exacto, sin importar mayúsculas ni tildes); si no la encuentra muestra las recetas cuyo nombre contiene ese texto.
- **3 → 2** búsqueda binaria por nombre. El `Recetario` recuerda por qué criterio está ordenado (`orden_actual`). Si no está ordenado por nombre, **primero lo ordena (inserción) y avisa**; nunca corre la binaria sobre datos desordenados. Al agregar una receta al final que rompe el orden, `orden_actual` pasa a `None`.
- **3 → 3 / 3 → 4** búsqueda lineal de todas las recetas de una categoría / que usan un ingrediente.
- **3 → 5** por id con el índice `dict`.
- **4** ordenar por nombre, tiempo, dificultad o id con selección, inserción o shell.

Como el catálogo vive en una `ListaEnlazada` (sin acceso por índice), para ordenar y para la binaria se copia a una `list` con `a_lista()` (O(n)), se trabaja sobre la copia y, al ordenar, se rearma la lista enlazada en el nuevo orden (O(n)). Ese costo lineal queda tapado por el O(n²) del ordenamiento, pero sí pesa en la binaria (ver abajo).

### Tabla de complejidad

| Operación | Tiempo | Espacio extra | Por qué |
| --- | --- | --- | --- |
| Listar catálogo (opción 1) | O(n) | O(1) | El iterador visita cada nodo una vez. |
| Ver detalle por id (opción 2, con índice dict) | O(1) promedio | O(n) el índice | El dict calcula el hash del id y va directo a la receta. |
| Obtener por id sin índice (recorriendo la lista) | O(n) | O(1) | En el peor caso (último o inexistente) compara con los n nodos. |
| Búsqueda lineal por nombre | O(n) peor / O(1) mejor | O(1) | Compara de a uno hasta encontrarla o terminar la lista. |
| Búsqueda por categoría / ingrediente | O(n) / O(n·k) | O(r) resultados | Recorre todo el catálogo (quiere *todas* las coincidencias); k = ingredientes por receta. |
| Búsqueda binaria por nombre (lista ya ordenada) | O(log n) | O(1) | Cada comparación descarta la mitad del rango: con 3000 recetas, ~12 comparaciones. |
| Copiar `ListaEnlazada` → `list` antes de la binaria | O(n) | O(n) | Hay que recorrer los n nodos; es el precio de no tener índices en la lista enlazada. |
| Ordenar por selección | O(n²) siempre | O(n) copia | Para cada i busca el mínimo de lo que queda: n−1 + n−2 + … + 1 ≈ n²/2 comparaciones, aunque ya esté ordenado. |
| Ordenar por inserción | O(n) mejor / O(n²) peor y promedio | O(n) copia | Si ya está ordenado cada elemento se compara una vez; si está al revés desplaza todo. |
| Ordenar por shell (gaps n/2, n/4, …, 1) | ~O(n^1.3) en la práctica, O(n²) peor | O(n) copia | Inserción con saltos: acerca rápido los elementos lejanos y la pasada final con gap 1 trabaja sobre algo casi ordenado. |
| Rearmar la lista enlazada después de ordenar | O(n) | O(n) | `insertar_al_final` es O(1) gracias a `_ultimo`. |
| Agregar receta al catálogo | O(1) | O(1) | `insertar_al_final` O(1) + alta en el dict O(1). |
| Menú semanal: agregar / quitar / cambiar día | O(1) / O(n) / O(n) | O(1) | Agregar al final usa `_ultimo`; quitar y cambiar día recorren (n ≤ 7). |
| Pila: apilar / desapilar / ver tope | O(1) | O(1) | Siempre se opera sobre la cabeza de la lista. |
| Cola: encolar / desencolar / ver frente | O(1) | O(1) | Se encola por `_ultimo` y se desencola por la cabeza. |
| Recursión `ingredientes_totales` | O(R + I) | O(p) pila de llamadas | R = recetas del árbol de sub-recetas, I = ingredientes de esas recetas; p = profundidad del árbol (2 en el dataset). |

### Estabilidad (selección vs. inserción)

Un ordenamiento es **estable** si dos elementos con la misma clave quedan en el mismo orden relativo que tenían antes. Ejemplo real, ordenando por **tiempo** el catálogo recién cargado (orden por id): Flan casero (#15) y Pollo al horno con papas (#22) tardan los dos 70 min.

- **Inserción (estable):** quedan Flan casero (#15) y después Pollo al horno (#22), como estaban. Solo desplaza los elementos *estrictamente* mayores, así que nunca saltea a uno igual.
- **Selección (no estable):** quedan al revés, #22 antes que #15. En la vuelta i = 14 el Flan (#15) estaba en la posición 14, el mínimo de lo que faltaba era Curry de garbanzos (#29, 40 min, posición 28) y el intercambio mandó al Flan a la posición 28, detrás del Pollo. Lo mismo pasa al ordenar por dificultad: entre las 11 recetas "media", selección las deja en orden 10, 11, 20, 21, 13, 5, ... e inserción en 5, 6, 9, 10, ...
- **Shell (no estable):** los saltos grandes también pueden invertir elementos iguales.

Por eso, si se quiere "ordenar por tiempo y, a igual tiempo, mantener el orden anterior", hay que usar inserción.

### Mediciones (`time.perf_counter`)

Script: `python -m src.algoritmos.medicion`. n = 30 es el dataset original; 300 y 3000 son copias agrandadas (×10 y ×100) repitiendo las filas con otro id y un sufijo en el nombre. Las operaciones rápidas se repiten cientos/miles de veces y se informa el promedio de una llamada. Máquina: notebook con Windows 11, Python 3.13.

| Operación | n | segundos |
| --- | --- | --- |
| listar catálogo (iterador ListaEnlazada) | 30 | 0.00000564 |
| listar catálogo (iterador ListaEnlazada) | 300 | 0.00004833 |
| listar catálogo (iterador ListaEnlazada) | 3000 | 0.00036503 |
| búsqueda lineal por nombre (peor caso: no existe) | 30 | 0.00000884 |
| búsqueda lineal por nombre (peor caso: no existe) | 300 | 0.00008022 |
| búsqueda lineal por nombre (peor caso: no existe) | 3000 | 0.00063646 |
| búsqueda binaria por nombre (no existe; lista ya ordenada) | 30 | 0.00000159 |
| búsqueda binaria por nombre (no existe; lista ya ordenada) | 300 | 0.00000325 |
| búsqueda binaria por nombre (no existe; lista ya ordenada) | 3000 | 0.00000318 |
| copiar ListaEnlazada a list (a_lista, previo a la binaria) | 30 | 0.00000524 |
| copiar ListaEnlazada a list (a_lista, previo a la binaria) | 300 | 0.00004327 |
| copiar ListaEnlazada a list (a_lista, previo a la binaria) | 3000 | 0.00034573 |
| obtener por id con índice dict (último id) | 30 | 0.00000018 |
| obtener por id con índice dict (último id) | 300 | 0.00000016 |
| obtener por id con índice dict (último id) | 3000 | 0.00000017 |
| obtener por id recorriendo la lista (último id) | 30 | 0.00000789 |
| obtener por id recorriendo la lista (último id) | 300 | 0.00006719 |
| obtener por id recorriendo la lista (último id) | 3000 | 0.00066842 |
| ordenar por nombre: selección | 30 | 0.00012757 |
| ordenar por nombre: selección | 300 | 0.00951773 |
| ordenar por nombre: selección | 3000 | 1.02643860 |
| ordenar por nombre: inserción (entrada desordenada) | 30 | 0.00007016 |
| ordenar por nombre: inserción (entrada desordenada) | 300 | 0.00423880 |
| ordenar por nombre: inserción (entrada desordenada) | 3000 | 0.45140850 |
| ordenar por nombre: inserción (entrada ya ordenada, mejor caso) | 30 | 0.00001211 |
| ordenar por nombre: inserción (entrada ya ordenada, mejor caso) | 300 | 0.00010287 |
| ordenar por nombre: inserción (entrada ya ordenada, mejor caso) | 3000 | 0.00157860 |
| ordenar por nombre: shell | 30 | 0.00005723 |
| ordenar por nombre: shell | 300 | 0.00095810 |
| ordenar por nombre: shell | 3000 | 0.01634770 |
| [apéndice] sorted() de Python por nombre | 30 | 0.00000581 |
| [apéndice] sorted() de Python por nombre | 300 | 0.00007187 |
| [apéndice] sorted() de Python por nombre | 3000 | 0.00180880 |

Lectura de los resultados (lo que se ve en la tendencia):

- **Lineal (O(n))**: al multiplicar n por 10 el tiempo se multiplica por ~10 (listar, búsqueda lineal, obtener sin índice, copiar a list).
- **Binaria (O(log n))**: casi no cambia entre 30, 300 y 3000; pasa de ~5 a ~12 comparaciones.
- **Selección e inserción (O(n²))**: al multiplicar n por 10 el tiempo se multiplica por ~100 (de 300 a 3000 pasa de centésimas de segundo a casi un segundo en selección).
- **Inserción en el mejor caso (ya ordenada)**: crece lineal, como predice O(n).
- **Shell** queda muy por debajo de selección e inserción a medida que n crece.
- **Índice dict**: el tiempo es el mismo con 30 o con 3000 recetas (O(1)), mientras que buscar el mismo id recorriendo la lista crece lineal.
- `sorted()` de Python (Timsort, en C) es el más rápido: se deja solo como referencia, no se usa para cumplir el requisito.

### Índice dict además de la lista enlazada (nota extra)

El catálogo completo vive en la `ListaEnlazada` (es la estructura "oficial": el listado, el orden y las búsquedas por nombre la recorren). Además `Recetario` mantiene `_indice`, un `dict` id → `Receta`.

- **Qué ganamos:** buscar por id (ver detalle, agregar al menú, encolar, la recursión que pide cada sub-receta por id) pasa de O(n) a O(1). En las mediciones: con 3000 recetas, ~0,17 µs con el índice contra ~670 µs recorriendo la lista.
- **Qué pagamos:** memoria extra O(n) (una entrada por receta, aunque las recetas no se duplican: el dict guarda referencias a los mismos objetos) y **sincronización**: cada alta o baja tiene que actualizar la lista **y** el dict; si uno se olvida, quedan inconsistentes. Por eso todas las altas/bajas pasan por métodos de `Recetario` (`agregar`, y en E5 `eliminar`) y nadie toca `_indice` desde afuera.
- El índice solo sirve para buscar por id exacto: para nombre, categoría o ingrediente igual hay que recorrer (o ordenar y usar binaria).

### Tercer algoritmo (nota extra)

Además de selección e inserción se implementó **Shell sort** (`ordenar_shell`), disponible en el menú (opción 4 → algoritmo 3) y medido en la tabla de arriba.

## 6. Persistencia (E5)

- Layout del registro binario (campos, `struct`, anchos):
- Header:
- Cómo se actualiza un registro por posición:

## 7. Reparto de trabajo (E6)

| Integrante | Qué hizo | Qué puede defender |
| --- | --- | --- |
| Viliani Christian | Todo el trabajo (trabajo individual) | Todo el repo |
