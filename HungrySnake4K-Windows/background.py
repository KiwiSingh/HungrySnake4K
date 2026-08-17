import random
from PIL import Image, ImageOps, ImageTk

BACKGROUND_FILES = tuple(
    f"assets/backgrounds/background_{number:02}.png"
    for number in range(1, 11)
)

class Background:
    def __init__(self, screen, get_resource_path, x_limit, y_limit):
        self.screen = screen
        self.get_resource_path = get_resource_path
        self.x_limit = x_limit
        self.y_limit = y_limit
        self.canvas = screen.getcanvas()
        self.image_item = None
        self.photo_image = None

    def randomize(self):
        background_path = self.get_resource_path(random.choice(BACKGROUND_FILES))

        # Ensure width and height are strictly mapped to the playable grid bounds
        target_width = max(1, self.x_limit * 2)
        target_height = max(1, self.y_limit * 2)

        with Image.open(background_path) as source_image:
            # Pad exactly to the playable bounds so users see where the boundary is
            fitted_background = ImageOps.pad(
                source_image.convert("RGB"),
                (target_width, target_height),
                method=Image.Resampling.LANCZOS,
                color=(0, 0, 0)
            )

        self.photo_image = ImageTk.PhotoImage(fitted_background)

        if self.image_item is None:
            self.image_item = self.canvas.create_image(
                0,
                0,
                image=self.photo_image,
            )
        else:
            self.canvas.itemconfig(self.image_item, image=self.photo_image)

        self.canvas.tag_lower(self.image_item)