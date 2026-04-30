import sys
import json
import os
import pygame
from config import *
from game  import GameState
import db

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULT_SETTINGS = {
    "snake_color": DEFAULT_SNAKE_COLOR,
    "grid_overlay": True,
    "sound": True,
}

def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        # fill missing keys
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[Settings] save error: {e}")


def draw_text(surface, text, font, color, cx, cy, anchor="center"):
    surf = font.render(text, True, color)
    r    = surf.get_rect()
    if anchor == "center":
        r.center = (cx, cy)
    elif anchor == "topleft":
        r.topleft = (cx, cy)
    elif anchor == "midleft":
        r.midleft = (cx, cy)
    surface.blit(surf, r)


def draw_button(surface, rect, text, font, active=False, color=None):
    bg  = color if color else (ACCENT if active else PANEL_BG)
    fg  = BLACK if active else LIGHT_GRAY
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, ACCENT if not color else color, rect, 2, border_radius=8)
    draw_text(surface, text, font, fg, rect.centerx, rect.centery)
    return rect


def make_buttons(labels, cx, start_y, w, h, gap):
    buttons = []
    for i, lbl in enumerate(labels):
        r = pygame.Rect(0, 0, w, h)
        r.centerx = cx
        r.top = start_y + i * (h + gap)
        buttons.append((lbl, r))
    return buttons



class TextInput:
    def __init__(self, rect, font, max_len=20, placeholder=""):
        self.rect        = rect
        self.font        = font
        self.max_len     = max_len
        self.placeholder = placeholder
        self.text        = ""
        self.active      = True
        self._cursor_vis = True
        self._cursor_t   = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "confirm"
            elif event.unicode.isprintable() and len(self.text) < self.max_len:
                self.text += event.unicode
        return None

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if now - self._cursor_t > 500:
            self._cursor_vis = not self._cursor_vis
            self._cursor_t   = now

        pygame.draw.rect(surface, PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, ACCENT, self.rect, 2, border_radius=6)

        display = self.text if self.text else self.placeholder
        color   = WHITE if self.text else GRAY
        if self._cursor_vis and self.active and self.text is not None:
            display = self.text + "|"
            color   = WHITE
        txt_surf = self.font.render(display, True, color)
        surface.blit(txt_surf, txt_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery)))



def draw_hud(surface, gs: GameState, username: str, fonts: dict, settings: dict):
    now   = pygame.time.get_ticks()
    hud_h = 36
    hud_r = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, hud_h)

    pygame.draw.rect(surface, PANEL_BG, hud_r)

    items = [
        f"👤 {username}",
        f"Score: {gs.score}",
        f"Best: {gs.personal_best}",
        f"Level: {gs.level}",
        f"Len: {len(gs.snake.body)}",
    ]
    x = 12
    for item in items:
        s = fonts["sm"].render(item, True, LIGHT_GRAY)
        surface.blit(s, (x, WINDOW_HEIGHT + 8))
        x += s.get_width() + 28

    # effect indicator
    if gs.effect:
        etype = gs.effect.etype
        label = {"speed": "⚡SPEED", "slow": "~SLOW", "shield": "🛡SHIELD"}[etype]
        clr   = {"speed": ORANGE, "slow": CYAN, "shield": PURPLE}[etype]
        if etype == "shield":
            rem = "until hit"
        else:
            rem = f"{gs.effect.remaining_ms(now) // 1000 + 1}s"
        effect_str = f"{label} ({rem})"
        s = fonts["sm"].render(effect_str, True, clr)
        surface.blit(s, (WINDOW_WIDTH - s.get_width() - 12, WINDOW_HEIGHT + 8))



