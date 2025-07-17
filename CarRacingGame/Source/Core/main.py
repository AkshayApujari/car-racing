import pygame
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Audio setup
audio_path = os.path.join(os.path.dirname(__file__), '../../Assets/Audio')
bg_music_file = os.path.join(audio_path, 'background_music.ogg')
engine_sound_file = os.path.join(audio_path, 'engine.ogg')
lap_sound_file = os.path.join(audio_path, 'lap.ogg')

# Load sounds (use try/except for missing files)
try:
    pygame.mixer.music.load(bg_music_file)
    pygame.mixer.music.play(-1)
except Exception:
    pass
try:
    engine_sound = pygame.mixer.Sound(engine_sound_file)
except Exception:
    engine_sound = None
try:
    lap_sound = pygame.mixer.Sound(lap_sound_file)
except Exception:
    lap_sound = None

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Car Racing Game')
clock = pygame.time.Clock()

# Player Car class
import math

class PlayerCar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (200, 0, 0), [(0,0),(50,15),(0,30)])

    def update(self, keys):
        if keys[pygame.K_UP]:
            self.speed += 0.2
        elif keys[pygame.K_DOWN]:
            self.speed -= 0.2
        else:
            self.speed *= 0.95  # friction

        if keys[pygame.K_LEFT]:
            self.angle -= 3
        if keys[pygame.K_RIGHT]:
            self.angle += 3

        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)
        
# Opponent Car class
class OpponentCar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 2
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (0, 0, 200), [(0,0),(50,15),(0,30)])
        self.path = [(150, 150), (650, 150), (650, 450), (150, 450)]
        self.target_idx = 0

    def update(self):
        target = self.path[self.target_idx]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.hypot(dx, dy)
        if dist < 5:
            self.target_idx = (self.target_idx + 1) % len(self.path)
        else:
            self.angle = math.degrees(math.atan2(dy, dx))
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y += self.speed * math.sin(math.radians(self.angle))

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

# Track boundaries (simple rectangle)
TRACK_RECT = pygame.Rect(100, 100, 600, 400)

# Lap checkpoints (corners of the track)
CHECKPOINTS = [(150, 150), (650, 150), (650, 450), (150, 450)]

# Create player car
player = PlayerCar(WIDTH//2, HEIGHT//2)
opponent = OpponentCar(150, 150)

# Game state
game_state = "menu"  # menu, running, paused, gameover
lap_start_time = None
lap_time = 0
best_lap = None
score = 0
checkpoint_idx = 0

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "menu" and event.key == pygame.K_RETURN:
                game_state = "running"
                lap_start_time = time.time()
            elif game_state == "running" and event.key == pygame.K_p:
                game_state = "paused"
            elif game_state == "paused" and event.key == pygame.K_p:
                game_state = "running"
            elif game_state == "gameover" and event.key == pygame.K_RETURN:
                # Reset game
                player.x, player.y = WIDTH//2, HEIGHT//2
                player.angle, player.speed = 0, 0
                opponent.x, opponent.y = 150, 150
                opponent.target_idx = 0
                lap_start_time = time.time()
                lap_time = 0
                best_lap = None
                score = 0
                checkpoint_idx = 0
                game_state = "menu"

    if game_state == "running":
        keys = pygame.key.get_pressed()
        player.update(keys)
        opponent.update()

        # Engine sound volume based on speed
        if engine_sound:
            engine_sound.set_volume(min(1.0, abs(player.speed)/10))
            if not pygame.mixer.Channel(0).get_busy():
                pygame.mixer.Channel(0).play(engine_sound, loops=-1)

    # Keep car within track boundaries
        if not TRACK_RECT.contains(pygame.Rect(player.x-25, player.y-15, 50, 30)):
            player.speed = -player.speed * 0.5
            player.x = max(TRACK_RECT.left+25, min(player.x, TRACK_RECT.right-25))
            player.y = max(TRACK_RECT.top+15, min(player.y, TRACK_RECT.bottom-15))

    # Collision detection
        player_rect = pygame.Rect(player.x-25, player.y-15, 50, 30)
        opponent_rect = pygame.Rect(opponent.x-25, opponent.y-15, 50, 30)
        if player_rect.colliderect(opponent_rect):
            player.speed = -abs(player.speed) * 0.7

        # Lap timer and checkpoints
        cp_x, cp_y = CHECKPOINTS[checkpoint_idx]
        if math.hypot(player.x-cp_x, player.y-cp_y) < 40:
            checkpoint_idx += 1
            if checkpoint_idx >= len(CHECKPOINTS):
                checkpoint_idx = 0
                lap_time = time.time() - lap_start_time
                lap_start_time = time.time()
                score += 1
                if best_lap is None or lap_time < best_lap:
                    best_lap = lap_time
                if score >= 3:
                    game_state = "gameover"
                # Play lap sound
                if lap_sound:
                    lap_sound.play()

    screen.fill((30, 30, 30))  # Clear screen
    pygame.draw.rect(screen, (60, 120, 60), TRACK_RECT, 5)
    player.draw(screen)
    opponent.draw(screen)

    font = pygame.font.SysFont(None, 36)
    if game_state == "menu":
        title = font.render("Car Racing Game", True, (255,255,0))
        prompt = font.render("Press ENTER to Start", True, (255,255,255))
        screen.blit(title, (WIDTH//2-120, HEIGHT//2-60))
        screen.blit(prompt, (WIDTH//2-140, HEIGHT//2))
    elif game_state == "paused":
        paused = font.render("Paused - Press P to Resume", True, (255,255,255))
        screen.blit(paused, (WIDTH//2-180, HEIGHT//2))
    elif game_state == "gameover":
        over = font.render("Game Over!", True, (255,0,0))
        laps = font.render(f"Laps: {score}", True, (255,255,255))
        best = font.render(f"Best Lap: {best_lap:.2f}s" if best_lap else "Best Lap: --", True, (255,255,255))
        prompt = font.render("Press ENTER to Restart", True, (255,255,255))
        screen.blit(over, (WIDTH//2-100, HEIGHT//2-60))
        screen.blit(laps, (WIDTH//2-60, HEIGHT//2))
        screen.blit(best, (WIDTH//2-100, HEIGHT//2+40))
        screen.blit(prompt, (WIDTH//2-160, HEIGHT//2+80))
    elif game_state == "running":
        speed_text = font.render(f"Speed: {abs(player.speed):.1f}", True, (255,255,255))
        lap_text = font.render(f"Lap: {score+1}/3", True, (255,255,255))
        timer_text = font.render(f"Lap Time: {time.time()-lap_start_time:.2f}s", True, (255,255,255))
        best_text = font.render(f"Best: {best_lap:.2f}s" if best_lap else "Best: --", True, (255,255,255))
        screen.blit(speed_text, (20, 20))
        screen.blit(lap_text, (20, 60))
        screen.blit(timer_text, (20, 100))
        screen.blit(best_text, (20, 140))
        pause_text = font.render("Press P to Pause", True, (200,200,200))
        screen.blit(pause_text, (WIDTH-220, 20))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
