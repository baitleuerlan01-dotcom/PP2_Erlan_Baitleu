import pygame
from racer import game_loop
from ui import menu, leaderboard, settings_menu
from persistence import load_settings, save_score

pygame.init()

screen = pygame.display.set_mode((400,600))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def get_name():
    name = ""
    while True:
        screen.fill((0,0,0))
        txt = font.render("Enter name: " + name, True, (255,255,255))
        screen.blit(txt, (50,250))
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return name if name else "Player"
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += e.unicode

def main():
    settings = load_settings()

    while True:
        state = menu(screen, font)

        if state == "game":
            name = get_name()
            score, dist = game_loop(screen, clock, settings, font)
            save_score(name, score, dist)

        elif state == "leaderboard":
            leaderboard(screen, font)

        elif state == "settings":
            settings_menu(screen, font, settings)

main()