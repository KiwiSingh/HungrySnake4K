import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import asyncio
import traceback

class HungrySnake4K(toga.App):
    def startup(self):
        # Platform detection
        if hasattr(sys, 'getandroidapilevel'):
            self.platform = 'android'
        elif sys.platform == "ios":
            self.platform = 'ios'
        else:
            self.platform = 'desktop'

        # Log file
        self.log_path = self.paths.data / "debug.log"
        try:
            with open(self.log_path, "w") as f:
                f.write("=== App started ===\n")
        except:
            pass
        self.log("Startup: platform = " + self.platform)

        # Canvas dimensions
        self.canvas_width = 400
        self.canvas_height = 800

        # Simple state for color toggling
        self.color = "blue"

        # Canvas with black background
        self.canvas = toga.Canvas(
            style=Pack(flex=1, background_color="black"),
            on_resize=self.on_resize,
        )

        # Debug label
        self.debug_label = toga.Label(
            "Starting...",
            style=Pack(padding=10, color="white", background_color="black", font_size=12)
        )

        box = toga.Box(children=[self.canvas, self.debug_label], style=Pack(direction=COLUMN, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        # Force initial draw
        self.redraw()

        # Start a simple timer to change color every 2 seconds to test updates
        self.log("Starting color change timer")
        asyncio.create_task(self.color_loop())

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

    async def color_loop(self):
        colors = ["blue", "green", "red", "yellow", "cyan"]
        i = 0
        while True:
            await asyncio.sleep(2)
            self.color = colors[i % len(colors)]
            i += 1
            self.log(f"Changing color to {self.color}")
            self.redraw()

    def redraw(self):
        try:
            # Update debug label
            self.debug_label.text = f"Color: {self.color} W:{self.canvas_width} H:{self.canvas_height}"

            # Clear and fill with the current color using the simplest context
            with self.canvas.fill(color=self.color):
                self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            # Force native redraw on iOS
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