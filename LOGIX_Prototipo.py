#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 LOGIX-ANALYZER  (prototipo de ingeniería hacia adelante) - AE4 / TIFAS 2026
 Ingeniería de Requerimientos I  +  Matemática Discreta  (Protocolo ISI26MAD09V26)
 Universidad de la Cuenca del Plata (UCP) - Corrientes
================================================================================
 Programa estructurado en funciones (un módulo matemático por requerimiento):

   RF1  cargar_grafo / cargar_desde_archivo / cargar_desde_teclado   Digrafo, matriz A
   RF2  grados_entrada_salida                                         Sumas de columnas / filas
   RF3  warshall, modulos_afectados (+ potencias booleanas de A)      Cierre transitivo A*
   RF4  detectar_ciclos                                               Diagonal de A*, CFC
   RF5  resolver_sistema                                              Gauss-Jordan, det, Rouché-Frobenius
   RF6  equilibrio                                                    Sistema 2 x 2
   RF7  dijkstra                                                      Grafo ponderado (opcional)
   RF8  orden_topologico                                              DAG (opcional)
   EXT  trazabilidad_RT, alcance_superposicion, decision_ponderada    Punto 5, Punto 1, Punto 4

 Convención del protocolo: los módulos se ordenan PED, CLI, INV, ROB, ASG, RUT,
 SEG, ENT, REP y A[i][j] = 1  <=>  el módulo i DEPENDE del módulo j.
 Montos en miles de unidades monetarias (mil u.m.).

 Uso:
     python LOGIX_Analyzer.py            -> ejecuta la batería de casos de prueba CP1..CP10
     python LOGIX_Analyzer.py --menu     -> menú interactivo (carga por teclado o archivo)
     python LOGIX_Analyzer.py --archivo grafo.txt   -> analiza un grafo leído de archivo

 Formato del archivo de entrada (RF1):
     línea 1: códigos de módulos separados por coma o espacio (máx. 15)
     líneas 2..n+1: fila i de la matriz de adyacencia (n valores 0/1 por fila)
