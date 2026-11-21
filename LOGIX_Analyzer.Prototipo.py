# LOGIX-Analyzer - AE4 TIFAS 2026
# Ingenieria de Requerimientos I - Matematica Discreta - Programacion
# Alumnos: Bianchi Lucas Nahuel - Sabugo Fabricio
# UCP - Ingenieria en Sistemas de Informacion
#
# Los modulos van en el orden PED, CLI, INV, ROB, ASG, RUT, SEG, ENT, REP
# A[i][j] = 1 quiere decir que el modulo i depende del modulo j
# Los montos estan en miles de u.m.

MAX_MODULOS = 15
INFINITO = 999999          # para dijkstra
TOLERANCIA = 0.000001      # para comparar decimales

MODULOS_OFICIALES = ["PED", "CLI", "INV", "ROB", "ASG", "RUT", "SEG", "ENT", "REP"]

# Tabla 2: (X, Y) = X depende de Y
DEPENDENCIAS_TABLA2 = [
    ("PED", "CLI"), ("PED", "INV"), ("PED", "ASG"),
    ("INV", "ROB"), ("ROB", "INV"),
    ("ASG", "RUT"), ("ASG", "INV"),
    ("RUT", "SEG"), ("SEG", "ASG"),
    ("ENT", "PED"), ("ENT", "SEG"),
    ("REP", "PED"), ("REP", "ENT"), ("REP", "INV"),
]


# ----- funciones para matrices -----
# crea una matriz llena con el valor que le paso
def crear_matriz(filas, columnas, valor):
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(valor)
        matriz.append(fila)
    return matriz


# copia la matriz para no modificar la original
def copiar_matriz(matriz):
    copia = []
    for fila in matriz:
        nueva_fila = []
        for valor in fila:
            nueva_fila.append(valor)
        copia.append(nueva_fila)
    return copia


# cuenta los 1 de la matriz (sirve para contar arcos o pares alcanzables)
def contar_unos(matriz):
    total = 0
    for fila in matriz:
        for valor in fila:
            if valor == 1:
                total = total + 1
    return total


def diagonal(matriz):
    resultado = []
    for i in range(len(matriz)):
        resultado.append(matriz[i][i])
    return resultado


# muestra la matriz con los nombres de filas y columnas
def mostrar_matriz(matriz, nombres_filas, nombres_columnas):
    encabezado = "     "
    for nombre in nombres_columnas:
        encabezado = encabezado + nombre.rjust(5)
    print(encabezado)
    for i in range(len(matriz)):
        linea = nombres_filas[i].ljust(5)
        for valor in matriz[i]:
            linea = linea + str(valor).rjust(5)
        print(linea)


# si el numero es entero lo muestra sin coma
def formatear(numero):
    if abs(numero - round(numero)) < TOLERANCIA:
        return str(int(round(numero)))
    return str(round(numero, 2))


# ----- RF1: carga de modulos y matriz -----
# devuelve "" si esta todo bien, o el mensaje de error
def validar_grafo(modulos, A):
    n = len(modulos)
    if n == 0:
        return "Debe haber al menos un módulo."
    if n > MAX_MODULOS:
        return "El número máximo de módulos permitido es " + str(MAX_MODULOS) + "."
    for i in range(n):
        for j in range(i + 1, n):
            if modulos[i] == modulos[j]:
                return "Los nombres de los módulos no se pueden repetir."
    if len(A) != n:
        return "La matriz debe tener " + str(n) + " filas."
    for fila in A:
        if len(fila) != n:
            return "Cada fila de la matriz debe tener " + str(n) + " valores."
        for valor in fila:
            if valor != 0 and valor != 1:
                return "La matriz de adyacencia sólo admite valores 0 o 1."
    return ""


# si no le paso nada carga la Tabla 2 de la consigna
def cargar_grafo(modulos=None, A=None):
    if modulos is None:
        modulos = []
        for m in MODULOS_OFICIALES:
            modulos.append(m)
        n = len(modulos)
        A = crear_matriz(n, n, 0)
        for dependencia in DEPENDENCIAS_TABLA2:
            i = modulos.index(dependencia[0])
            j = modulos.index(dependencia[1])
            A[i][j] = 1
    error = validar_grafo(modulos, A)
    if error != "":
        print("Error:", error)
        return None, None
    return modulos, A


# pasa un texto "0 1 0" a la lista [0, 1, 0]
def convertir_fila(texto):
    texto = texto.replace(",", " ")
    fila = []
    for parte in texto.split():
        fila.append(int(parte))
    return fila


