import pygame
import random

WIDTH, HEIGHT = 400, 800
LANES = [50, 150, 250]


road = pygame.image.load("/Users/erlan/Documents/PP2_Erlan_Baitleu/TSIS/TSIS3/images/road.png")
road = pygame.transform.scale(road, (WIDTH, HEIGHT))

player_img = pygame.image.load("/Users/erlan/Documents/PP2_Erlan_Baitleu/TSIS/TSIS3/images/player.png")
player_img = pygame.transform.scale(player_img, (50, 80))
player_img = pygame.transform.rotate(player_img, 180)

enemy_img = pygame.image.load("/Users/erlan/Documents/PP2_Erlan_Baitleu/TSIS/TSIS3/images/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (50, 80))

obstacle_img = pygame.image.load("TSIS/TSIS3/images/obstacle.png")
obstacle_img = pygame.transform.scale(obstacle_img, (50, 50))

nitro_img = pygame.image.load("TSIS/TSIS3/images/nitro.png")
shield_img = pygame.image.load("TSIS/TSIS3/images/shield.png")
repair_img = pygame.image.load("TSIS/TSIS3/images/repair.png")

nitro_img = pygame.transform.scale(nitro_img, (40, 40))
shield_img = pygame.transform.scale(shield_img, (40, 40))
repair_img = pygame.transform.scale(repair_img, (40, 40))



class Player:
    def __init__(self):
        self.lane = 1
        self.rect = pygame.Rect(LANES[self.lane], 500, 50, 80)
        self.speed = 5
        self.power = None
        self.timer = 0
        self.shield = False

    def move(self, d):
        self.lane = max(0, min(2, self.lane + d))
        self.rect.x = LANES[self.lane]

    def update(self):
        if self.power == "nitro":
            self.timer -= 1
            if self.timer <= 0:
                self.speed = 5
                self.power = None



def game_loop(screen, clock, settings, font):
    player = Player()

    obstacles = []
    cars = []
    powers = []

    score = 0
    distance = 0

    road_y = 0
    spawn_timer = 0

    while True:
       
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    player.move(-1)
                if e.key == pygame.K_RIGHT:
                    player.move(1)

        
        speed = 5 + score // 150

        # ROAD
        road_y += speed
        if road_y >= HEIGHT:
            road_y = 0

        screen.blit(road, (0, road_y))
        screen.blit(road, (0, road_y - HEIGHT))

        
        spawn_timer += 1

        if spawn_timer > 50:
            spawn_timer = 0

            
            safe_lane = random.randint(0, 2)

            for lane in range(3):

                
                if lane == safe_lane:
                    continue

                
                busy = False
                for obj in obstacles + cars + [p["rect"] for p in powers]:
                    if obj.x == LANES[lane] and obj.y < 200:
                        busy = True
                        break

                if busy:
                    continue

                
                r = random.random()

                if r < 0.4:
                    cars.append(pygame.Rect(LANES[lane], -80, 50, 80))

                elif r < 0.7:
                    obstacles.append(pygame.Rect(LANES[lane], -50, 50, 50))

                elif r < 0.85:
                    powers.append({
                        "rect": pygame.Rect(LANES[lane], -40, 40, 40),
                        "type": random.choice(["nitro","shield","repair"])
                    })

        
        for o in obstacles[:]:
            o.y += speed
            screen.blit(obstacle_img, o)

            if player.rect.colliderect(o):
                if player.shield:
                    player.shield = False
                    obstacles.remove(o)
                else:
                    return score, distance

       
        for c in cars[:]:
            c.y += speed + 1
            screen.blit(enemy_img, c)

            if player.rect.colliderect(c):
                if player.shield:
                    player.shield = False
                    cars.remove(c)
                else:
                    return score, distance

        
        for p in powers[:]:
            p["rect"].y += speed

            if p["type"] == "nitro":
                screen.blit(nitro_img, p["rect"])
            elif p["type"] == "shield":
                screen.blit(shield_img, p["rect"])
            else:
                screen.blit(repair_img, p["rect"])

            if player.rect.colliderect(p["rect"]):
                if p["type"] == "nitro":
                    player.power = "nitro"
                    player.speed = 10
                    player.timer = 180

                elif p["type"] == "shield":
                    player.shield = True

                elif p["type"] == "repair":
                    obstacles.clear()

                powers.remove(p)

       
        player.update()
        screen.blit(player_img, player.rect)

        
        score += 1
        distance += speed

        s = font.render(f"Score: {score}", True, (255,255,255))
        d = font.render(f"Dist: {distance}", True, (255,255,255))

        screen.blit(s, (10,10))
        screen.blit(d, (10,40))

        pygame.display.update()
        clock.tick(60)