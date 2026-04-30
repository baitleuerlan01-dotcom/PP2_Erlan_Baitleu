import pygame
import math
from collections import deque



def draw_dashed_rect(surface, color, rect, dash=6):
    """Draws a dashed rectangle outline (used for selection previews)."""
    x, y, w, h = rect
    for i in range(0, w, dash * 2):
        pygame.draw.line(surface, color, (x + i, y), (min(x + i + dash, x + w), y))
        pygame.draw.line(surface, color, (x + i, y + h), (min(x + i + dash, x + w), y + h))
    for i in range(0, h, dash * 2):
        pygame.draw.line(surface, color, (x, y + i), (x, min(y + i + dash, y + h)))
        pygame.draw.line(surface, color, (x + w, y + i), (x + w, min(y + i + dash, y + h)))



class PencilTool:
    def __init__(self):
        self.last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.last_pos = pos
        pygame.draw.circle(canvas, color, pos, size // 2)

    def on_mouse_drag(self, canvas, pos, color, size):
        if self.last_pos:
            pygame.draw.line(canvas, color, self.last_pos, pos, size)
        self.last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self.last_pos = None

    def draw_preview(self, surface, pos, color, size):
        pass  




class LineTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass  

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pygame.draw.line(canvas, color, self.start, pos, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pygame.draw.line(surface, color, self.start, pos, size)




class RectangleTool:
    def __init__(self):
        self.start = None

    def _get_rect(self, pos):
        x = min(self.start[0], pos[0])
        y = min(self.start[1], pos[1])
        w = abs(pos[0] - self.start[0])
        h = abs(pos[1] - self.start[1])
        return (x, y, w, h)

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pygame.draw.rect(canvas, color, self._get_rect(pos), size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pygame.draw.rect(surface, color, self._get_rect(pos), size)




class SquareTool:
    def __init__(self):
        self.start = None

    def _get_rect(self, pos):
        dx = pos[0] - self.start[0]
        dy = pos[1] - self.start[1]
        side = min(abs(dx), abs(dy))
        x = self.start[0] if dx >= 0 else self.start[0] - side
        y = self.start[1] if dy >= 0 else self.start[1] - side
        return (x, y, side, side)

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pygame.draw.rect(canvas, color, self._get_rect(pos), size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pygame.draw.rect(surface, color, self._get_rect(pos), size)




class CircleTool:
    def __init__(self):
        self.start = None

    def _get_rect(self, pos):
        x = min(self.start[0], pos[0])
        y = min(self.start[1], pos[1])
        w = abs(pos[0] - self.start[0])
        h = abs(pos[1] - self.start[1])
        return (x, y, w, h)

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            r = self._get_rect(pos)
            if r[2] > 0 and r[3] > 0:
                pygame.draw.ellipse(canvas, color, r, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            r = self._get_rect(pos)
            if r[2] > 0 and r[3] > 0:
                pygame.draw.ellipse(surface, color, r, size)




class RightTriangleTool:
    def __init__(self):
        self.start = None

    def _get_points(self, pos):
        x1, y1 = self.start
        x2, y2 = pos
        return [(x1, y1), (x1, y2), (x2, y2)]

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pygame.draw.polygon(canvas, color, self._get_points(pos), size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pygame.draw.polygon(surface, color, self._get_points(pos), size)



class EquilateralTriangleTool:
    def __init__(self):
        self.start = None

    def _get_points(self, pos):
        cx = (self.start[0] + pos[0]) / 2
        base_y = max(self.start[1], pos[1])
        width = abs(pos[0] - self.start[0])
        height = width * math.sqrt(3) / 2
        top_y = base_y - height
        return [
            (cx, top_y),
            (cx - width / 2, base_y),
            (cx + width / 2, base_y),
        ]

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pts = self._get_points(pos)
            pygame.draw.polygon(canvas, color, pts, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pts = self._get_points(pos)
            pygame.draw.polygon(surface, color, pts, size)




class RhombusTool:
    def __init__(self):
        self.start = None

    def _get_points(self, pos):
        x1, y1 = self.start
        x2, y2 = pos
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        return [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pygame.draw.polygon(canvas, color, self._get_points(pos), size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pygame.draw.polygon(surface, color, self._get_points(pos), size)




class EraserTool:
    def __init__(self):
        self.last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.last_pos = pos
        pygame.draw.circle(canvas, (255, 255, 255), pos, size)

    def on_mouse_drag(self, canvas, pos, color, size):
        eraser_size = size * 3
        if self.last_pos:
            pygame.draw.line(canvas, (255, 255, 255), self.last_pos, pos, eraser_size)
        pygame.draw.circle(canvas, (255, 255, 255), pos, eraser_size // 2)
        self.last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self.last_pos = None

    def draw_preview(self, surface, pos, color, size):
        eraser_size = size * 3
        pygame.draw.circle(surface, (180, 180, 180), pos, eraser_size // 2, 2)




class FillTool:
    def on_mouse_down(self, canvas, pos, color, size):
        flood_fill(canvas, pos, color)

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def draw_preview(self, surface, pos, color, size):
       
        pygame.draw.circle(surface, color, pos, 6)
        pygame.draw.circle(surface, (0, 0, 0), pos, 6, 1)


def flood_fill(canvas, start_pos, fill_color):
    """BFS flood-fill on a pygame Surface."""
    w, h = canvas.get_size()
    x0, y0 = int(start_pos[0]), int(start_pos[1])
    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target_color = canvas.get_at((x0, y0))[:3]
    fc = fill_color[:3] if len(fill_color) >= 3 else fill_color

    if target_color == fc:
        return  

    visited = [[False] * h for _ in range(w)]
    queue = deque()
    queue.append((x0, y0))
    visited[x0][y0] = True

    while queue:
        cx, cy = queue.popleft()
        canvas.set_at((cx, cy), fc)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                if canvas.get_at((nx, ny))[:3] == target_color:
                    visited[nx][ny] = True
                    queue.append((nx, ny))




class TextTool:

    def __init__(self):
        self.active = False
        self.pos = None
        self.text = ""
        self.font = None
        self._cursor_visible = True
        self._cursor_timer = 0

    def _ensure_font(self, size):
        try:
            self.font = pygame.font.SysFont("consolas", max(12, size * 3))
        except Exception:
            self.font = pygame.font.Font(None, max(16, size * 3))

    def on_mouse_down(self, canvas, pos, color, size):
        self._ensure_font(size)
        self.active = True
        self.pos = pos
        self.text = ""
        self._cursor_timer = 0
        self._cursor_visible = True

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def handle_key(self, event, canvas, color, size):
        """Returns True if the tool consumed the event."""
        if not self.active:
            return False
        if event.key == pygame.K_RETURN:
            self._commit(canvas, color)
            return True
        elif event.key == pygame.K_ESCAPE:
            self.active = False
            self.text = ""
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return True
        else:
            char = event.unicode
            if char and char.isprintable():
                self.text += char
            return True

    def _commit(self, canvas, color):
        if self.font and self.pos and self.text:
            surf = self.font.render(self.text, True, color)
            canvas.blit(surf, self.pos)
        self.active = False
        self.text = ""

    def update(self, dt_ms):
        """Call every frame with elapsed ms to blink the cursor."""
        self._cursor_timer += dt_ms
        if self._cursor_timer >= 500:
            self._cursor_timer = 0
            self._cursor_visible = not self._cursor_visible

    def draw_preview(self, surface, pos, color, size):
        if not self.active or not self.font:
            return
        
        display = self.text + ("|" if self._cursor_visible else " ")
        surf = self.font.render(display, True, color)
        surface.blit(surf, self.pos)

    @property
    def is_active(self):
        return self.active