# respuestas es para poder probarla en los casos de prueba sin escribir
def cargar_desde_teclado(respuestas=None):
    if respuestas is None:
        texto = input("Nombres de los módulos (separados por espacio, máximo 15): ")
    else:
        texto = respuestas[0]
    modulos = texto.replace(",", " ").upper().split()
    A = []
    for k in range(len(modulos)):
        if respuestas is None:
            texto = input("Fila de " + modulos[k] + " (" + str(len(modulos)) + " valores 0 o 1): ")
        else:
            texto = respuestas[k + 1]
        try:
            A.append(convertir_fila(texto))
        except ValueError:
            print("Error: sólo se pueden ingresar números 0 o 1.")
            return None, None
    return cargar_grafo(modulos, A)


# primera linea: los modulos. despues una fila de la matriz por linea
def cargar_desde_archivo(ruta):
    try:
        archivo = open(ruta, "r", encoding="utf-8")
    except FileNotFoundError:
        print("Error: no se encontró el archivo", ruta)
        return None, None
    lineas = []
    for linea in archivo:
        linea = linea.strip()
        if linea != "":
            lineas.append(linea)
    archivo.close()
    if len(lineas) == 0:
        print("Error: el archivo está vacío.")
        return None, None
    modulos = lineas[0].replace(",", " ").upper().split()
    A = []
    for k in range(1, len(lineas)):
        try:
            A.append(convertir_fila(lineas[k]))
        except ValueError:
            print("Error: la línea", k + 1, "del archivo tiene valores que no son 0 o 1.")
            return None, None
    return cargar_grafo(modulos, A)


def guardar_en_archivo(modulos, A, ruta):
    archivo = open(ruta, "w", encoding="utf-8")
    archivo.write(" ".join(modulos) + "\n")
    for fila in A:
        texto = ""
        for valor in fila:
            texto = texto + str(valor) + " "
        archivo.write(texto.strip() + "\n")
    archivo.close()


# ----- RF2: grados -----
# salida = suma de la fila, entrada = suma de la columna
def grados_entrada_salida(A, modulos):
    n = len(modulos)
    salida = []
    entrada = []
    for i in range(n):
        suma_fila = 0
        suma_columna = 0
        for j in range(n):
            suma_fila = suma_fila + A[i][j]
            suma_columna = suma_columna + A[j][i]
        salida.append(suma_fila)
        entrada.append(suma_columna)
    return salida, entrada


# ----- RF3: alcanzabilidad (warshall) -----
# Z[i][j] = 1 si hay algun k con X[i][k] = 1 y Y[k][j] = 1
def producto_booleano(X, Y):
    filas = len(X)
    columnas = len(Y[0])
    intermedio = len(Y)
    Z = crear_matriz(filas, columnas, 0)
    for i in range(filas):
        for j in range(columnas):
            for k in range(intermedio):
                if X[i][k] == 1 and Y[k][j] == 1:
                    Z[i][j] = 1
    return Z


# devuelve A, A^2, ..., A^n
def potencias_booleanas(A):
    potencias = [copiar_matriz(A)]
    actual = copiar_matriz(A)
    for k in range(len(A) - 1):
        actual = producto_booleano(actual, A)
        potencias.append(actual)
    return potencias


# A* = A or A^2 or ... or A^n (lo uso para comprobar warshall)
def alcanzabilidad_por_potencias(A):
    n = len(A)
    R = crear_matriz(n, n, 0)
    for P in potencias_booleanas(A):
        for i in range(n):
            for j in range(n):
                if P[i][j] == 1:
                    R[i][j] = 1
    return R


# si i llega a k y k llega a j, entonces i llega a j
def warshall(A):
    n = len(A)
    R = copiar_matriz(A)
    for k in range(n):
        for i in range(n):
            if R[i][k] == 1:
                for j in range(n):
                    if R[k][j] == 1:
                        R[i][j] = 1
    return R


# los afectados por modificar j estan en la columna j de A*
def modulos_afectados(Astar, j, modulos):
    afectados = []
    for i in range(len(modulos)):
        if Astar[i][j] == 1:
            afectados.append(modulos[i])
    return afectados


# ----- RF4: ciclos -----
# si A*[i][i] = 1 el modulo esta en un ciclo
# i y j estan en la misma componente si A*[i][j] = 1 y A*[j][i] = 1
def detectar_ciclos(Astar, modulos):
    n = len(modulos)
    en_ciclo = []
    for i in range(n):
        if Astar[i][i] == 1:
            en_ciclo.append(modulos[i])
    cfc = []
    ya_usados = []
    for i in range(n):
        if Astar[i][i] == 1 and i not in ya_usados:
            componente = [modulos[i]]
            ya_usados.append(i)
            for j in range(i + 1, n):
                if Astar[i][j] == 1 and Astar[j][i] == 1:
                    componente.append(modulos[j])
                    ya_usados.append(j)
            cfc.append(componente)
    return en_ciclo, cfc


