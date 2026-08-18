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
        self.snake = [(200, 400), (160, 400), (120, 400)]  # dummy snake
        self.snake_dir = (1, 0)  # moving right
        self.food_pos = (300, 300)
        self.food_color = "red"

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

        # Start game loop
        asyncio.create_task(self.game_loop(None))
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
        self.redraw()

    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)

    def on_touch_up(self, widget, x, y, **kwargs):
        if not self.touch_start:
            return
        # Toggle state on touch
        if self.state == "MENU":
            self.state = "PLAY"
        else:
            self.state = "MENU"
        self.touch_start = None
        # No need to redraw here, loop does it

    async def game_loop(self, widget):
        self.log("game_loop started")
        while True:
            await asyncio.sleep(0.08)
            try:
                if self.state == "PLAY":
                    # Move snake
                    head = self.snake[0]
                    new_head = (head[0] + self.snake_dir[0]*self.grid_size,
                                head[1] + self.snake_dir[1]*self.grid_size)
                    # Wrap around or simple move (no collision for now)
                    self.snake.insert(0, new_head)
                    self.snake.pop()
                    # Check if head on food
                    if (abs(new_head[0] - self.food_pos[0]) < self.grid_size and
                        abs(new_head[1] - self.food_pos[1]) < self.grid_size):
                        # Grow and respawn food
                        self.snake.append(self.snake[-1])  # duplicate last
                        self.food_pos = (random.randint(1, 8)*self.grid_size,
                                         random.randint(1, 15)*self.grid_size)
                        self.food_color = random.choice(["red", "green", "blue", "yellow", "cyan", "magenta", "white"])
                self.redraw()
            except Exception as e:
                self.log(f"Loop error: {e}")
                self.log(traceback.format_exc())

    def redraw(self):
        try:
            self.debug_label.text = f"State:{self.state} W:{self.canvas_width} H:{self.canvas_height}"

            # Clear with black
            with self.canvas.fill(color="black"):
                self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            if self.state == "MENU":
                # Draw a simple menu: just two colored rectangles
                with self.canvas.fill(color="blue"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height/2)
                with self.canvas.fill(color="darkblue"):
                    self.canvas.rect(0, self.canvas_height/2, self.canvas_width, self.canvas_height/2)
                # No text
            else:  # PLAY
                # Background green
                with self.canvas.fill(color="darkgreen"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

                # Draw food
                with self.canvas.fill(color=self.food_color):
                    self.canvas.rect(self.food_pos[0], self.food_pos[1],
                                     self.grid_size, self.grid_size)

                # Draw snake (just fill, no stroke)
                for segment in self.snake:
                    with self.canvas.fill(color="yellow"):
                        self.canvas.rect(segment[0], segment[1],
                                         self.grid_size-2, self.grid_size-2)

            if self.platform == 'ios':
                try:
                    from rubicon.objc import ObjCClass
                    UIView = ObjCClass('UIView')
                    self.canvas._impl.native.setNeedsDisplay()
                except:
                    pass

        except Exception as e:
            self.log(f"redraw error: {e}")
            self.log(traceback.format_exc())
            self.debug_label.text = f"ERROR: {str(e)[:50]}"

def main():
    return HungrySnake4K()