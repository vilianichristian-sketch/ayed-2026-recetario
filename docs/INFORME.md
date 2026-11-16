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

En E2–E4 los datos iniciales estaban armados en el código (`src/dominio/datos_iniciales.py`, tuplas inmutables copiadas del dataset). **Desde E5 ese módulo se borró**: el catálogo se lee de `data/*.txt` al arrancar (`src/persistencia/repositorio.py`).

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
- Mutabilidad en el modelo final: `Receta` es mutable a propósito (la modificación del ABM cambia sus campos a través de setters que validan) pero su `id` no; `Ingrediente` es inmutable; las claves del dict de la recursión son tuplas `(nombre, unidad)`, que pueden ser clave justamente por ser inmutables (una `list` no podría); `DIFICULTADES` y `DIAS` son tuplas.

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

Archivo: `src/dominio/desglose.py`. Datos: `subrecetas.txt` + `ingredientes.txt` (en E2–E4 cargados desde `datos_iniciales.py`; desde E5 leídos de los `.txt`).

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
| `ListaEnlazada` | `esta_vacia`, `tamanio`/`len`, `insertar_al_inicio` O(1), `insertar_al_final` O(1), `insertar_ordenado` O(n), `eliminar(dato)` O(n), `eliminar_primero` O(1), `primero` / `ultimo` O(1), `buscar` / `buscar_por(condicion)` O(n), `obtener_en` / `reemplazar_en` O(n), `a_lista` O(n), `__iter__` (iterador propio con `__next__`) | `_tamanio == 0` ⇔ `_cabeza is None` ⇔ `_ultimo is None`; desde `_cabeza` siguiendo `.siguiente` se visitan exactamente `_tamanio` nodos y el último es `_ultimo` (con `.siguiente is None`) |
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
| Cargar / guardar `.txt` (E5) | O(n + I + S) | O(n + I + S) | Lectura/escritura secuencial: una línea por receta, ingrediente (I) y relación de sub-receta (S). |
| Guardar / cargar binario completo (E5) | O(n) | O(n) | Un `struct.pack` / `unpack` de 74 bytes por registro. |
| Leer o actualizar un registro del binario por posición (E5) | O(1) | O(1) | `seek(9 + p·74)` va directo al registro; se leen/escriben solo 74 bytes. |
| Alta en el binario (append) (E5) | O(1) | O(1) | `seek(0, 2)` al final, un registro, y se reescribe solo el header. |
| Baja en el binario (E5) | O(n) | O(n) | Hay que correr los registros siguientes: se reescribe el archivo sin ese registro. |
| Posición de un id en la lista (E5) | O(n) | O(1) | `posicion_de` recorre la lista con el iterador hasta encontrarlo. |
| Baja de receta en memoria (E5) | O(n + S) | O(1) | Revisa si otra receta la usa (S relaciones) y la saca de la lista enlazada (O(n)) y del dict (O(1)). |

### Estabilidad (selección vs. inserción)

