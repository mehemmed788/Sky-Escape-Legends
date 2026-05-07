import pygame
import sys
import json
import random
import math
from datetime import datetime, timedelta
import array

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_VELOCITY = -9
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPACING = 300
GROUND_HEIGHT = 80
BASE_SCROLL_SPEED = 3
SCROLL_SPEED_INCREMENT = 0.2
MIN_PIPE_GAP = 90
GAP_DECREMENT = 0.5
COIN_RADIUS = 8
COIN_VALUE = 1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
SKY_BLUE = (135, 206, 235)
NIGHT_SKY = (25, 25, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
GOLD = (255, 215, 0)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 140, 0)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)

# Helper functions for sound generation
def generate_sound_wave(frequency, duration, volume=0.5, wave_type='sine'):
    sample_rate = pygame.mixer.get_init()[0]
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0]) * n_samples
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'sine':
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        elif wave_type == 'square':
            value = int(volume * 32767 * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1))
        else:
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        buf[i] = value
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

def generate_click_sound():
    return generate_sound_wave(800, 0.05, 0.2, 'square')

def generate_jump_sound():
    return generate_sound_wave(880, 0.1, 0.3)

def generate_collision_sound():
    sample_rate = pygame.mixer.get_init()[0]
    duration = 0.3
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0]) * n_samples
    for i in range(n_samples):
        t = i / sample_rate
        freq = 300 - 200 * (t / duration)
        value = int(0.5 * 32767 * math.sin(2 * math.pi * freq * t) * (1 + 0.5 * math.sin(2 * math.pi * 50 * t)))
        buf[i] = value
    return pygame.mixer.Sound(buffer=buf)

def generate_score_sound():
    return generate_sound_wave(1500, 0.05, 0.2)

def generate_menu_music():
    sample_rate = pygame.mixer.get_init()[0]
    duration = 4.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0]) * n_samples
    notes = [261.63, 293.66, 329.63, 261.63, 196.00, 174.61, 146.83, 130.81]
    note_duration = duration / len(notes)
    volume = 0.08
    for i, freq in enumerate(notes):
        start = int(i * note_duration * sample_rate)
        end = int((i+1) * note_duration * sample_rate)
        for j in range(start, min(end, n_samples)):
            t = j / sample_rate
            value = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * (1 + 0.2 * math.sin(2 * math.pi * 2 * t)))
            buf[j] = value
    return pygame.mixer.Sound(buffer=buf)

def generate_game_music():
    sample_rate = pygame.mixer.get_init()[0]
    duration = 2.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0]) * n_samples
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    note_duration = duration / len(notes)
    volume = 0.1
    for i, freq in enumerate(notes):
        start = int(i * note_duration * sample_rate)
        end = int((i+1) * note_duration * sample_rate)
        for j in range(start, min(end, n_samples)):
            t = j / sample_rate
            value = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * math.sin(2 * math.pi * 4 * t) * 0.5)
            buf[j] = value
    return pygame.mixer.Sound(buffer=buf)

def generate_adrenaline_music():
    sample_rate = pygame.mixer.get_init()[0]
    duration = 1.5
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0]) * n_samples
    notes = [349.23, 392.00, 440.00, 523.25, 587.33, 659.25, 698.46, 783.99]
    note_duration = duration / len(notes)
    volume = 0.15
    for i, freq in enumerate(notes):
        start = int(i * note_duration * sample_rate)
        end = int((i+1) * note_duration * sample_rate)
        for j in range(start, min(end, n_samples)):
            t = j / sample_rate
            value = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * math.sin(2 * math.pi * 8 * t) * 0.7)
            buf[j] = value
    return pygame.mixer.Sound(buffer=buf)

def generate_ping_sound():
    return generate_sound_wave(1800, 0.08, 0.25)

def generate_event_sound():
    return generate_sound_wave(1200, 0.15, 0.35)

# Sound Manager
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_channel = None
        self.current_music = None
        self.music_playing = False
        self.jump_cooldown = 0
        self.adrenaline_active = False
        self.music_switched = False
        self.generate_sounds()

    def generate_sounds(self):
        self.sounds["click"] = generate_click_sound()
        self.sounds["jump"] = generate_jump_sound()
        self.sounds["hit"] = generate_collision_sound()
        self.sounds["point"] = generate_score_sound()
        self.sounds["menu_music"] = generate_menu_music()
        self.sounds["game_music"] = generate_game_music()
        self.sounds["adrenaline_music"] = generate_adrenaline_music()
        self.sounds["coin"] = generate_sound_wave(1000, 0.07, 0.25)
        self.sounds["purchase"] = generate_sound_wave(1200, 0.1, 0.3)
        self.sounds["mission_complete"] = generate_sound_wave(1400, 0.2, 0.4)
        self.sounds["ping"] = generate_ping_sound()
        self.sounds["event"] = generate_event_sound()

    def play_click(self):
        if "click" in self.sounds:
            self.sounds["click"].play()

    def play_jump(self):
        if self.jump_cooldown <= 0:
            if "jump" in self.sounds:
                self.sounds["jump"].play()
                self.jump_cooldown = 0.2

    def play_collision(self):
        if "hit" in self.sounds:
            self.sounds["hit"].play()

    def play_score(self):
        if "point" in self.sounds:
            self.sounds["point"].play()

    def play_coin(self):
        if "coin" in self.sounds:
            self.sounds["coin"].play()

    def play_purchase(self):
        if "purchase" in self.sounds:
            self.sounds["purchase"].play()

    def play_mission_complete(self):
        if "mission_complete" in self.sounds:
            self.sounds["mission_complete"].play()

    def play_ping(self):
        if "ping" in self.sounds:
            self.sounds["ping"].play()

    def play_event(self):
        if "event" in self.sounds:
            self.sounds["event"].play()

    def play_menu_music(self):
        self.stop_music()
        if "menu_music" in self.sounds:
            self.current_music = self.sounds["menu_music"]
            self.music_channel = self.current_music.play(-1)
            self.music_playing = True
        self.adrenaline_active = False
        self.music_switched = False

    def play_game_music(self):
        self.stop_music()
        if "game_music" in self.sounds:
            self.current_music = self.sounds["game_music"]
            self.music_channel = self.current_music.play(-1)
            self.music_playing = True
        self.adrenaline_active = False
        self.music_switched = False

    def activate_adrenaline(self):
        if not self.adrenaline_active:
            self.adrenaline_active = True
            self.music_switched = False

    def update_music(self):
        if self.adrenaline_active and not self.music_switched and self.music_playing:
            self.stop_music()
            if "adrenaline_music" in self.sounds:
                self.current_music = self.sounds["adrenaline_music"]
                self.music_channel = self.current_music.play(-1)
                self.music_playing = True
                self.music_switched = True
        elif not self.adrenaline_active and self.music_switched:
            self.stop_music()
            if "game_music" in self.sounds:
                self.current_music = self.sounds["game_music"]
                self.music_channel = self.current_music.play(-1)
                self.music_playing = True
                self.music_switched = False

    def stop_music(self):
        if self.music_channel:
            self.music_channel.stop()
            self.music_channel = None
            self.music_playing = False

    def update(self, dt):
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        self.update_music()

# Data Manager
class DataManager:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        default_data = {
            "highscore": 0,
            "coins": 100,
            "selected_bird": "Baby Bird",
            "beta_joined": False,
            "unlocked_birds": ["Baby Bird"],
            "last_login_date": None,
            "login_streak": 0,
            "total_coins_earned": 0,
            "total_score": 0
        }
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                for key, value in default_data.items():
                    if key not in data:
                        data[key] = value
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return default_data

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_coins(self, amount):
        self.data["coins"] += amount
        self.data["total_coins_earned"] += amount
        self.save()

    def spend_coins(self, amount):
        if self.data["coins"] >= amount:
            self.data["coins"] -= amount
            self.save()
            return True
        return False

