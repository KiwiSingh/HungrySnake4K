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
    def __init__(self):
        super().__init__()

        self.shape("turtle")
        self.penup()
        self.shapesize(stretch_len=0.5, stretch_wid=0.5)
        self.speed("fastest")

        self.refresh()

    def refresh(self):
        self.foodcolor = random.choice(COLORS)
        self.color(self.foodcolor)

        random_x = random.randrange(-1060, 1060, 20)
        random_y = random.randrange(-1060, 1060, 20)
        self.goto(random_x, random_y)