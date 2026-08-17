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


class Food(Turtle):
    def __init__(self, x_limit, y_limit):
        super().__init__()

        self.x_limit = x_limit
        self.y_limit = y_limit
        self.shape("turtle")
        self.penup()
        self.shapesize(stretch_len=0.5, stretch_wid=0.5)
        self.speed("fastest")

        self.refresh()

    def refresh(self):
        self.foodcolor = random.choice(COLORS)
        self.color(self.foodcolor)

        random_x = random.randrange(-self.x_limit, self.x_limit + 20, 20)
        random_y = random.randrange(-self.y_limit, self.y_limit + 20, 20)
        self.goto(random_x, random_y)
