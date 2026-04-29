import pygame
from datetime import datetime

DARK_GREY = (45, 45, 45)
LIGHT_GREY = (229, 229, 229)
WHITE = (255, 255, 255)

class AnalogClock:
	def __init__(self, size, position, window_width, window_height):
		self.__size = size
		self.__position = position
		self.__rotation_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
		self.__hour = 0
		self.__minute = 0
		self.__second = 0

	def update(self):
		now = datetime.now()
		self.__hour = now.hour % 12
		self.__minute = now.minute
		self.__second = now.second

	def draw(self, window):
		#self.__draw_face(window)
		#self.__draw_hour_marks(window)
		self.__draw_minute_hand(window, self.__minute)
		self.__draw_hour_hand(window, self.__hour, self.__minute)
		self.__draw_second_hand(window, self.__second)
		#self.__draw_circle(window, self.__position, 15, DARK_GREY)

	def __draw_circle(self, window, position, size, color):
		pygame.gfxdraw.aacircle(window, position[0], position[1], size, color)
		pygame.gfxdraw.filled_circle(window, position[0],position[1], size, color)

	def __draw_face(self, window):
		self.__draw_circle(window, self.__position, self.__size, DARK_GREY)
		self.__draw_circle(window, self.__position, self.__size - 30, LIGHT_GREY)
		self.__draw_circle(window, self.__position, self.__size - 40, WHITE)

	def __draw_hour_marks(self, window):
		rect_width = 10
		rect_height = self.__size

		rect_x = self.__position[0] - rect_width // 2
		rect_y = self.__position[1] - rect_height

		for i in range(12):
			self.__rotation_surface.fill((0, 0, 0, 0))
			pygame.draw.rect(self.__rotation_surface, DARK_GREY, (rect_x, rect_y, rect_width, rect_height))
			rotated_surface = pygame.transform.rotate(self.__rotation_surface, 30 * i)
			rotated_rect = rotated_surface.get_rect(center = self.__position)
			window.blit(rotated_surface, rotated_rect)

		self.__draw_circle(window, self.__position, self.__size - 60, WHITE)

	def __draw_minute_hand(self, window, minute):
		hand_width = 10
		hand_length = self.__size * 0.7
		self.__draw_hand(window, hand_width, hand_length, 6*minute, DARK_GREY)

	def __draw_hand(self, window, hand_width, hand_length, angle, color, offset = 0):
		rect_x = self.__position[0] - hand_width // 2
		rect_y = self.__position[1] - hand_length + offset

		self.__rotation_surface.fill((0, 0, 0, 0))
		pygame.draw.rect(self.__rotation_surface, color, (rect_x, rect_y, hand_width, hand_length))
		rotated_surface = pygame.transform.rotate(self.__rotation_surface, -angle)
		rotated_rect = rotated_surface.get_rect(center = self.__position)
		window.blit(rotated_surface, rotated_rect)

	def __draw_hour_hand(self, window, hour, minute):
		hand_width = 15
		hand_length = self.__size * 0.6
		angle = 30 * hour + (minute/60) * 30
		self.__draw_hand(window, hand_width, hand_length, angle, DARK_GREY)

	def __draw_second_hand(self, window, second):
		hand_width = 5
		hand_length = self.__size * 1.05
		angle = second * 6
		self.__draw_hand(window, hand_width, hand_length, angle, "red", 55)