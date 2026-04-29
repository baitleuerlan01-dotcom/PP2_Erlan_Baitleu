

import random
import pygame
from config import *




def random_cell(exclude: set[tuple] = None) -> tuple[int, int]:
    """Return a random (col, row) not in exclude."""
    exclude = exclude or set()
    while True:
        c = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
        if c not in exclude:
            return c




class Snake:
    DIRS = {
        pygame.K_UP:    (0, -1), pygame.K_w: (0, -1),
        pygame.K_DOWN:  (0,  1), pygame.K_s: (0,  1),
        pygame.K_LEFT:  (-1, 0), pygame.K_a: (-1, 0),
        pygame.K_RIGHT: (1,  0), pygame.K_d: (1,  0),
    }

    def __init__(self, color):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        self.body  = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir   = (1, 0)
        self.color = color
        self._grow  = 0

    def handle_key(self, key):
        if key in self.DIRS:
            nd = self.DIRS[key]
            # prevent 180° reversal
            if (nd[0] + self.dir[0], nd[1] + self.dir[1]) != (0, 0):
                self.dir = nd

    def move(self) -> tuple[int, int]:
        """Advance one cell. Returns the new head position."""
        hx, hy = self.body[0]
        new_head = (hx + self.dir[0], hy + self.dir[1])
        self.body.insert(0, new_head)
        if self._grow > 0:
            self._grow -= 1
        else:
            self.body.pop()
        return new_head

    def grow(self, amount=1):
        self._grow += amount

    def shorten(self, amount=2) -> bool:
        """Remove tail segments. Returns False if snake is too short (≤1)."""
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()
            else:
                return False
        return len(self.body) > 1

    @property
    def head(self):
        return self.body[0]

    def occupies(self) -> set:
        return set(self.body)

    def draw(self, surface):
        for i, (cx, cy) in enumerate(self.body):
            r = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = self.color if i > 0 else tuple(min(255, c + 60) for c in self.color)
            pygame.draw.rect(surface, color, r.inflate(-2, -2), border_radius=4)



class Food:
    """
    type: 'normal' | 'bonus' | 'disappearing' | 'poison'
    """
    TYPE_CFG = {
        "normal":       {"color": (240, 80,  80),  "score": 10, "shape": "circle"},
        "bonus":        {"color": (255, 200, 40),  "score": 25, "shape": "diamond"},
        "disappearing": {"color": (80,  180, 255), "score": 15, "shape": "circle"},
        "poison":       {"color": (139, 0,   0),   "score": 0,  "shape": "x"},
    }

    def __init__(self, ftype: str, pos: tuple, spawn_time: int):
        self.ftype      = ftype
        self.pos        = pos
        self.spawn_time = spawn_time
        cfg             = self.TYPE_CFG[ftype]
        self.color      = cfg["color"]
        self.score      = cfg["score"]
        self.shape      = cfg["shape"]

    def is_expired(self, now: int) -> bool:
        if self.ftype == "disappearing":
            return now - self.spawn_time > FOOD_DISAPPEAR_TIME
        return False

    def draw(self, surface):
        cx, cy = self.pos
        px = cx * CELL_SIZE + CELL_SIZE // 2
        py = cy * CELL_SIZE + CELL_SIZE // 2
        r  = CELL_SIZE // 2 - 2

        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (px, py), r)
        elif self.shape == "diamond":
            pts = [(px, py - r), (px + r, py), (px, py + r), (px - r, py)]
            pygame.draw.polygon(surface, self.color, pts)
        elif self.shape == "x":
            # Draw poison as a dark-red X
            t = 2
            pygame.draw.line(surface, self.color, (px - r, py - r), (px + r, py + r), t + 1)
            pygame.draw.line(surface, self.color, (px + r, py - r), (px - r, py + r), t + 1)
            pygame.draw.circle(surface, self.color, (px, py), r, 2)


def spawn_food(existing_positions: set, ftype: str, now: int) -> Food:
    pos = random_cell(existing_positions)
    return Food(ftype, pos, now)


def pick_food_type() -> str:
    """Weighted random food type (excludes poison — handled separately)."""
    pool = []
    for ftype, w in FOOD_WEIGHTS.items():
        pool.extend([ftype] * w)
    return random.choice(pool)



POWERUP_CFG = {
    "speed":  {"color": ORANGE, "label": "⚡",  "symbol": "S"},
    "slow":   {"color": CYAN,   "label": "🐢",  "symbol": "~"},
    "shield": {"color": PURPLE, "label": "🛡",  "symbol": "O"},
}


class PowerUp:
    def __init__(self, ptype: str, pos: tuple, spawn_time: int):
        self.ptype      = ptype
        self.pos        = pos
        self.spawn_time = spawn_time
        self.color      = POWERUP_CFG[ptype]["color"]
        self.symbol     = POWERUP_CFG[ptype]["symbol"]

    def is_expired(self, now: int) -> bool:
        return now - self.spawn_time > POWERUP_FIELD_TIME

    def draw(self, surface, font):
        cx, cy = self.pos
        px = cx * CELL_SIZE
        py = cy * CELL_SIZE
        r = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(surface, self.color, r, border_radius=4)
        txt = font.render(self.symbol, True, WHITE)
        surface.blit(txt, txt.get_rect(center=r.center))



class ActiveEffect:
    def __init__(self, etype: str, start: int):
        self.etype = etype
        self.start = start

    def remaining_ms(self, now: int) -> int:
        return max(0, POWERUP_EFFECT_TIME - (now - self.start))

    def is_done(self, now: int) -> bool:
        return self.etype != "shield" and self.remaining_ms(now) == 0



