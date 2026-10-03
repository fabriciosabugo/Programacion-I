import os

NOMBRE_ARCHIVO = "jugadores.txt"

# -------------------------------------------------------------------
# FUNCIONES AUXILIARES DE ARCHIVO
# -------------------------------------------------------------------

def cargar_jugadores_desde_archivo():
    """Lee el archivo de texto y pasa los datos a listas en memoria."""
    nombres = []
    categorias = []
    
    if os.path.exists(NOMBRE_ARCHIVO):
        with open(NOMBRE_ARCHIVO, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    # Formato en el archivo: Nombre,Categoria
                    partes = linea.split(",")
                    if len(partes) == 2:
                        nombres.append(partes[0])
                        categorias.append(partes[1])
    return nombres, categorias


def guardar_jugadores_en_archivo(nombres, categorias):
    """Sobrescribe el archivo con el contenido actualizado de las listas."""
    with open(NOMBRE_ARCHIVO, "w", encoding="utf-8") as f:
        for i in range(len(nombres)):
            f.write(f"{nombres[i]},{categorias[i]}\n")


# -------------------------------------------------------------------
# REQUERIMIENTOS DEL CLIENTE
# -------------------------------------------------------------------

def agregar_jugador():
    """Solicitud 1: Guardar e inscriptar un nuevo jugador (modo 'a' - append)."""
    print("\n--- AGREGAR NUEVO JUGADOR ---")
    nombre = input("Ingrese el nombre del jugador: ").strip()
    categoria = input("Ingrese la categoría (ej. 4ª, 5ª, 6ª): ").strip()

    if nombre and categoria:
        # Abrimos en modo 'a' (append) para agregar sin borrar lo anterior
        with open(NOMBRE_ARCHIVO, "a", encoding="utf-8") as f:
            f.write(f"{nombre},{categoria}\n")
        print(f"¡Jugador '{nombre}' agregado exitosamente!")
    else:
        print("Error: El nombre y la categoría no pueden estar vacíos.")


def mostrar_lista_completa():
    """Solicitud 2: Mostrar la lista completa guardada sin recargar todo."""
    nombres, categorias = cargar_jugadores_desde_archivo()

    print("\n==========================================")
    print("      LISTA DE JUGADORES INSCRIPTOS")
    print("==========================================")

    if not nombres:
        print("No hay jugadores inscriptos en el archivo.")
    else:
        for i in range(len(nombres)):
            print(f"{i + 1}. {nombres[i]} - Categoría: {categorias[i]}")
    print("==========================================")


def buscar_jugador():
    """Solicitud 3: Escribir el nombre de un jugador y consultar su categoría."""
    print("\n--- BUSCAR JUGADOR ---")
    buscado = input("Ingrese el nombre del jugador a buscar: ").strip().lower()

    nombres, categorias = cargar_jugadores_desde_archivo()
    encontrado = False

    for i in range(len(nombres)):
        if nombres[i].lower() == buscado:
            print(f"\nResultados: El jugador '{nombres[i]}' está inscripto en la categoría '{categorias[i]}'.")
            encontrado = True
            break

    if not encontrado:
        print(f"El jugador '{buscado}' NO se encuentra inscripto en el torneo.")


def eliminar_jugador():
    """Solicitud 4: Eliminar un jugador lesionado o dado de baja."""
    print("\n--- DAR DE BAJA A UN JUGADOR ---")
    buscado = input("Ingrese el nombre del jugador a eliminar: ").strip().lower()

    nombres, categorias = cargar_jugadores_desde_archivo()
    encontrado = False

    # Recorremos la lista para buscar y eliminar
    for i in range(len(nombres)):
        if nombres[i].lower() == buscado:
            eliminado_nombre = nombres.pop(i)
            categorias.pop(i)
            encontrado = True
            
            # Guardamos los cambios en el archivo
            guardar_jugadores_en_archivo(nombres, categorias)
            print(f"El jugador '{eliminado_nombre}' ha sido eliminado exitosamente.")
            break

    if not encontrado:
        print(f"No se encontró al jugador '{buscado}' para eliminar.")


def armar_parejas():
    """NUEVA FUNCIÓN: Lee los jugadores guardados en el archivo y arma las parejas."""
    print("\n--- ARMADO DE PAREJAS ---")
    nombres, categorias = cargar_jugadores_desde_archivo()
    cant_jugadores = len(nombres)

    if cant_jugadores == 0:
        print("No hay jugadores inscriptos en el archivo.")
        return

    if cant_jugadores % 2 != 0:
        print(f"Hay {cant_jugadores} jugadores inscriptos. Se necesita una cantidad PAR de jugadores para formar parejas.")
        return

    cant_parejas = cant_jugadores // 2
    jugadores_asignados = []

    for i in range(cant_parejas):
        print(f"\n--- Pareja N° {i + 1} de {cant_parejas} ---")
        nombre_pareja = input("Ingrese el nombre de la pareja (ej. Los Tanos): ").strip()

        # Mostrar lista de jugadores
        print("\nLista de jugadores:")
        for j in range(cant_jugadores):
            estado = "DISPONIBLE" if j not in jugadores_asignados else "ASIGNADO"
            print(f"  {j + 1}. {nombres[j]} (Categoría: {categorias[j]}) - [{estado}]")

        # Elección del Jugador 1
        while True:
            opc1 = int(input("\nSeleccione el número del Jugador 1: ")) - 1
            if opc1 < 0 or opc1 >= cant_jugadores:
                print("Número fuera de rango.")
            elif opc1 in jugadores_asignados:
                print("Ese jugador ya pertenece a otra pareja.")
            else:
                break

        # Elección del Jugador 2
        while True:
            opc2 = int(input("Seleccione el número del Jugador 2: ")) - 1
            if opc2 < 0 or opc2 >= cant_jugadores:
                print("Número fuera de rango.")
            elif opc2 == opc1:
                print("Un jugador no puede ser pareja de sí mismo.")
            elif opc2 in jugadores_asignados:
                print("Ese jugador ya pertenece a otra pareja.")
            else:
                break

        # Registrar selección
        jugadores_asignados.extend([opc1, opc2])
        print(f"¡Pareja '{nombre_pareja}' conformada por {nombres[opc1]} y {nombres[opc2]}!")


# -------------------------------------------------------------------
# MENÚ PRINCIPAL
# -------------------------------------------------------------------

def menu():
    while True:
        print("\n==========================================")
        print("     SISTEMA DE GESTIÓN DEL TORNEO")
        print("==========================================")
        print("1. Agregar nuevo inscripto")
        print("2. Mostrar lista completa de inscriptos")
        print("3. Buscar jugador y ver su categoría")
        print("4. Eliminar jugador lesionado/baja")
        print("5. Armar parejas del torneo")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción (1-6): ").strip()

        if opcion == "1":
            agregar_jugador()
        elif opcion == "2":
            mostrar_lista_completa()
        elif opcion == "3":
            buscar_jugador()
        elif opcion == "4":
            eliminar_jugador()
        elif opcion == "5":
            armar_parejas()
        elif opcion == "6":
            print("\n¡Programa finalizado! Todos los datos están a salvo en el archivo.")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

# Ejecutar programa
if _name_ == "_main_":
    menu()