Un ordenamiento es **estable** si dos elementos con la misma clave quedan en el mismo orden relativo que tenían antes. Ejemplo real, ordenando por **tiempo** el catálogo recién cargado (orden por id): Flan casero (#15) y Pollo al horno con papas (#22) tardan los dos 70 min.

- **Inserción (estable):** quedan Flan casero (#15) y después Pollo al horno (#22), como estaban. Solo desplaza los elementos *estrictamente* mayores, así que nunca saltea a uno igual.
- **Selección (no estable):** quedan al revés, #22 antes que #15. En la vuelta i = 14 el Flan (#15) estaba en la posición 14, el mínimo de lo que faltaba era Curry de garbanzos (#29, 40 min, posición 28) y el intercambio mandó al Flan a la posición 28, detrás del Pollo. Lo mismo pasa al ordenar por dificultad: entre las 11 recetas "media", selección las deja en orden 10, 11, 20, 21, 13, 5, ... e inserción en 5, 6, 9, 10, ...
- **Shell (no estable):** los saltos grandes también pueden invertir elementos iguales.

Por eso, si se quiere "ordenar por tiempo y, a igual tiempo, mantener el orden anterior", hay que usar inserción.

### Mediciones (`time.perf_counter`)

Script: `python -m src.algoritmos.medicion` (desde E5 lee el dataset de `data/*.txt`). n = 30 es el dataset original; 300 y 3000 son copias agrandadas (×10 y ×100) repitiendo las filas con otro id y un sufijo en el nombre. Las operaciones rápidas se repiten cientos/miles de veces y se informa el promedio de una llamada. Máquina: notebook con Windows 11, Python 3.13.

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

Código: `src/persistencia/texto.py` (texto genérico), `src/persistencia/binario.py` (struct) y `src/persistencia/repositorio.py` (traduce filas ⇄ objetos del dominio y aplica la regla de oro). En el menú: opción **9** (cargar/guardar en los dos formatos y ver un registro por posición) y opción **6** (ABM persistente).

| Opción | Qué hace |
| --- | --- |
| 9 → 1 | cargar el catálogo desde un `.txt` (Enter = `data/recetas.txt`) |
| 9 → 2 | guardar el catálogo en `.txt` |
| 9 → 3 | guardar el catálogo en binario |
| 9 → 4 | cargar el catálogo desde binario |
| 9 → 5 | leer UN registro del binario por posición (acceso directo) |
| 6 → 2 / 3 / 4 | alta / baja / modificación del menú semanal (se guarda en `data/menu_semanal.txt`) |
| 6 → 5 / 6 / 7 | alta / baja / modificación de recetas del catálogo (se guardan en `.txt` y `.bin`) |

### Texto simple (.txt)

- Formato: UTF-8, un registro por línea, campos separados por coma, primera línea con los encabezados.
- Archivos: `recetas.txt` (`id,nombre,tiempo_min,dificultad,categoria`), `ingredientes.txt` (`receta_id,nombre,cantidad,unidad`) y `subrecetas.txt` (`receta_id,subreceta_id`).
- **Lectura secuencial:** `cargar_texto` recorre el archivo línea por línea, valida que los encabezados sean los esperados y que cada línea tenga la cantidad justa de campos; si no, lanza `ArchivoInvalidoError` con el número de línea. `repositorio.py` convierte cada fila en `Receta` / `Ingrediente` (valida tipos: id y tiempo enteros, dificultad válida, etc.) y verifica que ingredientes y sub-recetas apunten a recetas que existen.
- **Escritura completa:** `guardar_texto` reescribe el archivo entero (encabezados + filas). Primero escribe un `.tmp` y después hace `os.replace`: si algo falla a la mitad, el archivo anterior queda intacto. No se permiten comas en los valores (los setters de `Receta` e `Ingrediente` ya las rechazan).
- Al arrancar, `main.py` carga el catálogo desde `data/*.txt`, genera `data/recetas.bin` con ese catálogo y recupera el menú semanal guardado. Si los archivos están mal, avisa y arranca con el catálogo vacío (no explota).
- Se escribe con fin de línea `\r\n`, igual que el dataset de la cátedra: si los datos no cambiaron, git no ve diferencias.

### Regla de oro: memoria = archivos

Después de **cada** cambio del catálogo (cargar, ordenar, alta, baja, modificación) se actualizan los archivos (`repositorio.guardar_todo` y las funciones `persistir_*`). El `.bin` queda siempre **en el mismo orden que la lista enlazada en memoria**, así que la posición de una receta en la lista (`Recetario.posicion_de(id)`, que recorre con el iterador) es también la posición de su registro en el binario. Eso es lo que permite el acceso directo en la modificación.

- Los `.txt` se guardan siempre completos y ordenados por id (es un archivo secuencial: no se puede "pisar" una línea del medio).
- Si alguna vez el `.bin` no coincide con la memoria (no existe, está dañado o tiene otra cantidad de registros), en lugar de append/baja/seek se reescribe entero con `guardar_binario`.

### Regla de oro: memoria = archivos

Después de **cada** cambio del catálogo (cargar, ordenar, alta, baja, modificación) se actualizan los archivos (`repositorio.guardar_todo` y las funciones `persistir_*`). El `.bin` queda siempre **en el mismo orden que la lista enlazada en memoria**, así que la posición de una receta en la lista (`Recetario.posicion_de(id)`, que recorre con el iterador) es también la posición de su registro en el binario. Eso es lo que permite el acceso directo en la modificación.

- Los `.txt` se guardan siempre completos y ordenados por id (es un archivo secuencial: no se puede "pisar" una línea del medio).
- Si alguna vez el `.bin` no coincide con la memoria (no existe, está dañado o tiene otra cantidad de registros), en lugar de append/baja/seek se reescribe entero con `guardar_binario`.

### ABM persistente (opción 6)

**Catálogo de recetas** (6 → 5, 6, 7). El cambio se hace en memoria y enseguida en los archivos, así sigue al cerrar y volver a abrir (P13, P14, P24, P27):

| Operación | Memoria | `.txt` | `.bin` |
| --- | --- | --- | --- |
| Alta (6 → 5) | `insertar_al_final` en la lista + índice | se reescribe completo | **append**: `alta_binario` hace `seek(0, 2)`, escribe el registro nuevo y vuelve al header (`seek(0)`) para poner cantidad + 1 |
| Baja (6 → 6) | se saca de la lista, del índice y del menú semanal | se reescribe completo | `baja_binario`: lee los registros, saca el de esa posición, `truncate()` y reescribe (si no, quedaría un hueco de 74 bytes y los siguientes se correrían) |
| Modificación (6 → 7) | setters de `Receta` (validan) | se reescribe completo | **acceso directo**: `actualizar_registro` hace `seek(9 + p·74)` y pisa solo esos 74 bytes |

- **Alta:** el id es el mayor id + 1; se piden nombre, tiempo, dificultad, categoría, ingredientes (`nombre,cantidad,unidad`) y sub-recetas existentes. Todo se valida antes de tocar el catálogo.
- **Baja:** no se permite borrar una receta que otra usa como sub-receta (por ejemplo Chimichurri, que usan Asado y Choripan): quedaría una sub-receta faltante y la recursión fallaría. Pide confirmación.
- **Modificación:** Enter vacío deja el valor actual; si algún valor nuevo es inválido no se cambia nada (se valida armando una `Receta` de prueba antes de asignar). El id no se puede cambiar.

**Menú semanal** (colección principal, 6 → 2, 3, 4): cada alta, baja o cambio de día se guarda en `data/menu_semanal.txt` (`dia,receta_id`). Al arrancar se recupera (P26). Si una receta del menú guardado ya no existe en el catálogo, se avisa y se omite. Ese archivo lo genera el programa y está en `.gitignore`.

### Binario con `struct` (registros de longitud fija)

Todo en *little-endian* (`<`), sin relleno entre campos. Tamaños calculados con `struct.calcsize`.

**Header** — formato `'<4s1sI'`, 9 bytes:

| Campo | Formato | Bytes | Valor |
| --- | --- | --- | --- |
| magia | `4s` | 4 | `b'AYED'` |
| tema | `1s` | 1 | `b'R'` (recetario) |
| cantidad | `I` | 4 | cantidad de registros (unsigned int) |

**Registro de receta** — formato `'<I40sH8s20s'`, 74 bytes:

| Campo | Formato | Bytes | Notas |
| --- | --- | --- | --- |
| id | `I` | 4 | unsigned int |
| nombre | `40s` | 40 | UTF-8; si sobra se rellena con `\0`, si no entra se recorta sin partir una letra con tilde |
| tiempo_min | `H` | 2 | unsigned short (0–65535) |
| dificultad | `8s` | 8 | UTF-8 (`baja`, `media`, `alta`), relleno con `\0` |
| categoria | `20s` | 20 | UTF-8, relleno con `\0` |

Tamaño del archivo = 9 + 74 × cantidad. Con las 30 recetas del dataset: 9 + 2220 = **2229 bytes**.

Al leer, las cadenas se recuperan con `datos.rstrip(b"\0").decode("utf-8")`.

En el binario va el **registro principal del catálogo**; los ingredientes y las sub-recetas (tablas auxiliares de largo variable) siguen en `.txt`. Al cargar desde binario se toman de ahí y se omiten las filas de recetas que no estén en el binario.

### Acceso directo: actualizar un registro por posición

Como todos los registros miden lo mismo, el registro de la posición `p` (0-based) empieza en el byte:

```text
offset(p) = TAM_HEADER + p * TAM_REGISTRO = 9 + p * 74
```

`actualizar_registro(ruta, p, receta)` abre el archivo en modo `"r+b"` (leer y escribir sin borrar; `"wb"` lo vaciaría), valida el header, hace `seek(offset(p))` y escribe **solo esos 74 bytes**; el resto del archivo no se toca: O(1). `leer_registro(ruta, p)` hace lo mismo pero leyendo. Ejemplo: con el catálogo ordenado por id, el Asado (id 9) está en la posición 8 → byte 9 + 8·74 = **601** (caso P14).

Ejemplo para la defensa: "si quiero modificar el registro 7, ¿a qué byte voy?" → 9 + 7·74 = **527**, porque el header ocupa 9 bytes y cada registro anterior 74.

Acceso secuencial vs. directo: en el `.txt`, para llegar al registro 500 hay que leer los 499 anteriores (las líneas miden distinto); en el `.bin` se calcula el byte y se salta con `seek`.

Para modificar "por id", la posición se obtiene de la lista en memoria (`Recetario.posicion_de`), que por la regla de oro coincide con la del `.bin`. En el menú: 6 → 7 (modificar) y 9 → 5 (ver un registro por posición).

### Validaciones de archivos (`ArchivoInvalidoError`)

| Problema | Cómo se detecta |
| --- | --- |
| el archivo no existe | `FileNotFoundError` se convierte en `ArchivoInvalidoError` |
| truncado (menos de 9 bytes) | no alcanza para leer el header |
| magia distinta de `AYED` | se compara el primer campo del header |
| otro tema | el byte de tema no es `R` |
| truncado o con bytes de más | el tamaño real no es 9 + 74 × cantidad |
| registro con datos inválidos | texto que no es UTF-8 o valores que la `Receta` rechaza |
| posición fuera de rango | `ItemNoEncontradoError` ("fuera de rango") |
| `.txt` roto: línea con más o menos campos que el encabezado | `cargar_texto` compara la cantidad de campos de cada línea ("línea N: tiene X campos y se esperaban Y") |
| `.txt` con encabezados distintos, valores no numéricos o ids repetidos | se valida al convertir cada fila |
| `.txt` roto: línea con más o menos campos que el encabezado | `cargar_texto` compara la cantidad de campos de cada línea ("línea N: tiene X campos y se esperaban Y") |
| `.txt` con encabezados distintos, valores no numéricos o ids repetidos | se valida al convertir cada fila |

En todos los casos el menú muestra "Archivo inválido: ..." y el catálogo en memoria no cambia (casos P15 y P23).

## 7. Reparto de trabajo (E6)

| Integrante | Qué hizo | Qué puede defender |
| --- | --- | --- |
| Viliani Christian | Todo el trabajo (trabajo individual) | Todo el repo |

## 8. Dónde está cada requisito de la consigna

| Requisito (consigna) | Dónde está | Opción del menú |
| --- | --- | --- |
| 1. Listar catálogo con el iterador | `Recetario.__iter__` → `ListaEnlazada.__iter__` / `IteradorLista.__next__`; `pantallas.listar_catalogo` | 1 |
| 2. Ver detalle | `Recetario.obtener` (índice dict), `Receta.detalle` | 2 |
| 3. Buscar (lineal; binaria con catálogo ordenado) | `algoritmos/busqueda.py`; `Recetario.buscar_lineal_por_nombre`, `buscar_binaria_por_nombre`, `filtrar_por_categoria`, `filtrar_por_ingrediente` | 3 |
| 4. Ordenar por al menos dos criterios | `algoritmos/ordenamiento.py` (selección, inserción, shell); `Recetario.ordenar` con criterios nombre / tiempo / dificultad / id | 4 |
| 5. Operación recursiva del dominio | `dominio/desglose.py`: `arbol_subrecetas`, `ingredientes_totales` | 5 |
| 6. ABM sobre la colección principal (persistente) | `MenuSemanal.agregar` / `quitar` / `reemplazar_dia` (ListaEnlazada, tope 7) + `repositorio.guardar_menu`; ABM del catálogo con `persistir_alta` / `persistir_baja` / `persistir_modificacion` | 6 |
| 7. Push/pop de la pila | `Historial` sobre `tads/pila.py` | 7 (y 8.3 apila automáticamente) |
| 8. Encolar/desencolar la cola | `ColaPreparacion` sobre `tads/cola.py` | 8 |
| 9. Guardar y cargar en .txt y binario | `persistencia/texto.py`, `binario.py`, `repositorio.py` | 9 → 1 a 4 |
| 10. Salir | `main.py` | 0 |
| TADs propios en módulos separados | `src/tads/nodo.py`, `lista_enlazada.py`, `pila.py`, `cola.py` | — |
| `ArchivoInvalidoError` con binario corto, magia incorrecta y .txt roto | `binario._leer_header`, `texto.cargar_texto` | 9 → 4 y 9 → 1 |
| Excepciones propias, sin `except:` pelado | `src/excepciones.py`; capturas en `src/cli/pantallas.py` y red de seguridad en `main.py` | — |
| Acceso directo a un registro binario por posición | `binario.leer_registro` y `actualizar_registro` (`seek(9 + p·74)`) | 9 → 5 y 6 → 7 |
| Alta / baja / modificación persistente | `SistemaRecetario.alta_receta` / `baja_receta` / `modificar_receta` + `persistir_*` (append, baja y seek en el .bin; .txt completo) | 6 → 5, 6, 7 |
| Tabla de complejidad y mediciones | §5 de este informe; `python -m src.algoritmos.medicion` | — |
| Nota extra: lista enlazada en el catálogo + índice dict comparado | `Recetario._recetas` + `Recetario._indice`; §5 | — |
| Nota extra: tercer algoritmo medido | `ordenar_shell`; §5 | 4 → algoritmo 3 |

## 9. Regresión (E6)

- El protocolo (`docs/PROTOCOLO_PRUEBAS.md`) tiene 27 casos (P01–P15 de la cátedra + P16–P27 propios); en E6 se volvieron a ejecutar **todos** sobre el código final (recursión, TADs, pila, cola, búsquedas, ordenamientos, archivos de texto y binarios, ABM persistente, entradas inválidas). Resultado: 27 pasan.
- Cada tag (`entrega-1` … `entrega-6`) arranca con `python -m src.main` y lista el catálogo.
- Los casos que modifican archivos (P13, P14, P24, P26, P27) se corrieron sobre una copia del repo para no alterar el dataset de la cátedra.
- Prueba del clone limpio: se clonó el repo en una carpeta nueva, se corrió `python -m src.main` y se probaron las 10 opciones (no depende de archivos sin commitear: el `.bin` y el menú guardado los genera el programa).

## 10. Limitaciones conocidas

- Los nombres no pueden tener comas (la coma separa campos en el `.txt`); el programa lo valida y lo rechaza.
- En el binario el nombre ocupa 40 bytes: uno más largo se recorta (sin cortar una letra con tilde).
- En el binario solo va el registro principal de la receta; ingredientes y sub-recetas viven en los `.txt`.
- No se pueden agregar sub-recetas a una receta que ya existe (solo al darla de alta), y no se puede borrar una receta que otra usa como sub-receta.
- El historial (pila) y la cola de preparación no se guardan en archivo: duran lo que dura la ejecución.
- La baja en el binario reescribe el archivo (O(n)); no se usa la técnica de "marcar como borrado".

