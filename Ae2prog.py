import os

CAT = "catalogo.txt"
VEN = "ventas.txt"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]


def cargar(catalogo, ventas):
    if not os.path.exists(CAT):
        base = {"101": {"nombre": "Café con leche", "precio": 1500.0}, "102": {"nombre": "Medialuna", "precio": 700.0}, "103": {"nombre": "Sándwich de miga", "precio": 1800.0}, "104": {"nombre": "Agua mineral 500 ml", "precio": 1000.0}, "105": {"nombre": "Empanada", "precio": 1200.0}, "106": {"nombre": "Chipá (100 g)", "precio": 1300.0}}
        catalogo.update(base)
        guardar(catalogo, ventas)
    else:
        with open(CAT, "r", encoding="utf-8") as f:
            for linea in f:
                p = linea.strip().split(";")
                if len(p) == 3:
                    cod, nombre, precio = p
                    catalogo[cod] = {"nombre": nombre, "precio": float(precio)}
    if os.path.exists(VEN):
        with open(VEN, "r", encoding="utf-8") as f:
            for linea in f:
                p = linea.strip().split(";")
                if len(p) == 3:
                    dia, cod, cant = p
                    if cod not in ventas:
                        ventas[cod] = [0] * 5
                    ventas[cod][int(dia) - 1] += int(cant)


def guardar(catalogo, ventas):
    with open(CAT, "w", encoding="utf-8") as f:
        for cod, info in catalogo.items():
            f.write(f"{cod};{info['nombre']};{info['precio']}\n")
    with open(VEN, "w", encoding="utf-8") as f:
        for cod, dias in ventas.items():
            for i, cant in enumerate(dias):
                if cant > 0:
                    f.write(f"{i + 1};{cod};{cant}\n")


def informes(catalogo, ventas):
    print("\n==============================")
    print("      INFORMES DE VENTAS")
    print("==============================")
    print("\n1. Unidades vendidas por producto:")
    for cod, info in catalogo.items():
        total = sum(ventas.get(cod, [0] * 5))
        print(f"   - [{cod}] {info['nombre']}: {total} unidades")
    print("\n2. Recaudación por día:")
    rec = []
    for i in range(5):
        total = 0.0
        for cod, info in catalogo.items():
            total += ventas.get(cod, [0] * 5)[i] * info["precio"]
        rec.append(total)
        print(f"   - {DIAS[i]}: ${total:,.2f}")
    max_un = -1
    prod = []
    for cod, info in catalogo.items():
        total = sum(ventas.get(cod, [0] * 5))
        if total > max_un:
            max_un = total
            prod = [info["nombre"]]
        elif total == max_un and max_un > 0:
            prod.append(info["nombre"])
    print(f"\n3. a) Producto(s) más vendido(s) ({max(max_un, 0)} unidades):")
    for n in prod:
        print(f"      * {n}")
    mayor = max(rec) if rec else 0
    dias_top = [DIAS[i] for i, v in enumerate(rec) if v == mayor and mayor > 0]
    print(f"   b) Día(s) de mayor recaudación (${mayor:,.2f}):")
    print(f"      * {', '.join(dias_top) if dias_top else 'Sin ventas registradas'}")
    print("\n4. Productos sin ventas:")
    sin = []
    for cod, info in catalogo.items():
        if sum(ventas.get(cod, [0] * 5)) == 0:
            sin.append(info["nombre"])
    if sin:
        for n in sin:
            print(f"   - {n}")
    else:
        print("   - Todos tuvieron ventas.")
    print(f"\n5. Recaudación total de la semana: ${sum(rec):,.2f}")
    print("==============================\n")


def main():
    catalogo = {}
    ventas = {}
    cargar(catalogo, ventas)
    for cod in catalogo:
        if cod not in ventas:
            ventas[cod] = [0] * 5
    while True:
        print("\n--- MENÚ ---")
        print("1. Agregar producto")
        print("2. Registrar venta")
        print("3. Ver informes")
        print("4. Salir")
        op = input("Elegí una opción (1-4): ").strip()
        if op == "1":
            cod = input("Código: ").strip()
            if cod in catalogo:
                print("Ese código ya existe.")
                continue
            nombre = input("Nombre: ").strip()
            try:
                precio = float(input("Precio: "))
                if precio <= 0:
                    print("El precio tiene que ser mayor a cero.")
                    continue
                catalogo[cod] = {"nombre": nombre, "precio": precio}
                ventas[cod] = [0] * 5
                guardar(catalogo, ventas)
                print(f"Producto '{nombre}' agregado.")
            except ValueError:
                print("Ingresá un número válido para el precio.")
        elif op == "2":
            try:
                dia = int(input("Día (1=Lunes, 2=Martes, 3=Miércoles, 4=Jueves, 5=Viernes): "))
                if dia < 1 or dia > 5:
                    print("El día debe estar entre 1 y 5.")
                    continue
                cod = input("Código del producto: ").strip()
                if cod not in catalogo:
                    print("Ese código no existe.")
                    continue
                cant = int(input("Cantidad: "))
                if cant <= 0:
                    print("La cantidad debe ser mayor a cero.")
                    continue
                ventas[cod][dia - 1] += cant
                guardar(catalogo, ventas)
                print(f"Venta cargada: {cant} de '{catalogo[cod]['nombre']}' en el día {dia}.")
            except ValueError:
                print("Ingresá números válidos.")
        elif op == "3":
            informes(catalogo, ventas)
        elif op == "4":
            guardar(catalogo, ventas)
            print("Datos guardados. ¡Chau!")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()