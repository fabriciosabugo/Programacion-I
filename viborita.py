import tkinter as tk
import random

# Constantes del juego
GAME_WIDTH = 600
GAME_HEIGHT = 600
SPEED = 100  # ms por movimiento
SPACE_SIZE = 20
BODY_PARTS = 3
SNAKE_COLOR = "#00FF66"
SNAKE_HEAD_COLOR = "#00CC52"
FOOD_COLOR = "#FF3366"
BACKGROUND_COLOR = "#121212"
TEXT_COLOR = "#FFFFFF"

class Snake:
    def __init__(self, canvas):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []
        self.canvas = canvas

        # Posición inicial al centro
        start_x = (GAME_WIDTH // (2 * SPACE_SIZE)) * SPACE_SIZE
        start_y = (GAME_HEIGHT // (2 * SPACE_SIZE)) * SPACE_SIZE

        for i in range(0, BODY_PARTS):
            self.coordinates.append([start_x - i * SPACE_SIZE, start_y])

        for index, (x, y) in enumerate(self.coordinates):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_COLOR
            square = self.canvas.create_rectangle(
                x, y, x + SPACE_SIZE, y + SPACE_SIZE, 
                fill=color, outline="#1e1e1e", tag="snake"
            )
            self.squares.append(square)

class Food:
    def __init__(self, canvas, snake_coords):
        self.canvas = canvas
        self.coordinates = self.generate_position(snake_coords)

        x, y = self.coordinates
        self.id = self.canvas.create_oval(
            x + 2, y + 2, x + SPACE_SIZE - 2, y + SPACE_SIZE - 2,
            fill=FOOD_COLOR, outline="", tag="food"
        )

    def generate_position(self, snake_coords):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if [x, y] not in snake_coords:
                return [x, y]

class SnakeGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Juego de la Viborita 🐍")
        self.window.resizable(False, False)

        self.score = 0
        self.high_score = 0
        self.direction = "Right"
        self.next_direction = "Right"
        self.is_paused = False
        self.is_game_over = False

        # Panel de puntuación
        self.score_frame = tk.Frame(self.window, bg="#1e1e1e", pady=10)
        self.score_frame.pack(fill=tk.X)

        self.label_score = tk.Label(
            self.score_frame, 
            text=f"Puntaje: {self.score}  |  Récord: {self.high_score}", 
            font=('Segoe UI', 14, 'bold'), 
            fg=TEXT_COLOR, 
            bg="#1e1e1e"
        )
        self.label_score.pack()

        # Canvas del juego
        self.canvas = tk.Canvas(
            self.window, 
            bg=BACKGROUND_COLOR, 
            height=GAME_HEIGHT, 
            width=GAME_WIDTH,
            highlightthickness=0
        )
        self.canvas.pack()

        # Controles e Instrucciones en la parte inferior
        self.info_label = tk.Label(
            self.window,
            text="Usa Flechas/WASD para moverte | Espacio: Pausa | R: Reiniciar",
            font=('Segoe UI', 9),
            fg="#888888",
            bg="#1e1e1e",
            pady=5
        )
        self.info_label.pack(fill=tk.X)

        # Eventos de teclado
        self.window.bind('<Left>', lambda event: self.change_direction('Left'))
        self.window.bind('<Right>', lambda event: self.change_direction('Right'))
        self.window.bind('<Up>', lambda event: self.change_direction('Up'))
        self.window.bind('<Down>', lambda event: self.change_direction('Down'))
        self.window.bind('<a>', lambda event: self.change_direction('Left'))
        self.window.bind('<d>', lambda event: self.change_direction('Right'))
        self.window.bind('<w>', lambda event: self.change_direction('Up'))
        self.window.bind('<s>', lambda event: self.change_direction('Down'))
        self.window.bind('<space>', lambda event: self.toggle_pause())
        self.window.bind('<r>', lambda event: self.restart_game())

        # Centrar ventana en pantalla
        self.center_window()

        # Iniciar juego
        self.start_game()

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Traer la ventana al frente de la pantalla y darle foco
        self.window.attributes('-topmost', True)
        self.window.update()
        self.window.attributes('-topmost', False)
        self.window.focus_force()

    def start_game(self):
        self.score = 0
        self.direction = "Right"
        self.next_direction = "Right"
        self.is_paused = False
        self.is_game_over = False
        
        self.label_score.config(text=f"Puntaje: {self.score}  |  Récord: {self.high_score}")
        self.canvas.delete("all")

        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas, self.snake.coordinates)

        self.next_turn()

    def change_direction(self, new_dir):
        if self.is_paused or self.is_game_over:
            return

        # Prevenir rotación de 180 grados
        opposite_dirs = {
            'Left': 'Right', 'Right': 'Left',
            'Up': 'Down', 'Down': 'Up'
        }
        if new_dir != opposite_dirs.get(self.direction):
            self.next_direction = new_dir

    def toggle_pause(self):
        if self.is_game_over:
            self.restart_game()
            return
        
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.canvas.create_text(
                GAME_WIDTH / 2, GAME_HEIGHT / 2,
                font=('Segoe UI', 30, 'bold'),
                text="PAUSA", fill="#FFCC00", tag="pause_text"
            )
        else:
            self.canvas.delete("pause_text")
            self.next_turn()

    def next_turn(self):
        if self.is_paused or self.is_game_over:
            return

        self.direction = self.next_direction

        x, y = self.snake.coordinates[0]

        if self.direction == "Up":
            y -= SPACE_SIZE
        elif self.direction == "Down":
            y += SPACE_SIZE
        elif self.direction == "Left":
            x -= SPACE_SIZE
        elif self.direction == "Right":
            x += SPACE_SIZE

        # Insertar nueva cabeza
        self.snake.coordinates.insert(0, [x, y])

        # Renderizar nueva cabeza y actualizar el color del segmento anterior
        new_square = self.canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=SNAKE_HEAD_COLOR, outline="#1e1e1e", tag="snake"
        )
        self.snake.squares.insert(0, new_square)

        if len(self.snake.squares) > 1:
            self.canvas.itemconfig(self.snake.squares[1], fill=SNAKE_COLOR)

        # Verificar si comió la comida
        if x == self.food.coordinates[0] and y == self.food.coordinates[1]:
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score

            self.label_score.config(text=f"Puntaje: {self.score}  |  Récord: {self.high_score}")
            self.canvas.delete("food")
            self.food = Food(self.canvas, self.snake.coordinates)
        else:
            # Eliminar último segmento si no comió
            del self.snake.coordinates[-1]
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]

        # Verificar colisiones
        if self.check_collisions():
            self.game_over()
        else:
            self.window.after(SPEED, self.next_turn)

    def check_collisions(self):
        x, y = self.snake.coordinates[0]

        # Colisión con bordes
        if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
            return True

        # Colisión con el propio cuerpo
        for body_part in self.snake.coordinates[1:]:
            if x == body_part[0] and y == body_part[1]:
                return True

        return False

    def game_over(self):
        self.is_game_over = True
        self.canvas.delete("all")
        
        self.canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 - 30,
            font=('Segoe UI', 36, 'bold'),
            text="¡GAME OVER!", fill="#FF3366"
        )
        self.canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20,
            font=('Segoe UI', 16),
            text=f"Puntaje final: {self.score}", fill=TEXT_COLOR
        )
        self.canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2 + 60,
            font=('Segoe UI', 14, 'italic'),
            text="Presiona 'R' o 'Espacio' para reiniciar", fill="#AAAAAA"
        )

    def restart_game(self):
        self.start_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
