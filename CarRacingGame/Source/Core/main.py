import pygame
import sys

# Initialize Pygame
pygame.init()

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

# Track boundaries (simple rectangle)
TRACK_RECT = pygame.Rect(100, 100, 600, 400)

# Create player car
player = PlayerCar(WIDTH//2, HEIGHT//2)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys)

    # Keep car within track boundaries
    if not TRACK_RECT.contains(pygame.Rect(player.x-25, player.y-15, 50, 30)):
        player.speed = -player.speed * 0.5
        player.x = max(TRACK_RECT.left+25, min(player.x, TRACK_RECT.right-25))
        player.y = max(TRACK_RECT.top+15, min(player.y, TRACK_RECT.bottom-15))

    screen.fill((30, 30, 30))  # Clear screen
    pygame.draw.rect(screen, (60, 120, 60), TRACK_RECT, 5)
    player.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
