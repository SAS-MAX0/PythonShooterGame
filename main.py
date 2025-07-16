#Initialising the gme setup along with setting display settings , resources and defining the groups for each sprites using pygame. the inistial stage to be used for the game is also set to main menu along with other important core variables like score, lives and also organse the game objects like bullets, players and enemies.
import pygame
import os
import random
import sys # Import sys for clean exits from Pygame

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python 2D Themed Shooter Game")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
title_font = pygame.font.Font(None, 96)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

game_state = 'main_menu' # Initial game state

score = 0
lives = 5
game_time = 0
difficulty_level = 1
last_enemy_spawn_time = 0
enemy_spawn_interval = 1500
# --- Player Fire Rate Variables ---
last_shot_time = 0 # Track when the last bullet was fired (milliseconds)
FIRE_DELAY = 250   # Minimum delay between shots (milliseconds, e.g., 250ms = 4 shots per second)

all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()


# this is not fully in use yet as only the default theme is in use for now. this helps store the file path for the needed assets like player, backgrounds and enemy. this helps reduce the need to repeat code when they can all be in the dictionaries.
THEMES = {
    'default': {
        'player': 'default/def_player.png',
        'enemy': 'default/def_enemy.png',
        'background': 'default/background.png',
        'menu_background': 'background.png', # Assuming this is a general background image for menu
        'bullet_color': RED,
        'enemy_bullet_color': BLACK
    }
}

THEME_AUDIO = {
    'default': 'dmusic.mp3',
}

current_game_theme_name = 'default'
current_theme = THEMES[current_game_theme_name]

#the load image function is just to make sure that we have proper error handling for the loading the images .this is the same reason for the play music function.
def load_image(path, size=None):
    # Determine the base path for assets for PyInstaller compatibility
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    
    full_path = os.path.join(base_path, 'assets', path) # Corrected path
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Error loading image {full_path}: {e}")
        placeholder = pygame.Surface(size if size else (50, 50))
        placeholder.fill(RED)
        return placeholder

