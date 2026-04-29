


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 640
CELL_SIZE = 20
GRID_COLS = WINDOW_WIDTH // CELL_SIZE   # 40
GRID_ROWS = WINDOW_HEIGHT // CELL_SIZE  # 32
FPS = 60


BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
DARK_BG     = (15,  15,  25)
PANEL_BG    = (20,  20,  35)
ACCENT      = (0,   220, 130)
ACCENT2     = (80,  160, 255)
RED         = (220, 50,  50)
POISON_CLR  = (139, 0,   0)
YELLOW      = (255, 220, 40)
ORANGE      = (255, 140, 0)
CYAN        = (0,   200, 220)
PURPLE      = (160, 80,  220)
GRAY        = (100, 100, 120)
LIGHT_GRAY  = (180, 180, 200)
WALL_CLR    = (80,  80,  100)
GRID_CLR    = (25,  25,  40)


DEFAULT_SNAKE_COLOR = [0, 220, 130]


BASE_SPEED       = 8
SPEED_BOOST_MUL  = 1.8
SLOW_MOTION_MUL  = 0.5


POWERUP_FIELD_TIME  = 8000  
POWERUP_EFFECT_TIME = 5000   


OBSTACLE_START_LEVEL = 3
OBSTACLES_PER_LEVEL  = 5    


FOOD_WEIGHTS = {"normal": 60, "bonus": 25, "disappearing": 15}
FOOD_DISAPPEAR_TIME = 6000   # ms


DB_CONFIG = {
    "host":     "localhost",
    "dbname":   "snake_game",
    "user":     "postgres",
    "password": "era110117",
}