def screen_main_menu(surface, clock, fonts, db_ok: bool) -> tuple[str, str]:
    """Returns (action, username). action in ('play','leaderboard','settings','quit')"""
    text_input = TextInput(
        pygame.Rect(WINDOW_WIDTH // 2 - 150, 240, 300, 42),
        fonts["md"],
        placeholder="Enter username…"
    )
    btns = make_buttons(
        ["Play", "Leaderboard", "Settings", "Quit"],   # ← исправлено
        WINDOW_WIDTH // 2, 320, 220, 48, 12
    )
    error = ""

    while True:
        clock.tick(FPS)
        surface.fill(DARK_BG)

        # title
        draw_text(surface, "SNAKE", fonts["title"], ACCENT, WINDOW_WIDTH // 2, 90)
        draw_text(surface, "ULTIMATE", fonts["lg"], ACCENT2, WINDOW_WIDTH // 2, 148)

        # username label
        draw_text(surface, "Username", fonts["sm"], GRAY, WINDOW_WIDTH // 2, 222)
        text_input.draw(surface)

        if error:
            draw_text(surface, error, fonts["sm"], RED, WINDOW_WIDTH // 2, 292)

        mx, my = pygame.mouse.get_pos()
        for lbl, r in btns:
            hover = r.collidepoint(mx, my)
            draw_button(surface, r, lbl, fonts["md"], active=hover)

        if not db_ok:
            draw_text(surface, "⚠ DB offline – scores won't be saved", fonts["sm"],
                      RED, WINDOW_WIDTH // 2, WINDOW_HEIGHT + 20)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", ""

            res = text_input.handle_event(event)
            if res == "confirm":
                if text_input.text.strip():
                    return "play", text_input.text.strip()
                else:
                    error = "Please enter a username first!"

            if event.type == pygame.MOUSEBUTTONDOWN:
                for lbl, r in btns:
                    if r.collidepoint(event.pos):
                        action = lbl.lower()
                        if action == "play":
                            if not text_input.text.strip():
                                error = "Please enter a username first!"
                            else:
                                return "play", text_input.text.strip()
                        else:
                            return action, text_input.text.strip()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit", ""



def screen_game(surface, clock, fonts, username: str, settings: dict, personal_best: int) -> dict:
    """Run the game. Returns result dict with score, level, etc."""
    snake_color = tuple(settings.get("snake_color", DEFAULT_SNAKE_COLOR))
    gs          = GameState(snake_color, personal_best)

    hud_surface = pygame.Surface((WINDOW_WIDTH, 36))
    game_area   = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"quit": True, "score": gs.score, "level": gs.level}
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return {"quit": False, "score": gs.score, "level": gs.level}
                gs.snake.handle_key(event.key)

        died = gs.update()

        # Draw game area
        game_area.fill(DARK_BG)
        gs.draw(game_area, fonts["sm_mono"], settings.get("grid_overlay", True))

        surface.blit(game_area, (0, 0))
        draw_hud(surface, gs, username, fonts, settings)
        pygame.display.flip()

        if died:
            return {"quit": False, "score": gs.score, "level": gs.level}



def screen_game_over(surface, clock, fonts, score: int, level: int, personal_best: int) -> str:
    """Returns 'retry' or 'menu'."""
    btns = make_buttons(["Retry", "Main Menu"], WINDOW_WIDTH // 2, 400, 220, 48, 12)  # ← исправлено

    while True:
        clock.tick(FPS)
        surface.fill(DARK_BG)

        draw_text(surface, "GAME OVER", fonts["title"], RED, WINDOW_WIDTH // 2, 130)
        draw_text(surface, f"Score:  {score}",         fonts["lg"],  WHITE,  WINDOW_WIDTH // 2, 220)
        draw_text(surface, f"Level:  {level}",         fonts["md"],  LIGHT_GRAY, WINDOW_WIDTH // 2, 270)
        draw_text(surface, f"Best:   {max(score, personal_best)}", fonts["md"],
                  ACCENT, WINDOW_WIDTH // 2, 310)

        mx, my = pygame.mouse.get_pos()
        for lbl, r in btns:
            draw_button(surface, r, lbl, fonts["md"], active=r.collidepoint(mx, my))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for lbl, r in btns:
                    if r.collidepoint(event.pos):
                        return "retry" if "Retry" in lbl else "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"



def screen_leaderboard(surface, clock, fonts) -> None:
    rows  = db.get_top10()
    back  = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 20, 200, 44)

    headers = ["#", "Username", "Score", "Level", "Date"]
    col_x   = [60, 140, 370, 470, 560]

    while True:
        clock.tick(FPS)
        surface.fill(DARK_BG)

        draw_text(surface, "LEADERBOARD", fonts["title"], ACCENT, WINDOW_WIDTH // 2, 60)

        # header row
        for h, x in zip(headers, col_x):
            draw_text(surface, h, fonts["md"], ACCENT2, x, 120, anchor="midleft")

        pygame.draw.line(surface, GRAY, (40, 138), (WINDOW_WIDTH - 40, 138), 1)

        if not rows:
            draw_text(surface, "No scores yet!", fonts["md"], GRAY, WINDOW_WIDTH // 2, 250)
        else:
            for i, row in enumerate(rows):
                y    = 158 + i * 34
                clr  = YELLOW if i == 0 else (LIGHT_GRAY if i < 3 else GRAY)
                vals = [
                    str(row["rank"]),
                    str(row["username"])[:16],
                    str(row["score"]),
                    str(row["level_reached"]),
                    str(row.get("played_date", "—")),
                ]
                for val, x in zip(vals, col_x):
                    draw_text(surface, val, fonts["sm"], clr, x, y, anchor="midleft")

        mx, my = pygame.mouse.get_pos()
        draw_button(surface, back, "Back", fonts["md"], active=back.collidepoint(mx, my))  # ← исправлено

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and back.collidepoint(event.pos):
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return



COLOR_OPTIONS = [
    ((0, 220, 130),  "Green"),
    ((80, 160, 255), "Blue"),
    ((255, 200, 40), "Yellow"),
    ((220, 80, 80),  "Red"),
    ((200, 80, 220), "Purple"),
    ((255, 140, 0),  "Orange"),
]


def screen_settings(surface, clock, fonts, settings: dict) -> dict:
    """Returns updated settings dict."""
    s       = dict(settings)
    save_r  = pygame.Rect(WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT - 20, 220, 44)

    while True:
        clock.tick(FPS)
        surface.fill(DARK_BG)

        draw_text(surface, "SETTINGS", fonts["title"], ACCENT, WINDOW_WIDTH // 2, 60)

        # Grid overlay toggle
        draw_text(surface, "Grid Overlay", fonts["md"], LIGHT_GRAY, 120, 150, anchor="midleft")
        grid_r = pygame.Rect(480, 132, 120, 36)
        on_off = "ON" if s["grid_overlay"] else "OFF"
        clr    = ACCENT if s["grid_overlay"] else GRAY
        pygame.draw.rect(surface, clr, grid_r, border_radius=6)
        draw_text(surface, on_off, fonts["md"], BLACK, grid_r.centerx, grid_r.centery)

        # Sound toggle
        draw_text(surface, "Sound", fonts["md"], LIGHT_GRAY, 120, 220, anchor="midleft")
        snd_r = pygame.Rect(480, 202, 120, 36)
        on_off2 = "ON" if s["sound"] else "OFF"
        clr2    = ACCENT if s["sound"] else GRAY
        pygame.draw.rect(surface, clr2, snd_r, border_radius=6)
        draw_text(surface, on_off2, fonts["md"], BLACK, snd_r.centerx, snd_r.centery)

        # Snake color picker
        draw_text(surface, "Snake Color", fonts["md"], LIGHT_GRAY, 120, 300, anchor="midleft")
        color_rects = []
        for idx, (col, name) in enumerate(COLOR_OPTIONS):
            cr = pygame.Rect(120 + idx * 80, 325, 60, 32)
            color_rects.append(cr)
            pygame.draw.rect(surface, col, cr, border_radius=5)
            if list(col) == list(s["snake_color"]):
                pygame.draw.rect(surface, WHITE, cr, 3, border_radius=5)
            draw_text(surface, name, fonts["sm"], GRAY, cr.centerx, cr.bottom + 12)

        mx, my = pygame.mouse.get_pos()
        draw_button(surface, save_r, "💾  Save & Back", fonts["md"], active=save_r.collidepoint(mx, my))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(s)
                return s
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_r.collidepoint(event.pos):
                    s["grid_overlay"] = not s["grid_overlay"]
                elif snd_r.collidepoint(event.pos):
                    s["sound"] = not s["sound"]
                elif save_r.collidepoint(event.pos):
                    save_settings(s)
                    return s
                for idx, cr in enumerate(color_rects):
                    if cr.collidepoint(event.pos):
                        s["snake_color"] = list(COLOR_OPTIONS[idx][0])
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(s)
                return s



def main():
    pygame.init()

    # Window: game area + HUD bar at bottom
    total_h = WINDOW_HEIGHT + 36
    surface = pygame.display.set_mode((WINDOW_WIDTH, total_h))
    pygame.display.set_caption("Snake Ultimate")
    clock   = pygame.time.Clock()

    # Fonts
    try:
        title_f = pygame.font.SysFont("consolas", 72, bold=True)
        lg_f    = pygame.font.SysFont("consolas", 40, bold=True)
        md_f    = pygame.font.SysFont("consolas", 26)
        sm_f    = pygame.font.SysFont("consolas", 18)
        smm_f   = pygame.font.SysFont("consolas", 14)
    except Exception:
        title_f = pygame.font.Font(None, 72)
        lg_f    = pygame.font.Font(None, 48)
        md_f    = pygame.font.Font(None, 32)
        sm_f    = pygame.font.Font(None, 24)
        smm_f   = pygame.font.Font(None, 20)

    fonts = {
        "title":   title_f,
        "lg":      lg_f,
        "md":      md_f,
        "sm":      sm_f,
        "sm_mono": smm_f,
    }

    # Init DB
    db_ok = db.init_db()

    # Load settings
    settings = load_settings()

    username      = ""
    personal_best = 0
    screen        = "menu"

    while True:
        if screen == "menu":
            action, username = screen_main_menu(surface, clock, fonts, db_ok)
            if action == "quit":
                break
            elif action == "play":
                if db_ok:
                    personal_best = db.get_personal_best(username)
                screen = "game"
            elif action == "leaderboard":
                screen_leaderboard(surface, clock, fonts)
                screen = "menu"
            elif action == "settings":
                settings = screen_settings(surface, clock, fonts, settings)
                screen = "menu"

        elif screen == "game":
            result = screen_game(surface, clock, fonts, username, settings, personal_best)
            if result.get("quit"):
                break
            score = result["score"]
            level = result["level"]
            # auto-save
            if db_ok and username:
                db.save_result(username, score, level)
                personal_best = max(personal_best, score)
            action = screen_game_over(surface, clock, fonts, score, level, personal_best)
            if action == "retry":
                screen = "game"
            else:
                screen = "menu"

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()