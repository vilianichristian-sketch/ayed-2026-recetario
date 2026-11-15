"""Una función por opción del menú. Piden datos, llaman al dominio y muestran el resultado.

Acá no hay lógica del negocio: solo entrada/salida y captura de excepciones propias.
Nunca se accede a atributos internos (los que empiezan con _) de las clases.
"""

from src.cli.entrada import ejecutar_submenu, pedir_entero, pedir_texto
from src.dominio.desglose import arbol_subrecetas, ingredientes_totales
from src.excepciones import (
    CicloSubrecetasError,
    ColaVaciaError,
    ColeccionLlenaError,
    ColeccionVaciaError,
    ItemNoEncontradoError,
    PilaVaciaError,
    SubrecetaFaltanteError,
)

ENCABEZADO = f"{'ID':>3}  {'Nombre':<30} {'Tiempo':>8}  {'Dific.':<6} Categoría"


def _pedir_receta(sistema, mensaje="Id de la receta (Enter para cancelar): "):
    """Pide un id y devuelve la receta, o None si cancela o no existe (avisando)."""
    id_receta = pedir_entero(mensaje)
    if id_receta is None:
        print("Cancelado.")
        return None
    try:
        return sistema.recetario.obtener(id_receta)
    except ItemNoEncontradoError as error:
        print(f"Error: {error}")
        return None


# ---------------------------------------------------------------- 1. Listar
def listar_catalogo(sistema):
    print(ENCABEZADO)
    for receta in sistema.recetario:  # usa el iterador de la ListaEnlazada
        print(receta.resumen())
    orden = sistema.recetario.orden_actual or "sin orden (se agregaron recetas)"
    print(f"Total: {sistema.recetario.cantidad()} recetas. Orden actual: {orden}.")


# ---------------------------------------------------------------- 2. Detalle
def ver_detalle(sistema):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    print(receta.detalle())
    ids_sub = sistema.recetario.subrecetas_de(receta.id)
    if ids_sub:
        nombres = []
        for id_sub in ids_sub:
            try:
                nombres.append(f"{sistema.recetario.obtener(id_sub).nombre} (#{id_sub})")
            except ItemNoEncontradoError:
                nombres.append(f"#{id_sub} (no está en el catálogo)")
        print("  Usa las sub-recetas: " + ", ".join(nombres))


# ---------------------------------------------------------------- 3. Buscar
def _imprimir_recetas(recetas):
    print(ENCABEZADO)
    for receta in recetas:
        print(receta.resumen())


def _buscar_nombre_lineal(sistema):
    nombre = pedir_texto("Nombre exacto (sin importar mayúsculas/tildes): ")
    if nombre == "":
        print("Cancelado.")
        return
    receta = sistema.recetario.buscar_lineal_por_nombre(nombre)
    if receta is not None:
        print("Encontrada con búsqueda lineal:")
        print(receta.detalle())
        return
    print(f"No se encontró ninguna receta llamada '{nombre}'.")
    parecidas = sistema.recetario.buscar_por_texto_en_nombre(nombre)
    if parecidas:
        print("Recetas cuyo nombre contiene ese texto:")
        _imprimir_recetas(parecidas)


def _buscar_nombre_binaria(sistema):
    nombre = pedir_texto("Nombre exacto (sin importar mayúsculas/tildes): ")
    if nombre == "":
        print("Cancelado.")
        return
    receta, se_reordeno = sistema.recetario.buscar_binaria_por_nombre(nombre)
    if se_reordeno:
        print("Aviso: el catálogo no estaba ordenado por nombre. Se ordenó por nombre "
              "(inserción) para poder usar búsqueda binaria.")
    else:
        print("El catálogo ya estaba ordenado por nombre: se usa búsqueda binaria directamente.")
    if receta is None:
        print(f"No se encontró ninguna receta llamada '{nombre}' (búsqueda binaria).")
    else:
        print("Encontrada con búsqueda binaria:")
        print(receta.detalle())


def _buscar_categoria(sistema):
    print("Categorías: " + ", ".join(sistema.recetario.categorias()))
    categoria = pedir_texto("Categoría: ")
    if categoria == "":
        print("Cancelado.")
        return
    recetas = sistema.recetario.filtrar_por_categoria(categoria)
    if not recetas:
        print(f"No se encontraron recetas de la categoría '{categoria}'.")
        return
    _imprimir_recetas(recetas)
    print(f"{len(recetas)} recetas encontradas (búsqueda lineal).")


def _buscar_ingrediente(sistema):
    ingrediente = pedir_texto("Ingrediente (o parte del nombre): ")
    if ingrediente == "":
        print("Cancelado.")
        return
    recetas = sistema.recetario.filtrar_por_ingrediente(ingrediente)
    if not recetas:
        print(f"No se encontraron recetas que usen '{ingrediente}'.")
        return
    _imprimir_recetas(recetas)
    print(f"{len(recetas)} recetas usan '{ingrediente}' entre sus ingredientes propios (búsqueda lineal).")


