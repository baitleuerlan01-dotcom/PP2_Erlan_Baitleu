import pygame
import os
import time

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((720, 300))
pygame.display.set_caption("Simple Music Player")

font = pygame.font.SysFont("Arial", 24)

playlist = [
    "/Users/erlan/Documents/Semester 2/pp2/practice9/music_player/music/track1.mp3",
    "/Users/erlan/Documents/Semester 2/pp2/practice9/music_player/music/track2.mp3",
]

current_track_index = 0
is_playing = False

def load_and_play_current():
    global is_playing
    if 0 <= current_track_index < len(playlist):
        filename = playlist[current_track_index]
        pygame.mixer.music.unload()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        is_playing = True

load_and_play_current()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            key = event.unicode.lower()

            if key == "p":
                if not is_playing:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.play()
                is_playing = True

            elif key == "s":
                pygame.mixer.music.stop()
                is_playing = False

            elif key == "n":
                current_track_index = (current_track_index + 1) % len(playlist)
                load_and_play_current()

            elif key == "b":  
                current_track_index = (current_track_index - 1) % len(playlist)
                load_and_play_current()

            elif key == "q":        
                running = False

    screen.fill((30, 30, 40)) 

    if 0 <= current_track_index < len(playlist):
        filename = os.path.basename(playlist[current_track_index])
    else:
        filename = "No track"

    title_text = font.render(f"Track: {filename}", True, (255, 255, 255))
    screen.blit(title_text, (20, 40))

    if pygame.mixer.music.get_busy():
        pos_seconds = pygame.mixer.music.get_pos() / 1000.0  # convert to seconds
    else:
        pos_seconds = 0.0

    pos_text = font.render(f"Time: {pos_seconds:.1f}s", True, (200, 200, 200))
    screen.blit(pos_text, (20, 90))

    inst_text = font.render("P=Play, S=Stop, N=Next, B=Prev, Q=Quit", True, (180, 180, 180))
    screen.blit(inst_text, (20, 140))

    pygame.display.update()

    time.sleep(0.05) 

pygame.mixer.quit()
pygame.quit()