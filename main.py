import pygame
import random

pygame.init()
pygame.font.init()

WIDTH = 1200
HEIGHT = 800
FPS = 60
speed = 5
zoom = 1.0
zoom_target = 1.0
zoom_speed = 0.02

x = 1000
y = 600

gravity = 1
jump_height = 15
player_velocity_y = 0

RED = (255, 0, 0)
WHITE = (255, 255, 255)
CYAN = (100, 100, 255)

player_damage = 10

BG_COLOR = (20, 20, 20)
PLAYER_COLOR = (0, 0, 0)
PLATFORM_COLOR = (50, 100, 20)
ENTITY_COLOR = (255, 0, 0)
ATTACK_COLOR = (255, 255, 0)

player_exp = 0
player_health = 100
player_max_health = 100

time_since_last_damage = 0
heal_timer = 0
damage_interval = FPS // 2
heal_interval = FPS
damage_amount = 20

run = True
playerdead = False
jump = False

player_texture = pygame.image.load("textures/player/player.png")

sc = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 30)
HEALTH_FONT = pygame.font.SysFont("Arial", 25, bold=True)

class DamageText:
    def __init__(self, x, y, text, duration=60):
        self.x = x + random.randint(-20, 20)
        self.y = HEIGHT - 50
        self.text = text
        self.duration = duration
        self.alpha = 255

    def update(self):
        self.alpha -= 4
        self.duration -= 1

    def draw(self, surface):
        if self.duration > 0:
            temp_surface = HEALTH_FONT.render(self.text, True, (255, 0, 0))
            temp_surface.set_alpha(self.alpha)
            surface.blit(temp_surface, (self.x, self.y))


