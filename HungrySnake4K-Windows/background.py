import random

from PIL import Image, ImageOps, ImageTk


BACKGROUND_FILES = tuple(
    f"assets/backgrounds/background_{number:02}.png"
    for number in range(1, 11)
)


class Background:
    def __init__(self, screen, get_resource_path):
        self.screen = screen
        self.get_resource_path = get_resource_path
        self.canvas = screen.getcanvas()
        self.image_item = None
        self.photo_image = None

    def randomize(self):
        background_path = self.get_resource_path(random.choice(BACKGROUND_FILES))

        # Prevent PIL from receiving a 0 dimension during resize events
        target_width = max(1, self.screen.window_width())
        target_height = max(1, self.screen.window_height())

        with Image.open(background_path) as source_image:
            fitted_background = ImageOps.fit(
                source_image.convert("RGB"),
                (target_width, target_height),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
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
