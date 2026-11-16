# Protocolo de pruebas

Pruebas **manuales**. Cada fila es un caso. Ejecutar sobre el tag que entregan, desde la raíz del repo con `python -m src.main`.

Leyenda de resultado: `pasa` / `no pasa` / `no corrido`.

Mínimos: 8 casos escritos en E2; ejecutados en E3; 15 de regresión en E6 (pila, cola, archivos, recursión, búsquedas).

Los IDs P01–P15 son los del esqueleto de la cátedra; P16 en adelante son casos agregados por el grupo.

**Última ejecución:** 16-nov-2026, sobre el código de la entrega E6. Los casos de entregas anteriores se vuelven a correr como regresión.

| ID | Entrega | Acción (pasos en el CLI) | Datos | Resultado esperado | Resultado | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | E1 | Arrancar el programa y elegir `1` (listar catálogo) | dataset de la cátedra | se listan las 30 recetas y "Total: 30 recetas.", sin traceback | pasa |  |
| P02 | E1 | Elegir `2` (ver detalle) e ingresar un id inexistente | id = `-1` | "Error: No existe una receta con id -1." y vuelve el menú | pasa |  |
| P03 | E2 | Elegir `5` → `1` (árbol de sub-recetas) con una receta que usa sub-recetas | id = `10` (Empanadas de carne) | imprime Empanadas de carne y debajo `+-- Sofrito` y `+-- Masa de empanadas` | pasa |  |
| P04 | E2 | Elegir `5` → `1` con una receta que no usa sub-recetas | id = `3` (Sofrito) | imprime solo Sofrito y aclara que es receta hoja (caso base) | pasa |  |
| P05 | E3 | Elegir `6` → `2` (agregar al menú semanal) ocho veces | ids `1` a `8` | las 7 primeras se agregan; la octava muestra "El menú semanal está completo (máximo 7...)" (`ColeccionLlenaError`) y el programa sigue | pasa |  |
| P06 | E3 | Elegir `7` → `3` (deshacer) sin haber cocinado nada | pila vacía | "Error: No hay recetas cocinadas en el historial para deshacer." (`PilaVaciaError`), el menú sigue | pasa |  |
| P07 | E3 | Elegir `8` → `3` (preparar la siguiente) con la cola vacía | cola vacía | "Error: No hay recetas en la cola de preparación." (`ColaVaciaError`), el menú sigue | pasa |  |
| P08 | E3 | Elegir `6` → `2` tres veces y después `6` → `1` (ver menú, usa el iterador) | ids `12`, `1`, `25` | Lunes Locro, Martes Chimichurri, Miércoles Brownies: el orden coincide con las inserciones | pasa |  |
| P09 | E4 | Elegir `3` → `1` (búsqueda lineal por nombre) con un nombre que existe | `locro` (en minúsculas) | muestra la receta Locro (150 min); no distingue mayúsculas | pasa |  |
| P10 | E4 | Elegir `3` → `1` con un nombre que no existe | `Ravioles` | "No se encontró...", sin traceback, el menú sigue | pasa |  |
| P11 | E4 | Recién arrancado (catálogo ordenado por id, no por nombre) elegir `3` → `2` (búsqueda binaria) | `Pesto` | avisa "El catálogo no estaba ordenado por nombre: se ordenó..." y recién ahí usa binaria; encuentra Pesto (no da falso "no encontrado") | pasa |  |
| P12 | E4 | Elegir `4` → criterio `1` (nombre) → algoritmo `1` (selección); después `4` → criterio `2` (tiempo) → algoritmo `2` (inserción) | catálogo completo | primero queda ordenado alfabéticamente (empieza en Arroz con leche); después por tiempo (empieza por las de 15 min); el orden cambia | pasa |  |
| P13 | E5 | `6` → `5` (alta de receta en el catálogo) con una receta nueva que usa la sub-receta 5; salir con `0`; volver a entrar y `1` (listar) y `5` → `1` con id `31` | Tarta de jamon y queso, 55, media, principal, ingredientes jamon,200,g y queso,200,g, sub-receta `5` | "Alta guardada: #31 ... (recetas.txt + append al final del .bin)"; al volver a entrar aparece en el listado, el total es 31 y su árbol muestra la Masa de empanadas | pasa | se probó sobre una copia del repo para no modificar el dataset |
| P14 | E5 | `9` → `3` (guardar binario); `6` → `7` (modificar receta del catálogo) id `9`, tiempo `200`; `9` → `4` (cargar binario); `2` detalle de `9` | id 9 (Asado, 180 min) | "Modificación guardada ... registro 8 del .bin pisado con seek al byte 601"; al recargar desde el binario el Asado tiene 200 minutos | pasa |  |
| P15 | E5 | `9` → `4` (cargar binario) con un archivo truncado y con otro de magia mala; `9` → `1` (cargar .txt) con una línea con un campo de más | `data/basura.bin` (6 bytes), `data/magia.bin` (magia `NOPE`), `data/roto.txt` (6 campos en la línea 2) | `ArchivoInvalidoError` con mensaje claro en los tres casos ("truncado", "magia", "línea 2: tiene 6 campos"); sin traceback; el catálogo en memoria no cambia (sigue en 30) | pasa |  |
| P16 | E1 | Elegir `2` (ver detalle) con un id que existe | id = `9` (Asado) | muestra nombre, 180 minutos, dificultad, categoría, ingredientes propios y "Usa las sub-recetas: Chimichurri (#1), Salsa criolla (#2)" | pasa |  |
| P17 | E1 | Escribir una opción inválida en el menú principal | `9z` | "Opción inválida..." y vuelve a mostrar el menú | pasa |  |
| P18 | E1 | Apretar Enter sin escribir nada en el menú principal | (vacío) | "Opción inválida..." y vuelve a mostrar el menú, no explota | pasa |  |
| P19 | E2 | Elegir `5` → `3` (ingredientes totales con traza) | id = `9` (Asado) | muestra la traza: llamada a 9, luego 1 y 2 como caso base; total 12 ingredientes con 120 ml de aceite de oliva y 50 ml de vinagre | pasa |  |
| P20 | E2 | Elegir `2` (ver detalle) y escribir letras en lugar del id; después Enter vacío | `abc`, luego Enter | avisa que no es un número y vuelve a preguntar; con Enter vacío dice "Cancelado." | pasa |  |
| P21 | E3 | `6` → `2` agregar `10` y `3` al menú semanal; `8` → `5` (encolar el menú) → `3` (preparar) → `1` (ver cola); `7` → `1` (ver historial) | ids `10`, `3` | se encolan 2; se prepara Empanadas de carne (FIFO); en la cola queda Sofrito como próxima; el historial tiene Empanadas en el tope | pasa | integra lista, cola y pila |
| P22 | E4 | Elegir `3` → `4` (búsqueda lineal por ingrediente) | `papa` | lista Pure de papas, Noquis con pesto, Tortilla de papas, Pollo al horno con papas y Ensalada rusa | pasa |  |
| P23 | E5 | `9` → `5` (ver registro del binario por posición) con una posición fuera de rango y después con `0` | posición `99`, luego `0` | con 99 avisa "fuera de rango"; con 0 muestra el registro 0 (Chimichurri) leído con seek, sin leer el resto | pasa | el .bin se genera al arrancar |
| P24 | E5 | `6` → `6` (baja de receta del catálogo) de una receta usada como sub-receta y después de una que no se usa; `1` listar; `9` → `5` (ver cantidad del binario) | id `1` (Chimichurri), luego id `18` (Guacamole), confirmar `s` | con 1 avisa que "es sub-receta de" Asado y Choripan y no la borra; con 18 "Baja guardada"; el listado queda en 29 y el binario tiene 29 registros | pasa | se probó sobre una copia del repo |
| P25 | E6 | Arrancar el programa y cerrar la entrada (Ctrl+Z + Enter en Windows / Ctrl+D en Linux) | fin de archivo en `input()` | sale con "Chau." sin traceback | pasa |  |
| P26 | E5 | `6` → `2` (agregar al menú semanal) ids `12` y `25`; salir; volver a entrar y `6` → `1` (ver menú) | ids `12` (Locro), `25` (Brownies) | cada cambio dice "guardado en menu_semanal.txt"; al volver a entrar: "Menú semanal recuperado: 2 recetas", Lunes Locro y Martes Brownies | pasa | ABM persistente de la colección principal |
| P27 | E5 | `6` → `5` (alta) de una receta sin ingredientes; `9` → `5` (ver registro) posición `30` | Tarta, 55, media, principal | el alta se agrega con append al final del .bin; el binario pasa a tener 31 registros y el registro 30 es la Tarta | pasa |  |

Resumen: 27 casos ejecutados, 27 pasan, 0 no pasan.
