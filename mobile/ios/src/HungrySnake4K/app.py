import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import random
import asyncio
import traceback

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class HungrySnake4K(toga.App):
    def startup(self):
        if hasattr(sys, 'getandroidapilevel'):
            self.platform = 'android'
        elif sys.platform == "ios":
            self.platform = 'ios'
        else:
            self.platform = 'desktop'

        self.log_path = self.paths.data / "debug.log"
        try:
            with open(self.log_path, "w") as f:
                f.write("=== App started ===\n")
        except:
            pass
        self.log("Startup: platform = " + self.platform)

        self.grid_size = 40
        self.DEFAULT_WIDTH = 400
        self.DEFAULT_HEIGHT = 800
        self.canvas_width = self.DEFAULT_WIDTH
        self.canvas_height = self.DEFAULT_HEIGHT

        self.state = "MENU"
        self.snake = []
        self.snake_dir = (1, 0)
        self.next_dir = None
        self.food_pos = (0, 0)
        self.score = 0
        self.touch_start = None
        self.last_touch = None

        # --- Audio ---
        self.audio_players = {}
        self.bg_player = None
        self.audio_loaded = False
        self.init_audio()

        # Canvas
        self.canvas = toga.Canvas(
            style=Pack(flex=1, background_color="black"),
            on_resize=self.on_resize,
            on_press=self.on_touch_down,
            on_release=self.on_touch_up,
            on_drag=self.on_touch_drag,
        )

        self.debug_label = toga.Label(
            "Starting...",
            style=Pack(padding=10, color="white", background_color="black", font_size=12)
        )

        box = toga.Box(children=[self.canvas, self.debug_label], style=Pack(direction=COLUMN, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        self.redraw()
        asyncio.create_task(self.game_loop(None))
        self.add_background_task(self.game_loop)

    def log(self, msg):
        try:
            with open(self.log_path, "a") as f:
                f.write(f"{msg}\n")
        except:
            pass

    # ---------- Audio with flexible path ----------
    def init_audio(self):
        try:
            # Define audio files
            sfx_files = {
                "food_blip": "food_blip.wav",
                "game_over": "game_over.wav",
                "player1_begin": "player1_begin.wav",
            }
            bg_file = "background_score.mp3"

            # Try multiple possible locations
            possible_locations = [
                self.paths.app,                     # bundle root
                self.paths.app / "assets",          # assets folder
                self.paths.app / "Assets",          # alternative case
            ]

            # Find which location has the files
            bg_path = None
            sfx_paths = {}
            for loc in possible_locations:
                if (loc / bg_file).exists():
                    bg_path = loc / bg_file
                for key, fname in sfx_files.items():
                    if (loc / fname).exists():
                        sfx_paths[key] = loc / fname
                # If we found at least one, break
                if bg_path or sfx_paths:
                    break

            if not bg_path and not sfx_paths:
                self.log("No audio files found in any location")
                self.debug_label.text = "Audio: none found"
                return

            # Platform-specific loading
            if self.platform == 'ios':
                from rubicon.objc import ObjCClass
                from ctypes import cdll
                from ctypes.util import find_library
                cdll.LoadLibrary(find_library('AVFoundation'))
                AVAudioPlayer = ObjCClass('AVAudioPlayer')
                NSURL = ObjCClass('NSURL')

                if bg_path:
                    url = NSURL.fileURLWithPath_(str(bg_path))
                    self.bg_player = AVAudioPlayer.alloc().initWithContentsOfURL_error_(url, None)
                    if self.bg_player:
                        self.bg_player.numberOfLoops = -1
                        self.bg_player.volume = 0.4
                        self.bg_player.prepareToPlay()
                        self.log("iOS bg loaded: " + str(bg_path))
                    else:
                        self.log("iOS bg init failed")
                else:
                    self.log("iOS bg missing")

                for key, path in sfx_paths.items():
                    url = NSURL.fileURLWithPath_(str(path))
                    player = AVAudioPlayer.alloc().initWithContentsOfURL_error_(url, None)
                    if player:
                        player.volume = 0.8
                        player.prepareToPlay()
                        self.audio_players[key] = player
                        self.log(f"iOS SFX loaded: {key}")

            elif self.platform == 'android':
                from java import jclass
                MediaPlayer = jclass('android.media.MediaPlayer')
                if bg_path:
                    self.bg_player = MediaPlayer()
                    self.bg_player.setDataSource(str(bg_path))
                    self.bg_player.setLooping(True)
                    self.bg_player.setVolume(0.4, 0.4)
                    self.bg_player.prepare()
                    self.log("Android bg loaded")
                for key, path in sfx_paths.items():
                    player = MediaPlayer()
                    player.setDataSource(str(path))
                    player.setVolume(0.8, 0.8)
                    player.prepare()
                    self.audio_players[key] = player
                    self.log(f"Android SFX loaded: {key}")

            else:
                if not PYGAME_AVAILABLE:
                    self.log("Pygame not available")
                    return
                pygame.mixer.init()
                pygame.mixer.set_num_channels(8)
                if bg_path:
                    pygame.mixer.music.load(str(bg_path))
                    pygame.mixer.music.set_volume(0.4)
                    self.log("Desktop bg loaded")
                for key, path in sfx_paths.items():
                    snd = pygame.mixer.Sound(str(path))
                    snd.set_volume(0.8)
                    self.audio_players[key] = snd
                    self.log(f"Desktop SFX loaded: {key}")

            self.audio_loaded = True
            self.debug_label.text = "Audio: OK"

        except Exception as e:
            self.log(f"Audio init error: {e}")
            self.debug_label.text = f"Audio error: {str(e)[:30]}"
            self.audio_loaded = False

    def play_sound(self, sound_key):
        if not self.audio_loaded:
            return
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
        if not self.audio_loaded or not self.bg_player:
            return
        try:
            if self.platform == 'ios':
                self.bg_player.play()
            elif self.platform == 'android':
                self.bg_player.start()
            else:
                if PYGAME_AVAILABLE:
                    pygame.mixer.music.play(loops=-1)
        except Exception as e:
            self.log(f"play_bgm error: {e}")

    def stop_bgm(self):
        if not self.audio_loaded:
            return
        try:
            if self.platform == 'ios':
                if self.bg_player: self.bg_player.stop()
            elif self.platform == 'android':
                if self.bg_player: self.bg_player.pause()
            else:
                if PYGAME_AVAILABLE:
                    pygame.mixer.music.stop()
        except Exception as e:
            self.log(f"stop_bgm error: {e}")

    # ---------- Game logic (unchanged) ----------
    def on_resize(self, widget, width, height, **kwargs):
        if width > 0 and height > 0:
            self.canvas_width = width
            self.canvas_height = height
        self.redraw()

    def reset_player(self):
        w = self.canvas_width if self.canvas_width > 0 else self.DEFAULT_WIDTH
        h = self.canvas_height if self.canvas_height > 0 else self.DEFAULT_HEIGHT
        center_x = (w // 2 // self.grid_size) * self.grid_size
        center_y = (h // 2 // self.grid_size) * self.grid_size
        self.snake = [(center_x - i * self.grid_size, center_y) for i in range(3)]
        self.snake_dir = (1, 0)
        self.next_dir = None
        self.score = 0
        self.spawn_food()

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

    def on_touch_down(self, widget, x, y, **kwargs):
        self.touch_start = (x, y)
        self.last_touch = (x, y)

        if self.state == "MENU":
            self.reset_player()
            self.state = "PLAY"
            self.play_sound("player1_begin")
            self.play_bgm()
            self.redraw()
            return

        if self.state == "GAME_OVER":
            self.state = "MENU"
            self.stop_bgm()
            self.redraw()
            return

    def on_touch_drag(self, widget, x, y, **kwargs):
        if self.state != "PLAY" or not self.snake:
            return
        if self.last_touch is None:
            self.last_touch = (x, y)
            return

        dx = x - self.last_touch[0]
        dy = y - self.last_touch[1]
        self.last_touch = (x, y)

        if abs(dx) < 10 and abs(dy) < 10:
            return

        if abs(dx) > abs(dy):
            new_dir = (1, 0) if dx > 0 else (-1, 0)
        else:
            new_dir = (0, 1) if dy > 0 else (0, -1)

        if new_dir[0] != -self.snake_dir[0] or new_dir[1] != -self.snake_dir[1]:
            self.next_dir = new_dir

    def on_touch_up(self, widget, x, y, **kwargs):
        self.touch_start = None
        self.last_touch = None

    async def game_loop(self, widget):
        while True:
            await asyncio.sleep(0.03)
            try:
                if self.state == "PLAY":
                    if self.next_dir:
                        self.snake_dir = self.next_dir
                        self.next_dir = None

                    if not self.snake:
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
                        self.state = "GAME_OVER"
                        self.play_sound("game_over")
                        self.stop_bgm()
                        self.redraw()
                        continue

                    if new_head in self.snake:
                        self.state = "GAME_OVER"
                        self.play_sound("game_over")
                        self.stop_bgm()
                        self.redraw()
                        continue

                    self.snake.insert(0, new_head)

                    if (abs(new_head[0] - self.food_pos[0]) < self.grid_size and
                        abs(new_head[1] - self.food_pos[1]) < self.grid_size):
                        self.score += 1
                        self.play_sound("food_blip")
                        self.spawn_food()
                    else:
                        self.snake.pop()

                self.redraw()
            except Exception as e:
                self.log(f"Loop error: {e}")

    def redraw(self):
        try:
            self.debug_label.text = f"State:{self.state}  Score:{self.score}  W:{self.canvas_width} H:{self.canvas_height}"

            with self.canvas.fill(color="black"):
                self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            if self.state == "MENU":
                with self.canvas.fill(color="blue"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)
                with self.canvas.fill(color="white"):
                    self.canvas.rect(self.canvas_width//2 - 40, self.canvas_height//2 - 20, 80, 40)

            elif self.state == "PLAY":
                with self.canvas.fill(color="darkgreen"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

                with self.canvas.fill(color="red"):
                    self.canvas.rect(self.food_pos[0], self.food_pos[1],
                                     self.grid_size, self.grid_size)

                for seg in self.snake:
                    with self.canvas.fill(color="yellow"):
                        self.canvas.rect(seg[0], seg[1],
                                         self.grid_size - 2, self.grid_size - 2)

            elif self.state == "GAME_OVER":
                with self.canvas.fill(color="red"):
                    self.canvas.rect(0, 0, self.canvas_width, self.canvas_height)

            if self.platform == 'ios':
                try:
                    from rubicon.objc import ObjCClass
                    UIView = ObjCClass('UIView')
                    self.canvas._impl.native.setNeedsDisplay()
                except:
                    pass

        except Exception as e:
            self.debug_label.text = f"Render error: {str(e)[:40]}"

def main():
    return HungrySnake4K()