import pygame
from pygame.locals import *
import random

pygame.init()

# window
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Racer")

# colors
green = (76, 208, 56)
grey = (100, 100, 100)
yellow = (255, 232, 0)
white = (255, 255, 255)
red = (200, 0, 0)

# game settings
speed = 2
score = 0
gameover = False

# road
road = (100, 0, 300, height)
left_edge_marker = (95, 0, 10, height)
right_edge_marker = (395, 0, 10, height)

# lanes
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

lane_marker_move_y = 0
marker_width = 10
marker_height = 50


# ================= VEHICLE =================
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()

        scale = 80 / image.get_rect().width
        w = int(image.get_rect().width * scale)
        h = int(image.get_rect().height * scale)

        self.image = pygame.transform.scale(image, (w, h))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


# ================= PLAYER =================
class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('/Users/erlan/Documents/Semester 2/pp2/practice10/race/images/car.png')
        super().__init__(image, x, y)


# ================= COIN =================
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        image = pygame.image.load('/Users/erlan/Documents/Semester 2/pp2/practice10/race/images/coin.png')
        self.image = pygame.transform.scale(image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


# player
player = PlayerVehicle(250, 400)
player_group = pygame.sprite.Group()
player_group.add(player)

# enemy cars
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []

for name in image_filenames:
    img = pygame.image.load('/Users/erlan/Documents/Semester 2/pp2/practice10/race/images/' + name)
    vehicle_images.append(img)

vehicle_group = pygame.sprite.Group()

# coins
coin_group = pygame.sprite.Group()

# crash image
crash = pygame.image.load('/Users/erlan/Documents/Semester 2/pp2/practice10/race/images/crash.png')
crash_rect = crash.get_rect()

# loop
clock = pygame.time.Clock()
fps = 60
running = True

while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100

            if event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100

    # background
    screen.fill(green)
    pygame.draw.rect(screen, grey, road)
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    # lane animation
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0

    for y in range(-100, height, 100):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    # draw player
    player_group.draw(screen)

    # spawn vehicles
    if len(vehicle_group) < 2:
        lane = random.choice(lanes)
        img = random.choice(vehicle_images)
        vehicle = Vehicle(img, lane, -100)
        vehicle_group.add(vehicle)

    # move vehicles
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        if vehicle.rect.top > height:
            vehicle.kill()

    vehicle_group.draw(screen)

    # spawn coins
    if len(coin_group) < 3:
        lane = random.choice(lanes)
        coin = Coin(lane, -50)
        coin_group.add(coin)

    # move coins
    for coin in coin_group:
        coin.rect.y += speed
        if coin.rect.top > height:
            coin.kill()

    # collect coins
    collected = pygame.sprite.spritecollide(player, coin_group, True)
    if collected:
        score += len(collected)

    coin_group.draw(screen)

    # collision with cars
    if pygame.sprite.spritecollide(player, vehicle_group, False):
        gameover = True
        crash_rect.center = player.rect.center

    if gameover:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, red, (0, 50, width, 100))
        font = pygame.font.Font(None, 30)
        text = font.render("GAME OVER", True, white)
        screen.blit(text, (180, 90))

    # score
    font = pygame.font.Font(None, 30)
    score_text = font.render("Score: " + str(score), True, white)
    screen.blit(score_text, (10, 10))

    pygame.display.update()

pygame.quit()