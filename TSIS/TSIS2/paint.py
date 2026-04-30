import sys
import math
import datetime
import pygame
from tools import (
    PencilTool, LineTool, RectangleTool, SquareTool, CircleTool,
    RightTriangleTool, EquilateralTriangleTool, RhombusTool,
    EraserTool, FillTool, TextTool,
)

WIN_W, WIN_H = 1100, 720
TOOLBAR_H = 60
PALETTE_H = 46
CANVAS_W = WIN_W
CANVAS_H = WIN_H - TOOLBAR_H - PALETTE_H

BG_COLOR = (30, 30, 35)
TOOLBAR_COLOR = (22, 22, 28)
PALETTE_BG = (18, 18, 22)
BTN_NORMAL = (45, 45, 55)
BTN_HOVER = (65, 65, 78)
BTN_ACTIVE = (90, 130, 200)
BTN_TEXT = (220, 220, 230)
CANVAS_BG = (255, 255, 255)
ACCENT = (100, 160, 255)

PALETTE_COLORS = [
    (0, 0, 0),      # black
    (255, 255, 255),# white
    (220, 50, 50),  # red
    (230, 140, 20), # orange
    (241, 196, 15), # yellow
    (39, 174, 96),  # green
    (52, 152, 219), # blue
    (142, 68, 173), # purple
    (127, 140, 141),# grey
    (52, 73, 94),   # navy
]

BRUSH_SIZES = [2, 5, 10]
BRUSH_LABELS = ["S", "M", "L"]
SAVE_DIR = "."


class Button:
    """A simple rectangular clickable button."""
    def __init__(self, rect, label, shortcut="", tooltip=""):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.shortcut = shortcut
        self.tooltip = tooltip or label
        self.active = False
        self.hovered = False
        self._font = None

    def _get_font(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("segoeui", 13, bold=True)
            except Exception:
                self._font = pygame.font.Font(None, 16)
        return self._font

    def draw(self, surface):
        color = BTN_ACTIVE if self.active else (BTN_HOVER if self.hovered else BTN_NORMAL)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, ACCENT if self.active else (70, 70, 85), self.rect, 1, border_radius=6)
        font = self._get_font()
        txt = font.render(self.label, True, BTN_TEXT)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def build_toolbar():
    """Создаём панель инструментов БЕЗ лишних символов"""
    tools_def = [
        ("pencil",   "Pen",      "P"),
        ("line",     "Line",     "L"),
        ("rect",     "Rect",     "R"),
        ("square",   "Sqr",      "S"),
        ("circle",   "Circ",     "C"),
        ("rtriangle","RTri",     "T"),
        ("etriangle","ETri",     "E"),
        ("rhombus",  "Rhom",     "D"),
        ("eraser",   "Erase",    "X"),
        ("fill",     "Fill",     "F"),
        ("text",     "Text",     "A"),
    ]
    buttons = []
    x = 8
    for key, label, sc in tools_def:
        btn = Button((x, 8, 80, 44), label, sc, f"{label} [{sc}]")
        buttons.append((key, btn))
        x += 84
    return buttons


def build_size_buttons():
    sizes = []
    x = WIN_W - 170
    for i, (lbl, sz) in enumerate(zip(BRUSH_LABELS, BRUSH_SIZES)):
        btn = Button((x, 10, 48, 40), f"{lbl} ({sz})", str(i + 1))
        sizes.append(btn)
        x += 52
    return sizes


def build_palette_rects():
    rects = []
    sw = 44
    gap = 4
    total = len(PALETTE_COLORS) * (sw + gap) - gap
    sx = (WIN_W - total) // 2
    sy = WIN_H - PALETTE_H + (PALETTE_H - sw) // 2
    for i in range(len(PALETTE_COLORS)):
        rects.append(pygame.Rect(sx + i * (sw + gap), sy, sw, sw))
    return rects


def save_canvas(canvas_surface):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_DIR}/canvas_{ts}.png"
    pygame.image.save(canvas_surface, filename)
    return filename