def generate_obstacles(level: int, snake_cells: set) -> set[tuple]:
    """Return a set of wall-block positions that don't trap the snake."""
    if level < OBSTACLE_START_LEVEL:
        return set()

    count   = OBSTACLES_PER_LEVEL * (level - OBSTACLE_START_LEVEL + 1)
    blocked = set(snake_cells)
    walls   = set()

    attempts = 0
    while len(walls) < count and attempts < 2000:
        attempts += 1
        pos = random_cell(blocked | walls)
        
        hx, hy = next(iter(snake_cells))   
        if abs(pos[0] - hx) < 4 and abs(pos[1] - hy) < 4:
            continue
        walls.add(pos)

    return walls


def draw_obstacles(surface, walls: set):
    for (cx, cy) in walls:
        r = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, WALL_CLR, r)
        pygame.draw.rect(surface, (60, 60, 80), r, 1)



class GameState:
    def __init__(self, snake_color, personal_best: int = 0):
        self.snake        = Snake(snake_color)
        self.score        = 0
        self.level        = 1
        self.personal_best = personal_best
        self.game_over    = False

        self.foods: list[Food] = []
       
        self.powerup: PowerUp | None = None
        
        self.effect: ActiveEffect | None = None
        
        self.shield_consumed = False

        
        self.walls: set[tuple] = set()

        self._last_move_time = 0
        self._next_level_score = 50

        
        self._spawn_food_set(pygame.time.get_ticks())
        
        self.walls = generate_obstacles(self.level, self.snake.occupies())

    def current_speed(self) -> float:
        base = BASE_SPEED + (self.level - 1) * 1.5
        if self.effect:
            if self.effect.etype == "speed":
                return base * SPEED_BOOST_MUL
            if self.effect.etype == "slow":
                return base * SLOW_MOTION_MUL
        return base

    def move_interval_ms(self) -> float:
        return 1000.0 / self.current_speed()

    def _all_occupied(self) -> set:
        return self.snake.occupies() | self.walls | {f.pos for f in self.foods} | (
            {self.powerup.pos} if self.powerup else set()
        )

    def _spawn_food_set(self, now: int):
        occ = self._all_occupied()
       
        self.foods.append(spawn_food(occ, pick_food_type(), now))
        occ.add(self.foods[-1].pos)
        
        if random.random() < 0.3:
            self.foods.append(spawn_food(occ, "poison", now))

    def _maybe_spawn_powerup(self, now: int):
        if self.powerup is None and random.random() < 0.15:
            ptype = random.choice(list(POWERUP_CFG.keys()))
            pos   = random_cell(self._all_occupied())
            self.powerup = PowerUp(ptype, pos, now)

    
    def update(self) -> bool:
        """Call every frame. Returns True when game-over just happened."""
        now = pygame.time.get_ticks()

        if self.effect and self.effect.is_done(now):
            self.effect = None

        if self.powerup and self.powerup.is_expired(now):
            self.powerup = None

        self.foods = [f for f in self.foods if not f.is_expired(now)]

        if now - self._last_move_time < self.move_interval_ms():
            return False
        self._last_move_time = now

        
        new_head = self.snake.move()
        hx, hy   = new_head

        if not (0 <= hx < GRID_COLS and 0 <= hy < GRID_ROWS):
            if self.effect and self.effect.etype == "shield" and not self.shield_consumed:
                self.shield_consumed = True
                self.effect = None
              
                hx = max(0, min(GRID_COLS - 1, hx))
                hy = max(0, min(GRID_ROWS - 1, hy))
                self.snake.body[0] = (hx, hy)
            else:
                self.game_over = True
                return True

        
        if new_head in self.walls:
            if self.effect and self.effect.etype == "shield" and not self.shield_consumed:
                self.shield_consumed = True
                self.effect = None
                self.snake.body.pop(0)   
                self.snake.body.insert(0, self.snake.body[0])
            else:
                self.game_over = True
                return True

        # self collision
        if new_head in set(self.snake.body[1:]):
            if self.effect and self.effect.etype == "shield" and not self.shield_consumed:
                self.shield_consumed = True
                self.effect = None
            else:
                self.game_over = True
                return True

       
        eaten = None
        for f in self.foods:
            if f.pos == new_head:
                eaten = f
                break
        if eaten:
            self.foods.remove(eaten)
            if eaten.ftype == "poison":
                alive = self.snake.shorten(2)
                if not alive:
                    self.game_over = True
                    return True
            else:
                self.snake.grow()
                self.score += eaten.score
            # re-spawn food
            self._spawn_food_set(now)
            self._maybe_spawn_powerup(now)

        if self.powerup and self.powerup.pos == new_head:
            pt = self.powerup.ptype
            self.powerup = None
            if pt == "shield":
                self.effect         = ActiveEffect("shield", now)
                self.shield_consumed = False
            else:
                self.effect = ActiveEffect(pt, now)

        if self.score >= self._next_level_score:
            self.level            += 1
            self._next_level_score = self.score + 50 + self.level * 20
            self.walls = generate_obstacles(self.level, self.snake.occupies())
            # clear food set and regenerate
            self.foods = []
            self._spawn_food_set(now)

        return False

    def draw(self, surface, font_sm, show_grid: bool):
        # grid
        if show_grid:
            for x in range(0, WINDOW_WIDTH, CELL_SIZE):
                pygame.draw.line(surface, GRID_CLR, (x, 0), (x, WINDOW_HEIGHT))
            for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
                pygame.draw.line(surface, GRID_CLR, (0, y), (WINDOW_WIDTH, y))

        draw_obstacles(surface, self.walls)

        for f in self.foods:
            f.draw(surface)

        if self.powerup:
            self.powerup.draw(surface, font_sm)

        self.snake.draw(surface)