================================================================================
"""
import heapq
import os
import sys
import tempfile

import numpy as np

MODULOS_OFICIALES = ['PED', 'CLI', 'INV', 'ROB', 'ASG', 'RUT', 'SEG', 'ENT', 'REP']

# Tabla 2 de la consigna: (X, Y) significa "X depende de Y"  (14 aristas)
ARISTAS_TABLA2 = [
    ('PED', 'CLI'), ('PED', 'INV'), ('PED', 'ASG'),
    ('INV', 'ROB'), ('ROB', 'INV'),
    ('ASG', 'RUT'), ('ASG', 'INV'),
    ('RUT', 'SEG'), ('SEG', 'ASG'),
    ('ENT', 'PED'), ('ENT', 'SEG'),
    ('REP', 'PED'), ('REP', 'ENT'), ('REP', 'INV'),
]
MAX_MODULOS = 15


# ==============================================================================
# RF1 - Cargar módulos y matriz de adyacencia (hasta 15 módulos)
# ==============================================================================
def validar_grafo(modulos, A):
    """Valida: n <= 15, códigos únicos, A cuadrada n x n con valores en {0, 1}."""
    n = len(modulos)
    if n == 0:
        raise ValueError("Debe haber al menos un módulo.")
    if n > MAX_MODULOS:
        raise ValueError(f"El número máximo de módulos permitido es {MAX_MODULOS}.")
    if len(set(modulos)) != n:
        raise ValueError("Los códigos de módulo deben ser únicos.")
    if A.shape != (n, n):
        raise ValueError(f"La matriz debe ser {n} x {n}; se recibió {A.shape[0]} x {A.shape[1]}.")
    if not np.isin(A, (0, 1)).all():
        raise ValueError("La matriz de adyacencia sólo admite valores 0 o 1.")


def cargar_grafo(modulos_custom=None, matriz_custom=None):
    """[RF1] Devuelve (modulos, A). Sin argumentos carga la Tabla 2 oficial (9 módulos)."""
    if modulos_custom is not None and matriz_custom is not None:
        modulos = list(modulos_custom)
        A = np.array(matriz_custom, dtype=int)
    else:
        modulos = list(MODULOS_OFICIALES)
        A = np.zeros((len(modulos), len(modulos)), dtype=int)
        for x, y in ARISTAS_TABLA2:
            A[modulos.index(x), modulos.index(y)] = 1
    validar_grafo(modulos, A)
    return modulos, A


def cargar_desde_archivo(ruta):
    """[RF1] Lee módulos y matriz desde un archivo de texto (formato en el encabezado)."""
    with open(ruta, encoding='utf-8') as f:
        lineas = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    modulos = lineas[0].replace(',', ' ').split()
    filas = [[int(v) for v in l.replace(',', ' ').split()] for l in lineas[1:]]
    return cargar_grafo(modulos, filas)


def cargar_desde_teclado(input_fn=input):
    """[RF1] Carga interactiva. `input_fn` es inyectable para poder probarla sin teclado."""
    modulos = input_fn("Códigos de los módulos (separados por espacio, máx. 15): ").replace(',', ' ').split()
    filas = []
    for m in modulos:
        txt = input_fn(f"Fila de '{m}' ({len(modulos)} valores 0/1): ")
        filas.append([int(v) for v in txt.replace(',', ' ').split()])
    return cargar_grafo(modulos, filas)


def guardar_en_archivo(modulos, A, ruta):
    """Escribe un grafo en el formato aceptado por cargar_desde_archivo."""
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(' '.join(modulos) + '\n')
        for fila in A:
            f.write(' '.join(str(int(v)) for v in fila) + '\n')


# ==============================================================================
# RF2 - Grados de entrada y salida
# ==============================================================================
def grados_entrada_salida(A, modulos):
    """[RF2] deg+(i) = suma de la fila i; deg-(j) = suma de la columna j."""
    out_deg = A.sum(axis=1)
    in_deg = A.sum(axis=0)
    return {m: {'salida': int(out_deg[i]), 'entrada': int(in_deg[i])} for i, m in enumerate(modulos)}


# ==============================================================================
# RF3 - Alcanzabilidad A* (Warshall) y módulos afectados
# ==============================================================================
def producto_booleano(X, Y):
    """Producto booleano X (.) Y : z_ij = OR_k (x_ik AND y_kj)."""
    return ((X.astype(int) @ Y.astype(int)) > 0).astype(int)


def potencias_booleanas(A):
    """Devuelve [A, A^2, ..., A^n] con producto booleano (A^k: caminos de longitud k)."""
    n = len(A)
    pot, P = [A.copy()], A.copy()
    for _ in range(n - 1):
        P = producto_booleano(P, A)
        pot.append(P)
    return pot


def alcanzabilidad_por_potencias(A):
    """A* = A v A^2 v ... v A^n  (verificación independiente de Warshall)."""
    R = np.zeros_like(A)
    for P in potencias_booleanas(A):
        R = np.logical_or(R, P).astype(int)
    return R


def warshall(A):
    """[RF3] Cierre transitivo por el algoritmo de Warshall. Complejidad O(n^3)."""
    n = len(A)
    R = A.copy().astype(int)
    for k in range(n):
        for i in range(n):
            if R[i, k]:
                for j in range(n):
                    if R[k, j]:
                        R[i, j] = 1
    return R


def modulos_afectados(Astar, idx_j, modulos):
    """[RF3] Si se modifica el módulo j, quedan afectados los i con A*[i, j] = 1 (columna j)."""
    return [modulos[i] for i in range(len(modulos)) if Astar[i, idx_j] == 1]


# ==============================================================================
# RF4 - Ciclos y componentes fuertemente conexas
# ==============================================================================
def detectar_ciclos(Astar, modulos):
    """[RF4] Módulos con A*[i,i] = 1 y sus componentes fuertemente conexas
    (i y j en la misma CFC  <=>  A*[i,j] = A*[j,i] = 1)."""
    n = len(modulos)
    en_ciclo = [modulos[i] for i in range(n) if Astar[i, i] == 1]
    cfc, vistos = [], set()
    for i in range(n):
        if i in vistos or Astar[i, i] != 1:
            continue
        comp = [i] + [j for j in range(i + 1, n) if Astar[i, j] and Astar[j, i]]
        vistos.update(comp)
        cfc.append([modulos[k] for k in comp])
    return en_ciclo, cfc


# ==============================================================================
# RF5 - Sistemas lineales hasta 5 x 5 (Gauss-Jordan con pivoteo parcial)
# ==============================================================================
def resolver_sistema(M, B, registrar_pasos=False):
    """[RF5] Resuelve M X = B (M cuadrada de orden 2..5).

    Clasificación por Rouché-Frobenius con rangos:
      rango(M) = rango([M|B]) = n  -> COMPATIBLE DETERMINADO (solución única)
      rango(M) = rango([M|B]) < n  -> COMPATIBLE INDETERMINADO (infinitas soluciones)
      rango(M) < rango([M|B])      -> INCOMPATIBLE (sin solución)

    Devuelve dict con: det, clasificacion, x (None si no hay solución única), pasos.
    """
    M = np.array(M, dtype=float)
    B = np.array(B, dtype=float).reshape(-1, 1)
    n = M.shape[0]
    if M.shape[0] != M.shape[1] or B.shape[0] != n:
        raise ValueError("M debe ser cuadrada y B tener n componentes.")
    if not 2 <= n <= 5:
        raise ValueError("El sistema debe ser de orden 2 a 5.")

    det = float(np.linalg.det(M))
    aug = np.hstack([M, B])
    r_M = int(np.linalg.matrix_rank(M))
    r_A = int(np.linalg.matrix_rank(aug))
    pasos = []

    if r_M < r_A:
        clasif = "INCOMPATIBLE"
    elif r_M < n:
        clasif = "COMPATIBLE INDETERMINADO"
    else:
        clasif = "COMPATIBLE DETERMINADO"

    x = None
    if clasif == "COMPATIBLE DETERMINADO":
        for i in range(n):
            p = i + int(np.argmax(np.abs(aug[i:, i])))     # pivoteo parcial
            if p != i:
                aug[[i, p]] = aug[[p, i]]
                if registrar_pasos:
                    pasos.append((f"F{i+1} <-> F{p+1}", aug.copy()))
            aug[i] = aug[i] / aug[i, i]
            if registrar_pasos:
                pasos.append((f"F{i+1} <- F{i+1} / pivote", aug.copy()))
            for k in range(n):
                if k != i and abs(aug[k, i]) > 1e-12:
                    aug[k] = aug[k] - aug[k, i] * aug[i]
            if registrar_pasos:
                pasos.append((f"ceros en columna {i+1}", aug.copy()))
        x = aug[:, -1].copy()
    return {'det': det, 'clasificacion': clasif, 'x': x, 'rangos': (r_M, r_A), 'pasos': pasos}


# ==============================================================================
# RF6 - Punto de equilibrio entre dos alternativas de costo lineal
# ==============================================================================
def equilibrio(a1, b1, a2, b2):
    """[RF6] C1(n) = b1 + a1 n ; C2(n) = b2 + a2 n  (a = costo anual, b = inversión inicial).
    Sistema 2x2:  C - a1 n = b1 ; C - a2 n = b2.
    Devuelve ('UNICO', n, C) | ('PARALELAS', None, None) | ('COINCIDENTES', None, None)."""
    if abs(a1 - a2) < 1e-12:
        return ('COINCIDENTES', None, None) if abs(b1 - b2) < 1e-12 else ('PARALELAS', None, None)
    n = (b2 - b1) / (a1 - a2)
    return ('UNICO', n, b1 + a1 * n)


# ==============================================================================
# RF7 - Camino mínimo (Dijkstra) en grafo ponderado no dirigido
# ==============================================================================
def dijkstra(nodos, aristas, origen, destino, registrar_etapas=False):
    """[RF7] Devuelve (distancia, camino, etapas). Si no hay camino: (inf, [], etapas)."""
    adj = {n: [] for n in nodos}
    for u, v, w in aristas:
        if w < 0:
            raise ValueError("Dijkstra requiere pesos no negativos.")
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = {n: float('inf') for n in nodos}
    padre = {n: None for n in nodos}
    dist[origen] = 0
    fijos, etapas, pq = [], [], [(0, origen)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in fijos or d > dist[u]:
            continue
        fijos.append(u)
        for v, w in adj[u]:
            if v not in fijos and d + w < dist[v]:
                dist[v] = d + w
                padre[v] = u
                heapq.heappush(pq, (dist[v], v))
        if registrar_etapas:
            etapas.append((u, d, dict(dist), list(fijos)))
        if u == destino:
            break
    if dist[destino] == float('inf'):
        return float('inf'), [], etapas
    camino, cur = [], destino
    while cur is not None:
        camino.append(cur)
        cur = padre[cur]
    return dist[destino], camino[::-1], etapas


# ==============================================================================
# RF8 - Orden topológico (algoritmo de Kahn) para un grafo acíclico
# ==============================================================================
def orden_topologico(A, modulos):
    """[RF8] Orden de migración: j se migra antes que i si A[i][j] = 1 (i depende de j).
    Devuelve (orden, mensaje). Si hay ciclos no existe orden topológico."""
    if np.any(np.diag(warshall(A)) == 1):
        return None, "El grafo contiene dependencias circulares (ciclos); no existe orden topológico."
    n = len(modulos)
    pendientes = A.sum(axis=1).astype(int)       # dependencias aún no migradas de cada módulo
    restantes, orden = list(range(n)), []
    while restantes:
        listos = [i for i in restantes if pendientes[i] == 0]
        elegido = listos[0]                      # desempate por orden oficial de módulos
        orden.append(modulos[elegido])
        restantes.remove(elegido)
        for i in restantes:
            if A[i, elegido] == 1:
                pendientes[i] -= 1
    return orden, "Orden topológico calculado."


def verificar_orden(A, modulos, orden):
    """Comprueba que cada módulo aparece DESPUÉS de todos aquellos de los que depende."""
    pos = {m: k for k, m in enumerate(orden)}
    return all(pos[modulos[j]] < pos[modulos[i]]
               for i in range(len(modulos)) for j in range(len(modulos)) if A[i, j])


# ==============================================================================
# EXTRAS - Trazabilidad (Punto 5), alcance/superposición (Punto 1), decisión (Punto 4)
# ==============================================================================
def trazabilidad_RT(RC, CT):
    """RT = RC (.) CT (producto booleano). Devuelve (RT, requerimientos_sin_prueba, componentes_sin_prueba)."""
    RC, CT = np.array(RC, dtype=int), np.array(CT, dtype=int)
    RT = producto_booleano(RC, CT)
    req_sin = [f"R{i+1}" for i in range(RT.shape[0]) if not RT[i].any()]
    comp_sin = [f"C{k+1}" for k in range(CT.shape[0]) if not CT[k].any()]
    return RT, req_sin, comp_sin


def alcance_superposicion(S):
    """a = S . u (alcance directo) y  S . S^T (superposición entre solicitudes)."""
    S = np.array(S, dtype=int)
    return S @ np.ones(S.shape[1], dtype=int), S @ S.T


def decision_ponderada(P, w):
    """v = P . w con w_i >= 0 y suma(w) = 1."""
    P, w = np.array(P, dtype=float), np.array(w, dtype=float)
    if (w < 0).any() or abs(w.sum() - 1) > 1e-9:
        raise ValueError("Los pesos deben ser no negativos y sumar 1.")
    return P @ w


# ==============================================================================
# Informe de un grafo (usado por el menú y por --archivo)
# ==============================================================================
def informe_grafo(modulos, A):
    Astar = warshall(A)
    print("\nGrados (salida / entrada):")
    for m, g in grados_entrada_salida(A, modulos).items():
        print(f"  {m}: deg+ = {g['salida']}   deg- = {g['entrada']}")
    print(f"\nPares alcanzables en A*: {int(Astar.sum())}")
    en_ciclo, cfc = detectar_ciclos(Astar, modulos)
    print(f"Módulos en ciclos: {en_ciclo or 'ninguno'}   CFC: {cfc}")
    for j, m in enumerate(modulos):
        print(f"  Si se modifica {m}: afecta a {modulos_afectados(Astar, j, modulos)}")
    orden, msg = orden_topologico(A, modulos)
    print(f"\nOrden de migración: {orden if orden else msg}")


def menu():
    modulos, A = cargar_grafo()
    while True:
        print("\n--- LOGIX-ANALYZER ---\n1) Cargar por teclado\n2) Cargar desde archivo\n"
              "3) Usar Tabla 2 oficial\n4) Informe del grafo actual\n5) Resolver sistema lineal\n"
              "6) Punto de equilibrio\n7) Camino mínimo (red Tabla 5)\n0) Salir")
        op = input("Opción: ").strip()
        try:
            if op == '1':
                modulos, A = cargar_desde_teclado()
            elif op == '2':
                modulos, A = cargar_desde_archivo(input("Ruta del archivo: ").strip())
            elif op == '3':
                modulos, A = cargar_grafo()
            elif op == '4':
                informe_grafo(modulos, A)
            elif op == '5':
                n = int(input("Orden n (2..5): "))
                M = [[float(v) for v in input(f"Fila {i+1} de M: ").split()] for i in range(n)]
                B = [float(v) for v in input("Vector B: ").split()]
                r = resolver_sistema(M, B)
                print(r['clasificacion'], '| det =', round(r['det'], 6), '| x =', r['x'])
            elif op == '6':
                a1, b1, a2, b2 = (float(input(t)) for t in
                                  ("Costo anual alt.1: ", "Inversión alt.1: ", "Costo anual alt.2: ", "Inversión alt.2: "))
                print(equilibrio(a1, b1, a2, b2))
            elif op == '7':
                d, cam, _ = dijkstra(*red_distribucion(), 'D', input("Destino (H1,H2,Z1,Z2,Z3): ").strip())
                print(f"{d} min por {cam}")
            elif op == '0':
                break
        except (ValueError, IndexError, KeyError) as e:
            print("Error de entrada:", e)


def red_distribucion():
    """Tabla 5 de la consigna (minutos). Devuelve (nodos, aristas)."""
    nodos = ['D', 'H1', 'H2', 'Z1', 'Z2', 'Z3']
    aristas = [('D', 'H1', 8), ('D', 'H2', 5), ('H1', 'H2', 2), ('H1', 'Z1', 6), ('H2', 'Z1', 10),
               ('H2', 'Z2', 7), ('Z1', 'Z2', 3), ('Z1', 'Z3', 9), ('Z2', 'Z3', 4)]
    return nodos, aristas


# ==============================================================================
# BATERÍA DE CASOS DE PRUEBA (CP1 a CP10)
# ==============================================================================
def _resultado(nombre, ok):
    print(f"VERIFICACIÓN {nombre}: {'[OK]' if ok else '[ERROR]'}")
    return ok


def ejecutar_casos_de_prueba():
    resultados = []
    print("=" * 80 + "\n BATERÍA DE CASOS DE PRUEBA LOGIX-ANALYZER (CP1 a CP10)\n" + "=" * 80)

    # ---- CP1: Tabla 2 completa ------------------------------------------------
    print("\n--- CP1: Tabla 2 completa (9 módulos, 14 aristas) ---")
    modulos, A = cargar_grafo()
    g = grados_entrada_salida(A, modulos)
    Astar = warshall(A)
    en_ciclo, cfc = detectar_ciclos(Astar, modulos)
    afect_inv = modulos_afectados(Astar, modulos.index('INV'), modulos)
    print("Grados (salida/entrada):", {m: (v['salida'], v['entrada']) for m, v in g.items()})
    print(f"Aristas: {int(A.sum())} | pares alcanzables en A*: {int(Astar.sum())}")
    print(f"Módulos en ciclo: {en_ciclo}\nCFC: {cfc}")
    print(f"Modificar INV afecta a {len(afect_inv)} módulos: {afect_inv}")
    esperados = {'PED': (3, 2), 'CLI': (0, 1), 'INV': (1, 4), 'ROB': (1, 1), 'ASG': (2, 2),
                 'RUT': (1, 1), 'SEG': (1, 2), 'ENT': (2, 1), 'REP': (3, 0)}
    ok = (all((g[m]['salida'], g[m]['entrada']) == esperados[m] for m in modulos)
          and int(A.sum()) == 14 and int(Astar.sum()) == 40
          and set(en_ciclo) == {'INV', 'ROB', 'ASG', 'RUT', 'SEG'}
          and sorted(map(sorted, cfc)) == [['ASG', 'RUT', 'SEG'], ['INV', 'ROB']]
          and len(afect_inv) == 8 and np.array_equal(Astar, alcanzabilidad_por_potencias(A)))
    resultados.append(_resultado("CP1", ok))

    # ---- CP2: grafo reestructurado G' ----------------------------------------
    print("\n--- CP2: G' (sin INV->ROB y sin SEG->ASG) ---")
    Ap = A.copy()
    Ap[modulos.index('INV'), modulos.index('ROB')] = 0
    Ap[modulos.index('SEG'), modulos.index('ASG')] = 0
    Apstar = warshall(Ap)
    orden, msg = orden_topologico(Ap, modulos)
    print(f"Aristas: {int(Ap.sum())} | pares en A'*: {int(Apstar.sum())} | diag(A'*) = {[int(v) for v in np.diag(Apstar)]}")
    print(f"Orden de migración (RF8): {orden}")
    ok = (int(Ap.sum()) == 12 and int(Apstar.sum()) == 23 and not np.diag(Apstar).any()
          and orden is not None and verificar_orden(Ap, modulos, orden)
          and orden == ['CLI', 'INV', 'ROB', 'SEG', 'RUT', 'ASG', 'PED', 'ENT', 'REP'])
    resultados.append(_resultado("CP2", ok))

    # ---- CP3: Tabla 6 por Gauss-Jordan ---------------------------------------
    print("\n--- CP3: Sistema de costos 3x3 (Tabla 6) ---")
    M = [[2, 3, 1], [1, 2, 2], [3, 1, 2]]
    B = [119, 122, 126]
    r = resolver_sistema(M, B, registrar_pasos=True)
    x, y, z = r['x']
    I_B = float(np.array([4, 6, 3]) @ r['x'])
    print(f"det(M) = {r['det']:.1f} -> {r['clasificacion']}  (rangos {r['rangos']})")
    print(f"x = {x:.1f}, y = {y:.1f}, z = {z:.1f} mil u.m.   I_B = {I_B:.1f} mil u.m.")
    print(f"Operaciones elementales registradas: {len(r['pasos'])}")
    ok = (abs(r['det'] - 11) < 1e-9 and r['clasificacion'] == "COMPATIBLE DETERMINADO"
          and np.allclose(r['x'], [12, 20, 35]) and abs(I_B - 273) < 1e-9
          and np.allclose(np.array(M) @ r['x'], B))
    resultados.append(_resultado("CP3", ok))

    # ---- CP4: puntos de equilibrio -------------------------------------------
    print("\n--- CP4: equilibrios (C_A = 110n ; C_B = 273 + 45n ; C_C = 420 + 40n) ---")
    eAB, eAC, eBC = equilibrio(110, 0, 45, 273), equilibrio(110, 0, 40, 420), equilibrio(45, 273, 40, 420)
    for nom, e in (("A-B", eAB), ("A-C", eAC), ("B-C", eBC)):
        print(f"  {nom}: n = {e[1]:.2f} años, costo = {e[2]:.1f} mil u.m.")
    ok = (abs(eAB[1] - 4.2) < 1e-9 and abs(eAB[2] - 462) < 1e-9 and abs(eAC[1] - 6) < 1e-9
          and abs(eAC[2] - 660) < 1e-9 and abs(eBC[1] - 29.4) < 1e-9 and abs(eBC[2] - 1596) < 1e-9)
    resultados.append(_resultado("CP4", ok))

    # ---- CP5: Dijkstra (Tabla 5) ---------------------------------------------
    print("\n--- CP5: Dijkstra D -> Z3 (Tabla 5) y corredor aéreo ---")
    nodos, aristas = red_distribucion()
    d1, c1, et1 = dijkstra(nodos, aristas, 'D', 'Z3', registrar_etapas=True)
    d2, c2, et2 = dijkstra(nodos, aristas + [('D', 'Z3', 14)], 'D', 'Z3', registrar_etapas=True)
    dfija = 8 + 6 + 9
    print(f"Ruta fija legacy D-H1-Z1-Z3 = {dfija} min")
    for u, d, dist, fijos in et1:
        print(f"  etapa: fija {u} (d={d})  S={fijos}")
    print(f"Terrestre mínimo: {d1} min por {c1}")
    print(f"Con corredor D-Z3 (14): {d2} min por {c2}")
    ok = (d1 == 16 and c1 == ['D', 'H2', 'Z2', 'Z3'] and d2 == 14 and c2 == ['D', 'Z3']
          and [e[0] for e in et1] == ['D', 'H2', 'H1', 'Z2', 'Z1', 'Z3'])
    resultados.append(_resultado("CP5", ok))

    # ---- CP6: casos límite -----------------------------------------------------
    print("\n--- CP6: casos límite ---")
    indet = resolver_sistema([[1, 2, 3], [2, 4, 6], [1, 1, 1]], [1, 2, 3])
    incomp = resolver_sistema([[1, 2, 3], [2, 4, 6], [1, 1, 1]], [1, 3, 3])
    print(f"  det = 0 con filas proporcionales y B consistente   -> {indet['clasificacion']}")
    print(f"  det = 0 con filas proporcionales y B inconsistente -> {incomp['clasificacion']}")
    par = equilibrio(50, 100, 50, 200)
    coin = equilibrio(50, 100, 50, 100)
    print(f"  rectas paralelas -> {par[0]} | rectas coincidentes -> {coin[0]}")
    _, msg_ciclo = orden_topologico(A, modulos)
    print(f"  RF8 sobre el grafo cíclico G: {msg_ciclo}")
    d_inf, c_inf, _ = dijkstra(['X', 'Y', 'Z'], [('X', 'Y', 1)], 'X', 'Z')
    print(f"  Dijkstra a nodo inalcanzable -> distancia {d_inf}, camino {c_inf}")
    try:
        cargar_grafo(['A'] * 16, np.zeros((16, 16), dtype=int))
        lim = False
    except ValueError as e:
        lim = True
        print(f"  16 módulos -> ValueError: {e}")
    try:
        cargar_grafo(['A', 'B'], [[0, 2], [0, 0]])
        val = False
    except ValueError as e:
        val = True
        print(f"  matriz con valor 2 -> ValueError: {e}")
    ok = (indet['clasificacion'] == "COMPATIBLE INDETERMINADO" and incomp['clasificacion'] == "INCOMPATIBLE"
          and par[0] == 'PARALELAS' and coin[0] == 'COINCIDENTES' and "circulares" in msg_ciclo
          and d_inf == float('inf') and c_inf == [] and lim and val)
    resultados.append(_resultado("CP6", ok))

    # ---- CP7: trazabilidad -------------------------------------------------------
    print("\n--- CP7: trazabilidad booleana RT = RC (.) CT ---")
    RC = [[1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    CT = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]
    RT, req_sin, comp_sin = trazabilidad_RT(RC, CT)
    print(RT)
    print(f"Requerimientos sin prueba: {req_sin} | componentes sin prueba: {comp_sin}")
    CT2 = [fila + [1 if k == 3 else 0] for k, fila in enumerate(CT)]      # se agrega T4 que verifica C4
    _, req_sin2, _ = trazabilidad_RT(RC, CT2)
    print(f"Tras agregar T4 (C4 -> T4): requerimientos sin prueba = {req_sin2}")
    ok = (req_sin == ['R4'] and comp_sin == ['C4'] and req_sin2 == []
          and np.array_equal(RT, [[1, 0, 0], [1, 1, 0], [0, 0, 1], [0, 0, 0]]))
    resultados.append(_resultado("CP7", ok))

    # ---- CP8: alcance y superposición (Punto 1) --------------------------------
    print("\n--- CP8: matriz de incidencia S (Tabla 3): a = S.u y S.S^T ---")
    S = [[1, 0, 0, 0, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 0],
         [0, 0, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 1, 1, 0, 1]]
    a, SS = alcance_superposicion(S)
    print("a =", [int(v) for v in a], "| m36 =", int(SS[2, 5]))
    ok = list(a) == [2, 2, 4, 2, 1, 4] and SS[2, 5] == 3 and SS[0, 2] == 1 and SS[4, 5] == 1 and SS[3].sum() == 2
    resultados.append(_resultado("CP8", ok))

    # ---- CP9: matriz de decisión (Punto 4) ---------------------------------------
    print("\n--- CP9: decisión ponderada v = P.w y sensibilidad ---")
    P = [[1, 2, 1, 1, 5], [5, 4, 4, 4, 5], [3, 2, 5, 5, 1]]
    esc = {'base': [.25, .25, .20, .15, .15], 'sens.1': [.40, .20, .15, .10, .15],
           'sens.2 (proporcional)': [.40, .20, .16, .12, .12], 'adverso': [.10, .10, .30, .40, .10]}
    res = {k: decision_ponderada(P, w) for k, w in esc.items()}
    for k, v in res.items():
        print(f"  {k:22s} A={v[0]:.2f}  B={v[1]:.2f}  C={v[2]:.2f}")
    try:
        decision_ponderada(P, [.5, .5, .5, 0, 0])
        w_ok = False
    except ValueError:
        w_ok = True
    ok = (np.allclose(res['base'], [1.85, 4.40, 3.15]) and np.allclose(res['sens.1'], [1.80, 4.55, 3.00])
          and np.allclose(res['sens.2 (proporcional)'], [1.68, 4.52, 3.12])
          and np.allclose(res['adverso'], [1.50, 4.20, 4.10]) and all(v.argmax() == 1 for v in res.values()) and w_ok)
    resultados.append(_resultado("CP9", ok))

    # ---- CP10: carga por archivo / teclado (RF1) y variante con bus ------------------
    print("\n--- CP10: RF1 desde archivo y teclado; G' con bus de eventos como vértice ---")
    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, 'grafo.txt')
        guardar_en_archivo(modulos, A, ruta)
        m_f, A_f = cargar_desde_archivo(ruta)
    ok_arch = m_f == modulos and np.array_equal(A_f, A)
    entradas = iter(['X Y Z', '0 1 0', '0 0 1', '0 0 0'])
    m_t, A_t = cargar_desde_teclado(lambda _prompt: next(entradas))
    ok_tec = m_t == ['X', 'Y', 'Z'] and int(warshall(A_t).sum()) == 3
    mod_b = modulos + ['BUS']
    Ab = np.zeros((10, 10), dtype=int)
    Ab[:9, :9] = Ap
    for m in ('SEG', 'ASG', 'ROB', 'INV'):          # publican o se suscriben al bus; el bus no depende de nadie
        Ab[mod_b.index(m), 9] = 1
    Abstar = warshall(Ab)
    print(f"  archivo OK: {ok_arch} | teclado OK: {ok_tec}")
    print(f"  G' + vértice BUS: diag(A*) nula = {not np.diag(Abstar).any()}, pares alcanzables = {int(Abstar.sum())}")
    ok = ok_arch and ok_tec and not np.diag(Abstar).any()
    resultados.append(_resultado("CP10", ok))

    print("\n" + "=" * 80)
    if all(resultados):
        print(f" RESULTADO GLOBAL: {len(resultados)} de {len(resultados)} casos de prueba aprobados")
    else:
        print(f" RESULTADO GLOBAL: {sum(resultados)} de {len(resultados)} aprobados -> HAY ERRORES")
    print("=" * 80)
    return all(resultados)


if __name__ == "__main__":
    if '--menu' in sys.argv:
        menu()
    elif '--archivo' in sys.argv:
        mods, Aa = cargar_desde_archivo(sys.argv[sys.argv.index('--archivo') + 1])
        informe_grafo(mods, Aa)
    else:
        sys.exit(0 if ejecutar_casos_de_prueba() else 1)
