import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
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

        self.canvas_width = 400
        self.canvas_height = 800

        # Simple state
        self.state = "MENU"   # "MENU" or "PLAY"
        self.color = "blue"   # default menu color

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

        # No game loop yet – we'll update via touch
        self.log("Startup complete")

    def log(self, msg):
        try:
            with open(self.log_path, "a") as f:
                f.write(f"{msg}\n")
        except:
            pass

    def on_resize(self, widget, width, height, **kwargs):
        self.canvas_width = width
        self.canvas_height = height
        self.log(f"Resize: {width}x{height}")
        self.redraw()

    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)

    def on_touch_up(self, widget, x, y, **kwargs):
        if not self.touch_start:
            return
        # Toggle state on any touch
        if self.state == "MENU":
            self.state = "PLAY"
            self.color = "green"
            self.log("Switched to PLAY")
        else:
            self.state = "MENU"
            self.color = "blue"
            self.log("Switched to MENU")
        self.touch_start = None
        self.redraw()

    def redraw(self):
        try:
            self.debug_label.text = f"State:{self.state} W:{self.canvas_width} H:{self.canvas_height}"

            # Fill entire canvas with current color
            with self.canvas.fill(color=self.color):
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
            self.log(f"redraw exception: {e}")
            self.log(traceback.format_exc())
            self.debug_label.text = f"ERROR: {str(e)[:50]}"

def main():
    return HungrySnake4K()