# Daily Reward Manager
class DailyRewardManager:
    def __init__(self):
        self.last_login = data_manager.data.get("last_login_date")
        self.streak = data_manager.data.get("login_streak", 0)
        self.reward_claimed_today = False
        self.check_daily()

    def check_daily(self):
        today = datetime.now().date().isoformat()
        if self.last_login != today:
            base_reward = 10
            bonus = 0
            if self.streak >= 7:
                bonus = 50
            elif self.streak >= 3:
                bonus = 20
            reward = base_reward + bonus
            data_manager.add_coins(reward)
            if self.last_login:
                yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
                if self.last_login == yesterday:
                    self.streak += 1
                else:
                    self.streak = 1
            else:
                self.streak = 1
            data_manager.data["last_login_date"] = today
            data_manager.data["login_streak"] = self.streak
            data_manager.save()
            self.reward_claimed_today = True
            self.reward_text = f"Daily Reward! +{reward} coins (Streak: {self.streak})"
            self.reward_timer = 180
        else:
            self.reward_claimed_today = False

    def get_streak_text(self):
        return f"Login Streak: {self.streak} days"

    def update(self, dt):
        if hasattr(self, 'reward_timer') and self.reward_timer > 0:
            self.reward_timer -= 1

    def draw(self, screen):
        if hasattr(self, 'reward_timer') and self.reward_timer > 0:
            font = pygame.font.Font(None, 28)
            text = font.render(self.reward_text, True, GOLD)
            text_shadow = font.render(self.reward_text, True, BLACK)
            screen.blit(text_shadow, (SCREEN_WIDTH//2 - text.get_width()//2 + 2, 60 + 2))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 60))

# Progression System
class ProgressionManager:
    def __init__(self):
        self.total_coins = data_manager.data["total_coins_earned"]
        self.unlocked_birds = data_manager.data["unlocked_birds"]
        self.all_birds = list(shop.birds.keys())
        self.next_bird_index = self.get_next_unlock_index()
        self.progress = 0.0

    def get_next_unlock_index(self):
        for i, bird in enumerate(self.all_birds):
            if bird not in self.unlocked_birds:
                return i
        return -1

    def update(self):
        self.total_coins = data_manager.data["total_coins_earned"]
        self.unlocked_birds = data_manager.data["unlocked_birds"]
        self.next_bird_index = self.get_next_unlock_index()
        if self.next_bird_index != -1:
            next_bird = self.all_birds[self.next_bird_index]
            price = shop.get_bird_price(next_bird)
            self.progress = min(1.0, self.total_coins / price if price > 0 else 1.0)
        else:
            self.progress = 1.0

    def draw_progress_bar(self, screen, x, y, width=200, height=20):
        pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), border_radius=10)
        fill_width = int(width * self.progress)
        if fill_width > 0:
            pygame.draw.rect(screen, GOLD, (x, y, fill_width, height), border_radius=10)
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2, border_radius=10)
        if self.next_bird_index != -1:
            next_bird = self.all_birds[self.next_bird_index]
            price = shop.get_bird_price(next_bird)
            remaining = max(0, price - self.total_coins)
            font = pygame.font.Font(None, 20)
            text = font.render(f"Next: {next_bird} ({remaining} coins)", True, WHITE)
            screen.blit(text, (x, y - 22))

# Rare Event Manager
class RareEvent:
    def __init__(self, event_type, duration=5.0):
        self.event_type = event_type
        self.duration = duration
        self.timer = duration
        self.active = True

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

class RareEventManager:
    def __init__(self):
        self.active_events = []
        self.event_timer = 0
        self.event_cooldown = 30

    def update(self, dt, score):
        self.event_timer += dt
        if self.event_timer >= self.event_cooldown and len(self.active_events) == 0:
            chance = min(0.3, 0.05 + score / 500)
            if random.random() < chance:
                event_type = random.choice(["golden_pipe", "double_coins", "slow_motion"])
                self.active_events.append(RareEvent(event_type, duration=5.0))
                self.event_timer = 0
                sound_manager.play_event()
        for event in self.active_events[:]:
            event.update(dt)
            if not event.active:
                self.active_events.remove(event)

    def has_event(self, event_type):
        return any(e.event_type == event_type and e.active for e in self.active_events)

    def get_slow_motion_factor(self):
        if self.has_event("slow_motion"):
            return 0.5
        return 1.0

    def get_coin_multiplier(self):
        if self.has_event("double_coins"):
            return 2
        return 1

    def draw_indicators(self, screen):
        y = 100
        for event in self.active_events:
            font = pygame.font.Font(None, 24)
            if event.event_type == "golden_pipe":
                text = font.render("GOLDEN PIPE ACTIVE!", True, GOLD)
            elif event.event_type == "double_coins":
                text = font.render("DOUBLE COINS!", True, CYAN)
            elif event.event_type == "slow_motion":
                text = font.render("SLOW MOTION!", True, PURPLE)
            else:
                continue
            screen.blit(text, (SCREEN_WIDTH - text.get_width() - 10, y))
            y += 30

# Golden Pipe
class GoldenPipe:
    def __init__(self, x, gap_y, gap_height):
        self.x = x
        self.gap_y = gap_y
        self.gap_height = gap_height
        self.passed = False
        self.coin = Coin(x + PIPE_WIDTH//2, gap_y + gap_height//2)
        self.golden = True
        self.extra_coins = 5

    # FIX: pipe.update() was called as update(effective_dt * scroll_speed) but internally
    # the original just did self.x -= speed each frame. We keep speed as pixels/frame.
    def update(self, speed):
        self.x -= speed
        self.coin.x -= speed

    def draw(self, screen, offset_x=0, shake_offset=(0,0)):
        draw_x = self.x + offset_x + shake_offset[0]
        color = GOLD
        dark_color = (200, 150, 0)
        top_rect = pygame.Rect(draw_x, shake_offset[1], PIPE_WIDTH, self.gap_y)
        pygame.draw.rect(screen, dark_color, top_rect.inflate(6, 6))
        pygame.draw.rect(screen, color, top_rect)
        pygame.draw.rect(screen, dark_color, (draw_x, self.gap_y-30, PIPE_WIDTH, 30))
        bottom_y = self.gap_y + self.gap_height + shake_offset[1]
        bottom_rect = pygame.Rect(draw_x, bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y)
        pygame.draw.rect(screen, dark_color, bottom_rect.inflate(6, 6))
        pygame.draw.rect(screen, color, bottom_rect)
        pygame.draw.rect(screen, dark_color, (draw_x, bottom_y, PIPE_WIDTH, 30))
        self.coin.draw(screen, offset_x, shake_offset)

    def get_rects(self, offset_x=0, shake_offset=(0,0)):
        top_rect = pygame.Rect(self.x + offset_x + shake_offset[0], shake_offset[1], PIPE_WIDTH, self.gap_y)
        bottom_rect = pygame.Rect(self.x + offset_x + shake_offset[0], self.gap_y + self.gap_height + shake_offset[1], PIPE_WIDTH, SCREEN_HEIGHT - (self.gap_y + self.gap_height + shake_offset[1]))
        return top_rect, bottom_rect

# Difficulty Manager
class DifficultyManager:
    def __init__(self):
        self.intensity = 0
        self.speed_multiplier = 1.0
        self.last_intensity = 0

    def update(self, score):
        if score < 20:
            self.intensity = 0
            self.speed_multiplier = 1.0
        elif score < 50:
            self.intensity = 1
            self.speed_multiplier = 1.2
        elif score < 100:
            self.intensity = 2
            self.speed_multiplier = 1.5
        else:
            self.intensity = 3
            self.speed_multiplier = 2.0
        if self.intensity != self.last_intensity:
            self.last_intensity = self.intensity
            return True
        return False

    # FIX: original had get_speed(base_speed) but GameSession called get_speed_multiplier()
    # Adding get_speed_multiplier() as the correct method name used in GameSession.update()
    def get_speed_multiplier(self):
        return self.speed_multiplier

    def get_speed(self, base_speed):
        return base_speed * self.speed_multiplier

    # FIX: original had get_gap_factor() returning correct value - preserved as-is
    def get_gap_factor(self):
        return max(0.6, 1.0 - self.intensity * 0.1)

    def draw_intensity_indicator(self, screen):
        colors = [(100, 100, 100), (0, 200, 0), (255, 200, 0), (255, 0, 0)]
        names = ["CALM", "MEDIUM", "FAST", "INSANE"]
        color = colors[self.intensity]
        font = pygame.font.Font(None, 24)
        text = font.render(f"INTENSITY: {names[self.intensity]}", True, color)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 5))