# ----- RF5: sistema de ecuaciones -----
def mostrar_ampliada(aug):
    n = len(aug)
    for i in range(n):
        linea = "   ["
        for j in range(n):
            linea = linea + formatear(aug[i][j]).rjust(6)
        linea = linea + "  |" + formatear(aug[i][n]).rjust(7) + " ]"
        print(linea)


# metodo del pivote (Gauss-Jordan)
# en cada columna busco un pivote, lo hago 1 y hago ceros arriba y abajo
# el determinante es el producto de los pivotes (cambia de signo si cambio filas)
def resolver_sistema(M, B, mostrar_pasos=False):
    n = len(M)
    if n < 2 or n > 5:
        print("Error: el sistema debe ser de 2 x 2 hasta 5 x 5.")
        return None, None, None, 0
    # armo la matriz ampliada [M | B]
    aug = []
    for i in range(n):
        fila = []
        for j in range(n):
            fila.append(float(M[i][j]))
        fila.append(float(B[i]))
        aug.append(fila)
    if mostrar_pasos:
        print("Matriz ampliada inicial:")
        mostrar_ampliada(aug)

    determinante = 1.0
    operaciones = 0
    fila_pivote = 0
    for col in range(n):
        # busco una fila con 1, si no hay agarro la primera que no sea 0
        elegida = -1
        for i in range(fila_pivote, n):
            if abs(aug[i][col] - 1) < TOLERANCIA:
                elegida = i
                break
        if elegida == -1:
            for i in range(fila_pivote, n):
                if abs(aug[i][col]) > TOLERANCIA:
                    elegida = i
                    break
        if elegida == -1:
            determinante = 0.0          # no hay pivote, el det da 0
            continue
        # cambio de fila si hace falta
        if elegida != fila_pivote:
            aug[fila_pivote], aug[elegida] = aug[elegida], aug[fila_pivote]
            determinante = -determinante
            operaciones = operaciones + 1
            if mostrar_pasos:
                print("F" + str(fila_pivote + 1) + " <-> F" + str(elegida + 1))
                mostrar_ampliada(aug)
        # hago 1 el pivote
        pivote = aug[fila_pivote][col]
        determinante = determinante * pivote
        if abs(pivote - 1) > TOLERANCIA:
            for j in range(n + 1):
                aug[fila_pivote][j] = aug[fila_pivote][j] / pivote
            operaciones = operaciones + 1
            if mostrar_pasos:
                print("F" + str(fila_pivote + 1) + " <- F" + str(fila_pivote + 1) + " / (" + formatear(pivote) + ")")
                mostrar_ampliada(aug)
        # hago ceros en el resto de la columna
        hubo_cambios = False
        texto = ""
        for i in range(n):
            factor = aug[i][col]
            if i != fila_pivote and abs(factor) > TOLERANCIA:
                for j in range(n + 1):
                    aug[i][j] = aug[i][j] - factor * aug[fila_pivote][j]
                operaciones = operaciones + 1
                hubo_cambios = True
                if abs(abs(factor) - 1) < TOLERANCIA:
                    numero = ""                       # para que no quede "1F1"
                else:
                    numero = formatear(abs(factor))
                if factor > 0:
                    signo = " - "
                else:
                    signo = " + "
                texto = texto + "F" + str(i + 1) + " <- F" + str(i + 1) + signo + numero + "F" + str(fila_pivote + 1) + "   "
        if mostrar_pasos and hubo_cambios:
            print(texto)
            mostrar_ampliada(aug)
        fila_pivote = fila_pivote + 1

    # si queda una fila 0 = b (b distinto de 0) es incompatible, si queda 0 = 0 es indeterminado
    for i in range(fila_pivote, n):
        if abs(aug[i][n]) > TOLERANCIA:
            return "INCOMPATIBLE", 0.0, None, operaciones
    if fila_pivote < n:
        return "COMPATIBLE INDETERMINADO", 0.0, None, operaciones
    solucion = []
    for i in range(n):
        solucion.append(aug[i][n])
    return "COMPATIBLE DETERMINADO", determinante, solucion, operaciones


# ----- RF6: punto de equilibrio -----
# C1(n) = b1 + a1*n  y  C2(n) = b2 + a2*n  ->  n = (b2 - b1) / (a1 - a2)
def equilibrio(a1, b1, a2, b2):
    if abs(a1 - a2) < TOLERANCIA:
        if abs(b1 - b2) < TOLERANCIA:
            return "COINCIDENTES", None, None
        return "PARALELAS", None, None
    n = (b2 - b1) / (a1 - a2)
    costo = b1 + a1 * n
    return "UNICO", n, costo


