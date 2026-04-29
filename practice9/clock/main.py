import pygame, sys
import pygame.gfxdraw
from clock import AnalogClock

pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
LIGHT_BLUE = (225, 239, 240)

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Analog Clock")

clock = pygame.time.Clock()
analog_clock = AnalogClock(250, (300, 300), WINDOW_WIDTH, WINDOW_HEIGHT)

image = pygame.image.load("practice9/clock/images/clock_fone.png")
image_r = image.get_rect()


while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	analog_clock.update()

	window.fill(LIGHT_BLUE)
	window.blit(image,image_r)
	analog_clock.draw(window)
	pygame.display.update()
	clock.tick(15)