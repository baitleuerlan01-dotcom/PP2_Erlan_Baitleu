import pygame
import sys

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Moving Ball Game")

clock = pygame.time.Clock()
FPS = 60

ball_color = (255, 0, 0)        
ball_radius = 25                
ball_x = screen_width // 2      
ball_y = screen_height // 2
ball_speed = 20                 

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    old_x, old_y = ball_x, ball_y  


    if keys[pygame.K_LEFT]:
        ball_x -= ball_speed
    if keys[pygame.K_RIGHT]:
        ball_x += ball_speed
    if keys[pygame.K_UP]:
        ball_y -= ball_speed
    if keys[pygame.K_DOWN]:
        ball_y += ball_speed

    if ball_x - ball_radius < 0:
        ball_x = old_x
    if ball_x + ball_radius > screen_width:
        ball_x = old_x
    if ball_y - ball_radius < 0:
        ball_y = old_y
    if ball_y + ball_radius > screen_height:
        ball_y = old_y

    screen.fill((255, 255, 255))  
    pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), ball_radius)

    pygame.display.flip()  
    clock.tick(FPS)

pygame.quit()
sys.exit()