background_img = load_image(current_theme['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_background_img = load_image(current_theme['menu_background'], (SCREEN_WIDTH, SCREEN_HEIGHT))

#the load audio function is just to make sure that we have proper error handling for loading audio files.
def load_audio(path):
    # Determine the base path for assets for PyInstaller compatibility
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    full_path = os.path.join(base_path, 'assets', path) # Corrected path
    try:
        return pygame.mixer.Sound(full_path)
    except pygame.error as e:
        print(f"Error loading audio {full_path}: {e}")
        return None

def play_music():
    global background_music

    music_name = THEME_AUDIO[current_game_theme_name]
    # Determine the base path for assets for PyInstaller compatibility
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    music_path = os.path.join(base_path, 'assets', current_game_theme_name, music_name) # Corrected path

    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
        print(f"Successfully started playing music: {music_path}")
    except pygame.error as e:
        print(f"Error playing music {music_path}: {e}. Make sure the .mp3 file exists in the correct assets subfolder!")
    except Exception as e:
        print(f"An unexpected error occurred during music playback: {e}")

# these class all define the way the game objects will be with each one being straightfoward all from player to the enemybullet. 
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
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.velocity
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.velocity

        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)

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
        self.last_shot_time = pygame.time.get_ticks()
        self.shot_cooldown = max(1000 - difficulty_level * 100, 200)
    
    def update(self):
        self.rect.x -= self.velocity
        if self.rect.right < 0: 
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.size)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 5)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.velocity
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 20
        self.color = RED

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

        alpha = int(255 * (self.timer / 20))
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (*self.color, alpha), (20, 20), 20)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, target_x, target_y, velocity_factor, difficulty, owner):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 5)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.owner = owner

        try:
            direction_vector = pygame.math.Vector2(target_x - x, target_y - y).normalize()
        except ValueError:
            direction_vector = pygame.math.Vector2(0, -1)

        self.velocity = direction_vector * (velocity_factor + difficulty)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# this is where the game flow logic and UI that helps in drawing text, showing menus, resetting game state, firing bullets,and spawning enemie.
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
    global game_state
    mouse_pos = pygame.mouse.get_pos()
    
    screen.blit(menu_background_img, (0, 0))

    draw_text("Space Shooter", title_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    
    start_button = pygame.Rect(SCREEN_WIDTH/2 - 110, SCREEN_HEIGHT/2 - 30, 220, 60)
    quit_button = pygame.Rect(SCREEN_WIDTH/2 - 110, SCREEN_HEIGHT/2 + 60, 220, 60)
    
    pygame.draw.rect(screen, (0, 255, 180) if start_button.collidepoint(mouse_pos) else GREEN, start_button, border_radius=12)
    pygame.draw.rect(screen, (255, 100, 100) if quit_button.collidepoint(mouse_pos) else RED, quit_button, border_radius=12)
    
    draw_text("PLAY", font, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    draw_text("QUIT", font, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 90)
    
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                game_state = 'playing'
                reset_game()
            if quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

def game_over_screen():
    global game_state
    screen.blit(background_img, (0, 0))
    draw_text("GAME OVER", title_font, RED, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    
    draw_text(f"Final Score: {score}", large_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
    
    restart_button = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 50, 200, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 125, 200, 50)
    
    pygame.draw.rect(screen, GREEN, restart_button)
    pygame.draw.rect(screen, RED, quit_button)
    
    draw_text("RESTART", font, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75)
    draw_text("QUIT", font, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150)
    
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                game_state = 'playing'
                reset_game()
            if quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

def reset_game():
    global score, lives, game_time, difficulty_level, last_enemy_spawn_time, last_shot_time, player
    
    score = 0
    lives = 5
    game_time = 0
    difficulty_level = 1
    last_enemy_spawn_time = pygame.time.get_ticks()
    last_shot_time = pygame.time.get_ticks()

    all_sprites.empty()
    players.empty()
    enemies.empty()
    player_bullets.empty()
    explosions.empty()
    enemy_bullets.empty()

    player = Player(current_theme['player'], 50, SCREEN_HEIGHT / 2 - 50, 100, 5)
    all_sprites.add(player)
    players.add(player)
    
    play_music()

def launch_bullet():
    if player in players:
        global last_shot_time
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time > FIRE_DELAY:
            bullet_x = player.rect.right
            bullet_y = player.rect.centery
            bullet_velocity = 10 
            bullet = PlayerBullet(bullet_x, bullet_y, current_theme['bullet_color'], bullet_velocity) 
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            print("DEBUG: Bullet launched!")
            last_shot_time = current_time

def spawn_enemy():
    enemy_size = 50
    enemy_x = SCREEN_WIDTH
    enemy_y = random.randint(0, SCREEN_HEIGHT - enemy_size)
    enemy_velocity = 2 + (difficulty_level * 0.5)
    enemy_health = 1 + difficulty_level // 3
    enemy = Enemy(current_theme['enemy'], enemy_x, enemy_y, enemy_size, enemy_velocity, health=enemy_health)
    all_sprites.add(enemy)
    enemies.add(enemy)

def update_enemy_shooting():
    global game_time, difficulty_level
    now = pygame.time.get_ticks()
    game_time += 1
    difficulty_level = 1 + int(game_time / 2000)

    for enemy in enemies:
        if now - enemy.last_shot_time > enemy.shot_cooldown and player in players:
            if player.rect:
                bullet = EnemyBullet(
                    enemy.rect.centerx,
                    enemy.rect.centery,
                    current_theme['enemy_bullet_color'],
                    player.rect.centerx,
                    player.rect.centery,
                    2,
                    difficulty_level,
                    enemy
                )
                enemy_bullets.add(bullet)
                all_sprites.add(bullet)
                enemy.last_shot_time = now

# the main game loop handles the action in game like input, updating the objects, detecting collisions and also redrawing everything until quit.
player = Player(current_theme['player'], 50, SCREEN_HEIGHT / 2 - 50, 100, 5)
all_sprites.add(player)
players.add(player)

running = True
while running:
    clock.tick(FPS)

    if game_state == 'main_menu':
        main_menu()
    elif game_state == 'playing':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    launch_bullet()

        update_enemy_shooting()
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_spawn_time > enemy_spawn_interval:
            spawn_enemy()
            last_enemy_spawn_time = current_time

        keys = pygame.key.get_pressed()
        players.update(keys)
        enemies.update()
        player_bullets.update()
        explosions.update()
        enemy_bullets.update() 
        
        hits = pygame.sprite.groupcollide(player_bullets, enemies, True, False, pygame.sprite.collide_mask)
        for bullet_hit, hit_enemies in hits.items():
            for enemy_hit in hit_enemies:
                enemy_hit.health -= 1
                if enemy_hit.health <= 0:
                    for bullet in enemy_bullets:
                        if bullet.owner == enemy_hit:
                            bullet.kill()
                    enemy_hit.kill()
                    score += 10
                    explosion = Explosion(enemy_hit.rect.centerx, enemy_hit.rect.centery)
                    all_sprites.add(explosion)
                    explosions.add(explosion)

        if player in players:
            player_hit_by_enemy_bullets_this_frame = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_mask)
            if player_hit_by_enemy_bullets_this_frame:
                lives -= 1
                print(f"Player hit! Lives remaining: {lives}")
                if lives <= 0:
                    player.kill()
                    game_state = 'game_over'
                    pygame.mixer.music.stop()
                    print("Game Over!")

        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)

        draw_text(f"Score: {score}", font, WHITE, screen, 80, 25)
        draw_text(f"Lives: {lives}", font, WHITE, screen, SCREEN_WIDTH - 80, 25)

        pygame.display.flip()

    elif game_state == 'game_over':
        game_over_screen()

pygame.quit()
