# SUBALGORITMOS (FUNCIONES Y PROCEDIMIENTOS)

def cargar_matriz(nombre_archivo):
    matriz = []
    try:
        archivo = open(nombre_archivo, "r", encoding="utf-8")
        lineas = archivo.readlines()
        archivo.close()

        if len(lineas) == 0:
            print("Error: El archivo esta vacio.")
            return None, 0

        columnas_esperadas = -1

        for linea in lineas:
            linea = linea.strip()
            if linea != "":
                partes = linea.split(",")
                fila = []
                for valor in partes:
                    fila.append(float(valor))

                if columnas_esperadas == -1:
                    columnas_esperadas = len(fila)
                elif len(fila) != columnas_esperadas:
                    print("Error: Las filas no tienen la misma cantidad de columnas.")
                    return None, 0

                matriz.append(fila)

        n = len(matriz)

        # Validamos que sea matriz aumentada (n ecuaciones por n+1 columnas)
        if n <= 0 or n + 1 != columnas_esperadas:
            print("Error: La cantidad de ecuaciones no coincide con las incognitas.")
            return None, 0

        return matriz, n

    except FileNotFoundError:
        print("Error: No se encontro el archivo:", nombre_archivo)
        return None, 0
    except ValueError:
        print("Error: El archivo contiene datos que no son numeros.")
        return None, 0


def intercambiar_filas(matriz, n, f1, f2):
    for j in range(n + 1):
        aux = matriz[f1][j]
        matriz[f1][j] = matriz[f2][j]
        matriz[f2][j] = aux


def multiplicar_fila(matriz, n, fila, escalar):
    for j in range(n + 1):
        matriz[fila][j] = matriz[fila][j] * escalar


def sumar_filas(matriz, n, f_origen, f_destino, escalar):
    for j in range(n + 1):
        matriz[f_destino][j] = matriz[f_destino][j] + (matriz[f_origen][j] * escalar)


def gauss_jordan(matriz, n):
    for i in range(n):
        # Si el pivote es cero, buscamos una fila inferior para intercambiar
        if abs(matriz[i][i]) < 0.0000001:
            encontro = False
            k = i + 1
            while k < n and not encontro:
                if abs(matriz[k][i]) > 0.0000001:
                    intercambiar_filas(matriz, n, i, k)
                    encontro = True
                k = k + 1

        pivote = matriz[i][i]

        # Normalizamos la fila pivote y hacemos ceros arriba y abajo
        if abs(pivote) > 0.0000001:
            multiplicar_fila(matriz, n, i, 1.0 / pivote)

            for k in range(n):
                if k != i and abs(matriz[k][i]) > 0.0000001:
                    factor = -matriz[k][i]
                    sumar_filas(matriz, n, i, k, factor)


def clasificar_sistema(matriz, n):
    estado = "COMPATIBLE DETERMINADO"
    definido = False
    i = 0

    while i < n and not definido:
        todos_ceros = True
        j = 0
        while j < n and todos_ceros:
            if abs(matriz[i][j]) > 0.0000001:
                todos_ceros = False
            j = j + 1

        if todos_ceros:
            if abs(matriz[i][n]) > 0.0000001:
                estado = "INCOMPATIBLE"
                definido = True
            else:
                estado = "COMPATIBLE INDETERMINADO"
                definido = True

        i = i + 1

    return estado


def mostrar_matriz(matriz, n):
    for i in range(n):
        linea = ""
        for j in range(n + 1):
            num = round(matriz[i][j], 2)
            if num == -0.0:
                num = 0.0

            if j == n:
                linea = linea + "| " + str(num)
            else:
                linea = linea + str(num) + "\t"
        print(linea)


def guardar_reporte(nombre_salida, matriz, n, estado):
    archivo = open(nombre_salida, "w", encoding="utf-8")
    archivo.write("REPORTE DE OPTIMIZACION DE RECURSOS\n")
    archivo.write("===================================\n\n")
    archivo.write("Estado del sistema: " + estado + "\n\n")
    archivo.write("Matriz escalonada reducida:\n")

    for i in range(n):
        linea = ""
        for j in range(n + 1):
            num = round(matriz[i][j], 2)
            if num == -0.0:
                num = 0.0
            linea = linea + str(num) + "\t"
        archivo.write(linea + "\n")

    archivo.write("\nAsignacion optima:\n")
    if estado == "COMPATIBLE DETERMINADO":
        for i in range(n):
            valor = round(matriz[i][n], 2)
            archivo.write(" -> Variable x" + str(i + 1) + ": " + str(valor) + " horas\n")
    elif estado == "COMPATIBLE INDETERMINADO":
        archivo.write("El sistema tiene infinitas soluciones posibles.\n")
    else:
        archivo.write("El sistema no tiene solucion (restricciones contradictorias).\n")

    archivo.close()
    print("\nReporte guardado en:", nombre_salida)

# ALGORITMO PRINCIPAL
def main():
    print("=== OPTIMIZADOR DE HORAS DE SOPORTE ===")
    nombre_archivo = input("Ingrese el nombre del archivo de restricciones (ej. prueba1.txt): ")

    matriz, n = cargar_matriz(nombre_archivo)

    if matriz is not None:
        print("\nMatriz inicial:")
        mostrar_matriz(matriz, n)

        gauss_jordan(matriz, n)

        print("\nMatriz escalonada reducida:")
        mostrar_matriz(matriz, n)

        estado = clasificar_sistema(matriz, n)
        print("\nEstado del sistema:", estado)

        if estado == "COMPATIBLE DETERMINADO":
            print("Asignacion optima:")
            for i in range(n):
                valor = round(matriz[i][n], 2)
                print(" -> Variable x" + str(i + 1) + ":", valor, "horas")

        guardar_reporte("resultado_optimizacion.txt", matriz, n, estado)


main()