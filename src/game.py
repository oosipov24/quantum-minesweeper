import pygame

from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TILE_SIZE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    PANEL_X,
    PANEL_Y,
    PANEL_WIDTH,
    BG_COLOR,
    PANEL_COLOR,
    PANEL_BORDER_COLOR,
    GRID_LINE_COLOR,
    UNKNOWN_LOW_COLOR,
    UNKNOWN_MID_COLOR,
    UNKNOWN_HIGH_COLOR,
    SAFE_COLOR,
    DANGER_COLOR,
    PLAYER_COLOR,
    PLAYER_OUTLINE_COLOR,
    START_COLOR,
    EXIT_COLOR,
    ENTANGLED_COLOR,
    HOVER_COLOR,
    INTERFERENCE_POS_COLOR,
    INTERFERENCE_NEG_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    WARNING_TEXT_COLOR,
    BAD_TEXT_COLOR,
    GOOD_TEXT_COLOR,
)
from src.grid import Grid
from src.levels import LEVELS
from src.state import GameState
from src.rules import scan_tile, step_to_tile


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quantum Minesweeper: Safe Routes — Second Prototype")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 21)
        self.small_font = pygame.font.SysFont("arial", 17)
        self.tiny_font = pygame.font.SysFont("arial", 14)
        self.big_font = pygame.font.SysFont("arial", 38, bold=True)
        self.title_font = pygame.font.SysFont("arial", 28, bold=True)

        self.running = True
        self.level_index = 0
        self.hovered_cell = None
        self.reset_game(self.level_index)

    def reset_game(self, level_index=None):
        if level_index is not None:
            self.level_index = level_index % len(LEVELS)
        self.state = GameState(self.level_index)
        self.grid = Grid(self.state.level)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
        self.hovered_cell = self.mouse_to_grid(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_left_click(event.pos)

    def handle_keydown(self, key):
        if key == pygame.K_TAB:
            self.state.mode = "STEP" if self.state.mode == "SCAN" else "SCAN"

        elif key == pygame.K_1:
            self.state.mode = "SCAN"

        elif key == pygame.K_2:
            self.state.mode = "STEP"

        elif key == pygame.K_r:
            self.reset_game(self.level_index)

        elif key == pygame.K_n:
            self.reset_game(self.level_index + 1)

        elif key == pygame.K_p:
            self.reset_game(self.level_index - 1)

        elif self.state.mode == "STEP" and not self.state.game_over:
            current_row, current_col = self.state.player_pos
            target_row, target_col = current_row, current_col

            if key in (pygame.K_UP, pygame.K_w):
                target_row -= 1
            elif key in (pygame.K_DOWN, pygame.K_s):
                target_row += 1
            elif key in (pygame.K_LEFT, pygame.K_a):
                target_col -= 1
            elif key in (pygame.K_RIGHT, pygame.K_d):
                target_col += 1
            else:
                return

            if self.grid.in_bounds(target_row, target_col):
                tile = self.grid.get_tile(target_row, target_col)
                step_to_tile(self.state, self.grid, tile)

    def handle_left_click(self, mouse_pos):
        if self.state.mode != "SCAN" or self.state.game_over:
            return

        cell = self.mouse_to_grid(mouse_pos)
        if cell is None:
            return

        row, col = cell
        tile = self.grid.get_tile(row, col)
        if tile is not None:
            scan_tile(self.state, self.grid, tile)

    def mouse_to_grid(self, mouse_pos):
        mx, my = mouse_pos

        if mx < GRID_OFFSET_X or my < GRID_OFFSET_Y:
            return None

        col = (mx - GRID_OFFSET_X) // TILE_SIZE
        row = (my - GRID_OFFSET_Y) // TILE_SIZE

        if not self.grid.in_bounds(row, col):
            return None

        return row, col

    def draw(self):
        self.screen.fill(BG_COLOR)

        self.draw_header()
        self.draw_grid()
        self.draw_entanglement_links()
        self.draw_player()
        self.draw_side_panel()
        self.draw_endgame_message()

        pygame.display.flip()

    def draw_header(self):
        level = self.state.level
        title = self.title_font.render(level["name"], True, TEXT_COLOR)
        self.screen.blit(title, (40, 22))

        subtitle = self.font.render(level["subtitle"], True, WARNING_TEXT_COLOR)
        self.screen.blit(subtitle, (40, 55))

        story_lines = self.wrap_text(level["story"], self.small_font, 760)
        y = 88
        for line in story_lines[:3]:
            surf = self.small_font.render(line, True, MUTED_TEXT_COLOR)
            self.screen.blit(surf, (40, y))
            y += 20

        controls = "TAB/1/2 mode | Mouse scan | Arrows/WASD move | R restart | N/P level"
        surf = self.small_font.render(controls, True, MUTED_TEXT_COLOR)
        self.screen.blit(surf, (40, 150))

    def draw_grid(self):
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                tile = self.grid.get_tile(row, col)
                rect = self.tile_rect(row, col)

                pygame.draw.rect(self.screen, self.tile_color(tile), rect, border_radius=8)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, 2, border_radius=8)

                if tile.is_entangled:
                    pygame.draw.rect(self.screen, ENTANGLED_COLOR, rect.inflate(-6, -6), 3, border_radius=8)

                if self.hovered_cell == (row, col):
                    pygame.draw.rect(self.screen, HOVER_COLOR, rect.inflate(4, 4), 3, border_radius=8)

                self.draw_tile_label(tile, rect)

    def draw_entanglement_links(self):
        drawn_pairs = set()
        highlighted_pair = None

        if self.hovered_cell is not None:
            hover_tile = self.grid.get_tile(*self.hovered_cell)
            if hover_tile and hover_tile.entanglement_id:
                highlighted_pair = hover_tile.entanglement_id

        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                tile = self.grid.get_tile(row, col)
                if not tile.is_entangled or tile.entanglement_id in drawn_pairs:
                    continue

                other = self.grid.get_tile(*tile.entangled_with)
                if other is None:
                    continue

                start = self.tile_center(tile.row, tile.col)
                end = self.tile_center(other.row, other.col)
                width = 5 if tile.entanglement_id == highlighted_pair else 2
                pygame.draw.line(self.screen, ENTANGLED_COLOR, start, end, width)
                drawn_pairs.add(tile.entanglement_id)

    def draw_tile_label(self, tile, rect):
        if tile.is_start:
            label = "START"
            color = (15, 35, 45)
            font = self.tiny_font
        elif tile.is_exit:
            label = "EXIT"
            color = (55, 42, 10)
            font = self.tiny_font
        elif tile.collapsed:
            label = "SAFE" if tile.real_state == "SAFE" else "DANGER"
            color = (15, 25, 20)
            font = self.tiny_font
        else:
            label = f"{int(tile.danger_prob * 100)}%"
            color = TEXT_COLOR
            font = self.small_font

        text_surface = font.render(label, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

        if tile.entanglement_id:
            q_label = self.tiny_font.render(f"Q{tile.entanglement_id}", True, ENTANGLED_COLOR)
            self.screen.blit(q_label, (rect.x + 6, rect.y + 5))

        if not tile.collapsed and abs(tile.interference_delta) > 0.005:
            sign = "+" if tile.interference_delta > 0 else ""
            wave_color = INTERFERENCE_POS_COLOR if tile.interference_delta > 0 else INTERFERENCE_NEG_COLOR
            wave = self.tiny_font.render(f"{sign}{int(tile.interference_delta * 100)}", True, wave_color)
            self.screen.blit(wave, (rect.x + 6, rect.bottom - 19))

    def draw_player(self):
        row, col = self.state.player_pos
        center = self.tile_center(row, col)
        pygame.draw.circle(self.screen, PLAYER_OUTLINE_COLOR, center, TILE_SIZE // 4 + 4)
        pygame.draw.circle(self.screen, PLAYER_COLOR, center, TILE_SIZE // 4)

    def draw_side_panel(self):
        panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_WIDTH, 575)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, panel_rect, 2, border_radius=12)

        y = PANEL_Y + 18
        y = self.draw_panel_title("Mission status", y)
        y = self.draw_panel_line(f"Mode: {self.state.mode}", y, WARNING_TEXT_COLOR if self.state.mode == "SCAN" else GOOD_TEXT_COLOR)
        y = self.draw_panel_line(f"Trust: {self.state.trust}", y, self.value_color(self.state.trust, 100))
        y = self.draw_panel_line(f"Scans left: {self.state.scans_left}", y, TEXT_COLOR)
        y = self.draw_panel_line(f"Casualties: {self.state.casualties}/{self.state.max_casualties}", y, BAD_TEXT_COLOR if self.state.casualties else TEXT_COLOR)
        y = self.draw_panel_line(f"Turns: {self.state.turn_count}", y, MUTED_TEXT_COLOR)
        y += 12

        y = self.draw_panel_title("Quantum mechanics in play", y)
        quantum_lines = [
            "Superposition: unknown tiles store risk probability, not a fixed state.",
            "Measurement: SCAN/STEP collapses a tile into SAFE or DANGER.",
            "Entanglement: Q-pairs collapse together with opposite outcomes.",
            "Interference: each measurement shifts nearby unresolved probabilities.",
            "Observer cost: scans reduce Trust, so information is not free.",
        ]
        for line in quantum_lines:
            wrapped_lines = self.wrap_text(line, self.small_font, PANEL_WIDTH - 52)
            for index, wrapped in enumerate(wrapped_lines):
                prefix = "• " if index == 0 else "  "
                y = self.draw_panel_line(prefix + wrapped, y, MUTED_TEXT_COLOR, small=True)
        y += 12

        y = self.draw_panel_title("Event log", y)
        for message in self.state.event_log[-6:]:
            for wrapped in self.wrap_text(message, self.small_font, PANEL_WIDTH - 36):
                y = self.draw_panel_line(wrapped, y, TEXT_COLOR, small=True)

    def draw_panel_title(self, text, y):
        surf = self.font.render(text, True, TEXT_COLOR)
        self.screen.blit(surf, (PANEL_X + 18, y))
        return y + 29

    def draw_panel_line(self, text, y, color, small=False):
        font = self.small_font if small else self.font
        surf = font.render(text, True, color)
        self.screen.blit(surf, (PANEL_X + 18, y))
        return y + (21 if small else 27)

    def draw_endgame_message(self):
        if not self.state.game_over:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(250, 265, 600, 240)
        pygame.draw.rect(self.screen, PANEL_COLOR, box, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, box, 3, border_radius=16)

        message = "MISSION SUCCESS" if self.state.win else "MISSION FAILED"
        color = GOOD_TEXT_COLOR if self.state.win else BAD_TEXT_COLOR
        text_surface = self.big_font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, box.y + 58))
        self.screen.blit(text_surface, text_rect)

        reason_lines = self.wrap_text(self.state.end_reason, self.font, 500)
        y = box.y + 110
        for line in reason_lines:
            surf = self.font.render(line, True, TEXT_COLOR)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(surf, rect)
            y += 28

        hint = "R = restart level    N = next level    P = previous level"
        surf = self.small_font.render(hint, True, MUTED_TEXT_COLOR)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, box.bottom - 36))
        self.screen.blit(surf, rect)

    def tile_rect(self, row, col):
        x = GRID_OFFSET_X + col * TILE_SIZE
        y = GRID_OFFSET_Y + row * TILE_SIZE
        return pygame.Rect(x, y, TILE_SIZE - 4, TILE_SIZE - 4)

    def tile_center(self, row, col):
        return (
            GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2 - 2,
            GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2 - 2,
        )

    def tile_color(self, tile):
        if tile.collapsed:
            if tile.real_state == "SAFE":
                if tile.is_start:
                    return START_COLOR
                if tile.is_exit:
                    return EXIT_COLOR
                return SAFE_COLOR
            return DANGER_COLOR

        return self.risk_color(tile.danger_prob)

    def risk_color(self, probability):
        if probability < 0.35:
            return self.blend(UNKNOWN_LOW_COLOR, UNKNOWN_MID_COLOR, probability / 0.35)
        return self.blend(UNKNOWN_MID_COLOR, UNKNOWN_HIGH_COLOR, (probability - 0.35) / 0.50)

    def blend(self, color_a, color_b, t):
        t = max(0.0, min(1.0, t))
        return tuple(int(a + (b - a) * t) for a, b in zip(color_a, color_b))

    def value_color(self, value, max_value):
        ratio = value / max_value if max_value else 0
        if ratio > 0.6:
            return GOOD_TEXT_COLOR
        if ratio > 0.3:
            return WARNING_TEXT_COLOR
        return BAD_TEXT_COLOR

    def wrap_text(self, text, font, max_width):
        words = text.split()
        if not words:
            return [""]

        lines = []
        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines
