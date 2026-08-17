import pygame
import random
import sys
import os
from pathlib import Path

# --- Constants & Colors ---
GRID_SIZE = 40
COLORS = [
    (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255),
    (255, 0, 255), (255, 255, 0), (128, 128, 128), (255, 165, 0), (128, 0, 128)
]
SPECIAL_COLORS = {(255, 215, 0): "gold", (192, 192, 192): "silver"}

def get_resource_path(relative_path):
    # Briefcase runs the app from the root folder where `assets` is bundled alongside `src`
    base_path = Path(__file__).resolve().parent.parent.parent
    return base_path / relative_path

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)

    # Setup Mobile Fullscreen Display
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("courier", int(WIDTH * 0.08), bold=True)
    font_small = pygame.font.SysFont("courier", int(WIDTH * 0.04), bold=True)

    # --- Load Audio ---
    def load_snd(filename, vol=0.8):
        path = get_resource_path(f"assets/{filename}")
        if os.path.exists(path):
            snd = pygame.mixer.Sound(str(path))
            snd.set_volume(vol)
            return snd
        return None

    music_path = get_resource_path("assets/background_score.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(str(music_path))
        pygame.mixer.music.set_volume(0.4)

    food_snd = load_snd("food_blip.wav", 0.7)
    game_over_snd = load_snd("game_over.wav", 0.8)
    p1_begin_snd = load_snd("player1_begin.wav", 0.8) or food_snd
    p2_begin_snd = load_snd("player2_begin.wav", 0.8) or food_snd
    p1_wins_snd = load_snd("player1_wins.wav", 0.8) or game_over_snd
    p2_wins_snd = load_snd("player2_wins.wav", 0.8) or game_over_snd
    draw_snd = load_snd("its_a_draw.wav", 0.8) or game_over_snd

    # --- Background Loading ---
    def load_background():
        bg_num = random.randint(1, 10)
        bg_path = get_resource_path(f"assets/backgrounds/background_{bg_num:02}.png")
        if os.path.exists(bg_path):
            img = pygame.image.load(str(bg_path)).convert()
            return pygame.transform.scale(img, (WIDTH, HEIGHT))
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill((20, 20, 20))
        return surface

    current_bg = load_background()

    # --- Game State Variables ---
    state = "MENU"
    multiplayer = False
    p1_score = 0
    p2_score = 0
    current_score = 0
    level = 1
    current_level_points = 0
    points_to_next_level = 20

    snake = []
    snake_dir = (1, 0)
    food_pos = (0, 0)
    food_color = (255, 255, 255)
    touch_start = None

    def reset_player():
        nonlocal snake, snake_dir, current_score, current_level_points, points_to_next_level, level, current_bg
        center_x = (WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        center_y = (HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        snake = [(center_x - i*GRID_SIZE, center_y) for i in range(3)]
        snake_dir = (1, 0)
        current_score = 0
        current_level_points = 0
        points_to_next_level = 20
        level = 1
        current_bg = load_background()
        spawn_food()

    def spawn_food():
        nonlocal food_pos, food_color
        max_x = (WIDTH // GRID_SIZE) - 2
        max_y = (HEIGHT // GRID_SIZE) - 2
        while True:
            fx = random.randint(1, max_x) * GRID_SIZE
            fy = random.randint(1, max_y) * GRID_SIZE
            food_pos = (fx, fy)
            if food_pos not in snake:
                break
        
        is_special = random.random() < 0.15
        if is_special:
            food_color = random.choice(list(SPECIAL_COLORS.keys()))
        else:
            food_color = random.choice(COLORS[:10])

    def draw_text(text, font, color, y_offset):
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        screen.blit(text_surface, rect)

    def draw_tap_zones(top_text, bottom_text):
        # Top half tap hint
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, HEIGHT//2))
        draw_text(top_text, font_small, (200, 200, 200), -HEIGHT//4)
        # Bottom half tap hint
        pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT//2, WIDTH, HEIGHT//2))
        draw_text(bottom_text, font_small, (200, 200, 200), HEIGHT//4)

    def trigger_game_over(crashed_player):
        nonlocal state, p1_score, p2_score
        pygame.mixer.music.stop()
        
        if crashed_player == 1:
            p1_score = current_score
            if multiplayer:
                if game_over_snd: game_over_snd.play()
                state = "P2_TRANSITION"
            else:
                if game_over_snd: game_over_snd.play()
                state = "GAME_OVER"
        else:
            p2_score = current_score
            evaluate_winner()

    def evaluate_winner():
        nonlocal state
        if p1_score > p2_score:
            if p1_wins_snd: p1_wins_snd.play()
            pygame.time.set_timer(pygame.USEREVENT, int(p1_wins_snd.get_length() * 1000), 1)
            state = "GAME_OVER"
        elif p2_score > p1_score:
            if p2_wins_snd: p2_wins_snd.play()
            pygame.time.set_timer(pygame.USEREVENT, int(p2_wins_snd.get_length() * 1000), 1)
            state = "GAME_OVER"
        else:
            if draw_snd: draw_snd.play()
            state = "REMATCH_PROMPT"

    # --- Main Game Loop ---
    running = True
    while running:
        clock.tick(15)  # 15 FPS dictates snake speed
        
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Queue game over sound after win sound finishes
            if event.type == pygame.USEREVENT:
                if game_over_snd: game_over_snd.play()

            # Touch / Mouse inputs for mobile swipe and menu tapping
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if event.type == pygame.FINGERDOWN:
                    touch_start = (event.x * WIDTH, event.y * HEIGHT)
                else:
                    touch_start = event.pos

                ty = touch_start[1]

                if state == "MENU":
                    if ty < HEIGHT // 2:
                        multiplayer = False
                        reset_player()
                        state = "P1_PLAY"
                        pygame.mixer.music.play(loops=-1)
                    else:
                        multiplayer = True
                        reset_player()
                        state = "P1_PLAY"
                        if p1_begin_snd: p1_begin_snd.play()
                        pygame.mixer.music.play(loops=-1)

                elif state == "REMATCH_PROMPT":
                    if ty < HEIGHT // 2:
                        reset_player()
                        state = "P1_PLAY"
                        if p1_begin_snd: p1_begin_snd.play()
                        pygame.mixer.music.play(loops=-1)
                    else:
                        if game_over_snd: game_over_snd.play()
                        state = "MENU"

                elif state in ["P2_TRANSITION", "GAME_OVER"]:
                    if state == "P2_TRANSITION":
                        reset_player()
                        state = "P2_PLAY"
                        if p2_begin_snd: p2_begin_snd.play()
                        pygame.mixer.music.play(loops=-1)
                    else:
                        state = "MENU"

            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                if touch_start and state in ["P1_PLAY", "P2_PLAY"]:
                    if event.type == pygame.FINGERUP:
                        touch_end = (event.x * WIDTH, event.y * HEIGHT)
                    else:
                        touch_end = event.pos

                    dx = touch_end[0] - touch_start[0]
                    dy = touch_end[1] - touch_start[1]

                    # Minimum swipe threshold
                    if abs(dx) > 30 or abs(dy) > 30:
                        if abs(dx) > abs(dy):
                            if dx > 0 and snake_dir != (-1, 0): snake_dir = (1, 0)
                            elif dx < 0 and snake_dir != (1, 0): snake_dir = (-1, 0)
                        else:
                            if dy > 0 and snake_dir != (0, -1): snake_dir = (0, 1)
                            elif dy < 0 and snake_dir != (0, 1): snake_dir = (0, -1)
                touch_start = None

        # --- Game Logic ---
        if state in ["P1_PLAY", "P2_PLAY"]:
            new_head = (snake[0][0] + snake_dir[0] * GRID_SIZE, snake[0][1] + snake_dir[1] * GRID_SIZE)
            
            # Wall Collision
            if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
                trigger_game_over(1 if state == "P1_PLAY" else 2)
            # Tail Collision
            elif new_head in snake:
                trigger_game_over(1 if state == "P1_PLAY" else 2)
            else:
                snake.insert(0, new_head)
                
                # Food Collision
                if abs(new_head[0] - food_pos[0]) < GRID_SIZE and abs(new_head[1] - food_pos[1]) < GRID_SIZE:
                    if food_snd: food_snd.play()
                    pts = 10 if food_color == (255, 215, 0) else 5 if food_color == (192, 192, 192) else 1
                    current_score += pts
                    current_level_points += pts
                    
                    if current_level_points >= points_to_next_level:
                        level += 1
                        points_to_next_level = (level + 1) * 10
                        current_level_points = 0
                        current_bg = load_background()
                    
                    spawn_food()
                else:
                    snake.pop()

        # --- Rendering ---
        screen.fill((0, 0, 0))

        if state in ["P1_PLAY", "P2_PLAY"]:
            screen.blit(current_bg, (0, 0))
            
            # Draw Food
            pygame.draw.rect(screen, food_color, (food_pos[0], food_pos[1], GRID_SIZE, GRID_SIZE))
            
            # Draw Snake
            for segment in snake:
                pygame.draw.rect(screen, (255, 255, 255), (segment[0], segment[1], GRID_SIZE, GRID_SIZE))
            
            # Scoreboard
            score_text = font_small.render(f"Level: {level}   Score: {current_score}", True, (255, 255, 255))
            screen.blit(score_text, (20, 20))

        elif state == "MENU":
            draw_tap_zones("TAP HERE FOR 1 PLAYER", "TAP HERE FOR 2 PLAYERS")
            draw_text("HUNGRY SNAKE 4K", font_large, (255, 0, 0), -50)
            
        elif state == "REMATCH_PROMPT":
            draw_tap_zones("TAP HERE FOR YES (REMATCH)", "TAP HERE FOR NO (MENU)")
            draw_text("IT'S A TIE!", font_large, (255, 0, 0), -50)
            draw_text(f"Score: {p1_score}", font_small, (255, 255, 255), 10)

        elif state == "P2_TRANSITION":
            draw_text("PLAYER 1 CRASHED!", font_large, (255, 0, 0), -60)
            draw_text(f"P1 Score: {p1_score}", font_small, (255, 255, 255), 0)
            draw_text("TAP ANYWHERE FOR P2 TURN", font_small, (200, 200, 200), 80)

        elif state == "GAME_OVER":
            if multiplayer:
                winner = "PLAYER 1 WINS!" if p1_score > p2_score else "PLAYER 2 WINS!"
                draw_text(winner, font_large, (255, 0, 0), -60)
                draw_text(f"P1: {p1_score}   P2: {p2_score}", font_small, (255, 255, 255), 0)
            else:
                draw_text("GAME OVER", font_large, (255, 0, 0), -60)
                draw_text(f"Final Score: {p1_score}", font_small, (255, 255, 255), 0)
            draw_text("TAP ANYWHERE TO RETURN", font_small, (200, 200, 200), 80)

        pygame.display.flip()

    pygame.quit()
    sys.exit()