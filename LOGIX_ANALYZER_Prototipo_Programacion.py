import numpy as np

"""
================================================================================
 LOGIX-ANALYZER PROTOTYPE (VERSIÓN CORREGIDA SEGÚN PROTOCOLO AE4 2026)
 Asignaturas: Ingeniería de Requerimientos I, Matemática Discreta y Programación I
 Universidad de la Cuenca del Plata (UCP - Corrientes)
================================================================================
"""

# Módulos en el orden oficial de la convención del protocolo:
MODULOS_OFICIALES = ['PED', 'CLI', 'INV', 'ROB', 'ASG', 'RUT', 'SEG', 'ENT', 'REP']

# ==============================================================================
# RF1: Cargar módulos y matriz de adyacencia (hasta 15 módulos)
# ==============================================================================
def cargar_grafo(modulos_custom=None, matriz_custom=None):
    """
    [RF1] Carga los módulos y la matriz de adyacencia del digrafo.
    Apoyo matemático: Matriz de adyacencia A(n x n) con a_ij in {0, 1}.
    """
    if modulos_custom is not None and matriz_custom is not None:
        modulos = list(modulos_custom)
        A = np.array(matriz_custom, dtype=int)
    else:
        modulos = list(MODULOS_OFICIALES)
        n = len(modulos)
        A = np.zeros((n, n), dtype=int)
        
        # Aristas de la Tabla 2 del protocolo (X -> Y: X depende de Y)
        # PED(0) -> CLI(1), INV(2), ASG(4)
        A[0, 1] = 1; A[0, 2] = 1; A[0, 4] = 1
        # CLI(1) -> ninguno
        # INV(2) -> ROB(3)
        A[2, 3] = 1
        # ROB(3) -> INV(2)
        A[3, 2] = 1
        # ASG(4) -> RUT(5), INV(2)
        A[4, 5] = 1; A[4, 2] = 1
        # RUT(5) -> SEG(6)
        A[5, 6] = 1
        # SEG(6) -> ASG(4)
        A[6, 4] = 1
        # ENT(7) -> PED(0), SEG(6)
        A[7, 0] = 1; A[7, 6] = 1
        # REP(8) -> PED(0), ENT(7), INV(2)
        A[8, 0] = 1; A[8, 7] = 1; A[8, 2] = 1

    if len(modulos) > 15:
        raise ValueError("El número máximo de módulos permitido es 15.")
    return modulos, A

# ==============================================================================
# RF2: Grados de Entrada y Salida
# ==============================================================================
def grados_entrada_salida(A, modulos):
    """
    [RF2] Calcula e informa grados de salida (suma de filas) y entrada (suma de columnas).
    Apoyo matemático: deg_out(v_i) = sum_j a_ij, deg_in(v_j) = sum_i a_ij.
    """
    out_deg = np.sum(A, axis=1)
    in_deg = np.sum(A, axis=0)
    
    res = {}
    for idx, m in enumerate(modulos):
        res[m] = {'salida': int(out_deg[idx]), 'entrada': int(in_deg[idx])}
    return res

# ==============================================================================
# RF3: Matriz de Alcanzabilidad A* (Warshall) y Módulos Afectados
# ==============================================================================
def warshall(A):
    """
    [RF3] Algoritmo de Warshall para calcular el cierre transitivo (Matriz de Alcanzabilidad A*).
    Apoyo matemático: A* = A v A^2 v ... v A^n en álgebra booleana.
    """
    n = len(A)
    Astar = A.copy().astype(int)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                Astar[i, j] = Astar[i, j] or (Astar[i, k] and Astar[k, j])
    return Astar

def modulos_afectados(Astar, idx_j, modulos):
    """
    [RF3] Dado un módulo j, lista los módulos i que se ven afectados si j se modifica.
    Apoyo matemático: Lectura por columna j de A*: i tal que A*[i, j] == 1.
    """
    afectados = [modulos[i] for i in range(len(modulos)) if Astar[i, idx_j] == 1]
    return afectados