class Block_creator:
    def __init__(self, x, y, width, height, image=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.flipped = False

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface, camera_offset, color):
        draw_rect = self.rect.move(camera_offset[0], camera_offset[1])
        scaled_rect = pygame.Rect(
            draw_rect.x * zoom, draw_rect.y * zoom,
            draw_rect.width * zoom, draw_rect.height * zoom
        )
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (scaled_rect.width, scaled_rect.height))
            surface.blit(scaled_image, scaled_rect.topleft)
        else:
            pygame.draw.rect(surface, color, scaled_rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.update_rect()


class Player(Block_creator):
    def __init__(self, x, y, width, height,texture):
        super().__init__(x, y, width, height,texture)
        self.direction = "right"
        self.attack_rect = None
        self.player_health = 100
        self.walk_frames = [pygame.image.load(f"textures/player/animation/player_walk/player_walk{i}.png").convert_alpha() for i in range(1, 5)]
        self.current_frame = 0
        self.animation_speed = 0.2
        self.frame_index = 0

    def draw(self, surface, camera_offset, _color):
        draw_rect = self.rect.move(camera_offset[0], camera_offset[1])
        if self.direction == "left":
            scaled_image = pygame.transform.flip(self.walk_frames[int(self.frame_index)], True, False)
        else:
            scaled_image = self.walk_frames[int(self.frame_index)]
        surface.blit(scaled_image, draw_rect.topleft)

    def move(self, dx, dy):
        super().move(dx, dy)
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

    def attack(self, entities, ):
        global player_damage
        attack_width = 50
        attack_height = 20

        if self.direction == "left":
            attack_x = self.rect.left - attack_width
            attack_y = self.rect.top + (self.height // 2) - (attack_height // 2)

        elif self.direction == "right":
            attack_x = self.rect.right
            attack_y = self.rect.top + (self.height // 2) - (attack_height // 2)

        self.attack_rect = pygame.Rect(attack_x, attack_y, attack_width, attack_height)

        for entity in entities:
            if entity.is_alive() and self.attack_rect.colliderect(entity.rect):
                entity.take_damage(player_damage)
                show_damage(random.randint(50, WIDTH - 200), HEIGHT - 50, entity.health)


class Entity:
    def __init__(self, x_entity, y_entity, width, height, entity_health, entity_damage, image=None):
        self.x = x_entity
        self.y = y_entity
        self.width = width
        self.height = height
        self.image = image
        self.health = entity_health
        self.damage = entity_damage
        self.rect = pygame.Rect(x_entity, y_entity, width, height)
        self.direction = "left"
        self.start_x = x_entity
        self.target_left = self.start_x - 50
        self.target_right = self.start_x + 50

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface, camera_offset, color):
        draw_rect = self.rect.move(camera_offset[0], camera_offset[1])
        scaled_rect = pygame.Rect(
            draw_rect.x * zoom, draw_rect.y * zoom,
            draw_rect.width * zoom, draw_rect.height * zoom
        )
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (scaled_rect.width, scaled_rect.height))
            surface.blit(scaled_image, scaled_rect.topleft)
        else:
            pygame.draw.rect(surface, color, scaled_rect)

    def entity_move(self, entity_speed):
        if self.direction == "left":
            self.x -= entity_speed
            if self.x <= self.target_left:
                self.x = self.target_left
                self.direction = "right"
        elif self.direction == "right":
            self.x += entity_speed
            if self.x >= self.target_right:
                self.x = self.target_right
                self.direction = "left"
        self.update_rect()

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        if self.health <= 0:
            self.die()

    def die(self):
        global player_exp
        self.health = 0
        player_exp += random.randint(100, 200)

    def is_alive(self):
        return self.health > 0


class Area:
    def __init__(self, x, y, width, heght, color):
        self.rect = pygame.Rect(x, y, width, heght)
        self.fill_color = color

    def set_color(self, color):
        self.fill_color = color

    def fill(self):
        pygame.draw.rect(sc, self.fill_color, self.rect)

    def out_line(self, color, width):
        pygame.draw.rect(sc, color, self.rect, width)


class Label(Area):
    def set_text(self, text, height, color=(0, 0, 0)):
        self.font = pygame.font.SysFont(None, height)
        self.image = self.font.render(str(text), True, color)

    def draw(self, x, y):
        self.fill()
        sc.blit(self.image, (self.rect.x + x, self.rect.y + y))


player = Player(160, 474, 40, 86, player_texture)

damage_texts = []

blocks = [
    Block_creator(0, 560, 500, 40),
    Block_creator(480, 560, 500, 40),
    Block_creator(960, 560, 500, 40),
    Block_creator(1440, 520, 500, 40),
    Block_creator(1920, 480, 500, 40),
    Block_creator(2400, 440, 500, 40),
    Block_creator(2880, 480, 500, 40)
]

entities = [
    Entity(300, 510, 40, 50, 100, 10),
]

camera_offset = [0, 0]
wait_attack = 0


def draw_menu():
    menu_running = True
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((30, 30, 30))

    while menu_running:
        sc.blit(overlay, (0, 0))
        pygame.draw.rect(sc, (50, 50, 50), (300, 200, 600, 400), border_radius=20)

        title = FONT.render("Меню прокачки", True, (255, 255, 255))
        sc.blit(title, (500, 220))

        option1 = FONT.render("1: Додати HP (-150 XP)", True, (200, 200, 200))
        option2 = FONT.render("2: Додати швидкість (-150 XP)", True, (200, 200, 200))
        sc.blit(option1, (400, 300))
        sc.blit(option2, (400, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_running = False
        pygame.time.delay(50)

def show_damage(x, y, hp_left):
    damage_texts.append(DamageText(x, y, f"{hp_left} HP"))

while run:
    sc.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                draw_menu()
                pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if wait_attack <= 0:
                player.attack(entities)
                wait_attack = 45
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and playerdead:
                player_health = 100
                player_exp = 0
                playerdead = False
                speed = 5
                player_health = 100
                player = Player(x, y, 40, 86,player_texture)
                entities = [
                    Entity(300, 650, 40, 50, 100, 10),
                    Entity(500, 650, 40, 50, 100, 15),
                    Entity(700, 650, 40, 50, 100, 20)
                ]

    wait_attack -= 1

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.x -= speed
        player.direction = "left"
        player.frame_index = (player.frame_index + player.animation_speed) % len(player.walk_frames)
        player.flipped = True
        player.move(-speed, 0)

    elif keys[pygame.K_d]:
        player.x += speed
        player.direction = "right"
        player.frame_index = (player.frame_index + player.animation_speed) % len(player.walk_frames)
        player.flipped = True
        player.move(speed, 0)
    else:
        player.frame_index = 0

    if keys[pygame.K_SPACE] and not jump and not playerdead:
        jump = True
        player_velocity_y = -jump_height

    if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
        if zoom_target <= 2:
            zoom_target += zoom_speed
    if keys[pygame.K_MINUS]:
        if zoom_target >= 0.5:
            zoom_target -= zoom_speed

    zoom += (zoom_target - zoom) * 0.1

    if jump:
        player.move(0, player_velocity_y)
        player_velocity_y += gravity

    collided = False
    for b in blocks:
        if player.rect.colliderect(b.rect):
            if player_velocity_y > 0:
                player.rect.bottom = b.rect.top
                player.y = player.rect.top
                player.update_rect()
                jump = False
                player_velocity_y = 0
                collided = True
                break
            elif player_velocity_y < 0:
                player.rect.top = b.rect.bottom
                player.y = player.rect.top
                player.update_rect()
                player_velocity_y = 0
                break

    if not collided and player.rect.bottom < HEIGHT:
        jump = True

    camera_offset[0] = -player.rect.centerx + (WIDTH // 2) / zoom
    camera_offset[1] = -player.rect.centery + (HEIGHT // 2) / zoom

    for entity in entities:
        if entity.is_alive():
            entity.entity_move(2)
            if entity.rect.colliderect(player.rect):
                if time_since_last_damage >= damage_interval:
                    player_health -= entity.damage
                    time_since_last_damage = 0
                    if player_health <= 0:
                        playerdead = True

    if heal_timer >= heal_interval:
        player_health = min(player_health + 10, player_max_health)
        heal_timer = 0

    entities = [entity for entity in entities if entity.is_alive()]

    sc.fill(BG_COLOR)

    exp_bar = Label(WIDTH - 80, 10, 70, 70, CYAN)
    exp_bar.set_text(player_exp, 35)
    exp_bar.draw(10, 10)
    exp_bar.out_line((133, 109, 5), 2)

    health_bar = Label(WIDTH - 180, 10, 70, 70, RED)
    health_bar.set_text(player_health, 35)
    health_bar.draw(10, 10)
    health_bar.out_line((133, 109, 5), 2)

    player.draw(sc, camera_offset, PLAYER_COLOR)

    for entity in entities:
        if entity.is_alive():
            entity.draw(sc, camera_offset, ENTITY_COLOR)

    for b in blocks:
        b.draw(sc, camera_offset, PLATFORM_COLOR)

    for dmg_text in damage_texts[:]:
        dmg_text.update()
        dmg_text.draw(sc)
        if dmg_text.duration <= 0:
            damage_texts.remove(dmg_text)

    if entity.rect.colliderect(player.rect):
        if time_since_last_damage >= damage_interval:
            player_health -= damage_amount
            time_since_last_damage = 0
            if player_health <= 0:
                playerdead = True

    if heal_timer >= heal_interval:
        player_health = min(player_health + 10, player_max_health)
        heal_timer = 0

    entities = [entity for entity in entities if entity.is_alive()]

    if playerdead:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        sc.blit(overlay, (0, 0))
        speed = 0
        player_health = 0

        font = pygame.font.SysFont(None, 60)
        text = font.render("ПРОГРАШ!Нажми Q щоб грати заново", True, CYAN)
        sc.blit(text, (220, HEIGHT // 2))

    pygame.display.update()
    clock.tick(FPS)
    time_since_last_damage += 1
    heal_timer += 1

pygame.quit()
