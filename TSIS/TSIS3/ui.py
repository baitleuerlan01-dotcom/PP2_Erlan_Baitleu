import pygame
from persistence import load_scores, save_settings

def draw_text(screen, font, text, y):
    txt = font.render(text, True, (255,255,255))
    screen.blit(txt, (200 - txt.get_width()//2, y))

def menu(screen, font):
    while True:
        screen.fill((0,0,0))
        draw_text(screen, font, "RACER GAME", 150)
        draw_text(screen, font, "1 - Play", 250)
        draw_text(screen, font, "2 - Leaderboard", 300)
        draw_text(screen, font, "3 - Settings", 350)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return "game"
                if e.key == pygame.K_2:
                    return "leaderboard"
                if e.key == pygame.K_3:
                    return "settings"

def leaderboard(screen, font):
    data = load_scores()
    while True:
        screen.fill((0,0,0))
        draw_text(screen, font, "LEADERBOARD", 100)

        for i, d in enumerate(data):
            draw_text(screen, font, f"{i+1}. {d['name']} {d['score']}", 150+i*30)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

def settings_menu(screen, font, settings):
    while True:
        screen.fill((0,0,0))
        draw_text(screen, font, f"S Sound: {settings['sound']}", 250)
        draw_text(screen, font, f"D Difficulty: {settings['difficulty']}", 300)
        draw_text(screen, font, "ESC Back", 400)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:
                    settings["sound"] = not settings["sound"]
                if e.key == pygame.K_d:
                    settings["difficulty"] = (settings["difficulty"] % 3) + 1
                if e.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    return
def menu(screen, font):
    while True:
        screen.fill((0,0,0))
        draw_text(screen, font, "RACER GAME", 150)
        draw_text(screen, font, "1 - Play", 250)
        draw_text(screen, font, "2 - Leaderboard", 300)
        draw_text(screen, font, "3 - Settings", 350)
        draw_text(screen, font, "ESC - Quit", 400)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return "game"
                if e.key == pygame.K_2:
                    return "leaderboard"
                if e.key == pygame.K_3:
                    return "settings"
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()