# ==============================================================================
# RF4: Detección de Ciclos y Componentes Fuertemente Conexas
# ==============================================================================
def detectar_ciclos(Astar, modulos):
    """
    [RF4] Detecta e informa módulos involucrados en ciclos (a*[i,i] == 1) y
    agrupa en componentes fuertemente conexas.
    Apoyo matemático: Diagonal de A* no nula; a*[i,j] = a*[j,i] = 1.
    """
    n = len(modulos)
    en_ciclo = [modulos[i] for i in range(n) if Astar[i, i] == 1]
    
    # Agrupar componentes fuertemente conexas
    cfc = []
    visitados = set()
    for i in range(n):
        if i not in visitados and Astar[i, i] == 1:
            comp = [modulos[i]]
            visitados.add(i)
            for j in range(i + 1, n):
                if Astar[j, j] == 1 and Astar[i, j] == 1 and Astar[j, i] == 1:
                    comp.append(modulos[j])
                    visitados.add(j)
            cfc.append(comp)
            
    return en_ciclo, cfc

# ==============================================================================
# RF5: Resolución de Sistemas 3x3 a 5x5 por Gauss-Jordan con Pivoteo
# ==============================================================================
def resolver_sistema(M, B):
    """
    [RF5] Resuelve M*X = B mediante eliminación de Gauss-Jordan con pivoteo parcial.
    Apoyo matemático: Teorema de Rouché-Frobenius y determinante det(M).
    """
    M_arr = np.array(M, dtype=float)
    B_arr = np.array(B, dtype=float).reshape(-1, 1)
    n = len(M_arr)
    
    det_M = np.linalg.det(M_arr)
    
    # Construir matriz aumentada
    aug = np.hstack([M_arr, B_arr])
    
    # Gauss-Jordan con pivoteo
    for i in range(n):
        # Pivoteo parcial
        max_row = i + np.argmax(np.abs(aug[i:, i]))
        if abs(aug[max_row, i]) < 1e-9:
            continue
        aug[[i, max_row]] = aug[[max_row, i]]
        
        # Normalizar fila
        aug[i] = aug[i] / aug[i, i]
        
        # Eliminar otras filas
        for k in range(n):
            if k != i:
                factor = aug[k, i]
                aug[k] -= factor * aug[i]
                
    x = aug[:, -1]
    
    clasificacion = "Compatible Determinado" if abs(det_M) > 1e-5 else "Incompatible o Indeterminado"
    return det_M, x, clasificacion

# ==============================================================================
# RF6: Punto de Equilibrio Económico (Sistemas 2x2)
# ==============================================================================
def equilibrio(a1, b1, a2, b2):
    """
    [RF6] Resuelve C1(n) = C2(n) => b1 + a1*n = b2 + a2*n.
    Apoyo matemático: Intersección de rectas en R^2.
    """
    if abs(a1 - a2) < 1e-9:
        return None  # Paralelas
    n_eq = (b2 - b1) / (a1 - a2)
    c_eq = b1 + a1 * n_eq
    return n_eq, c_eq

# ==============================================================================
# RF7: Algoritmo de Dijkstra para Rutas Máximas / Mínimas (Opcional)
# ==============================================================================
def dijkstra(nodos, aristas, origen, destino):
    """
    [RF7] Camino mínimo en grafo ponderado no dirigido.
    Apoyo matemático: Algoritmo de Dijkstra sobre matriz de pesos W.
    """
    import heapq
    adj = {n: [] for n in nodos}
    for u, v, w in aristas:
        adj[u].append((v, w))
        adj[v].append((u, w))
        
    dist = {n: float('inf') for n in nodos}
    parent = {n: None for n in nodos}
    dist[origen] = 0
    pq = [(0, origen)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == destino:
            break
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))
                
    path = []
    curr = destino
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return dist[destino], path

