import json
import os

ARCH_INSCRIPTOS = "inscriptos.json"

DATOS_INICIALES = [
    {"nombre": "Martin Gomez", "categoria": "5ª"},
    {"nombre": "Lucas Peralta", "categoria": "5ª"},
    {"nombre": "Sofia Ruiz", "categoria": "4ª"},
    {"nombre": "Diego Acosta", "categoria": "6ª"},
    {"nombre": "Valentina Sosa", "categoria": "4ª"},
    {"nombre": "Tomas Benitez", "categoria": "5ª"},
    {"nombre": "Camila Diaz", "categoria": "6ª"},
    {"nombre": "Facundo Romero", "categoria": "4ª"},
    {"nombre": "Julieta Molina", "categoria": "6ª"},
    {"nombre": "Nicolas Ortiz", "categoria": "5ª"},
    {"nombre": "Agustina Lopez", "categoria": "4ª"},
    {"nombre": "Bruno Fernandez", "categoria": "6ª"}
]

class NodoABB:
    """Guarda un jugador dentro del árbol."""

    def __init__(self, nombre, categoria):
        self.nombre = nombre
        self.categoria = categoria
        self.izq = None
        self.der = None


class ABBInscriptos:
    """Árbol de búsqueda de jugadores."""

    def __init__(self):
        self.raiz = None

    def insertar(self, nombre, categoria):
        if self.raiz is None:
            self.raiz = NodoABB(nombre, categoria)
        else:
            self._insertar_rec(self.raiz, nombre, categoria)

    def _insertar_rec(self, nodo, nombre, categoria):
        if nombre < nodo.nombre:
            if nodo.izq is None:
                nodo.izq = NodoABB(nombre, categoria)
            else:
                self._insertar_rec(nodo.izq, nombre, categoria)
        elif nombre > nodo.nombre:
            if nodo.der is None:
                nodo.der = NodoABB(nombre, categoria)
            else:
                self._insertar_rec(nodo.der, nombre, categoria)

    def buscar(self, nombre):
        """Devuelve la categoría y cuántos nodos revisó."""
        return self._buscar_rec(self.raiz, nombre, 0)

    def _buscar_rec(self, nodo, nombre, comp):
        if nodo is None:
            return None, comp
        comp += 1
        if nombre == nodo.nombre:
            return nodo.categoria, comp
        elif nombre < nodo.nombre:
            return self._buscar_rec(nodo.izq, nombre, comp)
        else:
            return self._buscar_rec(nodo.der, nombre, comp)

    def obtener_inorden(self):
        """Devuelve los nombres en orden alfabético."""
        resultado = []
        self._inorden_rec(self.raiz, resultado)
        return resultado

    def _inorden_rec(self, nodo, resultado):
        if nodo is not None:
            self._inorden_rec(nodo.izq, resultado)
            resultado.append(nodo.nombre)
            self._inorden_rec(nodo.der, resultado)

    def obtener_altura(self):
        """La raíz cuenta como nivel 0; un árbol vacío tiene altura -1."""
        return self._altura_rec(self.raiz)

    def _altura_rec(self, nodo):
        if nodo is None:
            return -1
        return 1 + max(self._altura_rec(nodo.izq), self._altura_rec(nodo.der))

class NodoPartido:
    """Representa un partido del cuadro."""

    def __init__(self, nombre_partido, subarbol_izq=None, subarbol_der=None):
        self.nombre_partido = nombre_partido
        self.izq = subarbol_izq
        self.der = subarbol_der
        self.ganador = None


class HojaEquipo:
    """Equipo que aparece en una hoja del cuadro."""

    def __init__(self, nombre_pareja):
        self.nombre_pareja = nombre_pareja
        self.ganador = nombre_pareja


