from turtle import Turtle

ALIGNMENT = "center"
FONT = ("Courier New", 24, "normal")

class Scoreboard(Turtle):
    def __init__(self, score_y):
        super().__init__()

        self.score = 0
        self.level = 1
        self.score_y = score_y
        self.color("white")
        self.penup()
        self.goto(0, self.score_y)
        self.update_scoreboard()
        self.hideturtle()

    def update_scoreboard(self):
        self.clear()
        self.goto(0, self.score_y)
        self.write(
            f"Level: {self.level}   Score: {self.score}",
            align=ALIGNMENT,
            font=FONT
        )

    def show_message(self, message, size=48, y_offset=0):
        self.goto(0, y_offset)
        self.color("red")
        self.write(
            message,
            align=ALIGNMENT,
            font=("Courier New", size, "bold")
        )

    def increase_score(self, food):
        if food.foodcolor == "gold":
            self.score += 10
        elif food.foodcolor == "silver":
            self.score += 5
        else:
            self.score += 1

        self.update_scoreboard()
        return self.score
        
    def level_up(self):
        self.level += 1
        self.update_scoreboard()

    def reset(self):
        self.score = 0
        self.level = 1
        self.color("white")
        self.clear()
        self.update_scoreboard()