from turtle import Screen
from food import Food
from scoreboard import Scoreboard
from snake import Snake
import time
from controller import Controller

screen = Screen()
screen.setup(width=2160, height=2160)
screen.bgcolor("black")
screen.title("Hungry Snake 4K")
screen.tracer(0)

snake = Snake()
food = Food()
scoreboard = Scoreboard()
controller = Controller()


screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")


game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)

    controller.update(snake)
    snake.move()

    # Detect collision with food
    if snake.head.distance(food) < 15:
        scoreboard.increase_score(food)
        snake.extend()
        food.refresh()

    # Detect collision with wall
    if snake.head.xcor() > 1060 or snake.head.xcor() < -1060 or snake.head.ycor() > 1060 or snake.head.ycor() < -1060:
        game_is_on = False
        scoreboard.game_over()

    # Detect collision with tail
    for segment in snake.segments[1:]:
        if snake.head.distance(segment) < 10:
            game_is_on = False
            scoreboard.game_over()

screen.exitonclick()