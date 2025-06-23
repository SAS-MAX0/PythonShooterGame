import pygame
import os

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Shooter Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

score = 0
lives = 5
game_over = False
game_time = 0
difficulty_level = 1
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
enemies = pygame.sprite.Group()
last_enemy_spawn_time = pygame.time.get_ticks()
enemy_spawn_interval = 1500


THEMES= {
    'default' :{
        'player': 'default/def_player.png',
        'enemy': 'default/def_enemy.png',
        'background': 'default/background.png',
        'bullet_color': RED,
        'enemy_bullet_color': BLACK
    }
}

THEME_AUDIO = {
    'default': 'dmusic.mp3',
}

game_theme_name = 'default'
current_theme = THEMES[game_theme_name]

def load_image(path, size=None):
    full_path = os.path.join('assets', path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Error loading image {full_path}: {e}")
        placeholder = pygame.Surface((50, 50))
        placeholder.fill(RED)
        return placeholder

background_img = load_image(current_theme['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
def load_audio(path):
    full_path = os.path.join('assets', path)
    try:
        return pygame.mixer.Sound(full_path)
    except pygame.error as e:
        print(f"Error loading {full_path}: {e}")
        return None


class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, size, velocity):
        super().__init__()

        self.original_image = load_image(image_path, (size, size))
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.velocity = velocity
        self.size = size
        self.mask = pygame.mask.from_surface(self.image, 50)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.velocity
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.velocity
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.velocity

        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.left = max(0, self.rect.left)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, size, velocity, health=1):
        super().__init__()

        self.original_image = load_image(image_path, (size, size))
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = velocity
        self.size = size
        self.mask = pygame.mask.from_surface(self.image, 50)
        self.health = health
      
    def update(self):
        self.rect.x -= self.velocity
        if self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH
            self.rect.y = pygame.time.get_ticks() % (SCREEN_HEIGHT - self.size)
    def draw(self, surface):
        surface.blit(self.image, self.rect)

def play_music():
    global background_music
    music_name = THEME_AUDIO[game_theme_name]
    music_path = os.path.join('assets', game_theme_name, music_name)
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
        print(f"Started playing music: {music_path}")
    except:
        print(f"Error playing: {music_path}")

play_music()


def spawn_enemy():
    enemy_size = 50
    enemy_x = SCREEN_WIDTH
    enemy_y = pygame.time.get_ticks() % (SCREEN_HEIGHT - enemy_size)
    enemy_velocity = 2
    enemy = Enemy(current_theme['enemy'], enemy_x, enemy_y, enemy_size, enemy_velocity, health=1)
    all_sprites.add(enemy)
    enemies.add(enemy)

player = Player(
    current_theme['player'],
    50,
    SCREEN_HEIGHT - 150,
    100,
    5
)


all_sprites.add(player)
players.add(player)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_spawn_time > enemy_spawn_interval:
        spawn_enemy()
        last_enemy_spawn_time = current_time
    keys = pygame.key.get_pressed()
    player.update(keys)
    enemies.update()
    screen.fill(BLACK)
    screen.blit(background_img, (0,0))
    all_sprites.draw(screen)
    pygame.display.flip()

    clock.tick(FPS)
pygame.quit()