# ==============================================================================
# RF8: Orden Topológico para Grafo Acíclico (Opcional)
# ==============================================================================
def orden_topologico(A, modulos):
    """
    [RF8] Propone un orden de migración si el grafo es acíclico.
    Apoyo matemático: Orden topológico sobre Digrafo Acíclico Dirigido (DAG).
    """
    Astar = warshall(A)
    # Verificar si es acíclico
    if np.any(np.diag(Astar) == 1):
        return None, "El grafo contiene dependencias circulares (ciclos); no existe orden topológico."
        
    n = len(modulos)
    in_degree = np.sum(A, axis=0) # sum over rows gives who depends on me vs axis=1 sum over cols
    # Attention: A[i, j] = 1 if i depends on j.
    # Therefore, module i can be migrated ONLY AFTER module j is already migrated!
    # So in_degree_mig = sum_j A[i, j] (how many modules i depends on).
    dep_count = np.sum(A, axis=1) # number of unsatisfied dependencies for module i
    
    orden = []
    restantes = list(range(n))
    
    while restantes:
        candidatos = [i for i in restantes if dep_count[i] == 0]
        if not candidatos:
            return None, "Error en ordenamiento topológico."
        # Elegir el primer candidato
        elem = candidatos[0]
        orden.append(modulos[elem])
        restantes.remove(elem)
        # Reducir dependencias de los que dependían de elem
        for i in restantes:
            if A[i, elem] == 1:
                dep_count[i] -= 1
                
    return orden, "Orden topológico calculado con éxito."