def _buscar_id(sistema):
    receta = _pedir_receta(sistema)
    if receta is not None:
        print("Encontrada con el índice por id (dict, O(1)):")
        print(receta.detalle())


def buscar(sistema):
    ejecutar_submenu(
        "Buscar",
        {
            "1": ("Por nombre (búsqueda lineal)", _buscar_nombre_lineal),
            "2": ("Por nombre (búsqueda binaria; ordena por nombre si hace falta)", _buscar_nombre_binaria),
            "3": ("Por categoría (lineal, todas las coincidencias)", _buscar_categoria),
            "4": ("Por ingrediente (lineal, todas las coincidencias)", _buscar_ingrediente),
            "5": ("Por id (índice dict)", _buscar_id),
        },
        sistema,
    )


# ---------------------------------------------------------------- 4. Ordenar
CRITERIOS_MENU = {"1": "nombre", "2": "tiempo", "3": "dificultad", "4": "id"}
ALGORITMOS_MENU = {"1": ("seleccion", "selección"), "2": ("insercion", "inserción"), "3": ("shell", "shell")}


def ordenar(sistema):
    print("Ordenar por: 1) Nombre  2) Tiempo  3) Dificultad  4) Id (orden original)")
    criterio = CRITERIOS_MENU.get(pedir_texto("> "))
    if criterio is None:
        print("Criterio inválido. No se ordenó nada.")
        return
    print("Algoritmo: 1) Selección (no estable)  2) Inserción (estable)  3) Shell (no estable)")
    algoritmo = ALGORITMOS_MENU.get(pedir_texto("> "))
    if algoritmo is None:
        print("Algoritmo inválido. No se ordenó nada.")
        return
    clave_algoritmo, nombre_algoritmo = algoritmo
    sistema.recetario.ordenar(criterio, clave_algoritmo)
    print(f"Catálogo ordenado por {criterio} ({nombre_algoritmo}).")
    listar_catalogo(sistema)


# ---------------------------------------------------------------- 5. Recursión
def _mostrar_arbol(sistema):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    try:
        arbol = arbol_subrecetas(sistema.recetario, receta.id)
    except (SubrecetaFaltanteError, CicloSubrecetasError) as error:
        print(f"Error: {error}")
        return
    for nivel, sub in arbol:
        prefijo = "    " * nivel + ("+-- " if nivel > 0 else "")
        print(f"{prefijo}{sub.nombre} (#{sub.id}, {sub.tiempo_min} min)")
    if len(arbol) == 1:
        print("(No usa sub-recetas: es una receta hoja, caso base de la recursión.)")


def _mostrar_ingredientes_totales(sistema, con_traza=False):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    traza = [] if con_traza else None
    try:
        totales = ingredientes_totales(sistema.recetario, receta.id, traza=traza)
    except (SubrecetaFaltanteError, CicloSubrecetasError) as error:
        print(f"Error: {error}")
        return
    if con_traza:
        print("Traza de llamadas (cada sangría es un nivel más de recursión):")
        for linea in traza:
            print("  " + linea)
        print()
    print(f"Ingredientes totales de {receta.nombre} (incluye sub-recetas):")
    for (nombre, unidad), cantidad in totales.items():
        print(f"  - {cantidad:g} {unidad} de {nombre}")


def operacion_recursiva(sistema):
    ejecutar_submenu(
        "Operación recursiva: desglose de sub-recetas",
        {
            "1": ("Ver árbol de sub-recetas", _mostrar_arbol),
            "2": ("Ingredientes totales (explota sub-recetas)", _mostrar_ingredientes_totales),
            "3": ("Ingredientes totales con traza de la recursión",
                  lambda s: _mostrar_ingredientes_totales(s, con_traza=True)),
        },
        sistema,
    )


# ---------------------------------------------------------------- 6. Menú semanal
def _ver_menu(sistema):
    menu = sistema.menu
    if menu.esta_vacio():
        print("El menú semanal está vacío.")
        return
    for dia, receta in menu.dias_y_recetas():  # recorre la ListaEnlazada con su iterador
        print(f"  {dia:<10} {receta.nombre} (#{receta.id}, {receta.tiempo_min} min)")
    print(f"  {menu.cantidad()}/{menu.tope} días cargados. Tiempo total: {menu.tiempo_total()} min.")


def _agregar_al_menu(sistema):
    receta = _pedir_receta(sistema)
    if receta is None:
        return
    try:
        sistema.menu.agregar(receta)
        print(f"Agregada al menú: {receta.nombre}")
    except ColeccionLlenaError as error:
        print(f"Error: {error}")


def _quitar_del_menu(sistema):
    id_receta = pedir_entero("Id de la receta a quitar (Enter para cancelar): ")
    if id_receta is None:
        print("Cancelado.")
        return
    try:
        receta = sistema.menu.quitar(id_receta)
        print(f"Quitada del menú: {receta.nombre}")
    except (ColeccionVaciaError, ItemNoEncontradoError) as error:
        print(f"Error: {error}")


