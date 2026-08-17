import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import random
import asyncio
import traceback

class HungrySnake4K(toga.App):
    def startup(self):
        if hasattr(sys, 'getandroidapilevel'):
            self.platform = 'android'
        elif sys.platform == "ios":
            self.platform = 'ios'
        else:
            self.platform = 'desktop'

        self.log_path = self.paths.data / "debug.log"
        try:
            with open(self.log_path, "w") as f:
                f.write("=== App started ===\n")
        except:
            pass
        self.log("Startup: platform = " + self.platform)

        self.grid_size = 40
        self.DEFAULT_WIDTH = 400
        self.DEFAULT_HEIGHT = 800
        self.canvas_width = self.DEFAULT_WIDTH
        self.canvas_height = self.DEFAULT_HEIGHT

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

        self.canvas = toga.Canvas(
            style=Pack(flex=1, background_color="black"),
            on_resize=self.on_resize,
            on_press=self.on_touch_down,
            on_release=self.on_touch_up,
        )

        self.debug_label = toga.Label(
            "Starting...",
            style=Pack(padding=10, color="white", background_color="black", font_size=12)
        )

        box = toga.Box(children=[self.canvas, self.debug_label], style=Pack(direction=COLUMN, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        self.redraw()
        self.log("Creating game loop task")
        asyncio.create_task(self.game_loop(None))
        self.add_background_task(self.game_loop)
        self.log("Startup complete")

    def log(self, msg):
        try:
            with open(self.log_path, "a") as f:
                f.write(f"{msg}\n")
        except:
            pass

    def on_resize(self, widget, width, height, **kwargs):
        if width > 0 and height > 0:
            self.canvas_width = width
            self.canvas_height = height
            self.log(f"Resize: {width}x{height}")
        self.redraw()

    def reset_player(self):
        w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
        h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
        center_x = (w // 2 // self.grid_size) * self.grid_size
        center_y = (h // 2 // self.grid_size) * self.grid_size
        self.snake = [(center_x - i * self.grid_size, center_y) for i in range(3)]
        self.snake_dir = (1, 0)
        self.current_score = 0
        self.current_level_points = 0
        self.points_to_next_level = 20
        self.level = 1
        self.spawn_food()
        self.log(f"Player reset, snake: {self.snake}")

    def spawn_food(self):
        w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
        h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
        max_x = max(1, int(w // self.grid_size) - 2)
        max_y = max(1, int(h // self.grid_size) - 2)
        while True:
            fx = random.randint(1, max_x) * self.grid_size
            fy = random.randint(1, max_y) * self.grid_size
            self.food_pos = (fx, fy)
            if self.food_pos not in self.snake:
                break
        self.food_color = random.choice(["white", "red", "green", "blue", "cyan", "magenta", "yellow", "gold", "silver"])
        self.log(f"Food spawned at {self.food_pos}")

    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)

    def on_touch_up(self, widget, x, y, **kwargs):
        if not self.touch_start:
            return
        dx = x - self.touch_start[0]
        dy = y - self.touch_start[1]
        if self.state in ["P1_PLAY", "P2_PLAY"]:
            if abs(dx) > 30 or abs(dy) > 30:
                if abs(dx) > abs(dy):
                    if dx > 0 and self.snake_dir != (-1, 0): self.snake_dir = (1, 0)
                    elif dx < 0 and self.snake_dir != (1, 0): self.snake_dir = (-1, 0)
                else:
                    if dy > 0 and self.snake_dir != (0, -1): self.snake_dir = (0, 1)
                    elif dy < 0 and self.snake_dir != (0, 1): self.snake_dir = (0, -1)
        else:
            self.handle_menu_tap(y)
        self.touch_start = None

    def handle_menu_tap(self, y):
        top_half = (y < self.canvas_height / 2)
        if self.state == "MENU":
            self.multiplayer = not top_half
            self.reset_player()
            self.state = "P1_PLAY"
            self.log("Start game, multiplayer=" + str(self.multiplayer))
        elif self.state == "REMATCH_PROMPT":
            if top_half:
                self.reset_player()
                self.state = "P1_PLAY"
            else:
                self.state = "MENU"
        elif self.state == "P2_TRANSITION":
            self.reset_player()
            self.state = "P2_PLAY"
        elif self.state == "GAME_OVER":
            self.state = "MENU"

    def trigger_game_over(self, crashed_player):
        if crashed_player == 1:
            self.p1_score = self.current_score
            if self.multiplayer:
                self.state = "P2_TRANSITION"
            else:
                self.state = "GAME_OVER"
        else:
            self.p2_score = self.current_score
            if self.p1_score > self.p2_score:
                self.state = "GAME_OVER"
            elif self.p2_score > self.p1_score:
                self.state = "GAME_OVER"
            else:
                self.state = "REMATCH_PROMPT"
        self.log(f"Game over, state {self.state}")

    async def game_loop(self, widget, **kwargs):
        self.log("game_loop started")
        while True:
            await asyncio.sleep(0.08)
            try:
                if self.state in ["P1_PLAY", "P2_PLAY"]:
                    if not self.snake:
                        self.reset_player()
                    head_x, head_y = self.snake[0]
                    new_head = (
                        head_x + self.snake_dir[0] * self.grid_size,
                        head_y + self.snake_dir[1] * self.grid_size
                    )
                    w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
                    h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
                    if (new_head[0] < 0 or new_head[0] >= w or
                        new_head[1] < 0 or new_head[1] >= h):
                        self.trigger_game_over(1 if self.state == "P1_PLAY" else 2)
                    elif new_head in self.snake:
                        self.trigger_game_over(1 if self.state == "P1_PLAY" else 2)
                    else:
                        self.snake.insert(0, new_head)
                        if (abs(new_head[0] - self.food_pos[0]) < self.grid_size and
                            abs(new_head[1] - self.food_pos[1]) < self.grid_size):
                            # Eat food
                            pts = 10 if self.food_color in ["gold", "silver"] else 1
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
            except Exception:
                self.log("Exception in game_loop:")
                self.log(traceback.format_exc())

    def redraw(self):
        try:
            self.debug_label.text = f"State:{self.state} W:{self.canvas_width} H:{self.canvas_height} Score:{self.current_score}"

            # Clear with black
            with self.canvas.fill(color="black"):
                self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            # -------- MENU --------
            if self.state == "MENU":
                # Draw tap zones
                with self.canvas.fill(color="rgb(40,40,40)"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height / 2)
                with self.canvas.fill(color="rgb(20,20,20)"):
                    self.canvas.rect(0, self.canvas_height / 2, self.canvas_width, self.canvas_height / 2)

                # Draw text without optional parameters
                self.canvas.fill_text(
                    "TAP HERE FOR 1 PLAYER",
                    x=20, y=self.canvas_height/4 - 10,
                    font=toga.Font(size=16)
                )
                self.canvas.fill_text(
                    "TAP HERE FOR 2 PLAYERS",
                    x=20, y=3*self.canvas_height/4 - 10,
                    font=toga.Font(size=16)
                )
                self.canvas.fill_text(
                    "HUNGRY SNAKE 4K",
                    x=50, y=self.canvas_height/2 - 50,
                    font=toga.Font(size=24, weight="bold")
                )
                return

            # -------- PLAYING STATES --------
            if self.state in ["P1_PLAY", "P2_PLAY"]:
                # Background: dark green
                with self.canvas.fill(color="darkgreen"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

                # Draw food
                with self.canvas.fill(color=self.food_color):
                    self.canvas.rect(self.food_pos[0], self.food_pos[1],
                                     self.grid_size, self.grid_size)

                # Draw snake - without stroke, use a larger base rectangle for outline
                for segment in self.snake:
                    # Outline (slightly larger) in red
                    with self.canvas.fill(color="red"):
                        self.canvas.rect(segment[0]-1, segment[1]-1,
                                         self.grid_size, self.grid_size)
                    # Inner body in yellow
                    with self.canvas.fill(color="yellow"):
                        self.canvas.rect(segment[0]+1, segment[1]+1,
                                         self.grid_size-4, self.grid_size-4)

                # Score text
                self.canvas.fill_text(
                    f"Level: {self.level}   Score: {self.current_score}",
                    x=20, y=30,
                    font=toga.Font(size=18, weight="bold")
                )
                return

            # -------- OTHER STATES --------
            # REMATCH_PROMPT
            if self.state == "REMATCH_PROMPT":
                self.canvas.fill_text("IT'S A TIE!", x=100, y=200, font=toga.Font(size=24, weight="bold"))
                self.canvas.fill_text(f"Score: {self.p1_score}", x=100, y=250, font=toga.Font(size=18))
                self.canvas.fill_text("TAP TOP for Rematch, BOTTOM for Menu", x=30, y=350, font=toga.Font(size=14))
                return

            # P2_TRANSITION
            if self.state == "P2_TRANSITION":
                self.canvas.fill_text("PLAYER 1 CRASHED!", x=100, y=200, font=toga.Font(size=24, weight="bold"))
                self.canvas.fill_text(f"P1 Score: {self.p1_score}", x=100, y=250, font=toga.Font(size=18))
                self.canvas.fill_text("TAP ANYWHERE for P2 TURN", x=50, y=350, font=toga.Font(size=14))
                return

            # GAME_OVER
            if self.state == "GAME_OVER":
                if self.multiplayer:
                    winner = "PLAYER 1 WINS!" if self.p1_score > self.p2_score else "PLAYER 2 WINS!"
                    self.canvas.fill_text(winner, x=100, y=200, font=toga.Font(size=24, weight="bold"))
                    self.canvas.fill_text(f"P1: {self.p1_score}   P2: {self.p2_score}", x=100, y=250, font=toga.Font(size=18))
                else:
                    self.canvas.fill_text("GAME OVER", x=120, y=200, font=toga.Font(size=24, weight="bold"))
                    self.canvas.fill_text(f"Final Score: {self.p1_score}", x=100, y=250, font=toga.Font(size=18))
                self.canvas.fill_text("TAP ANYWHERE to return", x=50, y=350, font=toga.Font(size=14))

        except Exception as e:
            self.log(f"redraw exception: {e}")
            self.log(traceback.format_exc())
            self.debug_label.text = f"ERROR: {str(e)[:50]}"

def main():
    return HungrySnake4K()