# ----- RF7: dijkstra -----
# Tabla 5 de la consigna (minutos)
def red_distribucion():
    nodos = ["D", "H1", "H2", "Z1", "Z2", "Z3"]
    tramos = [("D", "H1", 8), ("D", "H2", 5), ("H1", "H2", 2), ("H1", "Z1", 6), ("H2", "Z1", 10),
              ("H2", "Z2", 7), ("Z1", "Z2", 3), ("Z1", "Z3", 9), ("Z2", "Z3", 4)]
    return nodos, tramos


# en cada etapa fijo el nodo no visitado con menor distancia y actualizo sus vecinos
def dijkstra(nodos, tramos, origen, destino, mostrar_etapas=False):
    n = len(nodos)
    # matriz de pesos W
    W = crear_matriz(n, n, INFINITO)
    for tramo in tramos:
        i = nodos.index(tramo[0])
        j = nodos.index(tramo[1])
        W[i][j] = tramo[2]
        W[j][i] = tramo[2]       # la red no es dirigida
    distancia = []
    anterior = []
    visitado = []
    for i in range(n):
        distancia.append(INFINITO)
        anterior.append(-1)
        visitado.append(False)
    distancia[nodos.index(origen)] = 0
    orden_fijados = []

    for etapa in range(n):
        # busco el de menor distancia
        u = -1
        for i in range(n):
            if not visitado[i] and (u == -1 or distancia[i] < distancia[u]):
                u = i
        if distancia[u] == INFINITO:
            break                # no se puede llegar a los que quedan
        visitado[u] = True
        orden_fijados.append(nodos[u])
        if mostrar_etapas:
            print("  Etapa", etapa + 1, ": se fija", nodos[u], "con distancia", distancia[u])
        if nodos[u] == destino:
            break
        # actualizo los vecinos
        for v in range(n):
            if not visitado[v] and W[u][v] != INFINITO:
                if distancia[u] + W[u][v] < distancia[v]:
                    distancia[v] = distancia[u] + W[u][v]
                    anterior[v] = u

    d = nodos.index(destino)
    if distancia[d] == INFINITO:
        return INFINITO, [], orden_fijados
    # armo el camino de atras para adelante
    camino = []
    actual = d
    while actual != -1:
        camino.insert(0, nodos[actual])
        actual = anterior[actual]
    return distancia[d], camino, orden_fijados


# ----- RF8: orden de migracion -----
# un modulo se migra cuando ya se migraron todos los modulos de los que depende
def orden_topologico(A, modulos):
    n = len(modulos)
    Astar = warshall(A)
    for i in range(n):
        if Astar[i][i] == 1:
            return None, "El grafo contiene dependencias circulares (ciclos); no existe orden topológico."
    migrado = []
    for i in range(n):
        migrado.append(False)
    orden = []
    while len(orden) < n:
        for i in range(n):
            if not migrado[i]:
                puede = True
                for j in range(n):
                    if A[i][j] == 1 and not migrado[j]:
                        puede = False          # depende de uno que todavia no se migro
                if puede:
                    migrado[i] = True
                    orden.append(modulos[i])
                    break
    return orden, "Orden topológico calculado."


def verificar_orden(A, modulos, orden):
    for i in range(len(modulos)):
        for j in range(len(modulos)):
            if A[i][j] == 1 and orden.index(modulos[j]) > orden.index(modulos[i]):
                return False
    return True


# ----- puntos 1, 4 y 5 -----
# Punto 1: a = S*u  y  S*S^T
def alcance_superposicion(S):
    filas = len(S)
    columnas = len(S[0])
    a = []
    for i in range(filas):
        suma = 0
        for j in range(columnas):
            suma = suma + S[i][j]
        a.append(suma)
    SS = crear_matriz(filas, filas, 0)
    for i in range(filas):
        for k in range(filas):
            for j in range(columnas):
                SS[i][k] = SS[i][k] + S[i][j] * S[k][j]
    return a, SS


# Punto 4: v = P*w (los pesos tienen que sumar 1)
def decision_ponderada(P, w):
    suma = 0
    for peso in w:
        if peso < 0:
            print("Error: los pesos no pueden ser negativos.")
            return None
        suma = suma + peso
    if abs(suma - 1) > TOLERANCIA:
        print("Error: los pesos deben sumar 1.")
        return None
    v = []
    for i in range(len(P)):
        puntaje = 0
        for j in range(len(w)):
            puntaje = puntaje + P[i][j] * w[j]
        v.append(puntaje)
    return v


