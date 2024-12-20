import pygame

pygame.init()

WIDTH = 1200
HEIGHT = 800
FPS = 60
speed = 5
zoom = 1.0
zoom_target = 1.0
zoom_speed = 0.02

x_player = WIDTH // 2
y_player = HEIGHT // 2

run = True
jump = False
gravity = 1
jump_height = 15
player_velocity_y = 0

RED = (255,0,0)
WHITE = (255, 255, 255)
BG_COLOR = (10,10,10)
PLAYER_COLOR = (0, 0, 0)
PLATFORM_COLOR = (50, 100, 20)

sc = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class block_creator:
    def __init__(self, x, y, width, height, image=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image

    def draw(self, surface, camera_offset, COLOR):
        draw_rect = self.rect.move(camera_offset[0], camera_offset[1])
        scaled_rect = pygame.Rect(
            draw_rect.x * zoom, draw_rect.y * zoom,
            draw_rect.width * zoom, draw_rect.height * zoom
        )
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (scaled_rect.width, scaled_rect.height))
            surface.blit(scaled_image, scaled_rect.topleft)
        else:
            pygame.draw.rect(surface, COLOR, scaled_rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

player = block_creator(x_player, y_player, 40, 70)
platform = block_creator(0, 700, WIDTH, 30)

blocks = [platform,
          block_creator(300, 600, 200, 30),
          block_creator(600, 500, 150, 30)
          ]

camera_offset = [0, 0]

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.move(-speed, 0)
    if keys[pygame.K_d]:
        player.move(speed, 0)
    if keys[pygame.K_SPACE] and not jump:
        jump = True
        player_velocity_y = -jump_height
    if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
        zoom_target += zoom_speed
    if keys[pygame.K_MINUS]:
        zoom_target = max(0.5, zoom_target - zoom_speed)

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
                jump = False
                player_velocity_y = 0
                collided = True
                break
            elif player_velocity_y < 0:
                player.rect.top = b.rect.bottom
                player.y = player.rect.top
                player_velocity_y = 0
                break

    if not collided and player.rect.bottom < HEIGHT:
        jump = True

    camera_offset[0] = -player.rect.centerx + (WIDTH // 2) / zoom
    camera_offset[1] = -player.rect.centery + (HEIGHT // 2) / zoom

    sc.fill(BG_COLOR)
    player.draw(sc, camera_offset, PLAYER_COLOR)
    for b in blocks:
        b.draw(sc, camera_offset, PLATFORM_COLOR)

    pygame.display.update()
    clock.tick(FPS)
