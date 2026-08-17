from turtle import Turtle

ALIGNMENT = "center"
FONT = ("Apple Color Emoji", 24, "normal")
FONT_LARGE = ("Apple Color Emoji", 48, "normal")


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()

        self.score = 0
        self.color("white")
        self.penup()
        self.goto(0, 1020)
        self.update_scoreboard()
        self.hideturtle()

    def update_scoreboard(self):
        self.clear()
        self.goto(0, 1020)
        self.write(
            f"Score: {self.score}",
            align=ALIGNMENT,
            font=FONT
        )

    def game_over(self):
        self.goto(0, 0)
        self.color("red")
        self.write(
            "GAME OVER",
            align=ALIGNMENT,
            font=FONT_LARGE
        )

    def increase_score(self, food):
        if food.foodcolor == "gold":
            self.score += 10
        elif food.foodcolor == "silver":
            self.score += 5
        else:
            self.score += 1

        self.update_scoreboard()