def _reemplazar_en_menu(sistema):
    numero_dia = pedir_entero("Número de día a cambiar (1 = Lunes ... 7 = Domingo, Enter cancela): ")
    if numero_dia is None:
        print("Cancelado.")
        return
    receta = _pedir_receta(sistema, "Id de la nueva receta (Enter para cancelar): ")
    if receta is None:
        return
    try:
        anterior = sistema.menu.reemplazar_dia(numero_dia, receta)
        print(f"Día {numero_dia}: {anterior.nombre} -> {receta.nombre}")
    except (ColeccionVaciaError, ItemNoEncontradoError) as error:
        print(f"Error: {error}")


def menu_semanal(sistema):
    ejecutar_submenu(
        "Menú semanal (colección principal, ListaEnlazada con tope 7)",
        {
            "1": ("Ver menú de la semana", _ver_menu),
            "2": ("Agregar receta al menú (alta)", _agregar_al_menu),
            "3": ("Quitar receta del menú (baja)", _quitar_del_menu),
            "4": ("Cambiar la receta de un día (modificación)", _reemplazar_en_menu),
        },
        sistema,
    )


# ---------------------------------------------------------------- 7. Historial (pila)
def _ver_historial(sistema):
    historial = sistema.historial
    if historial.esta_vacio():
        print("Todavía no se cocinó ninguna receta.")
        return
    print("Recetas cocinadas (de la más reciente a la más vieja):")
    posicion = 1
    for receta in historial:
        marca = "  <- tope" if posicion == 1 else ""
        print(f"  {posicion}. {receta.nombre} (#{receta.id}){marca}")
        posicion += 1


def _registrar_cocinada(sistema):
    receta = _pedir_receta(sistema, "Id de la receta que cocinaste (Enter para cancelar): ")
    if receta is None:
        return
    sistema.historial.registrar(receta)
    print(f"Apilada en el historial: {receta.nombre}")


def _deshacer(sistema):
    try:
        receta = sistema.historial.deshacer()
        print(f"Deshecho: se quitó '{receta.nombre}' del historial.")
    except PilaVaciaError as error:
        print(f"Error: {error}")


def _ver_ultima(sistema):
    try:
        print(f"Última receta cocinada: {sistema.historial.ultima().nombre}")
    except PilaVaciaError as error:
        print(f"Error: {error}")


def historial(sistema):
    ejecutar_submenu(
        "Historial de recetas cocinadas (pila)",
        {
            "1": ("Ver historial", _ver_historial),
            "2": ("Registrar receta cocinada (apilar)", _registrar_cocinada),
            "3": ("Deshacer la última (desapilar)", _deshacer),
            "4": ("Ver la última cocinada (tope)", _ver_ultima),
        },
        sistema,
    )


# ---------------------------------------------------------------- 8. Cola de preparación
def _ver_cola(sistema):
    cola = sistema.cola
    if cola.esta_vacia():
        print("La cola de preparación está vacía.")
        return
    print("Cola de preparación (del frente al final):")
    posicion = 1
    for receta in cola:
        marca = "  <- próxima" if posicion == 1 else ""
        print(f"  {posicion}. {receta.nombre} (#{receta.id}){marca}")
        posicion += 1


def _encolar(sistema):
    receta = _pedir_receta(sistema, "Id de la receta a encolar (Enter para cancelar): ")
    if receta is None:
        return
    sistema.cola.agregar(receta)
    print(f"Encolada: {receta.nombre} (hay {sistema.cola.cantidad()} en la cola)")


def _preparar_siguiente(sistema):
    try:
        receta = sistema.preparar_siguiente()
        print(f"Preparando: {receta.nombre}. Se registró en el historial de cocinadas.")
    except ColaVaciaError as error:
        print(f"Error: {error}")


def _ver_proxima(sistema):
    try:
        print(f"Próxima a preparar: {sistema.cola.proxima().nombre}")
    except ColaVaciaError as error:
        print(f"Error: {error}")


def _encolar_menu(sistema):
    try:
        cantidad = sistema.encolar_menu()
        print(f"Se encolaron las {cantidad} recetas del menú semanal.")
    except ColeccionVaciaError as error:
        print(f"Error: {error}")


def cola_preparacion(sistema):
    ejecutar_submenu(
        "Cola de preparación (cola)",
        {
            "1": ("Ver cola", _ver_cola),
            "2": ("Agregar receta a la cola (encolar)", _encolar),
            "3": ("Preparar la siguiente (desencolar -> pasa al historial)", _preparar_siguiente),
            "4": ("Ver la próxima (frente)", _ver_proxima),
            "5": ("Encolar todo el menú semanal", _encolar_menu),
        },
        sistema,
    )
