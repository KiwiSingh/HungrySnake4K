import pygame # type: ignore
from turtle import Screen
from food import Food
from scoreboard import Scoreboard
from snake import Snake
import time
from controller import Controller
from pathlib import Path
import sys


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path

        if sys.platform == "darwin":
            return (
                Path(sys.executable).resolve().parent.parent
                / "Resources"
                / relative_path
            )

        return Path(sys.executable).resolve().parent / relative_path

    return Path(__file__).resolve().parent / relative_path


background_score_path = get_resource_path("assets/background_score.mp3")
food_sound_path = get_resource_path("assets/food_blip.wav")
game_over_sound_path = get_resource_path("assets/game_over.wav")

pygame.mixer.init()

pygame.mixer.music.load(str(background_score_path))
pygame.mixer.music.set_volume(0.4)

food_sound = pygame.mixer.Sound(str(food_sound_path))
food_sound.set_volume(0.7)

game_over_sound = pygame.mixer.Sound(str(game_over_sound_path))
game_over_sound.set_volume(0.8)

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


def restart_game():
    global game_is_on

    snake.reset()
    food.refresh()
    scoreboard.reset()
    game_is_on = True
    pygame.mixer.music.unpause()


def end_game():
    global game_is_on

    if game_is_on:
        game_is_on = False
        pygame.mixer.music.pause()
        scoreboard.game_over()
        game_over_sound.play()


def handle_keypress(event):
    if not game_is_on:
        restart_game()


screen.getcanvas().bind_all("<KeyPress>", handle_keypress)
screen.listen()

pygame.mixer.music.play(loops=-1)

while True:
    screen.update()
    time.sleep(0.1)

    controller_button_pressed = controller.update(snake)

    if not game_is_on:
        if controller_button_pressed:
            restart_game()
        continue

    snake.move()

    # Detect collision with food

    if snake.head.distance(food) < 15:
        food_sound.play()
        scoreboard.increase_score(food)
        snake.extend()
        food.refresh()

    # Detect collision with wall
    if (
        snake.head.xcor() > 1060
        or snake.head.xcor() < -1060
        or snake.head.ycor() > 1060
        or snake.head.ycor() < -1060
    ):
        end_game()

    # Detect collision with tail
    for segment in snake.segments[1:]:
        if snake.head.distance(segment) < 10:
            end_game()