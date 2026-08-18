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

        # Optional log (not needed but kept)
        self.log_path = self.paths.data / "debug.log"
        try:
            with open(self.log_path, "w") as f:
                f.write("=== App started ===\n")
        except:
            pass

        self.grid_size = 40
        self.DEFAULT_WIDTH = 400
        self.DEFAULT_HEIGHT = 800
        self.canvas_width = self.DEFAULT_WIDTH
        self.canvas_height = self.DEFAULT_HEIGHT

        self.state = "MENU"          # MENU, PLAY, GAME_OVER
        self.snake = []
        self.snake_dir = (1, 0)
        self.food_pos = (0, 0)
        self.score = 0
        self.touch_start = None

        self.canvas = toga.Canvas(
            style=Pack(flex=1, background_color="black"),
            on_resize=self.on_resize,
            on_press=self.on_touch_down,
            on_release=self.on_touch_up,
        )

        # Debug label – we will show score and state here (no canvas text)
        self.debug_label = toga.Label(
            "Starting...",
            style=Pack(padding=10, color="white", background_color="black", font_size=12)
        )

        box = toga.Box(children=[self.canvas, self.debug_label], style=Pack(direction=COLUMN, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        self.redraw()
        asyncio.create_task(self.game_loop(None))
        self.add_background_task(self.game_loop)

    def on_resize(self, widget, width, height, **kwargs):
        if width > 0 and height > 0:
            self.canvas_width = width
            self.canvas_height = height
        self.redraw()

    def reset_player(self):
        w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
        h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
        center_x = (w // 2 // self.grid_size) * self.grid_size
        center_y = (h // 2 // self.grid_size) * self.grid_size
        self.snake = [(center_x - i * self.grid_size, center_y) for i in range(3)]
        self.snake_dir = (1, 0)
        self.score = 0
        self.spawn_food()

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

    # --- Touch ---
    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)

    def on_touch_up(self, widget, x, y, **kwargs):
        if not self.touch_start:
            return
        dx = x - self.touch_start[0]
        dy = y - self.touch_start[1]

        if self.state == "MENU":
            self.reset_player()
            self.state = "PLAY"
            self.touch_start = None
            self.redraw()
            return

        if self.state == "PLAY":
            # Lower threshold for responsive turns
            if abs(dx) > 20 or abs(dy) > 20:
                if abs(dx) > abs(dy):
                    if dx > 0 and self.snake_dir != (-1, 0):
                        self.snake_dir = (1, 0)
                    elif dx < 0 and self.snake_dir != (1, 0):
                        self.snake_dir = (-1, 0)
                else:
                    if dy > 0 and self.snake_dir != (0, -1):
                        self.snake_dir = (0, 1)
                    elif dy < 0 and self.snake_dir != (0, 1):
                        self.snake_dir = (0, -1)

        elif self.state == "GAME_OVER":
            self.state = "MENU"

        self.touch_start = None
        self.redraw()

    # --- Game Loop ---
    async def game_loop(self, widget):
        while True:
            await asyncio.sleep(0.05)   # 20 FPS
            try:
                if self.state == "PLAY":
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
                        self.state = "GAME_OVER"
                        self.redraw()
                        continue

                    if new_head in self.snake:
                        self.state = "GAME_OVER"
                        self.redraw()
                        continue

                    self.snake.insert(0, new_head)

                    if (abs(new_head[0] - self.food_pos[0]) < self.grid_size and
                        abs(new_head[1] - self.food_pos[1]) < self.grid_size):
                        self.score += 1
                        self.spawn_food()
                    else:
                        self.snake.pop()

                self.redraw()
            except Exception:
                pass   # Silently ignore to avoid crashes; debug label will show error

    # --- Rendering ---
    def redraw(self):
        try:
            # Update debug label with state and score
            self.debug_label.text = f"State:{self.state}  Score:{self.score}  W:{self.canvas_width} H:{self.canvas_height}"

            # Clear
            with self.canvas.fill(color="black"):
                self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            if self.state == "MENU":
                with self.canvas.fill(color="blue"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)
                # Visual cue: a small white rectangle in center as a tap indicator
                with self.canvas.fill(color="white"):
                    self.canvas.rect(self.canvas_width//2 - 40, self.canvas_height//2 - 20, 80, 40)

            elif self.state == "PLAY":
                with self.canvas.fill(color="darkgreen"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

                # Food (red)
                with self.canvas.fill(color="red"):
                    self.canvas.rect(self.food_pos[0], self.food_pos[1],
                                     self.grid_size, self.grid_size)

                # Snake (yellow with a slight border)
                for seg in self.snake:
                    with self.canvas.fill(color="yellow"):
                        self.canvas.rect(seg[0], seg[1],
                                         self.grid_size - 2, self.grid_size - 2)

            elif self.state == "GAME_OVER":
                with self.canvas.fill(color="red"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            # Force redraw on iOS
            if self.platform == 'ios':
                try:
                    from rubicon.objc import ObjCClass
                    UIView = ObjCClass('UIView')
                    self.canvas._impl.native.setNeedsDisplay()
                except:
                    pass

        except Exception as e:
            self.debug_label.text = f"ERROR: {str(e)[:50]}"

def main():
    return HungrySnake4K()