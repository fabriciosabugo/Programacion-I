import json

ARCH_INSCRIPTOS = "inscriptos.json"
ARCH_PAREJAS = "parejas.json"

# Datos que se usan si todavía no existen los archivos JSON.
DATOS_INSCRIPTOS_INICIALES = [
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

DATOS_PAREJAS_INICIALES = [
    {"pareja": "Los Tanos", "jugadores": "Martin Gomez y Lucas Peralta", "puntos": 6},
    {"pareja": "Las Leonas", "jugadores": "Sofia Ruiz y Valentina Sosa", "puntos": 9},
    {"pareja": "Doble Falta", "jugadores": "Diego Acosta y Camila Diaz", "puntos": 3}
]

def cargar_o_crear_json(archivo, datos_defecto):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos_defecto, f, ensure_ascii=False, indent=4)
        return datos_defecto

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def seleccion_por_nombre(lista):
    """Ordena una copia de la lista por nombre con selección."""
    copia = [item.copy() for item in lista]
    n = len(copia)
    comparaciones = 0
    intercambios = 0

    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparaciones += 1
            if copia[j]["nombre"] < copia[min_idx]["nombre"]:
                min_idx = j
        if min_idx != i:
            copia[i], copia[min_idx] = copia[min_idx], copia[i]
            intercambios += 1

    return copia, comparaciones, intercambios

def burbuja_por_categoria_y_nombre(lista):
    """Ordena una copia por categoría y nombre con burbuja."""
    copia = [item.copy() for item in lista]
    n = len(copia)
    comparaciones = 0
    intercambios = 0

    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(0, n - 1 - i):
            comparaciones += 1
            key_j = (copia[j]["categoria"], copia[j]["nombre"])
            key_next = (copia[j+1]["categoria"], copia[j+1]["nombre"])
            if key_j > key_next:
                copia[j], copia[j+1] = copia[j+1], copia[j]
                intercambios += 1
                hubo_intercambio = True
        if not hubo_intercambio:
            break

    return copia, comparaciones, intercambios

def seleccion_por_puntos_desc(lista):
    """Ordena una copia de las parejas por puntaje, de mayor a menor."""
    copia = [item.copy() for item in lista]
    n = len(copia)
    for i in range(n - 1):
        max_idx = i
        for j in range(i + 1, n):
            if copia[j]["puntos"] > copia[max_idx]["puntos"]:
                max_idx = j
        if max_idx != i:
            copia[i], copia[max_idx] = copia[max_idx], copia[i]
    return copia

def main():
    inscriptos = cargar_o_crear_json(ARCH_INSCRIPTOS, DATOS_INSCRIPTOS_INICIALES)
    parejas = cargar_o_crear_json(ARCH_PAREJAS, DATOS_PAREJAS_INICIALES)

    inscriptos_p1, comp_p1, inter_p1 = seleccion_por_nombre(inscriptos)

    print("==================================================")
    print("PEDIDO 1: Lista de inscriptos en orden alfabético")
    print("==================================================")
    nombres_alfabetico = [p["nombre"] for p in inscriptos_p1]
    print(", ".join(nombres_alfabetico))
    print()

    inscriptos_p2, comp_p2, inter_p2 = burbuja_por_categoria_y_nombre(inscriptos)

    print("==================================================")
    print("PEDIDO 2: Cartelera por categoría")
    print("==================================================")
    categorias = ["4ª", "5ª", "6ª"]
    for cat in categorias:
        jugadores_cat = [p["nombre"] for p in inscriptos_p2 if p["categoria"] == cat]
        print(f"{cat} {', '.join(jugadores_cat)}")
    print()

    parejas_ordenadas = seleccion_por_puntos_desc(parejas)
    guardar_json(ARCH_PAREJAS, parejas_ordenadas)

    print("==================================================")
    print("PEDIDO 3: Tabla de posiciones")
    print("==================================================")
    print(f"{'Puesto':<8} {'Pareja':<15} {'Puntos':<6}")
    print("-" * 30)
    for puesto, item in enumerate(parejas_ordenadas, start=1):
        print(f"{puesto:<8} {item['pareja']:<15} {item['puntos']:<6}")
    print()

    print("==================================================")
    print("PEDIDO 4: Cuadro comparativo de métodos")
    print("==================================================")
    print(f"{'Pedido':<25} {'Método':<12} {'Comparaciones':<15} {'Intercambios':<12}")
    print("-" * 65)
    print(f"{'1. Orden alfabético':<25} {'Selección':<12} {comp_p1:<15} {inter_p1:<12}")
    print(f"{'2. Por categoría':<25} {'Burbuja':<12} {comp_p2:<15} {inter_p2:<12}")
    print("==================================================")

if __name__ == "__main__":
    main()