def main():
    pygame.init()
    pygame.display.set_caption("Paint — Practice 10·11·12")
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()

    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    tool_map = {
        "pencil": PencilTool(),
        "line": LineTool(),
        "rect": RectangleTool(),
        "square": SquareTool(),
        "circle": CircleTool(),
        "rtriangle": RightTriangleTool(),
        "etriangle": EquilateralTriangleTool(),
        "rhombus": RhombusTool(),
        "eraser": EraserTool(),
        "fill": FillTool(),
        "text": TextTool(),
    }

    active_tool_key = "pencil"
    active_tool = tool_map[active_tool_key]
    active_color = (0, 0, 0)
    brush_idx = 1
    brush_size = BRUSH_SIZES[brush_idx]
    drawing = False

    tool_buttons = build_toolbar()
    size_buttons = build_size_buttons()
    palette_rects = build_palette_rects()

    # Активируем Pencil по умолчанию
    for key, btn in tool_buttons:
        btn.active = (key == active_tool_key)
    size_buttons[brush_idx].active = True

    try:
        ui_font = pygame.font.SysFont("segoeui", 13)
        status_font = pygame.font.SysFont("consolas", 12)
    except Exception:
        ui_font = pygame.font.Font(None, 16)
        status_font = pygame.font.Font(None, 14)

    status_msg = ""
    status_timer = 0
    CANVAS_OFFSET = (0, TOOLBAR_H)

    def canvas_pos(screen_pt):
        return (screen_pt[0] - CANVAS_OFFSET[0], screen_pt[1] - CANVAS_OFFSET[1])

    def in_canvas(screen_pt):
        cx, cy = canvas_pos(screen_pt)
        return 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H

    def set_tool(key):
        nonlocal active_tool_key, active_tool
        active_tool_key = key
        active_tool = tool_map[key]
        for k, btn in tool_buttons:
            btn.active = (k == key)

    def set_brush(idx):
        nonlocal brush_idx, brush_size
        brush_idx = idx
        brush_size = BRUSH_SIZES[idx]
        for i, btn in enumerate(size_buttons):
            btn.active = (i == idx)

    running = True
    prev_time = pygame.time.get_ticks()

    while running:
        now = pygame.time.get_ticks()
        dt = now - prev_time
        prev_time = now

        mouse_pos = pygame.mouse.get_pos()
        canvas_mouse = canvas_pos(mouse_pos)

        text_tool = tool_map["text"]
        text_tool.update(dt)

        if status_timer > 0:
            status_timer -= dt
            if status_timer < 0:
                status_timer = 0
                status_msg = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if text_tool.is_active:
                    text_tool.handle_key(event, canvas, active_color, brush_size)
                else:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and event.key == pygame.K_s:
                        fname = save_canvas(canvas)
                        status_msg = f"Saved: {fname}"
                        status_timer = 3000
                    elif event.key == pygame.K_1:
                        set_brush(0)
                    elif event.key == pygame.K_2:
                        set_brush(1)
                    elif event.key == pygame.K_3:
                        set_brush(2)
                    elif event.key == pygame.K_p:
                        set_tool("pencil")
                    elif event.key == pygame.K_l:
                        set_tool("line")
                    elif event.key == pygame.K_r:
                        set_tool("rect")
                    elif event.key == pygame.K_s:
                        set_tool("square")
                    elif event.key == pygame.K_c:
                        set_tool("circle")
                    elif event.key == pygame.K_t:
                        set_tool("rtriangle")
                    elif event.key == pygame.K_e:
                        set_tool("etriangle")
                    elif event.key == pygame.K_d:
                        set_tool("rhombus")
                    elif event.key == pygame.K_x:
                        set_tool("eraser")
                    elif event.key == pygame.K_f:
                        set_tool("fill")
                    elif event.key == pygame.K_a:
                        set_tool("text")
                    elif event.key == pygame.K_ESCAPE:
                        drawing = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_ui = False
                for key, btn in tool_buttons:
                    if btn.handle_event(event):
                        set_tool(key)
                        clicked_ui = True
                        break
                for i, btn in enumerate(size_buttons):
                    if btn.handle_event(event):
                        set_brush(i)
                        clicked_ui = True
                        break
                for i, rect in enumerate(palette_rects):
                    if rect.collidepoint(mouse_pos):
                        active_color = PALETTE_COLORS[i]
                        clicked_ui = True
                        break
                if not clicked_ui and in_canvas(mouse_pos):
                    drawing = True
                    active_tool.on_mouse_down(canvas, canvas_mouse, active_color, brush_size)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for _, btn in tool_buttons:
                    btn.handle_event(event)
                for btn in size_buttons:
                    btn.handle_event(event)
                if drawing and in_canvas(mouse_pos):
                    active_tool.on_mouse_up(canvas, canvas_mouse, active_color, brush_size)
                drawing = False

            elif event.type == pygame.MOUSEMOTION:
                for _, btn in tool_buttons:
                    btn.handle_event(event)
                for btn in size_buttons:
                    btn.handle_event(event)
                if drawing and in_canvas(mouse_pos):
                    active_tool.on_mouse_drag(canvas, canvas_mouse, active_color, brush_size)

        screen.fill(BG_COLOR)
        screen.blit(canvas, CANVAS_OFFSET)

        if in_canvas(mouse_pos) and not isinstance(active_tool, FillTool):
            preview_surf = canvas.copy()
            active_tool.draw_preview(preview_surf, canvas_mouse, active_color, brush_size)
            screen.blit(preview_surf, CANVAS_OFFSET)
        elif in_canvas(mouse_pos) and isinstance(active_tool, FillTool):
            active_tool.draw_preview(screen, mouse_pos, active_color, brush_size)

        if text_tool.is_active:
            text_tool.draw_preview(screen, mouse_pos, active_color, brush_size)

        pygame.draw.rect(screen, (60, 60, 75),
                         (CANVAS_OFFSET[0] - 1, CANVAS_OFFSET[1] - 1, CANVAS_W + 2, CANVAS_H + 2), 1)

        pygame.draw.rect(screen, TOOLBAR_COLOR, (0, 0, WIN_W, TOOLBAR_H))
        pygame.draw.line(screen, (50, 50, 65), (0, TOOLBAR_H), (WIN_W, TOOLBAR_H), 1)

        for _, btn in tool_buttons:
            btn.draw(screen)
        for btn in size_buttons:
            btn.draw(screen)

        pygame.draw.rect(screen, PALETTE_BG, (0, WIN_H - PALETTE_H, WIN_W, PALETTE_H))
        pygame.draw.line(screen, (50, 50, 65), (0, WIN_H - PALETTE_H), (WIN_W, WIN_H - PALETTE_H), 1)

        for i, (rect, color) in enumerate(zip(palette_rects, PALETTE_COLORS)):
            pygame.draw.rect(screen, color, rect, border_radius=4)
            if color == active_color:
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(4, 4), 2, border_radius=6)
            pygame.draw.rect(screen, ACCENT, rect.inflate(6, 6), 2, border_radius=7)

        preview_rect = pygame.Rect(8, WIN_H - PALETTE_H + 4, 38, 38)
        pygame.draw.rect(screen, active_color, preview_rect, border_radius=5)
        pygame.draw.rect(screen, (180, 180, 200), preview_rect, 2, border_radius=5)

        if status_msg:
            surf = status_font.render(status_msg, True, (180, 230, 180))
            screen.blit(surf, (56, WIN_H - PALETTE_H + 16))

        hud = f"Tool: {active_tool_key.upper()} | Brush: {brush_size}px | Ctrl+S to save"
        hud_surf = status_font.render(hud, True, (120, 120, 140))
        screen.blit(hud_surf, (WIN_W - hud_surf.get_width() - 10, WIN_H - PALETTE_H + 16))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()