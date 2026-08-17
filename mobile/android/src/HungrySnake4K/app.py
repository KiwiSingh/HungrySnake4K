import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from toga.constants import Baseline
import random
import asyncio

class HungrySnake4K(toga.App):
    def startup(self):
        # Game Settings
        self.grid_size = 40
        self.canvas_width = 400
        self.canvas_height = 800
        
        # State Variables
        self.state = "MENU"
        self.multiplayer = False
        self.p1_score = 0
        self.p2_score = 0
        self.current_score = 0
        self.level = 1
        self.current_level_points = 0
        self.points_to_next_level = 20

        self.snake = []
        self.snake_dir = (1, 0)
        self.food_pos = (0, 0)
        self.food_color = "white"
        self.touch_start = None

        # Setup Canvas and Main Window
        self.canvas = toga.Canvas(
            style=Pack(flex=1),
            on_resize=self.on_resize,
            on_press=self.on_touch_down,
            on_release=self.on_touch_up,
        )

        box = toga.Box(children=[self.canvas], style=Pack(direction=COLUMN, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        # Start the non-blocking game loop
        self.add_background_task(self.game_loop)

    def on_resize(self, widget, width, height, **kwargs):
        self.canvas_width = width
        self.canvas_height = height
        self.redraw()

    def reset_player(self):
        center_x = (self.canvas_width // 2 // self.grid_size) * self.grid_size
        center_y = (self.canvas_height // 2 // self.grid_size) * self.grid_size
        self.snake = [(center_x - i * self.grid_size, center_y) for i in range(3)]
        self.snake_dir = (1, 0)
        self.current_score = 0
        self.current_level_points = 0
        self.points_to_next_level = 20
        self.level = 1
        self.spawn_food()

    def spawn_food(self):
        max_x = max(1, int(self.canvas_width // self.grid_size) - 2)
        max_y = max(1, int(self.canvas_height // self.grid_size) - 2)
        
        while True:
            fx = random.randint(1, max_x) * self.grid_size
            fy = random.randint(1, max_y) * self.grid_size
            self.food_pos = (fx, fy)
            if self.food_pos not in self.snake:
                break
        
        is_special = random.random() < 0.15
        if is_special:
            self.food_color = random.choice(["gold", "silver"])
        else:
            self.food_color = random.choice(["white", "red", "green", "blue", "cyan", "magenta", "yellow"])

    def trigger_game_over(self, crashed_player):
        if crashed_player == 1:
            self.p1_score = self.current_score
            if self.multiplayer:
                self.state = "P2_TRANSITION"
            else:
                self.state = "GAME_OVER"
        else:
            self.p2_score = self.current_score
            self.evaluate_winner()

    def evaluate_winner(self):
        if self.p1_score > self.p2_score:
            self.state = "GAME_OVER"
        elif self.p2_score > self.p1_score:
            self.state = "GAME_OVER"
        else:
            self.state = "REMATCH_PROMPT"

    # --- Touch Input Handling ---
    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)

    def on_touch_up(self, widget, x, y, **kwargs):
        if not self.touch_start:
            return

        dx = x - self.touch_start[0]
        dy = y - self.touch_start[1]
        
        if self.state in ["P1_PLAY", "P2_PLAY"]:
            # Swipe detection threshold
            if abs(dx) > 30 or abs(dy) > 30:
                if abs(dx) > abs(dy):
                    if dx > 0 and self.snake_dir != (-1, 0): self.snake_dir = (1, 0)
                    elif dx < 0 and self.snake_dir != (1, 0): self.snake_dir = (-1, 0)
                else:
                    if dy > 0 and self.snake_dir != (0, -1): self.snake_dir = (0, 1)
                    elif dy < 0 and self.snake_dir != (0, 1): self.snake_dir = (0, -1)
        else:
            # Menu Tap detection
            self.handle_menu_tap(y)

        self.touch_start = None

    def handle_menu_tap(self, y):
        top_half = (y < self.canvas_height / 2)

        if self.state == "MENU":
            self.multiplayer = not top_half
            self.reset_player()
            self.state = "P1_PLAY"
            
        elif self.state == "REMATCH_PROMPT":
            if top_half:
                self.reset_player()
                self.state = "P1_PLAY"
            else:
                self.state = "MENU"
                
        elif self.state in ["P2_TRANSITION", "GAME_OVER"]:
            if self.state == "P2_TRANSITION":
                self.reset_player()
                self.state = "P2_PLAY"
            else:
                self.state = "MENU"

    # --- Game Loop (15 FPS equivalent) ---
    async def game_loop(self, widget, **kwargs):
        while True:
            await asyncio.sleep(0.08) # Game tick speed

            if self.state in ["P1_PLAY", "P2_PLAY"]:
                head_x, head_y = self.snake[0]
                new_head = (head_x + self.snake_dir[0] * self.grid_size, 
                            head_y + self.snake_dir[1] * self.grid_size)
                
                # Wall Collision
                if (new_head[0] < 0 or new_head[0] >= self.canvas_width or 
                    new_head[1] < 0 or new_head[1] >= self.canvas_height):
                    self.trigger_game_over(1 if self.state == "P1_PLAY" else 2)
                # Tail Collision
                elif new_head in self.snake:
                    self.trigger_game_over(1 if self.state == "P1_PLAY" else 2)
                else:
                    self.snake.insert(0, new_head)
                    
                    # Food Collision
                    if (abs(new_head[0] - self.food_pos[0]) < self.grid_size and 
                        abs(new_head[1] - self.food_pos[1]) < self.grid_size):
                        
                        pts = 10 if self.food_color == "gold" else 5 if self.food_color == "silver" else 1
                        self.current_score += pts
                        self.current_level_points += pts
                        
                        if self.current_level_points >= self.points_to_next_level:
                            self.level += 1
                            self.points_to_next_level = (self.level + 1) * 10
                            self.current_level_points = 0
                            
                        self.spawn_food()
                    else:
                        self.snake.pop()

            self.redraw()

    # --- Rendering logic using Toga Canvas ---
    def redraw(self):
        self.canvas.clear()
        
        # Background
        with self.canvas.Fill(color="black") as fill:
            fill.rect(0, 0, self.canvas_width, self.canvas_height)

        if self.state in ["P1_PLAY", "P2_PLAY"]:
            # Draw Food
            with self.canvas.Fill(color=self.food_color) as fill:
                fill.rect(self.food_pos[0], self.food_pos[1], self.grid_size, self.grid_size)
            
            # Draw Snake
            with self.canvas.Fill(color="white") as fill:
                for segment in self.snake:
                    fill.rect(segment[0], segment[1], self.grid_size - 2, self.grid_size - 2)

            # Scoreboard
            with self.canvas.Fill(color="white") as fill:
                fill.font = toga.Font(family="monospace", size=20)
                fill.write_text(f"Level: {self.level}   Score: {self.current_score}", 
                                x=20, y=30, baseline=Baseline.TOP)

        elif self.state == "MENU":
            self.draw_tap_zones("TAP HERE FOR 1 PLAYER", "TAP HERE FOR 2 PLAYERS")
            self.draw_centered_text("HUNGRY SNAKE 4K", "red", 32, -100)

        elif self.state == "REMATCH_PROMPT":
            self.draw_tap_zones("TAP HERE FOR YES (REMATCH)", "TAP HERE FOR NO (MENU)")
            self.draw_centered_text("IT'S A TIE!", "red", 32, -100)
            self.draw_centered_text(f"Score: {self.p1_score}", "white", 20, -50)

        elif self.state == "P2_TRANSITION":
            self.draw_centered_text("PLAYER 1 CRASHED!", "red", 32, -100)
            self.draw_centered_text(f"P1 Score: {self.p1_score}", "white", 20, -50)
            self.draw_centered_text("TAP ANYWHERE FOR P2 TURN", "gray", 16, 100)

        elif self.state == "GAME_OVER":
            if self.multiplayer:
                winner = "PLAYER 1 WINS!" if self.p1_score > self.p2_score else "PLAYER 2 WINS!"
                self.draw_centered_text(winner, "red", 32, -100)
                self.draw_centered_text(f"P1: {self.p1_score}   P2: {self.p2_score}", "white", 20, -50)
            else:
                self.draw_centered_text("GAME OVER", "red", 32, -100)
                self.draw_centered_text(f"Final Score: {self.p1_score}", "white", 20, -50)
            self.draw_centered_text("TAP ANYWHERE TO RETURN", "gray", 16, 100)

    def draw_tap_zones(self, top_text, bottom_text):
        with self.canvas.Fill(color="rgb(40,40,40)") as fill:
            fill.rect(0, 0, self.canvas_width, self.canvas_height / 2)
        self.draw_centered_text(top_text, "rgb(200,200,200)", 16, -self.canvas_height / 4)

        with self.canvas.Fill(color="rgb(20,20,20)") as fill:
            fill.rect(0, self.canvas_height / 2, self.canvas_width, self.canvas_height / 2)
        self.draw_centered_text(bottom_text, "rgb(200,200,200)", 16, self.canvas_height / 4)

    def draw_centered_text(self, text, color, size, y_offset):
        # Rough centering math for monospace fonts
        approx_char_width = size * 0.6
        text_width = len(text) * approx_char_width
        x = max(0, (self.canvas_width - text_width) / 2)
        y = (self.canvas_height / 2) + y_offset

        with self.canvas.Fill(color=color) as fill:
            fill.font = toga.Font(family="monospace", size=size, weight="bold")
            fill.write_text(text, x=x, y=y, baseline=Baseline.MIDDLE)


def main():
    return HungrySnake4K()