# Floating Text Effect
class FloatingText:
    def __init__(self, text, x, y, color=GOLD, lifetime=1.0):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        self.y -= 30 * dt

    def draw(self, screen):
        if self.age < self.lifetime:
            alpha = 255 * (1 - self.age / self.lifetime)
            font = pygame.font.Font(None, 28)
            text_surf = font.render(self.text, True, self.color)
            text_surf.set_alpha(int(alpha))
            screen.blit(text_surf, (self.x - text_surf.get_width()//2, self.y - text_surf.get_height()//2))

# Sparkle Effect
class Sparkle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 0.3
        self.age = 0.0
        self.particles = []
        for _ in range(8):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(50, 150)
            self.particles.append([angle, speed])

    def update(self, dt):
        self.age += dt
        for p in self.particles:
            p[1] -= dt * 200
        return self.age < self.lifetime

    def draw(self, screen):
        for p in self.particles:
            dx = math.cos(p[0]) * p[1] * self.age
            dy = math.sin(p[0]) * p[1] * self.age
            x = self.x + dx
            y = self.y + dy
            pygame.draw.circle(screen, GOLD, (int(x), int(y)), 2)

# Player Class
class Player:
    def __init__(self, x, y, bird_type="Baby Bird"):
        self.x = x
        self.y = y
        self.velocity = 0
        self.radius = 15
        self.rotation = 0
        self.bird_type = bird_type
        self.color = self.get_bird_color(bird_type)
        self.image = None
        self.shadow_image = None
        self.glow = False
        self.glow_timer = 0
        self.create_image()

    def get_bird_color(self, bird_type):
        colors = {
            "Baby Bird": (255, 255, 0),
            "Flying Squirrel": (160, 82, 45),
            "Bee": (255, 215, 0),
            "Eagle": (139, 69, 19),
            "Owl": (128, 128, 128),
            "Bat": (50, 50, 50),
            "Parrot": (0, 255, 0),
            "Butterfly": (255, 105, 180),
            "Dragon": (255, 0, 0),
            "Raven": (0, 0, 0),
            "UFO Bird": (0, 255, 255),
            "Cosmic Raven": (138, 43, 226),
            "Thunder Phoenix": (255, 69, 0)
        }
        return colors.get(bird_type, (255, 255, 0))

    def create_image(self):
        size = (self.radius*2, self.radius*2)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, BLACK, (self.radius-5, self.radius-5), 3)
        pygame.draw.circle(self.image, WHITE, (self.radius-6, self.radius-6), 1)
        pygame.draw.polygon(self.image, (255, 140, 0), [(self.radius+5, self.radius), (self.radius+12, self.radius-3), (self.radius+12, self.radius+3)])
        self.shadow_image = pygame.Surface((self.radius*2+10, self.radius*2+10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_image, (0,0,0,80), (5, 5, self.radius*2, self.radius*2))

    def jump(self):
        self.velocity = JUMP_VELOCITY

    def activate_glow(self, duration=0.5):
        self.glow = True
        self.glow_timer = duration

    def update(self, dt=1.0):
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt
        self.rotation = min(max(self.velocity * 3, -30), 30)
        if self.glow:
            self.glow_timer -= dt
            if self.glow_timer <= 0:
                self.glow = False

    def draw(self, screen, offset_x=0, shake_offset=(0,0)):
        shadow_y = SCREEN_HEIGHT - GROUND_HEIGHT + 5
        shadow_rect = self.shadow_image.get_rect(center=(self.x + offset_x + shake_offset[0], shadow_y + shake_offset[1]))
        screen.blit(self.shadow_image, shadow_rect)
        if self.glow:
            glow_surf = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 100, 80), (self.radius*2, self.radius*2), self.radius*2)
            screen.blit(glow_surf, (self.x + offset_x + shake_offset[0] - self.radius*2, self.y + shake_offset[1] - self.radius*2))
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        rect = rotated_image.get_rect(center=(self.x + offset_x + shake_offset[0], self.y + shake_offset[1]))
        screen.blit(rotated_image, rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

# Pipe Class
class Pipe:
    def __init__(self, x, gap_y, gap_height):
        self.x = x
        self.gap_y = gap_y
        self.gap_height = gap_height
        self.passed = False
        self.coin = Coin(x + PIPE_WIDTH//2, gap_y + gap_height//2)

    def update(self, speed):
        self.x -= speed
        self.coin.x -= speed

    def draw(self, screen, offset_x=0, shake_offset=(0,0)):
        draw_x = self.x + offset_x + shake_offset[0]
        top_rect = pygame.Rect(draw_x, shake_offset[1], PIPE_WIDTH, self.gap_y)
        pygame.draw.rect(screen, DARK_GREEN, top_rect.inflate(6, 6))
        pygame.draw.rect(screen, GREEN, top_rect)
        pygame.draw.rect(screen, DARK_GREEN, (draw_x, self.gap_y-30, PIPE_WIDTH, 30))
        bottom_y = self.gap_y + self.gap_height + shake_offset[1]
        bottom_rect = pygame.Rect(draw_x, bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y)
        pygame.draw.rect(screen, DARK_GREEN, bottom_rect.inflate(6, 6))
        pygame.draw.rect(screen, GREEN, bottom_rect)
        pygame.draw.rect(screen, DARK_GREEN, (draw_x, bottom_y, PIPE_WIDTH, 30))
        self.coin.draw(screen, offset_x, shake_offset)

    def get_rects(self, offset_x=0, shake_offset=(0,0)):
        top_rect = pygame.Rect(self.x + offset_x + shake_offset[0], shake_offset[1], PIPE_WIDTH, self.gap_y)
        bottom_rect = pygame.Rect(self.x + offset_x + shake_offset[0], self.gap_y + self.gap_height + shake_offset[1], PIPE_WIDTH, SCREEN_HEIGHT - (self.gap_y + self.gap_height + shake_offset[1]))
        return top_rect, bottom_rect

# Coin class
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS
        self.collected = False
        self.angle = 0
        self.float_offset = 0
        self.float_speed = 0.1

    def update(self, dt):
        self.angle += 5 * dt
        self.float_offset += self.float_speed * dt
        if self.float_offset > math.pi * 2:
            self.float_offset -= math.pi * 2

    def draw(self, screen, offset_x=0, shake_offset=(0,0)):
        if self.collected:
            return
        draw_x = self.x + offset_x + shake_offset[0]
        draw_y = self.y + math.sin(self.float_offset) * 3 + shake_offset[1]
        # FIX: pygame.draw.circle does not support 4-component RGBA tuples directly.
        # The original had (255, 215, 0, 100) which crashes. Use a 3-tuple instead.
        pygame.draw.circle(screen, GOLD, (int(draw_x), int(draw_y)), self.radius+2)
        pygame.draw.circle(screen, GOLD, (int(draw_x), int(draw_y)), self.radius)
        pygame.draw.circle(screen, YELLOW, (int(draw_x), int(draw_y)), self.radius-2)
        highlight_radius = self.radius // 2
        pygame.draw.circle(screen, WHITE, (int(draw_x-2), int(draw_y-2)), max(1, highlight_radius//2))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

# Mission Manager
class MissionManager:
    def __init__(self):
        self.active_mission = None
        self.mission_progress = 0
        self.mission_complete = False
        self.mission_reward = 0
        self.mission_types = [
            {"name": "Pass 3 pipes", "description": "Pass 3 pipes without dying", "target": 3, "reward": 10, "type": "pipe_count"},
            {"name": "Collect 5 coins", "description": "Collect 5 coins in a row", "target": 5, "reward": 15, "type": "coin_streak"},
            {"name": "Reach score 10", "description": "Reach score 10 without missing jump", "target": 10, "reward": 20, "type": "score_target"},
            {"name": "Pass 5 pipes", "description": "Pass 5 pipes in a row", "target": 5, "reward": 25, "type": "pipe_streak"},
            {"name": "Collect 10 coins", "description": "Collect total 10 coins", "target": 10, "reward": 30, "type": "coin_total"},
            {"name": "Score multiplier x3", "description": "Reach x3 combo multiplier", "target": 3, "reward": 40, "type": "combo_target"}
        ]
        self.current_mission_index = 0
        self.mission_timer = 0
        self.mission_update_cooldown = 0

    def generate_new_mission(self):
        if self.mission_update_cooldown > 0:
            return
        self.mission_types = [
            {"name": "Pass 3 pipes", "description": "Pass 3 pipes without dying", "target": 3, "reward": 15, "type": "pipe_count"},
            {"name": "Collect 5 coins", "description": "Collect 5 coins in a row", "target": 5, "reward": 20, "type": "coin_streak"},
            {"name": "Reach score 15", "description": "Reach score 15 without missing jump", "target": 15, "reward": 25, "type": "score_target"},
            {"name": "Pass 5 pipes", "description": "Pass 5 pipes in a row", "target": 5, "reward": 30, "type": "pipe_streak"},
            {"name": "Collect 10 coins", "description": "Collect total 10 coins", "target": 10, "reward": 35, "type": "coin_total"},
            {"name": "Score multiplier x3", "description": "Reach x3 combo multiplier", "target": 3, "reward": 45, "type": "combo_target"}
        ]
        self.active_mission = random.choice(self.mission_types).copy()
        self.mission_progress = 0
        self.mission_complete = False
        self.mission_reward = self.active_mission["reward"]
        self.mission_update_cooldown = 60

    def update(self, dt, game_state):
        if self.mission_update_cooldown > 0:
            self.mission_update_cooldown -= 1
        if self.mission_complete and self.mission_update_cooldown <= 0:
            self.generate_new_mission()
            return True
        if not self.active_mission:
            self.generate_new_mission()
        return False

    def update_progress(self, event_type, value=1, game_state=None):
        if self.mission_complete or not self.active_mission:
            return False
        progress_increased = False
        mission_type = self.active_mission["type"]
        if event_type == "pipe_passed" and mission_type in ["pipe_count", "pipe_streak"]:
            self.mission_progress += value
            progress_increased = True
        elif event_type == "coin_collected" and mission_type in ["coin_streak", "coin_total"]:
            self.mission_progress += value
            progress_increased = True
        elif event_type == "score_increased" and mission_type == "score_target":
            self.mission_progress += value
            progress_increased = True
        elif event_type == "combo_changed" and mission_type == "combo_target" and game_state:
            if game_state["combo"] >= self.active_mission["target"]:
                self.mission_progress = self.active_mission["target"]
                progress_increased = True
        if progress_increased and self.mission_progress >= self.active_mission["target"]:
            self.mission_complete = True
            return True
        return False

    def claim_reward(self):
        if self.mission_complete:
            reward = self.mission_reward
            self.mission_complete = False
            return reward
        return 0

    def draw(self, screen):
        if self.active_mission and not self.mission_complete:
            panel_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 240, 70)
            pygame.draw.rect(screen, (0,0,0,180), panel_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, panel_rect, 2, border_radius=8)
            font_small = pygame.font.Font(None, 18)
            font = pygame.font.Font(None, 22)
            desc_text = font.render(self.active_mission["description"], True, GOLD)
            prog_text = font_small.render(f"Progress: {self.mission_progress}/{self.active_mission['target']}", True, WHITE)
            reward_text = font_small.render(f"Reward: {self.mission_reward} coins", True, YELLOW)
            screen.blit(desc_text, (panel_rect.x + 10, panel_rect.y + 5))
            screen.blit(prog_text, (panel_rect.x + 10, panel_rect.y + 30))
            screen.blit(reward_text, (panel_rect.x + 10, panel_rect.y + 50))

# Game Session
class GameSession:
    def __init__(self, bird_type="Baby Bird"):
        self.player = Player(100, SCREEN_HEIGHT//2, bird_type)
        self.pipes = []
        self.score = 0
        self.combo = 0
        self.game_active = True
        self.pipe_timer = 0
        self.scroll_speed = BASE_SCROLL_SPEED
        self.current_gap = PIPE_GAP
        self.night_mode = False
        self.difficulty_score = 0
        self.floating_texts = []
        self.sparkles = []
        self.last_milestone = 0
        self.streak = 0
        self.adrenaline_mode = False
        self.adrenaline_timer = 0
        self.streak_multiplier = 1
        self.mission_manager = MissionManager()
        self.rare_event_manager = RareEventManager()
        self.difficulty_manager = DifficultyManager()
        self.screen_tilt = 0.0
        self.tilt_timer = 0.0
        self.base_speed = BASE_SCROLL_SPEED

    def add_floating_text(self, text, x, y, color=GOLD):
        self.floating_texts.append(FloatingText(text, x, y, color))

    def add_sparkle(self, x, y):
        self.sparkles.append(Sparkle(x, y))

    def reset_session(self):
        self.player = Player(100, SCREEN_HEIGHT//2, data_manager.data["selected_bird"])
        self.pipes.clear()
        self.score = 0
        self.combo = 0
        self.game_active = True
        self.pipe_timer = 0
        self.scroll_speed = BASE_SCROLL_SPEED
        self.current_gap = PIPE_GAP
        self.night_mode = False
        self.difficulty_score = 0
        self.floating_texts.clear()
        self.sparkles.clear()
        self.last_milestone = 0
        self.streak = 0
        self.adrenaline_mode = False
        self.adrenaline_timer = 0
        self.streak_multiplier = 1
        self.mission_manager = MissionManager()
        self.rare_event_manager = RareEventManager()
        self.difficulty_manager = DifficultyManager()
        self.screen_tilt = 0.0
        self.tilt_timer = 0.0
        self.base_speed = BASE_SCROLL_SPEED
        sound_manager.adrenaline_active = False
        sound_manager.music_switched = False
        sound_manager.play_game_music()

    def add_pipe(self):
        max_gap_y = SCREEN_HEIGHT - GROUND_HEIGHT - self.current_gap - 50
        min_gap_y = 50
        gap_y = random.randint(min_gap_y, max_gap_y)
        pipe_x = SCREEN_WIDTH
        if self.rare_event_manager.has_event("golden_pipe"):
            self.pipes.append(GoldenPipe(pipe_x, gap_y, self.current_gap))
        else:
            self.pipes.append(Pipe(pipe_x, gap_y, self.current_gap))

    def update(self, dt, shake_offset=(0,0)):
        if not self.game_active:
            return
        slow_factor = self.rare_event_manager.get_slow_motion_factor()
        effective_dt = dt * slow_factor

        self.player.update(effective_dt)

        if self.tilt_timer > 0:
            self.tilt_timer -= effective_dt
            self.screen_tilt = math.sin(self.tilt_timer * 20) * 2
        else:
            self.screen_tilt = 0.0

        self.rare_event_manager.update(effective_dt, self.score)

        mission_state = {"score": self.score, "combo": self.combo, "streak": self.streak}
        self.mission_manager.update(effective_dt, mission_state)

        intensity_changed = self.difficulty_manager.update(self.score)
        if intensity_changed:
            self.add_floating_text(f"INTENSITY {self.difficulty_manager.intensity}", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, RED)

        # FIX: was calling get_speed_multiplier() which didn't exist. Now it does.
        speed_mult = self.difficulty_manager.get_speed_multiplier()
        self.base_speed = BASE_SCROLL_SPEED + (self.score // 10) * SCROLL_SPEED_INCREMENT
        self.scroll_speed = self.base_speed * speed_mult
        gap_factor = self.difficulty_manager.get_gap_factor()
        self.current_gap = max(MIN_PIPE_GAP, int(PIPE_GAP * gap_factor - (self.score // 5) * GAP_DECREMENT))

        for pipe in self.pipes[:]:
            # FIX: pipe.update() takes speed in pixels-per-frame. We pass scroll_speed directly
            # (not multiplied by dt again) to match the original intent of x -= speed each frame.
            pipe.update(self.scroll_speed)
            pipe.coin.update(effective_dt)
            if pipe.x + PIPE_WIDTH < 0:
                self.pipes.remove(pipe)
                continue
            if not self.game_active:
                continue
            player_rect = self.player.get_rect()
            top_rect, bottom_rect = pipe.get_rects(offset_x=0, shake_offset=shake_offset)
            if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
                self.game_active = False
                return
            # Coin collection
            if not pipe.coin.collected:
                coin_rect = pipe.coin.get_rect()
                coin_rect.x += shake_offset[0]
                coin_rect.y += shake_offset[1]
                if player_rect.colliderect(coin_rect):
                    pipe.coin.collected = True
                    coin_multiplier = self.rare_event_manager.get_coin_multiplier()
                    earned = COIN_VALUE * coin_multiplier
                    if hasattr(pipe, 'golden') and pipe.golden:
                        earned += pipe.extra_coins
                    data_manager.add_coins(earned)
                    self.add_floating_text(f"+{earned}", self.player.x, self.player.y - 20, GOLD)
                    self.add_sparkle(pipe.coin.x, pipe.coin.y)
                    sound_manager.play_coin()
                    self.mission_manager.update_progress("coin_collected", 1, mission_state)
            # Score when passing pipe
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.player.x:
                pipe.passed = True
                self.streak += 1
                self.streak_multiplier = min(5, 1 + (self.streak // 5))
                points = 1 * self.streak_multiplier
                self.score += points
                combo_multiplier = max(1, self.combo)
                self.score += 1 * combo_multiplier
                coin_mult = self.rare_event_manager.get_coin_multiplier()
                earned = COIN_VALUE * coin_mult
                data_manager.add_coins(earned)
                self.add_floating_text(f"+{earned}", self.player.x, self.player.y - 20, GOLD)
                sound_manager.play_coin()
                if self.score // 10 > self.last_milestone:
                    self.last_milestone = self.score // 10
                    bonus = 5 * self.streak_multiplier
                    data_manager.add_coins(bonus)
                    self.add_floating_text(f"+{bonus} BONUS", self.player.x, self.player.y - 40, GOLD)
                    sound_manager.play_ping()
                self.combo += 1
                sound_manager.play_score()
                self.mission_manager.update_progress("pipe_passed", 1, mission_state)
                self.mission_manager.update_progress("score_increased", points, mission_state)
                self.mission_manager.update_progress("combo_changed", 0, mission_state)
                if self.streak > 5:
                    self.player.activate_glow(0.3)
                if self.streak >= 10 and not self.adrenaline_mode:
                    self.adrenaline_mode = True
                    self.adrenaline_timer = 5.0
                    sound_manager.activate_adrenaline()
                    self.add_floating_text("ADRENALINE MODE!", self.player.x, self.player.y - 60, RED)

        if self.player.y - self.player.radius <= 0 or self.player.y + self.player.radius >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.game_active = False
            return

        self.pipe_timer += effective_dt
        # FIX: pipe spacing should be time-based using scroll_speed for correct spacing
        pipe_spacing_frames = PIPE_SPACING / self.scroll_speed
        if self.pipe_timer > pipe_spacing_frames:
            self.pipe_timer = 0
            self.add_pipe()

        if self.score >= 15 and not self.night_mode:
            self.night_mode = True

        for ft in self.floating_texts[:]:
            ft.update(effective_dt)
            if ft.age >= ft.lifetime:
                self.floating_texts.remove(ft)
        for sp in self.sparkles[:]:
            if not sp.update(effective_dt):
                self.sparkles.remove(sp)

        if self.mission_manager.mission_complete:
            reward = self.mission_manager.claim_reward()
            if reward > 0:
                data_manager.add_coins(reward)
                self.add_floating_text(f"MISSION COMPLETE! +{reward}", SCREEN_WIDTH//2, 100, GOLD)
                sound_manager.play_mission_complete()

    def draw(self, screen, shake_offset=(0,0)):
        if self.night_mode:
            top = (25, 25, 50)
            bottom = (10, 10, 30)
        else:
            top = (80, 100, 150)
            bottom = (135, 206, 235)
        if self.adrenaline_mode:
            top = (min(255, top[0] + 50), top[1], min(255, top[2] + 50))
            bottom = (min(255, bottom[0] + 30), bottom[1], min(255, bottom[2] + 30))
        for y in range(SCREEN_HEIGHT):
            color = [top[i] + (bottom[i] - top[i]) * y / SCREEN_HEIGHT for i in range(3)]
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT + shake_offset[1], SCREEN_WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(screen, (100, 60, 10), ground_rect)
        pygame.draw.rect(screen, (80, 40, 5), ground_rect.inflate(0, -5))
        for pipe in self.pipes:
            pipe.draw(screen, offset_x=0, shake_offset=shake_offset)
        self.player.draw(screen, offset_x=0, shake_offset=shake_offset)
        for sp in self.sparkles:
            sp.draw(screen)
        for ft in self.floating_texts:
            ft.draw(screen)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_shadow = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_shadow, (20 + 2, 20 + 2))
        screen.blit(score_text, (20, 20))
        if self.streak > 0:
            streak_text = font.render(f"Streak: {self.streak}", True, GOLD)
            screen.blit(streak_text, (20, 60))
            mult_text = pygame.font.Font(None, 28).render(f"x{self.streak_multiplier}", True, YELLOW)
            screen.blit(mult_text, (20, 95))
        if self.combo > 1:
            combo_text = font.render(f"Combo x{self.combo}", True, GOLD)
            combo_shadow = font.render(f"Combo x{self.combo}", True, BLACK)
            screen.blit(combo_shadow, (20 + 2, 130 + 2))
            screen.blit(combo_text, (20, 130))
        if self.night_mode:
            night_text = font.render("NIGHT MODE", True, WHITE)
            screen.blit(night_text, (SCREEN_WIDTH - 120, 20))
        if self.adrenaline_mode:
            adrenaline_text = font.render("ADRENALINE MODE", True, RED)
            screen.blit(adrenaline_text, (SCREEN_WIDTH//2 - 100, 20))
        self.mission_manager.draw(screen)
        self.rare_event_manager.draw_indicators(screen)
        self.difficulty_manager.draw_intensity_indicator(screen)

    def get_jump_feedback(self):
        self.tilt_timer = 0.2
        self.player.activate_glow(0.2)

# Shop System
class Shop:
    def __init__(self):
        self.birds = {
            "Baby Bird": {"price": 0, "rarity": "Basic"},
            "Flying Squirrel": {"price": 10, "rarity": "Basic"},
            "Bee": {"price": 15, "rarity": "Basic"},
            "Eagle": {"price": 20, "rarity": "Rare"},
            "Owl": {"price": 25, "rarity": "Rare"},
            "Bat": {"price": 30, "rarity": "Rare"},
            "Parrot": {"price": 35, "rarity": "Rare"},
            "Butterfly": {"price": 40, "rarity": "Epic"},
            "Dragon": {"price": 45, "rarity": "Epic"},
            "Raven": {"price": 50, "rarity": "Epic"},
            "UFO Bird": {"price": 55, "rarity": "Legendary"},
            "Cosmic Raven": {"price": 60, "rarity": "Legendary"},
            "Thunder Phoenix": {"price": 65, "rarity": "Legendary"}
        }

    def purchase_bird(self, bird_name, current_coins, unlocked_birds):
        if bird_name in unlocked_birds:
            return "already_owned"
        price = self.birds[bird_name]["price"]
        if current_coins >= price:
            return "success"
        return "insufficient_funds"

    def get_bird_price(self, bird_name):
        return self.birds[bird_name]["price"]

# Button Class
class Button:
    def __init__(self, rect, text, font_size=36, base_color=GREEN, hover_color=(0, 230, 0), text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.scale = 1.0
        self.click_anim = 0

    def update(self, mouse_pos, dt):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.click_anim > 0:
            self.click_anim -= dt * 10
            if self.click_anim < 0:
                self.click_anim = 0
        target_scale = 1.05 if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.3
        if self.click_anim > 0:
            self.scale = 0.95

    def draw(self, screen):
        shadow_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=12)
        color = self.hover_color if self.hovered else self.base_color
        actual_rect = self.rect.inflate((self.scale-1)*self.rect.width, (self.scale-1)*self.rect.height)
        actual_rect.center = self.rect.center
        pygame.draw.rect(screen, color, actual_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, actual_rect, 2, border_radius=12)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=actual_rect.center)
        screen.blit(text_surf, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.click_anim = 0.15
            sound_manager.play_click()
            return True
        return False

# Main Game Manager
class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sky Escape: Legends - Challenge Mode")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MAIN_MENU"
        self.current_session = None
        self.menu_selected_index = 0
        self.menu_buttons = []
        self.transition_alpha = 0
        self.transition_direction = 0
        self.target_state = None
        self.beta_joined = data_manager.data["beta_joined"]
        self.beta_button_text = "Join Beta" if not self.beta_joined else "Joined Beta ✓"
        self.create_menu_buttons()
        self.shake_amount = 0
        self.shake_duration = 0
        self.shop_scroll_y = 0
        self.shop_selected = 0
        self.shop_item_height = 80
        self.shop_start_y = 100
        self.shop_visible_items = 6
        self.shop_total_items = len(shop.birds)
        self.shop_max_scroll = max(0, self.shop_total_items * self.shop_item_height - self.shop_visible_items * self.shop_item_height)
        self.daily_reward_manager = DailyRewardManager()
        self.progression_manager = ProgressionManager()
        self.game_over_popup_rect = None
        self.shop_feedback_text = ""
        self.shop_feedback_timer = 0
        self.best_run_diff = 0
        sound_manager.play_menu_music()

    def create_menu_buttons(self):
        button_width = 220
        button_height = 50
        start_y = 220
        spacing = 70
        btn_play = Button((SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height), "PLAY")
        btn_select = Button((SCREEN_WIDTH//2 - button_width//2, start_y + spacing, button_width, button_height), "SELECT")
        btn_exit = Button((SCREEN_WIDTH//2 - button_width//2, start_y + spacing*2, button_width, button_height), "EXIT")
        btn_beta = Button((20, SCREEN_HEIGHT - 50, 140, 40), self.beta_button_text, font_size=28, base_color=GOLD)
        self.menu_buttons = [btn_play, btn_select, btn_exit, btn_beta]

    def add_screen_shake(self, amount, duration):
        self.shake_amount = amount
        self.shake_duration = duration

    def get_shake_offset(self):
        if self.shake_duration <= 0:
            return (0, 0)
        angle = random.uniform(0, 2*math.pi)
        x = math.cos(angle) * self.shake_amount
        y = math.sin(angle) * self.shake_amount
        self.shake_duration -= 1
        if self.shake_duration <= 0:
            self.shake_amount = 0
        return (int(x), int(y))

    def reset_game(self):
        bird_type = data_manager.data["selected_bird"]
        self.current_session = GameSession(bird_type)
        self.state = "PLAYING"
        self.shake_amount = 0
        self.shake_duration = 0
        self.best_run_diff = 0

    def start_new_game(self):
        self.reset_game()
        self.start_transition("PLAYING")
        sound_manager.play_game_music()

    def instant_restart(self):
        if self.state in ["PLAYING", "GAME_OVER"]:
            self.reset_game()
            self.add_screen_shake(5, 10)
            sound_manager.play_click()
            sound_manager.play_game_music()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        self.start_transition("MAIN_MENU")
                        sound_manager.play_menu_music()
                    elif self.state in ["SHOP", "GAME_OVER"]:
                        self.start_transition("MAIN_MENU")
                        sound_manager.play_menu_music()
                    else:
                        self.state = "MAIN_MENU"
                elif event.key == pygame.K_p and self.state == "PLAYING":
                    self.state = "PAUSE"
                elif event.key == pygame.K_x:
                    self.instant_restart()
                if self.state == "MAIN_MENU":
                    if event.key == pygame.K_UP:
                        self.menu_selected_index = (self.menu_selected_index - 1) % len(self.menu_buttons)
                        sound_manager.play_click()
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected_index = (self.menu_selected_index + 1) % len(self.menu_buttons)
                        sound_manager.play_click()
                    elif event.key == pygame.K_RETURN:
                        self.activate_selected_button()
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        self.current_session.player.jump()
                        self.current_session.get_jump_feedback()
                        sound_manager.play_jump()
                elif self.state == "PAUSE":
                    if event.key == pygame.K_p:
                        self.state = "PLAYING"
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        self.reset_game()
                        sound_manager.play_game_music()
                    elif event.key == pygame.K_m:
                        self.start_transition("MAIN_MENU")
                        sound_manager.play_menu_music()
                elif self.state == "SHOP":
                    self.handle_shop_keys(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    if self.state == "SHOP":
                        self.shop_scroll_y = max(0, self.shop_scroll_y - self.shop_item_height * 0.8)
                        sound_manager.play_click()
                elif event.button == 5:
                    if self.state == "SHOP":
                        self.shop_scroll_y = min(self.shop_max_scroll, self.shop_scroll_y + self.shop_item_height * 0.8)
                        sound_manager.play_click()
                elif event.button == 1:
                    if self.state == "MAIN_MENU":
                        for i, btn in enumerate(self.menu_buttons):
                            if btn.handle_click(event.pos):
                                self.menu_selected_index = i
                                self.activate_selected_button()
                    elif self.state == "PLAYING":
                        self.current_session.player.jump()
                        self.current_session.get_jump_feedback()
                        sound_manager.play_jump()
                    elif self.state == "SHOP":
                        self.handle_shop_click(event.pos)
                    elif self.state == "GAME_OVER" and self.game_over_popup_rect:
                        self.handle_game_over_click(event.pos)

    def activate_selected_button(self):
        btn = self.menu_buttons[self.menu_selected_index]
        if btn.text == "PLAY":
            self.start_new_game()
        elif btn.text == "SELECT":
            self.state = "SHOP"
            self.shop_scroll_y = 0
            self.shop_selected = 0
        elif btn.text == "EXIT":
            self.running = False
        elif btn.text.startswith("Join Beta") or btn.text.startswith("Joined Beta"):
            if not self.beta_joined:
                self.beta_joined = True
                data_manager.data["beta_joined"] = True
                data_manager.save()
                self.beta_button_text = "Joined Beta ✓"
                self.menu_buttons[3].text = self.beta_button_text
                sound_manager.play_click()

    def start_transition(self, new_state):
        self.target_state = new_state
        self.transition_direction = 1
        self.transition_alpha = 0

    def update_transition(self, dt):
        if self.transition_direction == 1:
            self.transition_alpha += dt * 255 * 2
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.state = self.target_state
                self.transition_direction = -1
        elif self.transition_direction == -1:
            self.transition_alpha -= dt * 255 * 2
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transition_direction = 0

    def handle_shop_keys(self, event):
        if event.key == pygame.K_UP:
            self.shop_selected = max(0, self.shop_selected - 1)
            target_y = self.shop_selected * self.shop_item_height
            if target_y < self.shop_scroll_y:
                self.shop_scroll_y = target_y
            sound_manager.play_click()
        elif event.key == pygame.K_DOWN:
            self.shop_selected = min(self.shop_total_items - 1, self.shop_selected + 1)
            target_y = self.shop_selected * self.shop_item_height
            if target_y + self.shop_item_height > self.shop_scroll_y + self.shop_visible_items * self.shop_item_height:
                self.shop_scroll_y = target_y + self.shop_item_height - self.shop_visible_items * self.shop_item_height
            sound_manager.play_click()
        elif event.key == pygame.K_RETURN:
            self.purchase_selected_bird()
        elif event.key == pygame.K_ESCAPE:
            self.start_transition("MAIN_MENU")

    def handle_shop_click(self, pos):
        for i in range(self.shop_total_items):
            y = self.shop_start_y + i * self.shop_item_height - self.shop_scroll_y
            if 0 <= y < self.shop_visible_items * self.shop_item_height:
                item_rect = pygame.Rect(150, y, 500, self.shop_item_height - 5)
                if item_rect.collidepoint(pos):
                    self.shop_selected = i
                    self.purchase_selected_bird()
                    sound_manager.play_click()
                    break

    def handle_game_over_click(self, pos):
        btn_restart = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
        btn_menu = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 120, 200, 50)
        if btn_restart.collidepoint(pos):
            self.reset_game()
            sound_manager.play_game_music()
        elif btn_menu.collidepoint(pos):
            self.start_transition("MAIN_MENU")
            sound_manager.play_menu_music()

    def purchase_selected_bird(self):
        bird_name = list(shop.birds.keys())[self.shop_selected]
        result = shop.purchase_bird(bird_name, data_manager.data["coins"], data_manager.data["unlocked_birds"])
        if result == "success":
            price = shop.get_bird_price(bird_name)
            if data_manager.spend_coins(price):
                data_manager.data["unlocked_birds"].append(bird_name)
                data_manager.data["selected_bird"] = bird_name
                data_manager.save()
                self.shop_feedback_text = f"Purchased {bird_name}!"
                self.shop_feedback_timer = 90
                sound_manager.play_purchase()
                self.progression_manager.update()
            else:
                self.shop_feedback_text = "Error: Cannot deduct coins"
                self.shop_feedback_timer = 90
        elif result == "already_owned":
            data_manager.data["selected_bird"] = bird_name
            data_manager.save()
            self.shop_feedback_text = f"{bird_name} equipped!"
            self.shop_feedback_timer = 90
            sound_manager.play_click()
        else:
            price = shop.get_bird_price(bird_name)
            self.shop_feedback_text = f"Need {price} coins!"
            self.shop_feedback_timer = 90
            sound_manager.play_collision()

    def update(self, dt):
        sound_manager.update(dt)
        if self.transition_direction != 0:
            self.update_transition(dt)
            return
        if self.shop_feedback_timer > 0:
            self.shop_feedback_timer -= 1
        # FIX: get_shake_offset() mutates shake_duration each call. In the original draw()
        # it was called a second time separately, consuming shake twice. We compute once in
        # update() and store it, then reuse it in draw(). This also fixes double-shake consumption.
        self._cached_shake = self.get_shake_offset()
        if self.state == "PLAYING":
            self.current_session.update(dt, self._cached_shake)
            if not self.current_session.game_active:
                self.add_screen_shake(8, 15)
                sound_manager.play_collision()
                self.state = "GAME_OVER"
                self.calculate_game_over_data()
        elif self.state == "MAIN_MENU":
            mouse_pos = pygame.mouse.get_pos()
            for idx, btn in enumerate(self.menu_buttons):
                btn.update(mouse_pos, dt)
                if idx == self.menu_selected_index:
                    btn.hovered = True
            self.daily_reward_manager.update(dt)
            self.progression_manager.update()
            self.best_run_diff = data_manager.data["highscore"] - (self.current_session.score if self.current_session else 0)

    def calculate_game_over_data(self):
        session_score = self.current_session.score
        if session_score > data_manager.data["highscore"]:
            data_manager.data["highscore"] = session_score
        data_manager.data["total_score"] = data_manager.data.get("total_score", 0) + session_score
        data_manager.save()

    def draw_gradient_background(self, top_color, bottom_color):
        for y in range(SCREEN_HEIGHT):
            color = [top_color[i] + (bottom_color[i] - top_color[i]) * y / SCREEN_HEIGHT for i in range(3)]
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def draw_stats_panel(self):
        panel_width = 220
        panel_height = 110
        panel_x = SCREEN_WIDTH - panel_width - 20
        panel_y = 20
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        pygame.draw.rect(panel_surf, (0, 0, 0, 180), panel_surf.get_rect(), border_radius=12)
        pygame.draw.rect(panel_surf, WHITE, panel_surf.get_rect(), 2, border_radius=12)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        font = pygame.font.Font(None, 24)
        high_text = font.render(f"High Score: {data_manager.data['highscore']}", True, GOLD)
        self.screen.blit(high_text, (panel_x + 10, panel_y + 10))
        total_text = font.render(f"Total Score: {data_manager.data.get('total_score', 0)}", True, WHITE)
        self.screen.blit(total_text, (panel_x + 10, panel_y + 35))
        streak_text = font.render(self.daily_reward_manager.get_streak_text(), True, CYAN)
        self.screen.blit(streak_text, (panel_x + 10, panel_y + 60))
        if self.best_run_diff != 0:
            diff_text = font.render(f"Best Run: {self.best_run_diff:+}", True, YELLOW)
            self.screen.blit(diff_text, (panel_x + 10, panel_y + 85))
        coin_panel_width = 160
        coin_panel_height = 50
        coin_panel_x = 20
        coin_panel_y = 20
        coin_surf = pygame.Surface((coin_panel_width, coin_panel_height), pygame.SRCALPHA)
        coin_surf.fill((0, 0, 0, 180))
        pygame.draw.rect(coin_surf, (0, 0, 0, 180), coin_surf.get_rect(), border_radius=12)
        pygame.draw.rect(coin_surf, GOLD, coin_surf.get_rect(), 2, border_radius=12)
        self.screen.blit(coin_surf, (coin_panel_x, coin_panel_y))
        coin_text = font.render(f"Coins: {data_manager.data['coins']}", True, GOLD)
        self.screen.blit(coin_text, (coin_panel_x + 10, coin_panel_y + 12))

    def draw_main_menu(self):
        self.draw_gradient_background((20, 30, 80), (80, 100, 150))
        for layer in range(3):
            speed = 0.05 + layer * 0.03
            for i in range(8):
                cloud_x = (i * 180 + pygame.time.get_ticks() * speed) % (SCREEN_WIDTH + 300) - 150
                cloud_y = 50 + layer * 70
                alpha = 180 - layer * 50
                cloud_surf = pygame.Surface((120, 60), pygame.SRCALPHA)
                cloud_surf.set_alpha(alpha)
                pygame.draw.ellipse(cloud_surf, WHITE, (0, 0, 120, 60))
                pygame.draw.ellipse(cloud_surf, WHITE, (30, -20, 80, 50))
                self.screen.blit(cloud_surf, (cloud_x, cloud_y))
        font_large = pygame.font.Font(None, 72)
        title_y = 80 + math.sin(pygame.time.get_ticks() * 0.002) * 5
        title = font_large.render("SKY ESCAPE: LEGENDS", True, GOLD)
        title_shadow = font_large.render("SKY ESCAPE: LEGENDS", True, BLACK)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, title_y + 3))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, title_y))
        bird_y = 170 + math.sin(pygame.time.get_ticks() * 0.005) * 8
        demo_bird = Player(SCREEN_WIDTH//2, bird_y, data_manager.data["selected_bird"])
        demo_bird.draw(self.screen)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(SCREEN_WIDTH//2):
            alpha = int(30 * (1 - i/(SCREEN_WIDTH//2)))
            pygame.draw.circle(vignette, (0,0,0,alpha), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), SCREEN_WIDTH//2 - i)
        self.screen.blit(vignette, (0,0))
        self.draw_stats_panel()
        self.progression_manager.draw_progress_bar(self.screen, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 100, 220, 20)
        for btn in self.menu_buttons:
            btn.draw(self.screen)
        created_font = pygame.font.Font(None, 24)
        created_text = created_font.render("Created by Mehemmed", True, LIGHT_GRAY)
        self.screen.blit(created_text, (SCREEN_WIDTH//2 - created_text.get_width()//2, SCREEN_HEIGHT - 30))
        self.daily_reward_manager.draw(self.screen)

    def draw_shop(self):
        self.draw_gradient_background((30, 30, 50), (70, 70, 100))
        font = pygame.font.Font(None, 48)
        title = font.render("SHOP", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        coin_text = pygame.font.Font(None, 36).render(f"Coins: {data_manager.data['coins']}", True, GOLD)
        self.screen.blit(coin_text, (20, 20))
        self.progression_manager.draw_progress_bar(self.screen, SCREEN_WIDTH - 240, 30, 220, 20)
        for i in range(self.shop_total_items):
            y = self.shop_start_y + i * self.shop_item_height - self.shop_scroll_y
            if 0 <= y < self.shop_visible_items * self.shop_item_height:
                item_rect = pygame.Rect(150, y, 500, self.shop_item_height - 5)
                color = (100, 100, 150) if i == self.shop_selected else (60, 60, 90)
                pygame.draw.rect(self.screen, color, item_rect, border_radius=10)
                bird_name = list(shop.birds.keys())[i]
                preview = Player(item_rect.x + 40, item_rect.centery, bird_name)
                preview.draw(self.screen)
                name_text = pygame.font.Font(None, 28).render(bird_name, True, WHITE)
                self.screen.blit(name_text, (item_rect.x + 80, item_rect.y + 10))
                if bird_name in data_manager.data["unlocked_birds"]:
                    status = "SELECT" if data_manager.data["selected_bird"] != bird_name else "SELECTED"
                    status_color = GOLD if data_manager.data["selected_bird"] == bird_name else GREEN
                    status_text = pygame.font.Font(None, 24).render(status, True, status_color)
                    self.screen.blit(status_text, (item_rect.x + 80, item_rect.y + 40))
                else:
                    price_text = pygame.font.Font(None, 24).render(f"{shop.birds[bird_name]['price']} coins", True, GOLD)
                    self.screen.blit(price_text, (item_rect.x + 80, item_rect.y + 40))
        if self.shop_feedback_timer > 0:
            fb_font = pygame.font.Font(None, 32)
            fb_text = fb_font.render(self.shop_feedback_text, True, YELLOW)
            self.screen.blit(fb_text, (SCREEN_WIDTH//2 - fb_text.get_width()//2, SCREEN_HEIGHT - 80))
        inst_font = pygame.font.Font(None, 24)
        inst_text = inst_font.render("UP/DOWN: Navigate  ENTER: Buy/Select  ESC: Back  MOUSE WHEEL: Scroll", True, WHITE)
        self.screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, SCREEN_HEIGHT - 50))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 48)
        game_over_text = font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 150))
        score = self.current_session.score
        high_score = data_manager.data["highscore"]
        diff = score - high_score
        score_text = font.render(f"Score: {score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
        if diff > 0:
            new_record_text = font.render("NEW HIGH SCORE!", True, GOLD)
            self.screen.blit(new_record_text, (SCREEN_WIDTH//2 - new_record_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
        else:
            diff_text = font.render(f"Best: {high_score} ({diff:+})", True, YELLOW)
            self.screen.blit(diff_text, (SCREEN_WIDTH//2 - diff_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
        coins_text = font.render(f"Coins: {data_manager.data['coins']}", True, GOLD)
        self.screen.blit(coins_text, (SCREEN_WIDTH//2 - coins_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        btn_restart = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 80, 200, 50)
        pygame.draw.rect(self.screen, GREEN, btn_restart, border_radius=12)
        restart_text = pygame.font.Font(None, 36).render("RESTART", True, BLACK)
        self.screen.blit(restart_text, (btn_restart.centerx - restart_text.get_width()//2, btn_restart.centery - restart_text.get_height()//2))
        btn_menu = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 150, 200, 50)
        pygame.draw.rect(self.screen, GREEN, btn_menu, border_radius=12)
        menu_text = pygame.font.Font(None, 36).render("MENU", True, BLACK)
        self.screen.blit(menu_text, (btn_menu.centerx - menu_text.get_width()//2, btn_menu.centery - menu_text.get_height()//2))
        self.game_over_popup_rect = btn_restart.union(btn_menu)

    def draw(self):
        # FIX: use the shake offset cached in update() instead of calling get_shake_offset()
        # again here, which would double-consume and cause erratic shake behavior.
        shake = getattr(self, '_cached_shake', (0, 0))
        if self.state == "MAIN_MENU":
            self.draw_main_menu()
        elif self.state == "PLAYING":
            if self.current_session.screen_tilt != 0:
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                self.current_session.draw(surf, shake)
                rotated = pygame.transform.rotate(surf, self.current_session.screen_tilt)
                self.screen.blit(rotated, rotated.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            else:
                self.current_session.draw(self.screen, shake)
        elif self.state == "GAME_OVER":
            self.current_session.draw(self.screen, shake)
            self.draw_game_over()
        elif self.state == "PAUSE":
            self.current_session.draw(self.screen, shake)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 72)
            pause_text = font.render("PAUSED", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 36))
        elif self.state == "SHOP":
            self.draw_shop()
        if self.transition_direction != 0:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.set_alpha(int(self.transition_alpha))
            fade_surf.fill(BLACK)
            self.screen.blit(fade_surf, (0, 0))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 16.6667
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

# Initialize systems
data_manager = DataManager()
sound_manager = SoundManager()
shop = Shop()

# Run game
if __name__ == "__main__":
    game = GameManager()
    game.run()