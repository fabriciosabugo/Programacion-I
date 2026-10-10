import os

ARCHIVO_CATALOGO = "catalogo.txt"
ARCHIVO_VENTAS = "ventas.txt"


def cargar_datos_archivos(catalogo, ventas):
    """Carga lo que haya guardado antes. Si no existe, arma el catálogo base."""
    if not os.path.exists(ARCHIVO_CATALOGO):
        catalogo_inicial = {
            "101": {"nombre": "Café con leche", "precio": 1500.0},
            "102": {"nombre": "Medialuna", "precio": 700.0},
            "103": {"nombre": "Sándwich de miga", "precio": 1800.0},
            "104": {"nombre": "Agua mineral 500 ml", "precio": 1000.0},
            "105": {"nombre": "Empanada", "precio": 1200.0},
            "106": {"nombre": "Chipá (100 g)", "precio": 1300.0},
        }
        catalogo.update(catalogo_inicial)
        guardar_datos_archivos(catalogo, ventas)
    else:
        with open(ARCHIVO_CATALOGO, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    cod, nombre, precio = partes
                    catalogo[cod] = {"nombre": nombre, "precio": float(precio)}

    if os.path.exists(ARCHIVO_VENTAS):
        with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    dia, cod, cant = partes
                    indice_dia = int(dia) - 1
                    if cod not in ventas:
                        ventas[cod] = [0] * 5
                    ventas[cod][indice_dia] += int(cant)


def guardar_datos_archivos(catalogo, ventas):
    """Guarda el catálogo y las ventas en disco."""
    with open(ARCHIVO_CATALOGO, "w", encoding="utf-8") as archivo:
        for cod, info in catalogo.items():
            archivo.write(f"{cod};{info['nombre']};{info['precio']}\n")

    with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as archivo:
        for cod, dias in ventas.items():
            for indice, cantidad in enumerate(dias):
                if cantidad > 0:
                    archivo.write(f"{indice + 1};{cod};{cantidad}\n")


def mostrar_informes_semanales(catalogo, ventas):
    """Muestra los informes de ventas."""
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    print("\n===========================================")
    print("         INFORMES DE VENTAS SEMANALES")
    print("===========================================")

    print("\n1. Unidades vendidas por producto:")
    for cod, info in catalogo.items():
        total = obtener_total_unidades_producto(cod, ventas)
        print(f"   - [{cod}] {info['nombre']}: {total} unidades")

    print("\n2. Recaudación por día:")
    recaudaciones = []
    for dia in range(5):
        valor = calcular_recaudacion_dia(dia, catalogo, ventas)
        recaudaciones.append(valor)
        print(f"   - {dias_semana[dia]}: ${valor:,.2f}")

    productos_top, max_unidades = obtener_productos_mas_vendidos(catalogo, ventas)
    print(f"\n3. a) Producto(s) más vendido(s) ({max_unidades} unidades):")
    for nombre in productos_top:
        print(f"      * {nombre}")

    max_rec = max(recaudaciones) if recaudaciones else 0.0
    dias_top = [dias_semana[i] for i, valor in enumerate(recaudaciones) if valor == max_rec and max_rec > 0]
    print(f"   b) Día(s) de mayor recaudación (${max_rec:,.2f}):")
    print(f"      * {', '.join(dias_top) if dias_top else 'Sin ventas registradas'}")

    no_vendidos = obtener_productos_no_vendidos(catalogo, ventas)
    print("\n4. Productos sin ventas en la semana:")
    if no_vendidos:
        for nombre in no_vendidos:
            print(f"   - {nombre}")
    else:
        print("   - Todos los productos tuvieron ventas.")

    total_semana = sum(recaudaciones)
    print(f"\n5. Recaudación total de la semana: ${total_semana:,.2f}")
    print("===========================================\n")


def obtener_total_unidades_producto(codigo, ventas):
    """Devuelve la cantidad total vendida de un producto."""
    return sum(ventas.get(codigo, [0] * 5))


def calcular_recaudacion_dia(dia_idx, catalogo, ventas):
    """Calcula lo que se recaudó en un día específico."""
    total = 0.0
    for cod, info in catalogo.items():
        cant = ventas.get(cod, [0] * 5)[dia_idx]
        total += cant * info["precio"]
    return total


def obtener_productos_mas_vendidos(catalogo, ventas):
    """Devuelve los productos más vendidos y la cantidad máxima."""
    max_cant = -1
    productos = []

    for cod, info in catalogo.items():
        cantidad = obtener_total_unidades_producto(cod, ventas)
        if cantidad > max_cant:
            max_cant = cantidad
            productos = [info["nombre"]]
        elif cantidad == max_cant and max_cant > 0:
            productos.append(info["nombre"])

    return productos, max(max_cant, 0)


def obtener_productos_no_vendidos(catalogo, ventas):
    """Lista los productos que no tuvieron ninguna venta."""
    sin_ventas = []
    for cod, info in catalogo.items():
        if obtener_total_unidades_producto(cod, ventas) == 0:
            sin_ventas.append(info["nombre"])
    return sin_ventas


def main():
    catalogo = {}
    ventas = {}

    cargar_datos_archivos(catalogo, ventas)

    for cod in catalogo:
        if cod not in ventas:
            ventas[cod] = [0] * 5

    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Agregar producto")
        print("2. Registrar venta")
        print("3. Ver informes")
        print("4. Salir")

        opcion = input("Elegí una opción (1-4): ").strip()

        if opcion == "1":
            cod = input("Código del producto: ").strip()
            if cod in catalogo:
                print("Ese código ya existe.")
                continue

            nombre = input("Nombre del producto: ").strip()
            try:
                precio = float(input("Precio: "))
                if precio <= 0:
                    print("El precio tiene que ser mayor a 0.")
                    continue

                catalogo[cod] = {"nombre": nombre, "precio": precio}
                ventas[cod] = [0] * 5
                guardar_datos_archivos(catalogo, ventas)
                print(f"Producto '{nombre}' agregado correctamente.")
            except ValueError:
                print("Ingresá un número válido para el precio.")

        elif opcion == "2":
            try:
                dia = int(input("Día (1=Lunes, 2=Martes, 3=Miércoles, 4=Jueves, 5=Viernes): "))
                if dia < 1 or dia > 5:
                    print("El día tiene que estar entre 1 y 5.")
                    continue

                cod = input("Código del producto: ").strip()
                if cod not in catalogo:
                    print("Ese código no existe en el catálogo.")
                    continue

                cantidad = int(input("Cantidad vendida: "))
                if cantidad <= 0:
                    print("La cantidad tiene que ser mayor a 0.")
                    continue

                ventas[cod][dia - 1] += cantidad
                guardar_datos_archivos(catalogo, ventas)
                print(f"Venta registrada: {cantidad} unidades de '{catalogo[cod]['nombre']}' para el día {dia}.")
            except ValueError:
                print("Ingresá números válidos para el día y la cantidad.")

        elif opcion == "3":
            mostrar_informes_semanales(catalogo, ventas)

        elif opcion == "4":
            guardar_datos_archivos(catalogo, ventas)
            print("Se guardaron los datos. ¡Hasta luego!")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()