# Punto 5: RT = RC (.) CT
def trazabilidad_RT(RC, CT):
    RT = producto_booleano(RC, CT)
    req_sin_prueba = []
    for i in range(len(RT)):
        if 1 not in RT[i]:
            req_sin_prueba.append("R" + str(i + 1))
    comp_sin_prueba = []
    for k in range(len(CT)):
        if 1 not in CT[k]:
            comp_sin_prueba.append("C" + str(k + 1))
    return RT, req_sin_prueba, comp_sin_prueba


# ----- informe del grafo -----
def informe_grafo(modulos, A):
    print("\nMatriz de adyacencia A:")
    mostrar_matriz(A, modulos, modulos)
    salida, entrada = grados_entrada_salida(A, modulos)
    print("\nGrados de cada módulo:")
    for i in range(len(modulos)):
        print("  " + modulos[i].ljust(5) + " salida =", salida[i], "  entrada =", entrada[i])
    Astar = warshall(A)
    print("\nMatriz de alcanzabilidad A*:")
    mostrar_matriz(Astar, modulos, modulos)
    print("Pares alcanzables en A*:", contar_unos(Astar))
    en_ciclo, cfc = detectar_ciclos(Astar, modulos)
    if len(en_ciclo) == 0:
        print("No hay módulos en ciclos.")
    else:
        print("Módulos en ciclos:", en_ciclo, "  CFC:", cfc)
    print("\nMódulos afectados si se modifica cada uno:")
    for j in range(len(modulos)):
        print("  " + modulos[j].ljust(5), "->", modulos_afectados(Astar, j, modulos))
    orden, mensaje = orden_topologico(A, modulos)
    if orden is None:
        print("\nOrden de migración:", mensaje)
    else:
        print("\nOrden de migración:", " -> ".join(orden))


# ----- casos de prueba -----
def resultado(nombre, correcto):
    if correcto:
        print("VERIFICACIÓN " + nombre + ": [OK]")
    else:
        print("VERIFICACIÓN " + nombre + ": [ERROR]")
    return correcto


def casi_igual(x, y):
    return abs(x - y) < 0.001


