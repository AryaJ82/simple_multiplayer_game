

import pygame
from game_state import *

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
game = GameState()

game.selection_screen(screen, clock)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game.shutdown()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.fire_bullets()

    game.update(pygame.key.get_pressed())

    game.redraw(screen)
    clock.tick(30)

pygame.quit()
exit()
