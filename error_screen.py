# File: error_screen.py
import pygame


def show_server_disconnection_error():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Disconnected from Server")

    font_big = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 32)
    text1 = font_big.render("Connection Lost", True, (255, 0, 0))
    text2 = font_small.render("You were disconnected from the server.", True, (255, 255, 255))
    text3 = font_small.render("Please check your internet and try again.", True, (255, 255, 255))

    clock = pygame.time.Clock()
    done = False
    while not done:
        screen.fill((0, 0, 0))
        screen.blit(text1, (250, 200))
        screen.blit(text2, (200, 270))
        screen.blit(text3, (180, 310))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    exit()


