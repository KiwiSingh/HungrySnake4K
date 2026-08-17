import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from toga.constants import Baseline
import random
import asyncio
import traceback
import os

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class HungrySnake4K(toga.App):
    def startup(self):
        # Platform detection
        if hasattr(sys, 'getandroidapilevel'):
            self.platform = 'android'
        elif sys.platform == "ios":
            self.platform = 'ios'
        else:
            self.platform = 'desktop'

        # Debug log
        self.log_path = self.paths.data / "debug.log"
        try:
            with open(self.log_path, "w") as f:
                f.write("=== App started ===\n")
        except:
            pass
        self.log("Startup: platform = " + self.platform)

        # Game settings
        self.grid_size = 40
        self.DEFAULT_WIDTH = 400
        self.DEFAULT_HEIGHT = 800
        self.canvas_width = self.DEFAULT_WIDTH
        self.canvas_height = self.DEFAULT_HEIGHT

        # State
        self.state = "MENU"
        self.multiplayer = False
        self.p1_score = 0
        self.p2_score = 0
        self.current_score = 0
        self.level = 1
        self.current_level_points = 0
        self.points_to_next_level = 20

        self.snake = []
        self.snake_dir = (1, 0)
        self.food_pos = (0, 0)
        self.food_color = "white"
        self.touch_start = None

        self.init_audio()
        self.init_backgrounds()

        # Canvas
        self.canvas = toga.Canvas(
            style=Pack(flex=1, background_color="black"),
            on_resize=self.on_resize,
            on_press=self.on_touch_down,
            on_release=self.on_touch_up,
        )

        # Debug label – now we'll also show recent log entries on the menu
        self.debug_label = toga.Label(
            "Starting...",
            style=Pack(padding=10, color="white", background_color="black", font_size=12)
        )

        box = toga.Box(children=[self.canvas, self.debug_label], style=Pack(direction=COLUMN, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        self.redraw()
        self.log("Creating game loop task")
        asyncio.create_task(self.game_loop(None))
        self.add_background_task(self.game_loop)   # fallback

        self.log("Startup complete")

    def log(self, msg):
        try:
            with open(self.log_path, "a") as f:
                f.write(f"{msg}\n")
        except:
            pass

    def get_recent_log(self, lines=10):
        """Return the last `lines` lines of the log file as a string."""
        try:
            with open(self.log_path, "r") as f:
                all_lines = f.readlines()
            return "".join(all_lines[-lines:])
        except:
            return "Log not available"

    # ---------- Audio (with extra logging) ----------
    def init_audio(self):
        self.audio_players = {}
        self.bg_player = None
        sfx_files = {
            "food_blip": "food_blip.wav",
            "game_over": "game_over.wav",
            "player1_begin": "player1_begin.wav",
            "player2_begin": "player2_begin.wav",
            "player1_wins": "player1_wins.wav",
            "player2_wins": "player2_wins.wav",
            "its_a_draw": "its_a_draw.wav"
        }
        try:
            if self.platform == 'ios':
                from rubicon.objc import ObjCClass
                from ctypes import cdll
                from ctypes.util import find_library
                cdll.LoadLibrary(find_library('AVFoundation'))
                AVAudioPlayer = ObjCClass('AVAudioPlayer')
                NSURL = ObjCClass('NSURL')

                bg_path = self.paths.app / "assets" / "background_score.mp3"
                if bg_path.exists():
                    url = NSURL.fileURLWithPath_(str(bg_path))
                    self.bg_player = AVAudioPlayer.alloc().initWithContentsOfURL_error_(url, None)
                    if self.bg_player:
                        self.bg_player.numberOfLoops = -1
                        self.bg_player.volume = 0.4
                        self.bg_player.prepareToPlay()
                        self.log("iOS bg player created")
                else:
                    self.log("iOS bg file missing: " + str(bg_path))

                for key, filename in sfx_files.items():
                    path = self.paths.app / "assets" / filename
                    if path.exists():
                        url = NSURL.fileURLWithPath_(str(path))
                        player = AVAudioPlayer.alloc().initWithContentsOfURL_error_(url, None)
                        if player:
                            player.volume = 0.8
                            player.prepareToPlay()
                            self.audio_players[key] = player
                            self.log(f"iOS SFX loaded: {key}")
                    else:
                        self.log(f"iOS SFX missing: {key}")

            elif self.platform == 'android':
                from java import jclass
                MediaPlayer = jclass('android.media.MediaPlayer')
                bg_path = self.paths.app / "assets" / "background_score.mp3"
                if bg_path.exists():
                    self.bg_player = MediaPlayer()
                    self.bg_player.setDataSource(str(bg_path))
                    self.bg_player.setLooping(True)
                    self.bg_player.setVolume(0.4, 0.4)
                    self.bg_player.prepare()
                    self.log("Android bg player created")
                for key, filename in sfx_files.items():
                    path = self.paths.app / "assets" / filename
                    if path.exists():
                        player = MediaPlayer()
                        player.setDataSource(str(path))
                        player.setVolume(0.8, 0.8)
                        player.prepare()
                        self.audio_players[key] = player
                        self.log(f"Android SFX loaded: {key}")
            else:
                if not PYGAME_AVAILABLE:
                    self.log("Pygame not available, skipping audio")
                    return
                pygame.mixer.init()
                pygame.mixer.set_num_channels(8)
                bg_path = self.paths.app / "assets" / "background_score.mp3"
                if bg_path.exists():
                    pygame.mixer.music.load(str(bg_path))
                    pygame.mixer.music.set_volume(0.4)
                    self.log("Desktop bg loaded")
                for key, filename in sfx_files.items():
                    path = self.paths.app / "assets" / filename
                    if path.exists():
                        snd = pygame.mixer.Sound(str(path))
                        snd.set_volume(0.8)
                        self.audio_players[key] = snd
                        self.log(f"Desktop SFX loaded: {key}")
        except Exception as e:
            self.log(f"init_audio exception: {e}")
            traceback.print_exc()

    def play_sound(self, sound_key):
        try:
            if self.platform == 'ios':
                if sound_key in self.audio_players:
                    self.audio_players[sound_key].currentTime = 0
                    self.audio_players[sound_key].play()
            elif self.platform == 'android':
                if sound_key in self.audio_players:
                    self.audio_players[sound_key].seekTo(0)
                    self.audio_players[sound_key].start()
            else:
                if PYGAME_AVAILABLE and sound_key in self.audio_players:
                    self.audio_players[sound_key].play()
        except Exception as e:
            self.log(f"play_sound error: {e}")

    def play_bgm(self):
        try:
            if self.platform == 'ios':
                if self.bg_player: self.bg_player.play()
            elif self.platform == 'android':
                if self.bg_player: self.bg_player.start()
            else:
                if PYGAME_AVAILABLE: pygame.mixer.music.play(loops=-1)
        except Exception as e:
            self.log(f"play_bgm error: {e}")

    def stop_bgm(self):
        try:
            if self.platform == 'ios':
                if self.bg_player: self.bg_player.stop()
            elif self.platform == 'android':
                if self.bg_player: self.bg_player.pause()
            else:
                if PYGAME_AVAILABLE: pygame.mixer.music.stop()
        except Exception as e:
            self.log(f"stop_bgm error: {e}")

    # ---------- Backgrounds ----------
    def init_backgrounds(self):
        self.backgrounds = []
        self.current_bg = None
        for i in range(1, 11):
            filename = f"background_{i:02}.png"
            path = self.paths.app / "assets" / "backgrounds" / filename
            if path.exists():
                try:
                    self.backgrounds.append(toga.Image(path))
                    self.log(f"Loaded bg {i}")
                except Exception as e:
                    self.log(f"Failed to load bg {i}: {e}")
            else:
                self.log(f"BG file missing: {path}")
        self.randomize_background()

    def randomize_background(self):
        if self.backgrounds:
            self.current_bg = random.choice(self.backgrounds)
            self.log("Randomized background")
        else:
            self.current_bg = None

    # ---------- Resize ----------
    def on_resize(self, widget, width, height, **kwargs):
        if width > 0 and height > 0:
            self.canvas_width = width
            self.canvas_height = height
            self.log(f"Resize: {width}x{height}")
        else:
            self.log(f"Ignored resize with zero dims: {width}x{height}")
        self.redraw()

    # ---------- Game state ----------
    def reset_player(self):
        w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
        h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
        center_x = (w // 2 // self.grid_size) * self.grid_size
        center_y = (h // 2 // self.grid_size) * self.grid_size
        self.snake = [(center_x - i * self.grid_size, center_y) for i in range(3)]
        self.snake_dir = (1, 0)
        self.current_score = 0
        self.current_level_points = 0
        self.points_to_next_level = 20
        self.level = 1
        self.randomize_background()
        self.spawn_food()
        self.log(f"Player reset, snake: {self.snake}")

    def spawn_food(self):
        w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
        h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
        max_x = max(1, int(w // self.grid_size) - 2)
        max_y = max(1, int(h // self.grid_size) - 2)
        while True:
            fx = random.randint(1, max_x) * self.grid_size
            fy = random.randint(1, max_y) * self.grid_size
            self.food_pos = (fx, fy)
            if self.food_pos not in self.snake:
                break
        is_special = random.random() < 0.15
        self.food_color = random.choice(["gold", "silver"]) if is_special else random.choice(
            ["white", "red", "green", "blue", "cyan", "magenta", "yellow"]
        )
        self.log(f"Food spawned at {self.food_pos}")

    # ---------- Touch ----------
    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)

    def on_touch_up(self, widget, x, y, **kwargs):
        if not self.touch_start:
            return
        dx = x - self.touch_start[0]
        dy = y - self.touch_start[1]
        if self.state in ["P1_PLAY", "P2_PLAY"]:
            if abs(dx) > 30 or abs(dy) > 30:
                if abs(dx) > abs(dy):
                    if dx > 0 and self.snake_dir != (-1, 0): self.snake_dir = (1, 0)
                    elif dx < 0 and self.snake_dir != (1, 0): self.snake_dir = (-1, 0)
                else:
                    if dy > 0 and self.snake_dir != (0, -1): self.snake_dir = (0, 1)
                    elif dy < 0 and self.snake_dir != (0, 1): self.snake_dir = (0, -1)
        else:
            self.handle_menu_tap(y)
        self.touch_start = None

    def handle_menu_tap(self, y):
        top_half = (y < self.canvas_height / 2)
        if self.state == "MENU":
            self.multiplayer = not top_half
            self.play_sound("player1_begin")
            self.play_bgm()
            self.reset_player()
            self.state = "P1_PLAY"
            self.log("Start game, multiplayer=" + str(self.multiplayer))
        elif self.state == "REMATCH_PROMPT":
            if top_half:
                self.play_sound("player1_begin")
                self.play_bgm()
                self.reset_player()
                self.state = "P1_PLAY"
            else:
                self.play_sound("game_over")
                self.state = "MENU"
        elif self.state == "P2_TRANSITION":
            self.play_sound("player2_begin")
            self.play_bgm()
            self.reset_player()
            self.state = "P2_PLAY"
        elif self.state == "GAME_OVER":
            self.state = "MENU"

    # ---------- Game Loop ----------
    async def game_loop(self, widget, **kwargs):
        self.log("game_loop started")
        loop_count = 0
        while True:
            await asyncio.sleep(0.08)
            loop_count += 1
            if loop_count % 100 == 0:
                self.log(f"Loop alive, count {loop_count}")
            try:
                if self.state in ["P1_PLAY", "P2_PLAY"]:
                    if not self.snake:
                        self.log("WARNING: snake is empty! Resetting...")
                        self.reset_player()
                    head_x, head_y = self.snake[0]
                    new_head = (
                        head_x + self.snake_dir[0] * self.grid_size,
                        head_y + self.snake_dir[1] * self.grid_size
                    )
                    w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
                    h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
                    if (new_head[0] < 0 or new_head[0] >= w or
                        new_head[1] < 0 or new_head[1] >= h):
                        self.trigger_game_over(1 if self.state == "P1_PLAY" else 2)
                    elif new_head in self.snake:
                        self.trigger_game_over(1 if self.state == "P1_PLAY" else 2)
                    else:
                        self.snake.insert(0, new_head)
                        if (abs(new_head[0] - self.food_pos[0]) < self.grid_size and
                            abs(new_head[1] - self.food_pos[1]) < self.grid_size):
                            self.play_sound("food_blip")
                            pts = 10 if self.food_color == "gold" else 5 if self.food_color == "silver" else 1
                            self.current_score += pts
                            self.current_level_points += pts
                            if self.current_level_points >= self.points_to_next_level:
                                self.level += 1
                                self.points_to_next_level = (self.level + 1) * 10
                                self.current_level_points = 0
                                self.randomize_background()
                            self.spawn_food()
                        else:
                            self.snake.pop()
                self.redraw()
            except Exception:
                self.log("Exception in game_loop:")
                self.log(traceback.format_exc())
                traceback.print_exc()

    # ---------- Rendering ----------
    def redraw(self):
        try:
            # Update debug label
            self.debug_label.text = f"State:{self.state} W:{self.canvas_width} H:{self.canvas_height} Score:{self.current_score}"

            self.canvas.clear()

            # --- MENU: show log and tap zones ---
            if self.state == "MENU":
                # Dark background
                with self.canvas.fill(color="blue"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

                # Show last log entries
                log_text = self.get_recent_log(8)
                self.canvas.fill_text(
                    "--- DEBUG LOG ---",
                    x=10, y=30,
                    font=toga.Font(family="system", size=14, weight="bold"),
                    baseline=Baseline.TOP
                )
                y = 60
                for line in log_text.splitlines():
                    self.canvas.fill_text(
                        line,
                        x=10, y=y,
                        font=toga.Font(family="system", size=10),
                        baseline=Baseline.TOP
                    )
                    y += 16

                # Tap zones
                self.draw_tap_zones("TAP HERE FOR 1 PLAYER", "TAP HERE FOR 2 PLAYERS")
                return

            # --- PLAYING states ---
            if self.state in ["P1_PLAY", "P2_PLAY"]:
                # Fill with dark green (fallback background)
                with self.canvas.fill(color="darkgreen"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

                # --- BIG DIAGNOSTIC TEXT ---
                self.canvas.fill_text(
                    "PLAYING",
                    x=50, y=150,
                    font=toga.Font(family="system", size=40, weight="bold"),
                    baseline=Baseline.TOP,
                    color="white"
                )

                # --- RED RECTANGLE AT (0,0) ---
                with self.canvas.fill(color="red"):
                    self.canvas.rect(0, 0, 80, 80)

                # --- FOOD ---
                with self.canvas.fill(color=self.food_color):
                    self.canvas.rect(self.food_pos[0], self.food_pos[1],
                                     self.grid_size, self.grid_size)

                # --- SNAKE (yellow with red outline) ---
                if self.snake:
                    for segment in self.snake:
                        with self.canvas.fill(color="yellow"):
                            self.canvas.rect(segment[0], segment[1],
                                             self.grid_size - 2, self.grid_size - 2)
                        with self.canvas.stroke(color="red", line_width=2):
                            self.canvas.rect(segment[0], segment[1],
                                             self.grid_size - 2, self.grid_size - 2)
                else:
                    # Draw a big "NO SNAKE" message
                    self.canvas.fill_text(
                        "SNAKE EMPTY!",
                        x=100, y=300,
                        font=toga.Font(family="system", size=30, weight="bold"),
                        baseline=Baseline.TOP,
                        color="red"
                    )

                # Score text
                self.canvas.fill_text(
                    f"Level: {self.level}   Score: {self.current_score}",
                    x=20, y=30,
                    font=toga.Font(family="system", size=20, weight="bold"),
                    baseline=Baseline.TOP,
                    color="white"
                )

            # --- Other states ---
            elif self.state == "REMATCH_PROMPT":
                self.draw_tap_zones("TAP HERE FOR YES (REMATCH)", "TAP HERE FOR NO (MENU)")
                self.draw_centered_text("IT'S A TIE!", "red", 32, -100)
                self.draw_centered_text(f"Score: {self.p1_score}", "white", 20, -50)
            elif self.state == "P2_TRANSITION":
                self.draw_centered_text("PLAYER 1 CRASHED!", "red", 32, -100)
                self.draw_centered_text(f"P1 Score: {self.p1_score}", "white", 20, -50)
                self.draw_centered_text("TAP ANYWHERE FOR P2 TURN", "gray", 16, 100)
            elif self.state == "GAME_OVER":
                if self.multiplayer:
                    winner = "PLAYER 1 WINS!" if self.p1_score > self.p2_score else "PLAYER 2 WINS!"
                    self.draw_centered_text(winner, "red", 32, -100)
                    self.draw_centered_text(f"P1: {self.p1_score}   P2: {self.p2_score}", "white", 20, -50)
                else:
                    self.draw_centered_text("GAME OVER", "red", 32, -100)
                    self.draw_centered_text(f"Final Score: {self.p1_score}", "white", 20, -50)
                self.draw_centered_text("TAP ANYWHERE TO RETURN", "gray", 16, 100)

            # Force native redraw on iOS
            if self.platform == 'ios':
                try:
                    from rubicon.objc import ObjCClass
                    UIView = ObjCClass('UIView')
                    self.canvas._impl.native.setNeedsDisplay()
                except:
                    pass

        except Exception as e:
            self.log(f"Exception in redraw: {e}")
            self.log(traceback.format_exc())
            traceback.print_exc()

    # ---------- Helpers ----------
    def draw_tap_zones(self, top_text, bottom_text):
        with self.canvas.fill(color="rgb(40,40,40)"):
            self.canvas.rect(0, 0, self.canvas_width, self.canvas_height / 2)
        self.draw_centered_text(top_text, "rgb(200,200,200)", 16, -self.canvas_height / 4)
        with self.canvas.fill(color="rgb(20,20,20)"):
            self.canvas.rect(0, self.canvas_height / 2, self.canvas_width, self.canvas_height / 2)
        self.draw_centered_text(bottom_text, "rgb(200,200,200)", 16, self.canvas_height / 4)

    def draw_centered_text(self, text, color, size, y_offset):
        approx_char_width = size * 0.6
        text_width = len(text) * approx_char_width
        x = max(0, (self.canvas_width - text_width) / 2)
        y = (self.canvas_height / 2) + y_offset
        self.canvas.fill_text(
            text, x=x, y=y,
            font=toga.Font(family="system", size=size, weight="bold"),
            baseline=Baseline.MIDDLE,
            color=color
        )

def main():
    return HungrySnake4K()