# Objetivos de la semana: Introducir la estructura de datos en memoria mediante arreglos unidimensionales (vectores). Aplicar las operaciones básicas con vectores: inicialización, carga de datos por teclado y recorrido.
#
# Ningún torneo empieza con los jugadores ya anotados por arte de magia. Nuestro sistema necesita un módulo de inscripción para que el juez registre a los competidores antes de repartir puntos.
#
# Para poder poner en marcha el torneo, lo primero que necesitamos del sistema es
# poder cargar a los jugadores y luego armar las parejas que van a
# competir. Recuerden que en el pádel se juega de a dos: ninguna pareja puede
# tener más ni menos de 2 jugadores.
#
# a) Ingreso de jugadores
#
#  Al iniciar el programa, el sistema debe preguntarle al juez:
#   "¿Cuántos jugadores van a participar en el torneo?".
#  A partir de esa respuesta, debe permitir registrar cada competidor, uno por
#   uno, con la siguiente información:
#    su nombre (con el que se lo identificará dentro del torneo), y
#    su categoría (el nivel en el que juega, por ejemplo 4ª, 5ª o 6ª).
#
# b) Armado de parejas
#
#  Una vez cargados todos los jugadores, el sistema debe permitir formar las
#   parejas del torneo.
#  Cada pareja debe tener:
#    un nombre que la identifique dentro del torneo (por ejemplo,
#     "Los Tanos"), y
#    exactamente 2 jugadores, elegidos entre los que ya fueron inscriptos.


def ingresar_jugadores():
    """Carga los jugadores en arreglos unidimensionales."""
    while True:
        try:
            cantidad = int(input("¿Cuántos jugadores van a participar en el torneo? "))
        except ValueError:
            print("Debe ingresar un número entero válido.")
            continue

        if cantidad > 0:
            break
        print("La cantidad de jugadores debe ser mayor que cero.")

    nombres = [""] * cantidad
    categorias = [""] * cantidad

    for i in range(cantidad):
        nombres[i] = input(f"Ingrese el nombre del jugador {i + 1}: ").strip()
        categorias[i] = input(f"Ingrese la categoría del jugador {i + 1}: ").strip()

    return nombres, categorias


def mostrar_jugadores(nombres, categorias):
    """Recorre los arreglos y muestra todos los jugadores registrados."""
    print("\nJugadores inscriptos:")
    for i in range(len(nombres)):
        print(f"{i + 1}. {nombres[i]} - Categoría: {categorias[i]}")


def armar_parejas(nombres):
    """Permite crear parejas con dos jugadores de la lista."""
    if len(nombres) < 2:
        print("Debe haber al menos 2 jugadores para armar una pareja.")
        return []

    if len(nombres) % 2 != 0:
        print("La cantidad de jugadores es impar. No se puede armar una cantidad completa de parejas.")

    parejas = []
    jugadores_usados = []
    total_parejas = len(nombres) // 2

    for i in range(total_parejas):
        nombre_pareja = input(f"Ingrese el nombre de la pareja {i + 1}: ").strip()

        while True:
            print("Seleccione dos jugadores distintos usando sus números:")
            for j in range(len(nombres)):
                if j + 1 not in jugadores_usados:
                    print(f"{j + 1}. {nombres[j]}")

            try:
                jugador1 = int(input("Jugador 1: ")) - 1
                jugador2 = int(input("Jugador 2: ")) - 1
            except ValueError:
                print("Debe ingresar números válidos.")
                continue

            if 0 <= jugador1 < len(nombres) and 0 <= jugador2 < len(nombres):
                if jugador1 != jugador2:
                    if (jugador1 + 1) in jugadores_usados or (jugador2 + 1) in jugadores_usados:
                        print("Uno o ambos jugadores ya fueron usados en otra pareja.")
                        continue
                    parejas.append((nombre_pareja, nombres[jugador1], nombres[jugador2]))
                    jugadores_usados.extend([jugador1 + 1, jugador2 + 1])
                    break
                print("Los dos jugadores deben ser distintos.")
            else:
                print("Los números ingresados no corresponden a jugadores válidos.")

    return parejas


def mostrar_parejas(parejas):
    """Muestra las parejas armadas."""
    print("\nParejas del torneo:")
    if not parejas:
        print("Todavía no se armó ninguna pareja.")
        return

    for i in range(len(parejas)):
        nombre_pareja, jugador1, jugador2 = parejas[i]
        print(f"{i + 1}. {nombre_pareja}: {jugador1} y {jugador2}")


def menu():
    nombres = []
    categorias = []
    parejas = []

    while True:
        print("\n==== TORNEO DE PÁDEL ====")
        print("1. Cargar jugadores")
        print("2. Mostrar jugadores")
        print("3. Armar parejas")
        print("4. Mostrar parejas")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombres, categorias = ingresar_jugadores()
        elif opcion == "2":
            if len(nombres) == 0:
                print("Primero debe cargar los jugadores.")
            else:
                mostrar_jugadores(nombres, categorias)
        elif opcion == "3":
            if len(nombres) == 0:
                print("Primero debe cargar los jugadores.")
            else:
                parejas = armar_parejas(nombres)
        elif opcion == "4":
            mostrar_parejas(parejas)
        elif opcion == "5":
            print("Gracias por usar el sistema de torneo.")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    menu()