def ejecutar_casos_de_prueba():
    aprobados = 0
    print("=" * 70)
    print(" CASOS DE PRUEBA LOGIX-ANALYZER (CP1 a CP10)")
    print("=" * 70)

    # ---- CP1: Tabla 2 completa ----
    print("\n--- CP1: Tabla 2 completa (9 módulos, 14 aristas) ---")
    modulos, A = cargar_grafo()
    salida, entrada = grados_entrada_salida(A, modulos)
    Astar = warshall(A)
    en_ciclo, cfc = detectar_ciclos(Astar, modulos)
    afectados_inv = modulos_afectados(Astar, modulos.index("INV"), modulos)
    print("Grados de salida: ", salida)
    print("Grados de entrada:", entrada)
    print("Aristas:", contar_unos(A), "| pares alcanzables en A*:", contar_unos(Astar))
    print("Módulos en ciclo:", en_ciclo)
    print("CFC:", cfc)
    print("Modificar INV afecta a", len(afectados_inv), "módulos:", afectados_inv)
    ok = (salida == [3, 0, 1, 1, 2, 1, 1, 2, 3] and entrada == [2, 1, 4, 1, 2, 1, 2, 1, 0]
          and contar_unos(A) == 14 and contar_unos(Astar) == 40
          and en_ciclo == ["INV", "ROB", "ASG", "RUT", "SEG"]
          and cfc == [["INV", "ROB"], ["ASG", "RUT", "SEG"]]
          and len(afectados_inv) == 8 and Astar == alcanzabilidad_por_potencias(A))
    if resultado("CP1", ok):
        aprobados = aprobados + 1

    # ---- CP2: grafo reestructurado G' ----
    print("\n--- CP2: G' (sin INV->ROB y sin SEG->ASG) ---")
    Ap = copiar_matriz(A)
    Ap[modulos.index("INV")][modulos.index("ROB")] = 0
    Ap[modulos.index("SEG")][modulos.index("ASG")] = 0
    Apstar = warshall(Ap)
    orden, mensaje = orden_topologico(Ap, modulos)
    print("Aristas:", contar_unos(Ap), "| pares en A'*:", contar_unos(Apstar), "| diagonal de A'*:", diagonal(Apstar))
    print("Orden de migración (RF8):", orden)
    ok = (contar_unos(Ap) == 12 and contar_unos(Apstar) == 23 and 1 not in diagonal(Apstar)
          and orden == ["CLI", "INV", "ROB", "SEG", "RUT", "ASG", "PED", "ENT", "REP"]
          and verificar_orden(Ap, modulos, orden))
    if resultado("CP2", ok):
        aprobados = aprobados + 1

    # ---- CP3: Tabla 6 por Gauss-Jordan ----
    print("\n--- CP3: Sistema de costos 3x3 (Tabla 6) ---")
    M = [[2, 3, 1], [1, 2, 2], [3, 1, 2]]
    B = [119, 122, 126]
    clasificacion, det, X, operaciones = resolver_sistema(M, B, mostrar_pasos=True)
    I_B = 4 * X[0] + 6 * X[1] + 3 * X[2]           # I_B = Q * X, Q = [4, 6, 3]
    print("det(M) =", formatear(det), "->", clasificacion)
    print("x =", formatear(X[0]), " y =", formatear(X[1]), " z =", formatear(X[2]), "mil u.m.   I_B =", formatear(I_B), "mil u.m.")
    print("Operaciones elementales:", operaciones)
    ok = (casi_igual(det, 11) and clasificacion == "COMPATIBLE DETERMINADO"
          and casi_igual(X[0], 12) and casi_igual(X[1], 20) and casi_igual(X[2], 35) and casi_igual(I_B, 273))
    if resultado("CP3", ok):
        aprobados = aprobados + 1

    # ---- CP4: puntos de equilibrio ----
    print("\n--- CP4: equilibrios (C_A = 110n ; C_B = 273 + 45n ; C_C = 420 + 40n) ---")
    tAB, nAB, cAB = equilibrio(110, 0, 45, 273)
    tAC, nAC, cAC = equilibrio(110, 0, 40, 420)
    tBC, nBC, cBC = equilibrio(45, 273, 40, 420)
    print("  A-B: n =", formatear(nAB), "años, costo =", formatear(cAB), "mil u.m.")
    print("  A-C: n =", formatear(nAC), "años, costo =", formatear(cAC), "mil u.m.")
    print("  B-C: n =", formatear(nBC), "años, costo =", formatear(cBC), "mil u.m.")
    ok = (casi_igual(nAB, 4.2) and casi_igual(cAB, 462) and casi_igual(nAC, 6) and casi_igual(cAC, 660)
          and casi_igual(nBC, 29.4) and casi_igual(cBC, 1596))
    if resultado("CP4", ok):
        aprobados = aprobados + 1

    # ---- CP5: Dijkstra ----
    print("\n--- CP5: Dijkstra D -> Z3 (Tabla 5) y corredor aéreo ---")
    nodos, tramos = red_distribucion()
    print("Ruta fija legacy D-H1-Z1-Z3 =", 8 + 6 + 9, "min")
    d1, camino1, fijados1 = dijkstra(nodos, tramos, "D", "Z3", mostrar_etapas=True)
    print("Terrestre mínimo:", d1, "min por", camino1)
    tramos_con_corredor = tramos + [("D", "Z3", 14)]
    d2, camino2, fijados2 = dijkstra(nodos, tramos_con_corredor, "D", "Z3")
    print("Con corredor D-Z3 (14):", d2, "min por", camino2)
    ok = (d1 == 16 and camino1 == ["D", "H2", "Z2", "Z3"] and d2 == 14 and camino2 == ["D", "Z3"]
          and fijados1 == ["D", "H2", "H1", "Z2", "Z1", "Z3"])
    if resultado("CP5", ok):
        aprobados = aprobados + 1

    # ---- CP6: casos límite ----
    print("\n--- CP6: casos límite ---")
    c1, d_1, x_1, o_1 = resolver_sistema([[1, 2, 3], [2, 4, 6], [1, 1, 1]], [1, 2, 3])
    c2, d_2, x_2, o_2 = resolver_sistema([[1, 2, 3], [2, 4, 6], [1, 1, 1]], [1, 3, 3])
    print("  det = 0 con filas proporcionales y B consistente   ->", c1)
    print("  det = 0 con filas proporcionales y B inconsistente ->", c2)
    t_par, n_par, c_par = equilibrio(50, 100, 50, 200)
    t_coi, n_coi, c_coi = equilibrio(50, 100, 50, 100)
    print("  rectas paralelas ->", t_par, "| rectas coincidentes ->", t_coi)
    orden_ciclico, mensaje_ciclico = orden_topologico(A, modulos)
    print("  RF8 sobre el grafo cíclico G:", mensaje_ciclico)
    d_inf, camino_inf, f_inf = dijkstra(["X", "Y", "Z"], [("X", "Y", 1)], "X", "Z")
    print("  Dijkstra a un nodo inalcanzable -> camino", camino_inf)
    nombres16 = []
    for k in range(16):
        nombres16.append("M" + str(k + 1))
    m16, A16 = cargar_grafo(nombres16, crear_matriz(16, 16, 0))
    m2, A2 = cargar_grafo(["A", "B"], [[0, 2], [0, 0]])
    ok = (c1 == "COMPATIBLE INDETERMINADO" and c2 == "INCOMPATIBLE" and t_par == "PARALELAS"
          and t_coi == "COINCIDENTES" and orden_ciclico is None and camino_inf == []
          and m16 is None and m2 is None)
    if resultado("CP6", ok):
        aprobados = aprobados + 1

    # ---- CP7: trazabilidad ----
    print("\n--- CP7: trazabilidad booleana RT = RC (.) CT ---")
    RC = [[1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    CT = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]
    RT, req_sin, comp_sin = trazabilidad_RT(RC, CT)
    mostrar_matriz(RT, ["R1", "R2", "R3", "R4"], ["T1", "T2", "T3"])
    print("Requerimientos sin prueba:", req_sin, "| componentes sin prueba:", comp_sin)
    CT2 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]   # agrego T4 para C4
    RT2, req_sin2, comp_sin2 = trazabilidad_RT(RC, CT2)
    print("Con T4 (C4 -> T4): requerimientos sin prueba =", req_sin2)
    ok = (RT == [[1, 0, 0], [1, 1, 0], [0, 0, 1], [0, 0, 0]] and req_sin == ["R4"]
          and comp_sin == ["C4"] and req_sin2 == [])
    if resultado("CP7", ok):
        aprobados = aprobados + 1

    # ---- CP8: alcance y superposición (Punto 1) ----
    print("\n--- CP8: matriz de incidencia S (Tabla 3): a = S.u y S.S^T ---")
    S = [[1, 0, 0, 0, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 0],
         [0, 0, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 1, 1, 0, 1]]
    a, SS = alcance_superposicion(S)
    print("a =", a, "| superposición entre s3 y s6 =", SS[2][5])
    ok = a == [2, 2, 4, 2, 1, 4] and SS[2][5] == 3
    if resultado("CP8", ok):
        aprobados = aprobados + 1

    # ---- CP9: matriz de decisión (Punto 4) ----
    print("\n--- CP9: decisión ponderada v = P.w y sensibilidad ---")
    P = [[1, 2, 1, 1, 5], [5, 4, 4, 4, 5], [3, 2, 5, 5, 1]]
    escenarios = [["base", [0.25, 0.25, 0.20, 0.15, 0.15], [1.85, 4.40, 3.15]],
                  ["sens.1", [0.40, 0.20, 0.15, 0.10, 0.15], [1.80, 4.55, 3.00]],
                  ["sens.2 (proporcional)", [0.40, 0.20, 0.16, 0.12, 0.12], [1.68, 4.52, 3.12]],
                  ["adverso", [0.10, 0.10, 0.30, 0.40, 0.10], [1.50, 4.20, 4.10]]]
    ok = True
    for escenario in escenarios:
        v = decision_ponderada(P, escenario[1])
        print("  " + escenario[0].ljust(22), "A =", formatear(v[0]), " B =", formatear(v[1]), " C =", formatear(v[2]))
        for k in range(3):
            if not casi_igual(v[k], escenario[2][k]):
                ok = False
        if not (v[1] > v[0] and v[1] > v[2]):
            ok = False                     # B tiene que ganar siempre
    if decision_ponderada(P, [0.5, 0.5, 0.5, 0, 0]) is not None:
        ok = False                         # estos pesos suman 1,5 y tiene que dar error
    if resultado("CP9", ok):
        aprobados = aprobados + 1

    # ---- CP10: carga por archivo y por teclado (RF1) y G' con bus de eventos ----
    print("\n--- CP10: RF1 desde archivo y teclado; G' con bus de eventos como vértice ---")
    guardar_en_archivo(modulos, A, "grafo_prueba.txt")
    m_arch, A_arch = cargar_desde_archivo("grafo_prueba.txt")
    ok_archivo = m_arch == modulos and A_arch == A
    m_tec, A_tec = cargar_desde_teclado(["X Y Z", "0 1 0", "0 0 1", "0 0 0"])
    ok_teclado = m_tec == ["X", "Y", "Z"] and contar_unos(warshall(A_tec)) == 3
    modulos_bus = modulos + ["BUS"]
    A_bus = crear_matriz(10, 10, 0)
    for i in range(9):
        for j in range(9):
            A_bus[i][j] = Ap[i][j]
    for m in ["SEG", "ASG", "ROB", "INV"]:          # usan el bus
        A_bus[modulos_bus.index(m)][9] = 1
    A_bus_star = warshall(A_bus)
    print("  archivo OK:", ok_archivo, "| teclado OK:", ok_teclado)
    print("  G' + vértice BUS: sin ciclos =", 1 not in diagonal(A_bus_star),
          ", pares alcanzables =", contar_unos(A_bus_star))
    ok = ok_archivo and ok_teclado and 1 not in diagonal(A_bus_star) and contar_unos(A_bus_star) == 31
    if resultado("CP10", ok):
        aprobados = aprobados + 1

    print("\n" + "=" * 70)
    print(" RESULTADO GLOBAL:", aprobados, "de 10 casos de prueba aprobados")
    print("=" * 70)


