import pygame  # type: ignore
from turtle import Screen
from food import Food
from scoreboard import Scoreboard
from snake import Snake
import time
from controller import Controller
from background import Background
from pathlib import Path
import sys
import os

def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        if sys.platform == "darwin":
            return (Path(sys.executable).resolve().parent.parent / "Resources" / relative_path)
        return Path(sys.executable).resolve().parent / relative_path
    return Path(__file__).resolve().parent / relative_path

background_score_path = get_resource_path("assets/background_score.mp3")
food_sound_path = get_resource_path("assets/food_blip.wav")
game_over_sound_path = get_resource_path("assets/game_over.wav")

pygame.mixer.init()
pygame.mixer.set_num_channels(8)
pygame.mixer.music.load(str(background_score_path))
pygame.mixer.music.set_volume(0.4)

food_sound = pygame.mixer.Sound(str(food_sound_path))
food_sound.set_volume(0.7)

game_over_sound = pygame.mixer.Sound(str(game_over_sound_path))
game_over_sound.set_volume(0.8)

def load_placeholder_sound(filename, fallback_sound):
    filepath = get_resource_path(f"assets/{filename}")
    if os.path.exists(filepath):
        snd = pygame.mixer.Sound(str(filepath))
        snd.set_volume(0.8)
        return snd
    return fallback_sound

player1_begin_sound = load_placeholder_sound("player1_begin.wav", food_sound)
player2_begin_sound = load_placeholder_sound("player2_begin.wav", food_sound)
player1_wins_sound = load_placeholder_sound("player1_wins.wav", game_over_sound)
player2_wins_sound = load_placeholder_sound("player2_wins.wav", game_over_sound)
its_a_draw_sound = load_placeholder_sound("its_a_draw.wav", game_over_sound)

screen = Screen()
screen.setup(width=0.9, height=0.9)
screen.bgcolor("black")
screen.title("Hungry Snake 4K")
screen.tracer(0)