# ==============================================================================
# BATERÍA DE CASOS DE PRUEBA OFICIALES (CP1 a CP7)
# ==============================================================================
def ejecutar_casos_de_prueba():
    print("=" * 80)
    print(" EJECUTANDO BATERÍA DE CASOS DE PRUEBA OFICIALES (CP1 A CP7)")
    print("=" * 80)
    
    # --------------------------------------------------------------------------
    # CP1: Tabla 2 completa (9 módulos)
    # --------------------------------------------------------------------------
    print("\n--- [CP1] Tabla 2 Completa (9 Módulos) ---")
    modulos, A = cargar_grafo()
    grados = grados_entrada_salida(A, modulos)
    Astar = warshall(A)
    en_ciclo, cfc = detectar_ciclos(Astar, modulos)
    afectados_inv = modulos_afectados(Astar, modulos.index('INV'), modulos)
    total_ones = np.sum(Astar)
    
    print(f"Grados (In/Out): INV in={grados['INV']['entrada']} out={grados['INV']['salida']}; REP in={grados['REP']['entrada']} out={grados['REP']['salida']}")
    print(f"Pares alcanzables en A*: {total_ones} (Esperado: 40)")
    print(f"Módulos en ciclo: {en_ciclo} (Esperado: ['INV', 'ROB', 'ASG', 'RUT', 'SEG'])")
    print(f"Componentes Fuertemente Conexas: {cfc}")
    print(f"Si se modifica INV, afecta a ({len(afectados_inv)} módulos): {afectados_inv}")
    
    cp1_ok = (grados['INV']['entrada'] == 4 and grados['REP']['entrada'] == 0 and 
              total_ones == 40 and set(en_ciclo) == {'INV', 'ROB', 'ASG', 'RUT', 'SEG'} and
              len(afectados_inv) == 8)
    print(f"VERIFICACIÓN CP1: {'[OK - PASÓ]' if cp1_ok else '[ERROR]'}")

    # --------------------------------------------------------------------------
    # CP2: Grafo Reestructurado G' (Acíclico)
    # --------------------------------------------------------------------------
    print("\n--- [CP2] Grafo Reestructurado G' (Acíclico) ---")
    A_prime = A.copy()
    # Eliminar INV -> ROB (A[2,3] = 0) y SEG -> ASG (A[6,4] = 0)
    A_prime[2, 3] = 0
    A_prime[6, 4] = 0
    
    Astar_prime = warshall(A_prime)
    ones_prime = np.sum(Astar_prime)
    orden_mig, msg_top = orden_topologico(A_prime, modulos)
    
    print(f"Pares alcanzables A'*: {ones_prime} (Esperado: 23, reducción del 42.5%)")
    print(f"Diagonal de A'*: {np.diag(Astar_prime)} (Esperado: todo ceros)")
    print(f"Orden de migración sugerido (RF8): {orden_mig}")
    
    cp2_ok = (ones_prime == 23 and np.all(np.diag(Astar_prime) == 0) and orden_mig is not None)
    print(f"VERIFICACIÓN CP2: {'[OK - PASÓ]' if cp2_ok else '[ERROR]'}")

    # --------------------------------------------------------------------------
    # CP3: Sistema 3x3 de la Tabla 6 (Gauss-Jordan)
    # --------------------------------------------------------------------------
    print("\n--- [CP3] Sistema de Costos 3x3 (Tabla 6) ---")
    M = [[2, 3, 1], [1, 2, 2], [3, 1, 2]]
    B = [119, 122, 126]
    det_M, sol, clasif = resolver_sistema(M, B)
    x, y, z = sol
    I_B = 4*x + 6*y + 3*z
    
    print(f"det(M) = {det_M:.1f} ({clasif})")
    print(f"Solución: x = {x:.1f}, y = {y:.1f}, z = {z:.1f} (Esperado: 12, 20, 35)")
    print(f"Inversión Inicial I_B = {I_B:.1f} mil u.m. (Esperado: 273.0)")
    
    cp3_ok = (abs(det_M - 11.0) < 1e-3 and abs(x - 12) < 1e-3 and abs(y - 20) < 1e-3 and abs(z - 35) < 1e-3 and abs(I_B - 273) < 1e-3)
    print(f"VERIFICACIÓN CP3: {'[OK - PASÓ]' if cp3_ok else '[ERROR]'}")

    # --------------------------------------------------------------------------
    # CP4: Puntos de Equilibrio Económicos
    # --------------------------------------------------------------------------
    print("\n--- [CP4] Puntos de Equilibrio y Evaluación Temporal ---")
    # C_A = 110*n, C_B = 273 + 45*n, C_C = 420 + 40*n
    eq_AB = equilibrio(110, 0, 45, 273)
    eq_AC = equilibrio(110, 0, 40, 420)
    eq_BC = equilibrio(45, 273, 40, 420)
    
    print(f"Punto de Equilibrio A vs B: n = {eq_AB[0]:.2f} años ({eq_AB[1]:.1f} mil u.m.) (Esperado: 4.20)")
    print(f"Punto de Equilibrio A vs C: n = {eq_AC[0]:.2f} años ({eq_AC[1]:.1f} mil u.m.) (Esperado: 6.00)")
    print(f"Punto de Equilibrio B vs C: n = {eq_BC[0]:.2f} años ({eq_BC[1]:.1f} mil u.m.) (Esperado: 29.40)")
    
    cp4_ok = (abs(eq_AB[0] - 4.2) < 1e-2 and abs(eq_AC[0] - 6.0) < 1e-2 and abs(eq_BC[0] - 29.4) < 1e-2)
    print(f"VERIFICACIÓN CP4: {'[OK - PASÓ]' if cp4_ok else '[ERROR]'}")

    # --------------------------------------------------------------------------
    # CP5: Dijkstra Red de Distribución (Tabla 5)
    # --------------------------------------------------------------------------
    print("\n--- [CP5] Camino Mínimo en Red de Distribución (Dijkstra) ---")
    nodos = ['D', 'H1', 'H2', 'Z1', 'Z2', 'Z3']
    aristas = [
        ('D', 'H1', 8), ('D', 'H2', 5), ('H1', 'H2', 2),
        ('H1', 'Z1', 6), ('H2', 'Z1', 10), ('H2', 'Z2', 7),
        ('Z1', 'Z2', 3), ('Z1', 'Z3', 9), ('Z2', 'Z3', 4)
    ]
    d_std, path_std = dijkstra(nodos, aristas, 'D', 'Z3')
    
    # Agregar corredor aéreo directo D - Z3 (14 min)
    aristas_drone = aristas + [('D', 'Z3', 14)]
    d_drone, path_drone = dijkstra(nodos, aristas_drone, 'D', 'Z3')
    
    print(f"Camino Terrestre Mínimo D->Z3: {d_std} min por {path_std} (Esperado: 16 min por D-H2-Z2-Z3)")
    print(f"Camino con Corredor Dron D->Z3: {d_drone} min por {path_drone} (Esperado: 14 min por D-Z3)")
    
    cp5_ok = (d_std == 16 and path_std == ['D', 'H2', 'Z2', 'Z3'] and d_drone == 14)
    print(f"VERIFICACIÓN CP5: {'[OK - PASÓ]' if cp5_ok else '[ERROR]'}")

    # --------------------------------------------------------------------------
    # CP6: Casos Límite y Validaciones
    # --------------------------------------------------------------------------
    print("\n--- [CP6] Casos Límite y Validaciones de Borde ---")
    # Singular 3x3
    M_sing = [[1, 2, 3], [2, 4, 6], [1, 1, 1]]
    det_sing, _, clas_sing = resolver_sistema(M_sing, [1, 2, 3])
    print(f"Sistema Singular det={det_sing:.1f}: {clas_sing}")
    
    # Intento de orden topológico en grafo con ciclo CP1
    _, msg_ciclo = orden_topologico(A, modulos)
    print(f"Respuesta RF8 ante grafo con ciclos: {msg_ciclo}")
    
    cp6_ok = (abs(det_sing) < 1e-5 and "circulares" in msg_ciclo)
    print(f"VERIFICACIÓN CP6: {'[OK - PASÓ]' if cp6_ok else '[ERROR]'}")

    # --------------------------------------------------------------------------
    # CP7: Trazabilidad Booleana RT = RC (x) CT (Punto 5)
    # --------------------------------------------------------------------------
    print("\n--- [CP7] Trazabilidad Booleana Requerimiento-Componente-Prueba ---")
    RC = np.array([[1,0,0,0], [1,1,0,0], [0,0,1,0], [0,0,0,1]])
    CT = np.array([[1,0,0], [0,1,0], [0,0,1], [0,0,0]])
    
    # Producto booleano
    RT = np.zeros((4, 3), dtype=int)
    for i in range(4):
        for j in range(3):
            RT[i, j] = 1 if np.any(np.logical_and(RC[i, :], CT[:, j])) else 0
            
    print("Matriz RT = RC (x) CT:")
    print(RT)
    filas_nulas = [f"R{i+1}" for i in range(4) if np.all(RT[i, :] == 0)]
    print(f"Requerimientos sin prueba asociada (filas nulas): {filas_nulas} (Esperado: ['R4'])")
    
    cp7_ok = (filas_nulas == ['R4'] and np.array_equal(RT, [[1,0,0],[1,1,0],[0,0,1],[0,0,0]]))
    print(f"VERIFICACIÓN CP7: {'[OK - PASÓ]' if cp7_ok else '[ERROR]'}")

    print("\n" + "=" * 80)
    todas_pasaron = cp1_ok and cp2_ok and cp3_ok and cp4_ok and cp5_ok and cp6_ok and cp7_ok
    if todas_pasaron:
        print(" RESULTADO GLOBAL: TODOS LOS CASOS DE PRUEBA (CP1-CP7) PASARON EXITOSAMENTE [100% OK]")
    else:
        print(" RESULTADO GLOBAL: SE DETECTARON ERRORES EN ALGUNOS CASOS DE PRUEBA")
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_casos_de_prueba()
