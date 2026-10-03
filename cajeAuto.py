saldo = 50000
opcion = 0

while opcion != 4:
    print("=== MENÚ CAJERO AUTOMÁTICO ===")
    print("1. Consultar saldo disponible")
    print("2. Depositar dinero")
    print("3. Extraer dinero")
    print("4. Salir")
    opcion = int(input("Ingrese una opción: "))

    if opcion == 1:
        print(f"Su saldo actual es: ${saldo}")
    elif opcion == 2:
        deposito = float(input("Ingrese el monto a depositar: "))
        saldo += deposito
        print("Depósito realizado con éxito.")
        print(f"Nuevo saldo: ${saldo}")
    elif opcion == 3:
        extraccion = float(input("Ingrese el monto a extraer: "))
        if extraccion <= saldo:
            saldo -= extraccion
            print("Extracción realizada con éxito.")
            print(f"Nuevo saldo: ${saldo}")
        else:
            print("Fondos insuficientes para realizar la operación")
    elif opcion == 4:
        print("Gracias por utilizar el cajero automático.")
    else:
        print("Opción inválida, intente nuevamente.")

    print()