# Protocolo de pruebas

Pruebas **manuales**. Cada fila es un caso. Ejecutar sobre el tag que entregan, desde la raíz del repo con `python -m src.main`.

Leyenda de resultado: `pasa` / `no pasa` / `no corrido`.

Mínimos: 8 casos escritos en E2; ejecutados en E3; 15 de regresión en E6 (pila, cola, archivos, recursión, búsquedas).

Los IDs P01–P15 son los del esqueleto de la cátedra; P16 en adelante son casos agregados por el grupo.

| ID | Entrega | Acción (pasos en el CLI) | Datos | Resultado esperado | Resultado | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | E1 | Arrancar el programa y elegir `1` (listar catálogo) | dataset de la cátedra | se listan las 30 recetas y "Total: 30 recetas.", sin traceback | no corrido |  |
| P02 | E1 | Elegir `2` (ver detalle) e ingresar un id inexistente | id = `-1` | "Error: No existe una receta con id -1." y vuelve el menú | no corrido |  |
| P03 | E2 | Elegir `5` → `1` (árbol de sub-recetas) con una receta que usa sub-recetas | id = `10` (Empanadas de carne) | imprime Empanadas de carne y debajo Sofrito y Masa de empanadas | no corrido |  |
| P04 | E2 | Elegir `5` → `1` con una receta que no usa sub-recetas | id = `3` (Sofrito) | imprime solo "Sofrito" y aclara que es receta hoja (caso base) | no corrido |  |
| P05 | E3 | Elegir `6` → `2` (agregar al menú semanal) ocho veces | ids `1` a `8` | las 7 primeras se agregan; la octava muestra "El menú semanal está completo (máximo 7...)" y el programa sigue | no corrido | se ejecuta en E3 |
| P06 | E3 | Desapilar historial vacío |  | excepción propia, menú sigue |  | se ejecuta en E3 |
| P07 | E3 | Desencolar cola vacía |  | excepción propia, menú sigue |  | se ejecuta en E3 |
| P08 | E3 | Listar colección con el iterador | 2+ ítems | el orden coincide con las inserciones |  | se ejecuta en E3 |
| P09 | E4 | Búsqueda lineal de un nombre que existe |  | lo encuentra |  | se ejecuta en E4 |
| P10 | E4 | Búsqueda lineal de un nombre que no existe |  | no encontrado, sin traceback |  | se ejecuta en E4 |
| P11 | E4 | Búsqueda binaria con catálogo desordenado |  | avisa o reordena; no da un falso hit |  | se ejecuta en E4 |
| P12 | E4 | Ordenar por un criterio y después por otro |  | el orden cambia |  | se ejecuta en E4 |
| P13 | E5 | Guardar texto (`.txt`), salir, volver a entrar |  | los datos siguen |  | se ejecuta en E5 |
| P14 | E5 | Guardar binario y modificar un registro por id |  | al recargar, ese campo cambió |  | se ejecuta en E5 |
| P15 | E5 | Abrir un binario truncado o con magia mala | archivo basura | excepción de archivo inválido |  | se ejecuta en E5 |
| P16 | E1 | Elegir `2` (ver detalle) con un id que existe | id = `9` (Asado) | muestra nombre, tiempo (180), dificultad, categoría, ingredientes propios y sub-recetas (Chimichurri, Salsa criolla) | no corrido |  |
| P17 | E1 | Escribir una opción inválida en el menú principal | `9z` | "Opción inválida..." y vuelve a mostrar el menú | no corrido |  |
| P18 | E1 | Apretar Enter sin escribir nada en el menú principal | (vacío) | "Opción inválida..." y vuelve a mostrar el menú, no explota | no corrido |  |
| P19 | E2 | Elegir `5` → `3` (ingredientes totales con traza) | id = `9` (Asado) | muestra la traza: llamada a 9, luego 1 y 2 como caso base; total 12 ingredientes con aceite de oliva 120 ml y vinagre 50 ml | no corrido |  |
| P20 | E2 | Elegir `2` (ver detalle) y escribir letras en lugar del id | `abc`, luego Enter vacío | avisa que no es un número, vuelve a preguntar; con Enter vacío cancela | no corrido |  |
