from turtle import Turtle
import random

COLORS = [
    "white",
    "red",
    "green",
    "blue",
    "cyan",
    "magenta",
    "yellow",
    "gray",
    "orange",
    "purple",
    "brown",
    "pink",
    "gold",
    "violet",
    "indigo",
    "lime",
    "navy",
    "teal",
    "maroon",
    "olive",
    "silver",
    "coral",
    "salmon",
    "tomato",
    "khaki",
    "beige",
    "ivory",
    "lavender",
    "turquoise",
    "aquamarine",
    "chocolate",
    "crimson",
    "plum",
    "orchid",
    "tan",
    "wheat",
]

SPECIAL_FOOD_COLORS = {"gold", "silver"}
ANIMATE_SPECIAL_FOOD = True
NORMAL_SIZE = 0.5
SPECIAL_SIZE = 0.7


class Food(Turtle):
    def __init__(self, x_limit, y_limit):
        super().__init__()

        self.x_limit = x_limit
        self.y_limit = y_limit
        self.shape("turtle")
        self.penup()
        self.shapesize(stretch_len=NORMAL_SIZE, stretch_wid=NORMAL_SIZE)
        self.speed("fastest")
        self.animation_tick = 0

        self.refresh()

    def refresh(self):
        self.foodcolor = random.choice(COLORS)
        self.animation_tick = 0

        if self.foodcolor in SPECIAL_FOOD_COLORS:
            self.color("white", self.foodcolor)
            self.shapesize(stretch_len=SPECIAL_SIZE, stretch_wid=SPECIAL_SIZE)
        else:
            self.color(self.foodcolor)
            self.shapesize(stretch_len=NORMAL_SIZE, stretch_wid=NORMAL_SIZE)

        random_x = random.randrange(-self.x_limit, self.x_limit + 20, 20)
        random_y = random.randrange(-self.y_limit, self.y_limit + 20, 20)
        self.goto(random_x, random_y)

    def animate(self):
        if not ANIMATE_SPECIAL_FOOD:
            return

        if self.foodcolor not in SPECIAL_FOOD_COLORS:
            return

        self.animation_tick += 1

        if self.animation_tick % 8 < 4:
            size = SPECIAL_SIZE
        else:
            size = NORMAL_SIZE

        self.shapesize(stretch_len=size, stretch_wid=size)
