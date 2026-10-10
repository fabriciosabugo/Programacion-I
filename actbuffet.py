import os

# Nombres de archivos planos para persistencia
ARCHIVO_CATALOGO = "catalogo.txt"
ARCHIVO_VENTAS = "ventas.txt"

# =====================================================================
# SUBPROGRAMAS: PROCEDIMIENTOS (Acciones sin valor de retorno)
# =====================================================================

def cargar_archivos(catalogo, ventas):
    """
    PROCEDIMIENTO 1: Carga los datos guardados en los archivos.
    Si no existen, inicializa el catálogo base de 6 productos del buffet.
    """
    if not os.path.exists(ARCHIVO_CATALOGO):
        catalogo_inicial = {
            "101": {"nombre": "Café con leche", "precio": 1500.0},
            "102": {"nombre": "Medialuna", "precio": 700.0},
            "103": {"nombre": "Sándwich de miga", "precio": 1800.0},
            "104": {"nombre": "Agua mineral 500 ml", "precio": 1000.0},
            "105": {"nombre": "Empanada", "precio": 1200.0},
            "106": {"nombre": "Chipá (100 g)", "precio": 1300.0}
        }
        catalogo.update(catalogo_inicial)
        guardar_archivos(catalogo, ventas)
    else:
        with open(ARCHIVO_CATALOGO, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    cod, nom, pre = partes
                    catalogo[cod] = {"nombre": nom, "precio": float(pre)}

    if os.path.exists(ARCHIVO_VENTAS):
        with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    dia, cod, cant = partes
                    dia_idx = int(dia) - 1
                    if cod not in ventas:
                        ventas[cod] = [0] * 5
                    ventas[cod][dia_idx] += int(cant)


def guardar_archivos(catalogo, ventas):
    """
    PROCEDIMIENTO 2: Guarda el catálogo y las ventas en archivos de texto.
    """
    with open(ARCHIVO_CATALOGO, "w", encoding="utf-8") as f:
        for cod, info in catalogo.items():
            f.write(f"{cod};{info['nombre']};{info['precio']}\n")

    with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as f:
        for cod, dias in ventas.items():
            for dia_idx, cant in enumerate(dias):
                if cant > 0:
                    f.write(f"{dia_idx + 1};{cod};{cant}\n")


def mostrar_informes(catalogo, ventas):
    """
    PROCEDIMIENTO 3: Formatea e imprime los 5 informes requeridos por Marta.
    """
    dias_nombre = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    
    print("\n================ INFORMES DE LA SEMANA ================")
    
    # 1. Unidades vendidas por producto
    print("\n1. Unidades vendidas por producto:")
    for cod, info in catalogo.items():
        total_u = obtener_total_unidades_producto(cod, ventas)
        print(f"   - [{cod}] {info['nombre']}: {total_u} unidades")

    # 2. Recaudación por día
    print("\n2. Recaudación por día:")
    recaudacion_dias = []
    for dia_idx in range(5):
        rec_dia = calcular_recaudacion_dia(dia_idx, catalogo, ventas)
        recaudacion_dias.append(rec_dia)
        print(f"   - {dias_nombre[dia_idx]}: ${rec_dia:,.2f}")

    # 3. Producto más vendido y Día de mayor recaudación (con soporte de empates)
    prods_top, max_u = obtener_productos_mas_vendidos(catalogo, ventas)
    print(f"\n3. a) Producto(s) más vendido(s) ({max_u} unidades):")
    for prod in prods_top:
        print(f"      * {prod}")

    max_rec = max(recaudacion_dias) if recaudacion_dias else 0.0
    dias_top = [dias_nombre[i] for i, r in enumerate(recaudacion_dias) if r == max_rec and max_rec > 0]
    print(f"   b) Día(s) de mayor recaudación (${max_rec:,.2f}):")
    print(f"      * {', '.join(dias_top) if dias_top else 'Sin ventas registradas'}")

    # 4. Productos no vendidos
    no_vendidos = obtener_productos_no_vendidos(catalogo, ventas)
    print("\n4. Productos que NO se vendieron ningún día:")
    if no_vendidos:
        for nv in no_vendidos:
            print(f"   - {nv}")
    else:
        print("   - Todos los productos registraron al menos una venta.")

    # 5. Recaudación total semanal
    total_semana = sum(recaudacion_dias)
    print(f"\n5. Recaudación total de la semana: ${total_semana:,.2f}")
    print("========================================================\n")


# =====================================================================
# SUBPROGRAMAS: FUNCIONES (Retornan valores computados)
# =====================================================================

def obtener_total_unidades_producto(codigo, ventas):
    """
    FUNCIÓN 1: Devuelve la suma semanal de unidades vendidas de un producto.
    """
    return sum(ventas.get(codigo, [0] * 5))


def calcular_recaudacion_dia(dia_idx, catalogo, ventas):
    """
    FUNCIÓN 2: Devuelve la recaudación monetaria total en pesos de un día (0-4).
    """
    total_dia = 0.0
    for cod, info in catalogo.items():
        cant = ventas.get(cod, [0] * 5)[dia_idx]
        total_dia += cant * info['precio']
    return total_dia


def obtener_productos_mas_vendidos(catalogo, ventas):
    """
    FUNCIÓN 3: Devuelve una tupla ([nombres], max_unidades) resolviendo empates.
    """
    max_cant = -1
    mas_vendidos = []
    
    for cod, info in catalogo.items():
        total = obtener_total_unidades_producto(cod, ventas)
        if total > max_cant:
            max_cant = total
            mas_vendidos = [info['nombre']]
        elif total == max_cant and max_cant > 0:
            mas_vendidos.append(info['nombre'])
            
    return mas_vendidos, max(max_cant, 0)


def obtener_productos_no_vendidos(catalogo, ventas):
    """
    FUNCIÓN AUXILIAR: Devuelve la lista de nombres de productos sin ventas.
    """
    no_vendidos = []
    for cod, info in catalogo.items():
        if obtener_total_unidades_producto(cod, ventas) == 0:
            no_vendidos.append(info['nombre'])
    return no_vendidos


# =====================================================================
# PROGRAMA PRINCIPAL
# =====================================================================

def main():
    catalogo = {}
    ventas = {}  # Formato: {codigo: [lunes, martes, miercoles, jueves, viernes]}

    cargar_archivos(catalogo, ventas)

    # Garantizar presencia de todas las claves del catálogo en la matriz
    for cod in catalogo:
        if cod not in ventas:
            ventas[cod] = [0] * 5

    while True:
        print("\n--- BUFFET FACULTAD - SISTEMA DE VENTAS ---")
        print("1. Cargar nuevo producto al catálogo")
        print("2. Registrar venta")
        print("3. Generar informes de la semana")
        print("4. Salir")
        
        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion == "1":
            cod = input("Ingrese el código único del producto: ").strip()
            if cod in catalogo:
                print("Error: Ya existe un producto registrado con ese código.")
            else:
                nom = input("Nombre del producto: ").strip()
                try:
                    pre = float(input("Precio ($): "))
                    if pre <= 0:
                        print("Error: El precio debe ser un número mayor a cero.")
                        continue
                    catalogo[cod] = {"nombre": nom, "precio": pre}
                    ventas[cod] = [0] * 5
                    guardar_archivos(catalogo, ventas)
                    print(f"Producto '{nom}' cargado con éxito.")
                except ValueError:
                    print("Error: Debe ingresar un valor numérico válido para el precio.")

        elif opcion == "2":
            try:
                dia = int(input("Ingrese el día (1=Lunes, 2=Martes, 3=Miércoles, 4=Jueves, 5=Viernes): "))
                if dia < 1 or dia > 5:
                    print("Error: El día debe ser un entero entre 1 y 5.")
                    continue
                
                cod = input("Ingrese el código del producto: ").strip()
                
                # Búsqueda con corte de control anticipado
                if cod not in catalogo:
                    print("Error: El código ingresado no existe en el catálogo.")
                    continue

                cant = int(input("Ingrese la cantidad vendida: "))
                if cant <= 0:
                    print("Error: La cantidad debe ser un entero mayor a cero.")
                    continue

                # Incremento directo en la matriz
                ventas[cod][dia - 1] += cant
                guardar_archivos(catalogo, ventas)
                print(f"Venta registrada: {cant} u. de '{catalogo[cod]['nombre']}' el día {dia}.")
            except ValueError:
                print("Error: Entrada no válida. Ingrese enteros válidos para el día y la cantidad.")

        elif opcion == "3":
            mostrar_informes(catalogo, ventas)

        elif opcion == "4":
            guardar_archivos(catalogo, ventas)
            print("Datos guardados exitosamente. ¡Hasta luego, Marta!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()