GRID_SIZE = 20
X_LIMIT = int((screen.window_width() // 2 // GRID_SIZE) * GRID_SIZE - GRID_SIZE)
Y_LIMIT = int((screen.window_height() // 2 // GRID_SIZE) * GRID_SIZE - GRID_SIZE)

background = Background(screen, get_resource_path, X_LIMIT, Y_LIMIT)
snake = Snake()
food = Food(X_LIMIT, Y_LIMIT)
scoreboard = Scoreboard(Y_LIMIT - 40)
controller = Controller()

game_state = "MENU"
multiplayer = False
p1_score = 0
p2_score = 0
current_level_points = 0
points_to_next_level = 20

def hide_snake():
    for segment in snake.segments:
        segment.goto(2000, 2000)
        segment.hideturtle()
    food.hideturtle()
    food.goto(2000, 2000)

def show_menu():
    hide_snake()
    scoreboard.clear()
    scoreboard.show_message("HUNGRY SNAKE 4K", size=48, y_offset=60)
    scoreboard.show_message("Press 1 (or Circle/B) for Single Player", size=24, y_offset=0)
    scoreboard.show_message("Press 2 (or Cross/A) for Multiplayer (2P)", size=24, y_offset=-40)

def start_game(num_players):
    global game_state, multiplayer, p1_score, p2_score
    multiplayer = (num_players == 2)
    p1_score = 0
    p2_score = 0
    game_state = "P1_PLAY"
    
    if multiplayer:
        player1_begin_sound.play()
        
    reset_player_state()
    pygame.mixer.music.play(loops=-1)

def reset_player_state():
    global current_level_points, points_to_next_level
    current_level_points = 0
    points_to_next_level = 20
    scoreboard.reset()
    background.randomize()
    snake.reset()
    food.showturtle()
    food.refresh()

def check_level_up():
    global current_level_points, points_to_next_level
    if current_level_points >= points_to_next_level:
        scoreboard.level_up()
        points_to_next_level = (scoreboard.level + 1) * 10
        current_level_points = 0
        background.randomize()

def end_turn():
    global game_state, p1_score, p2_score
    pygame.mixer.music.stop()
    hide_snake()

    if game_state == "P1_PLAY":
        p1_score = scoreboard.score
        if multiplayer:
            game_over_sound.play()
            game_state = "P2_TRANSITION"
            scoreboard.clear()
            scoreboard.show_message("PLAYER 1 CRASHED!", size=36, y_offset=60)
            scoreboard.show_message(f"P1 Score: {p1_score}", size=24, y_offset=10)
            scoreboard.show_message("Player 2 - Press ENTER (or any button) to start", size=24, y_offset=-40)
        else:
            game_state = "GAME_OVER"
            display_results()
    elif game_state == "P2_PLAY":
        p2_score = scoreboard.score
        display_results()

def display_results():
    global game_state
    scoreboard.clear()
    channel = pygame.mixer.find_channel()
    
    if multiplayer:
        if p1_score > p2_score:
            if channel:
                channel.play(player1_wins_sound)
                if player1_wins_sound != game_over_sound:
                    channel.queue(game_over_sound)
            game_state = "GAME_OVER"
            scoreboard.show_message("PLAYER 1 WINS!", size=48, y_offset=60)
            scoreboard.show_message(f"P1: {p1_score}   P2: {p2_score}", size=24, y_offset=0)
            scoreboard.show_message("Press ENTER (or any button) to return", size=24, y_offset=-50)
            
        elif p2_score > p1_score:
            if channel:
                channel.play(player2_wins_sound)
                if player2_wins_sound != game_over_sound:
                    channel.queue(game_over_sound)
            game_state = "GAME_OVER"
            scoreboard.show_message("PLAYER 2 WINS!", size=48, y_offset=60)
            scoreboard.show_message(f"P1: {p1_score}   P2: {p2_score}", size=24, y_offset=0)
            scoreboard.show_message("Press ENTER (or any button) to return", size=24, y_offset=-50)
            
        else:
            if channel:
                channel.play(its_a_draw_sound)
            game_state = "REMATCH_PROMPT"
            scoreboard.show_message("IT'S A TIE!", size=48, y_offset=60)
            scoreboard.show_message(f"Score: {p1_score}", size=24, y_offset=10)
            scoreboard.show_message("Rematch? 1 (Yes)  |  2 (No)", size=24, y_offset=-40)
    else:
        if channel:
            channel.play(game_over_sound)
        game_state = "GAME_OVER"
        scoreboard.show_message("GAME OVER", size=48, y_offset=60)
        scoreboard.show_message(f"Final Score: {p1_score}", size=24, y_offset=0)
        scoreboard.show_message("Press ENTER (or any button) to return", size=24, y_offset=-50)

def handle_1():
    if game_state == "MENU": 
        start_game(1)
    elif game_state == "REMATCH_PROMPT":
        start_game(2)

def handle_2():
    global game_state  # <--- Move this to the very top!
    
    if game_state == "MENU": 
        start_game(2)
    elif game_state == "REMATCH_PROMPT":
        game_over_sound.play()
        game_state = "MENU"
        show_menu()

def handle_enter(event=None):
    global game_state
    if game_state == "P2_TRANSITION":
        game_state = "P2_PLAY"
        player2_begin_sound.play()
        reset_player_state()
        pygame.mixer.music.play(loops=-1)
    elif game_state == "GAME_OVER":
        game_state = "MENU"
        show_menu()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")
screen.onkey(handle_1, "1")
screen.onkey(handle_2, "2")
screen.onkey(handle_enter, "Return")
screen.getcanvas().bind_all("<Return>", handle_enter)

show_menu()

def game_loop():
    global current_level_points

    pressed_buttons = controller.update(snake)

    if game_state in ["P1_PLAY", "P2_PLAY"]:
        snake.move()
        food.animate()

        if snake.head.distance(food) < 15:
            food_sound.play()
            old_score = scoreboard.score
            scoreboard.increase_score(food)
            current_level_points += (scoreboard.score - old_score)
            
            check_level_up()
            snake.extend()
            food.refresh()

        if (
            snake.head.xcor() > X_LIMIT
            or snake.head.xcor() < -X_LIMIT
            or snake.head.ycor() > Y_LIMIT
            or snake.head.ycor() < -Y_LIMIT
        ):
            end_turn()

        for segment in snake.segments[1:]:
            if snake.head.distance(segment) < 10:
                end_turn()
    else:
        if game_state == "MENU":
            if 1 in pressed_buttons:
                start_game(1)
            elif 0 in pressed_buttons:
                start_game(2)
        elif game_state == "REMATCH_PROMPT":
            if 1 in pressed_buttons:
                start_game(2)
            elif 0 in pressed_buttons:
                game_over_sound.play()
                handle_enter() # Triggers transition to menu
        elif game_state in ["P2_TRANSITION", "GAME_OVER"]:
            if any(pressed_buttons):
                handle_enter()

    screen.update()
    screen.ontimer(game_loop, 100)

game_loop()
screen.mainloop()