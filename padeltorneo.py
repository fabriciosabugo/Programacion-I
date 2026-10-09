import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

NOMBRE_ARCHIVO = "jugadores.txt"

# -------------------------------------------------------------------
# FUNCIONES AUXILIARES DE ARCHIVO (BACKEND)
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
                    partes = linea.split(",")
                    if len(partes) == 2:
                        nombres.append(partes[0].strip())
                        categorias.append(partes[1].strip())
    return nombres, categorias


def guardar_jugadores_en_archivo(nombres, categorias):
    """Sobrescribe el archivo con el contenido actualizado de las listas."""
    with open(NOMBRE_ARCHIVO, "w", encoding="utf-8") as f:
        for i in range(len(nombres)):
            f.write(f"{nombres[i]},{categorias[i]}\n")


# -------------------------------------------------------------------
# INTERFAZ GRÁFICA CON TKINTER
# -------------------------------------------------------------------

class TorneoPadelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎾 Sistema de Gestión - Torneo de Pádel")
        self.root.geometry("780x620")
        self.root.minsize(700, 550)

        # Configurar estilo general
        self.configurar_estilos()

        # Datos en memoria
        self.nombres, self.categorias = cargar_jugadores_desde_archivo()
        self.parejas = []  # Lista de tuplas: (nombre_pareja, j1, cat1, j2, cat2)

        # Contenedor principal
        self.crear_interfaz()
        self.actualizar_tabla_jugadores()
        self.actualizar_combos_parejas()

    def configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Colores temáticos
        self.COLOR_PRIMARIO = "#1B5E20"     # Verde Pádel Oscuro
        self.COLOR_SECUNDARIO = "#2E7D32"
        self.COLOR_FONDO = "#F4F7F5"

        self.root.configure(bg=self.COLOR_FONDO)

        style.configure("TNotebook", background=self.COLOR_FONDO)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 6])
        style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", self.COLOR_PRIMARIO)])

        style.configure("TFrame", background=self.COLOR_FONDO)
        style.configure("TLabelframe", background=self.COLOR_FONDO, font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background=self.COLOR_FONDO, foreground=self.COLOR_PRIMARIO)

        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), foreground="#2D3748")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)

    def crear_interfaz(self):
        # Encabezado superior
        header_frame = tk.Frame(self.root, bg=self.COLOR_PRIMARIO, height=65)
        header_frame.pack(fill="x", side="top")

        lbl_titulo = tk.Label(
            header_frame,
            text="🎾 TORNEO DE PÁDEL - PANEL DE CONTROL",
            font=("Segoe UI", 15, "bold"),
            bg=self.COLOR_PRIMARIO,
            fg="#FFFFFF"
        )
        lbl_titulo.pack(pady=12)

        # Pestañas principales
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Pestaña 1: Inscriptos y Gestión
        self.tab_jugadores = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_jugadores, text=" 👥 Inscriptos y Gestión ")

        # Pestaña 2: Armado de Parejas
        self.tab_parejas = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_parejas, text=" 🏆 Armado de Parejas ")

        # Construir cada pestaña
        self.construir_tab_jugadores()
        self.construir_tab_parejas()

    # ---------------------------------------------------------------
    # PESTAÑA 1: GESTIÓN DE JUGADORES
    # ---------------------------------------------------------------
    def construir_tab_jugadores(self):
        # Panel superior: Agregar nuevo jugador
        frame_agregar = ttk.LabelFrame(self.tab_jugadores, text=" Inscribir Nuevo Jugador ", padding=10)
        frame_agregar.pack(fill="x", padx=5, pady=5)

        ttk.Label(frame_agregar, text="Nombre completo:", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nombre = ttk.Entry(frame_agregar, width=25, font=("Segoe UI", 9))
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.entry_nombre.bind("<Return>", lambda event: self.agregar_jugador())

        ttk.Label(frame_agregar, text="Categoría:", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_categoria = ttk.Combobox(
            frame_agregar,
            values=["1ª", "2ª", "3ª", "4ª", "5ª", "6ª", "7ª", "8ª", "Principiante"],
            width=14,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_categoria.set("7ª")
        self.combo_categoria.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        btn_agregar = tk.Button(
            frame_agregar,
            text="➕ Inscribir Jugador",
            bg=self.COLOR_PRIMARIO,
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.agregar_jugador
        )
        btn_agregar.grid(row=0, column=4, padx=15, pady=5)

        # Panel de Búsqueda y Filtros
        frame_filtro = ttk.Frame(self.tab_jugadores, padding=5)
        frame_filtro.pack(fill="x", padx=5, pady=(8, 2))

        ttk.Label(frame_filtro, text="🔍 Buscar por nombre:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        self.entry_buscar = ttk.Entry(frame_filtro, width=22, font=("Segoe UI", 9))
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.filtrar_jugadores())

        btn_limpiar = tk.Button(
            frame_filtro,
            text="Limpiar",
            bg="#E2E8F0",
            font=("Segoe UI", 8),
            relief="flat",
            padx=8,
            command=self.limpiar_busqueda
        )
        btn_limpiar.pack(side="left", padx=5)

        btn_eliminar = tk.Button(
            frame_filtro,
            text="🗑️ Dar de Baja Seleccionado",
            bg="#C53030",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.eliminar_jugador
        )
        btn_eliminar.pack(side="right", padx=5)

        # Tabla con Treeview y Scrollbar
        frame_tabla = ttk.Frame(self.tab_jugadores)
        frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

        columnas = ("id", "nombre", "categoria")
        self.tabla_jugadores = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")
        self.tabla_jugadores.heading("id", text="#")
        self.tabla_jugadores.heading("nombre", text="Nombre del Jugador")
        self.tabla_jugadores.heading("categoria", text="Categoría")

        self.tabla_jugadores.column("id", width=50, anchor="center")
        self.tabla_jugadores.column("nombre", width=380, anchor="w")
        self.tabla_jugadores.column("categoria", width=140, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_jugadores.yview)
        self.tabla_jugadores.configure(yscrollcommand=scroll_y.set)

        self.tabla_jugadores.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Barra de estado inferior
        self.lbl_estado = tk.Label(
            self.tab_jugadores,
            text="Cargando...",
            font=("Segoe UI", 9, "italic"),
            bg=self.COLOR_FONDO,
            fg="#4A5568",
            anchor="w"
        )
        self.lbl_estado.pack(fill="x", padx=5, pady=4)

    # ---------------------------------------------------------------
    # PESTAÑA 2: ARMADO DE PAREJAS
    # ---------------------------------------------------------------
    def construir_tab_parejas(self):
        # Información de estado de cupos
        self.lbl_info_parejas = tk.Label(
            self.tab_parejas,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#E8F5E9",
            fg=self.COLOR_PRIMARIO,
            padx=10,
            pady=6,
            relief="groove"
        )
        self.lbl_info_parejas.pack(fill="x", padx=5, pady=5)

        # Panel de Formación Manual
        frame_crear_pareja = ttk.LabelFrame(self.tab_parejas, text=" Formar Pareja Manual ", padding=10)
        frame_crear_pareja.pack(fill="x", padx=5, pady=5)

        ttk.Label(frame_crear_pareja, text="Nombre Pareja:", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nom_pareja = ttk.Entry(frame_crear_pareja, width=22, font=("Segoe UI", 9))
        self.entry_nom_pareja.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_crear_pareja, text="Jugador 1:", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_j1 = ttk.Combobox(frame_crear_pareja, width=22, state="readonly", font=("Segoe UI", 9))
        self.combo_j1.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_crear_pareja, text="Jugador 2:", font=("Segoe UI", 9)).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.combo_j2 = ttk.Combobox(frame_crear_pareja, width=22, state="readonly", font=("Segoe UI", 9))
        self.combo_j2.grid(row=1, column=3, padx=5, pady=5)

        btn_confirmar_pareja = tk.Button(
            frame_crear_pareja,
            text="🤝 Registrar Pareja",
            bg=self.COLOR_PRIMARIO,
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.registrar_pareja_manual
        )
        btn_confirmar_pareja.grid(row=0, column=4, rowspan=2, padx=15, pady=5)

        # Acciones automáticas
        frame_acciones = ttk.Frame(self.tab_parejas)
        frame_acciones.pack(fill="x", padx=5, pady=6)

        btn_aleatorio = tk.Button(
            frame_acciones,
            text="🎲 Generar Parejas al Azar (Todos)",
            bg="#2B6CB0",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.generar_parejas_aleatorias
        )
        btn_aleatorio.pack(side="left", padx=5)

        btn_reiniciar_parejas = tk.Button(
            frame_acciones,
            text="🔄 Reiniciar Parejas",
            bg="#E2E8F0",
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.reiniciar_parejas
        )
        btn_reiniciar_parejas.pack(side="right", padx=5)

        # Tabla de parejas armadas
        frame_tabla_p = ttk.LabelFrame(self.tab_parejas, text=" Parejas Oficiales del Torneo ", padding=5)
        frame_tabla_p.pack(fill="both", expand=True, padx=5, pady=5)

        cols_p = ("id", "pareja", "j1", "cat1", "j2", "cat2")
        self.tabla_parejas = ttk.Treeview(frame_tabla_p, columns=cols_p, show="headings")
        self.tabla_parejas.heading("id", text="#")
        self.tabla_parejas.heading("pareja", text="Nombre de Pareja")
        self.tabla_parejas.heading("j1", text="Jugador 1")
        self.tabla_parejas.heading("cat1", text="Cat 1")
        self.tabla_parejas.heading("j2", text="Jugador 2")
        self.tabla_parejas.heading("cat2", text="Cat 2")

        self.tabla_parejas.column("id", width=40, anchor="center")
        self.tabla_parejas.column("pareja", width=180, anchor="w")
        self.tabla_parejas.column("j1", width=160, anchor="w")
        self.tabla_parejas.column("cat1", width=60, anchor="center")
        self.tabla_parejas.column("j2", width=160, anchor="w")
        self.tabla_parejas.column("cat2", width=60, anchor="center")

        scroll_py = ttk.Scrollbar(frame_tabla_p, orient="vertical", command=self.tabla_parejas.yview)
        self.tabla_parejas.configure(yscrollcommand=scroll_py.set)

        self.tabla_parejas.pack(side="left", fill="both", expand=True)
        scroll_py.pack(side="right", fill="y")

    # ---------------------------------------------------------------
    # LÓGICA DE NEGOCIO Y EVENTOS
    # ---------------------------------------------------------------

    def actualizar_tabla_jugadores(self, lista_filtrada=None):
        """Refresca la tabla visual con los datos actuales."""
        for item in self.tabla_jugadores.get_children():
            self.tabla_jugadores.delete(item)

        items = lista_filtrada if lista_filtrada is not None else list(zip(self.nombres, self.categorias))
        
        for idx, (nom, cat) in enumerate(items, start=1):
            self.tabla_jugadores.insert("", "end", values=(idx, nom, cat))

        total = len(self.nombres)
        paridad = "número PAR" if total % 2 == 0 else "número IMPAR (se necesita 1 más para armar parejas)"
        self.lbl_estado.config(text=f"Total de inscriptos: {total} | Estado: {paridad}")
        self.actualizar_info_parejas()

    def agregar_jugador(self):
        nombre = self.entry_nombre.get().strip()
        categoria = self.combo_categoria.get().strip()

        if not nombre:
            messagebox.showwarning("Atención", "Por favor, ingrese el nombre del jugador.")
            self.entry_nombre.focus()
            return

        if "," in nombre:
            messagebox.showerror("Error", "El nombre no puede contener comas (,).")
            return

        # Comprobar si ya existe
        if any(n.lower() == nombre.lower() for n in self.nombres):
            if not messagebox.askyesno("Confirmación", f"El jugador '{nombre}' ya parece estar registrado. ¿Desea inscribirlo de todas formas?"):
                return

        # Guardar en memoria y archivo
        self.nombres.append(nombre)
        self.categorias.append(categoria)
        guardar_jugadores_en_archivo(self.nombres, self.categorias)

        # Limpiar formulario
        self.entry_nombre.delete(0, tk.END)
        self.actualizar_tabla_jugadores()
        self.actualizar_combos_parejas()
        messagebox.showinfo("Éxito", f"¡Jugador '{nombre}' ({categoria}) agregado con éxito!")

    def eliminar_jugador(self):
        seleccion = self.tabla_jugadores.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un jugador de la tabla para darlo de baja.")
            return

        item = self.tabla_jugadores.item(seleccion[0])
        nombre_sel = item["values"][1]
        cat_sel = str(item["values"][2])

        if messagebox.askyesno("Confirmar Baja", f"¿Está seguro de que desea dar de baja a '{nombre_sel}' ({cat_sel})?"):
            for i in range(len(self.nombres)):
                if self.nombres[i] == nombre_sel and self.categorias[i] == cat_sel:
                    self.nombres.pop(i)
                    self.categorias.pop(i)
                    break

            guardar_jugadores_en_archivo(self.nombres, self.categorias)
            self.reiniciar_parejas(silencioso=True)
            self.actualizar_tabla_jugadores()
            self.actualizar_combos_parejas()
            messagebox.showinfo("Baja Confirmada", f"El jugador '{nombre_sel}' ha sido eliminado.")

    def filtrar_jugadores(self):
        busqueda = self.entry_buscar.get().strip().lower()
        if not busqueda:
            self.actualizar_tabla_jugadores()
            return

        filtrados = [(n, c) for n, c in zip(self.nombres, self.categorias) if busqueda in n.lower() or busqueda in c.lower()]
        self.actualizar_tabla_jugadores(lista_filtrada=filtrados)

    def limpiar_busqueda(self):
        self.entry_buscar.delete(0, tk.END)
        self.actualizar_tabla_jugadores()

    # ---------------------------------------------------------------
    # LÓGICA DE PAREJAS
    # ---------------------------------------------------------------

    def obtener_jugadores_libres(self):
        """Retorna los nombres de jugadores que todavía no están en ninguna pareja armada."""
        asignados = []
        for _, j1, _, j2, _ in self.parejas:
            asignados.extend([j1, j2])
        return [f"{nom} ({cat})" for nom, cat in zip(self.nombres, self.categorias) if nom not in asignados]

    def actualizar_combos_parejas(self):
        libres = self.obtener_jugadores_libres()
        self.combo_j1["values"] = libres
        self.combo_j2["values"] = libres

        if libres:
            self.combo_j1.set(libres[0])
            self.combo_j2.set(libres[1] if len(libres) > 1 else libres[0])
        else:
            self.combo_j1.set("")
            self.combo_j2.set("")

    def actualizar_info_parejas(self):
        total = len(self.nombres)
        parejas_posibles = total // 2
        armadas = len(self.parejas)
        if total % 2 != 0:
            texto = f"⚠️ Inscriptos: {total} (Impar). Para armar parejas se necesita un número par de jugadores."
            self.lbl_info_parejas.config(text=texto, bg="#FFF3CD", fg="#856404")
        else:
            texto = f"✅ Inscriptos: {total} (Par). Parejas a conformar: {parejas_posibles} | Armadas: {armadas}"
            self.lbl_info_parejas.config(text=texto, bg="#E8F5E9", fg=self.COLOR_PRIMARIO)

    def registrar_pareja_manual(self):
        nombre_pareja = self.entry_nom_pareja.get().strip()
        str_j1 = self.combo_j1.get()
        str_j2 = self.combo_j2.get()

        if not nombre_pareja:
            messagebox.showwarning("Atención", "Ingrese un nombre identificador para la pareja.")
            return

        if not str_j1 or not str_j2:
            messagebox.showwarning("Atención", "Debe seleccionar ambos jugadores.")
            return

        if str_j1 == str_j2:
            messagebox.showerror("Error", "Un jugador no puede formar pareja consigo mismo.")
            return

        # Extraer nombre y categoría: "Nombre (Cat)"
        j1_nom = str_j1.rsplit(" (", 1)[0]
        j1_cat = str_j1.rsplit(" (", 1)[1].rstrip(")")
        j2_nom = str_j2.rsplit(" (", 1)[0]
        j2_cat = str_j2.rsplit(" (", 1)[1].rstrip(")")

        self.parejas.append((nombre_pareja, j1_nom, j1_cat, j2_nom, j2_cat))
        self.refrescar_tabla_parejas()
        self.actualizar_combos_parejas()
        self.actualizar_info_parejas()
        self.entry_nom_pareja.delete(0, tk.END)
        messagebox.showinfo("Éxito", f"¡Pareja '{nombre_pareja}' registrada con éxito!")

    def generar_parejas_aleatorias(self):
        total = len(self.nombres)
        if total < 2:
            messagebox.showwarning("Atención", "Se necesitan al menos 2 jugadores para armar parejas.")
            return

        if total % 2 != 0:
            messagebox.showerror(
                "Cantidad Impar",
                f"Actualmente hay {total} jugadores inscriptos.\nDeben ser una cantidad par para que nadie quede solo."
            )
            return

        if self.parejas:
            if not messagebox.askyesno("Confirmar", "¿Desea reemplazar las parejas existentes con un sorteo nuevo?"):
                return

        # Mezclar jugadores
        indices = list(range(total))
        random.shuffle(indices)

        self.parejas.clear()
        numero = 1
        for i in range(0, total, 2):
            idx1 = indices[i]
            idx2 = indices[i + 1]
            nom_pareja = f"Pareja #{numero} ({self.nombres[idx1]} / {self.nombres[idx2]})"
            self.parejas.append((
                nom_pareja,
                self.nombres[idx1],
                self.categorias[idx1],
                self.nombres[idx2],
                self.categorias[idx2]
            ))
            numero += 1

        self.refrescar_tabla_parejas()
        self.actualizar_combos_parejas()
        self.actualizar_info_parejas()
        messagebox.showinfo("Sorteo Completado", f"¡Se conformaron {len(self.parejas)} parejas al azar exitosamente!")

    def refrescar_tabla_parejas(self):
        for item in self.tabla_parejas.get_children():
            self.tabla_parejas.delete(item)

        for idx, (p_nom, j1, c1, j2, c2) in enumerate(self.parejas, start=1):
            self.tabla_parejas.insert("", "end", values=(idx, p_nom, j1, c1, j2, c2))

    def reiniciar_parejas(self, silencioso=False):
        if not self.parejas:
            return
        if not silencioso:
            if not messagebox.askyesno("Confirmar", "¿Desea reiniciar todas las parejas armadas?"):
                return
        self.parejas.clear()
        self.refrescar_tabla_parejas()
        self.actualizar_combos_parejas()
        self.actualizar_info_parejas()


# -------------------------------------------------------------------
# PUNTO DE ENTRADA PRINCIPAL
# -------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = TorneoPadelApp(root)
    root.mainloop()