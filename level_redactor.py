import pygame
import json

pygame.init()

WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 40

BG_COLOR = (20, 20, 20)
GRAY = (200, 200, 200)
PLATFORM_COLOR = (50, 100, 20)

sc = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Редактор карти")

camera_x, camera_y = 0, 0

class Block_creator:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

blocks = []
block_width, block_height = BLOCK_SIZE, BLOCK_SIZE
menu_open = False

run = True
while run:
    sc.fill(BG_COLOR)

    for block in blocks:
        pygame.draw.rect(sc, PLATFORM_COLOR, (block.x - camera_x, block.y - camera_y, block.width, block.height))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            x = ((x + camera_x) // BLOCK_SIZE) * BLOCK_SIZE
            y = ((y + camera_y) // BLOCK_SIZE) * BLOCK_SIZE
            if event.button == 1:
                if not any(b.x == x and b.y == y for b in blocks):
                    blocks.append(Block_creator(x, y, block_width, block_height))
            elif event.button == 3:
                blocks = [b for b in blocks if not (b.x == x and b.y == y)]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with open("map.json", "w") as f:
                    f.write("[\n")
                    for i, b in enumerate(blocks):
                        f.write(f"    Block_creator({b.x}, {b.y}, {b.width}, {b.height})")
                        if i < len(blocks) - 1:
                            f.write(",\n")
                    f.write("\n]")
                print("Карта збережена у map.json")
            elif event.key == pygame.K_LEFT:
                camera_x -= BLOCK_SIZE
            elif event.key == pygame.K_RIGHT:
                camera_x += BLOCK_SIZE
            elif event.key == pygame.K_UP:
                camera_y -= BLOCK_SIZE
            elif event.key == pygame.K_DOWN:
                camera_y += BLOCK_SIZE
            elif event.key == pygame.K_z:
                try:
                    block_width = int(input("Введіть ширину блока: "))
                    block_height = int(input("Введіть висоту блока: "))
                except ValueError:
                    print("Помилка: введіть числові значення!")

    pygame.display.flip()

pygame.quit()