def cargar_o_crear_json():
    if not os.path.exists(ARCH_INSCRIPTOS):
        with open(ARCH_INSCRIPTOS, "w", encoding="utf-8") as f:
            json.dump(DATOS_INICIALES, f, ensure_ascii=False, indent=4)
        return DATOS_INICIALES

    with open(ARCH_INSCRIPTOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_json(datos):
    with open(ARCH_INSCRIPTOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def construir_abb_desde_lista(lista_inscriptos):
    abb = ABBInscriptos()
    for jug in lista_inscriptos:
        abb.insertar(jug["nombre"], jug["categoria"])
    return abb

def simular_cuadro_torneo():
    leonas = HojaEquipo("Las Leonas")
    doble_falta = HojaEquipo("Doble Falta")
    tanos = HojaEquipo("Los Tanos")
    primos = HojaEquipo("Los Primos")

    sf1 = NodoPartido("Semifinal 1", leonas, doble_falta)
    sf2 = NodoPartido("Semifinal 2", tanos, primos)
    final = NodoPartido("Final", sf1, sf2)

    resultados_fijos = {
        "Semifinal 1": "Las Leonas",
        "Semifinal 2": "Los Tanos",
        "Final": "Las Leonas"
    }

    orden_partidos = []

    # En postorden se resuelven las semifinales antes que la final.
    def recorrido_postorden_torneo(nodo):
        if isinstance(nodo, NodoPartido):
            recorrido_postorden_torneo(nodo.izq)
            recorrido_postorden_torneo(nodo.der)

            eq1 = nodo.izq.ganador
            eq2 = nodo.der.ganador
            ganador = resultados_fijos[nodo.nombre_partido]
            nodo.ganador = ganador
            orden_partidos.append((nodo.nombre_partido, eq1, eq2, ganador))

    recorrido_postorden_torneo(final)
    return final, orden_partidos


def main():
    inscriptos = cargar_o_crear_json()
    abb = construir_abb_desde_lista(inscriptos)

    print("==================================================")
    print("  ACTIVIDAD 04: ÁRBOLES BINARIOS EN EL TORNEO")
    print("==================================================\n")

    # Pedido 1
    print("--- PEDIDO 1: Búsqueda de Inscriptos ---")
    busquedas = ["Martin Gomez", "Julieta Molina", "Bruno Fernandez", "Pedro Gimenez"]
    for nom in busquedas:
        cat, comp = abb.buscar(nom)
        if cat:
            print(f"Buscado: '{nom:<16}' -> Categoría: {cat} | Comparaciones: {comp}")
        else:
            print(f"Buscado: '{nom:<16}' -> No está inscripto | Comparaciones: {comp}")
    print()

    # Pedido 2
    print("--- PEDIDO 2: Inscriptos en Orden Alfabético (Recorrido Inorden) ---")
    lista_ordenada = abb.obtener_inorden()
    print(", ".join(lista_ordenada))
    print()

    # Pedido 3
    print("--- PEDIDO 3: Alta de Nuevo Inscripto (Pedro Gimenez) ---")
    h_antes = abb.obtener_altura()
    print(f"Altura del ABB antes del alta: {h_antes}")
    
    # Alta en memoria y persistencia JSON
    nuevo_jugador = {"nombre": "Pedro Gimenez", "categoria": "5ª"}
    inscriptos.append(nuevo_jugador)
    guardar_json(inscriptos)
    abb.insertar(nuevo_jugador["nombre"], nuevo_jugador["categoria"])

    h_despues = abb.obtener_altura()
    print(f"Altura del ABB después del alta: {h_despues}")

    cat_p, comp_p = abb.buscar("Pedro Gimenez")
    print(f"Búsqueda post-alta: 'Pedro Gimenez' -> Categoría: {cat_p} | Comparaciones: {comp_p}")
    print("Nueva lista alfabética (Inorden):")
    print(", ".join(abb.obtener_inorden()))
    print()

    # Pedidos 4 y 5
    print("--- PEDIDOS 4 y 5: Cuadro de Eliminación Directa y Orden de Partidos ---")
    raiz_final, partidos_jugados = simular_cuadro_torneo()

    print("Orden de disputa de los partidos (Recorrido Postorden):")
    for p_nom, eq1, eq2, gan in partidos_jugados:
        print(f"  • {p_nom}: {eq1} vs {eq2} -> Ganador: {gan}")

    print(f"\n¡CAMPEÓN DEL TORNEO: {raiz_final.ganador}! 🏆")

if __name__ == "__main__":
    main()