# ----- menu -----
def pedir_numero(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Error: escriba un número.")


def menu():
    modulos, A = cargar_grafo()          # arranca con la Tabla 2 cargada
    while True:
        print("\n========== LOGIX-ANALYZER ==========")
        print("1) Cargar módulos por teclado (RF1)")
        print("2) Cargar módulos desde archivo (RF1)")
        print("3) Usar la Tabla 2 de la consigna (RF1)")
        print("4) Informe del grafo: grados, A*, ciclos y orden de migración (RF2, RF3, RF4, RF8)")
        print("5) Módulos afectados al modificar un módulo (RF3)")
        print("6) Resolver un sistema de ecuaciones (RF5)")
        print("7) Punto de equilibrio entre dos alternativas (RF6)")
        print("8) Camino mínimo en la red de distribución (RF7)")
        print("9) Ejecutar los casos de prueba")
        print("0) Salir")
        opcion = input("Opción: ").strip()

        if opcion == "1" or opcion == "2" or opcion == "3":
            if opcion == "1":
                nuevos_modulos, nueva_A = cargar_desde_teclado()
            elif opcion == "2":
                nuevos_modulos, nueva_A = cargar_desde_archivo(input("Nombre del archivo: ").strip())
            else:
                nuevos_modulos, nueva_A = cargar_grafo()
            if nuevos_modulos is not None:
                modulos, A = nuevos_modulos, nueva_A
                print("Se cargaron", len(modulos), "módulos.")

        elif opcion == "4":
            informe_grafo(modulos, A)

        elif opcion == "5":
            nombre = input("Módulo a modificar " + str(modulos) + ": ").strip().upper()
            if nombre in modulos:
                Astar = warshall(A)
                print("Quedan afectados:", modulos_afectados(Astar, modulos.index(nombre), modulos))
            else:
                print("Ese módulo no existe.")

        elif opcion == "6":
            n = int(pedir_numero("Cantidad de incógnitas (2 a 5): "))
            if n < 2 or n > 5:
                print("Error: el sistema debe ser de 2 x 2 hasta 5 x 5.")
                continue
            M = []
            B = []
            for i in range(n):
                fila = []
                for j in range(n):
                    fila.append(pedir_numero("  Coeficiente fila " + str(i + 1) + ", columna " + str(j + 1) + ": "))
                M.append(fila)
                B.append(pedir_numero("  Término independiente de la fila " + str(i + 1) + ": "))
            clasificacion, det, X, operaciones = resolver_sistema(M, B, mostrar_pasos=True)
            if clasificacion is not None:
                print("Sistema", clasificacion, "| det =", formatear(det))
                if X is not None:
                    for i in range(n):
                        print("  x" + str(i + 1), "=", formatear(X[i]))

        elif opcion == "7":
            print("Costo acumulado: C(n) = inversión inicial + costo anual * n")
            b1 = pedir_numero("Inversión inicial de la alternativa 1: ")
            a1 = pedir_numero("Costo anual de la alternativa 1: ")
            b2 = pedir_numero("Inversión inicial de la alternativa 2: ")
            a2 = pedir_numero("Costo anual de la alternativa 2: ")
            tipo, n_eq, costo = equilibrio(a1, b1, a2, b2)
            if tipo == "UNICO":
                print("Equilibrio en n =", formatear(n_eq), "años, con un costo de", formatear(costo))
            elif tipo == "PARALELAS":
                print("Las rectas son paralelas: no hay punto de equilibrio.")
            else:
                print("Las rectas coinciden: las alternativas cuestan siempre lo mismo.")

        elif opcion == "8":
            nodos, tramos = red_distribucion()
            destino = input("Destino desde D " + str(nodos) + ": ").strip().upper()
            if destino in nodos:
                d, camino, fijados = dijkstra(nodos, tramos, "D", destino, mostrar_etapas=True)
                print("Camino mínimo:", " -> ".join(camino), "=", d, "min")
            else:
                print("Ese nodo no existe.")

        elif opcion == "9":
            ejecutar_casos_de_prueba()

        elif opcion == "0":
            print("Fin del programa.")
            break

        else:
            print("Opción inválida.")


menu()
