import pygame

from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GRID_ROWS,
    GRID_COLS,
    TILE_SIZE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    BG_COLOR,
    GRID_LINE_COLOR,
    UNKNOWN_COLOR,
    SAFE_COLOR,
    DANGER_COLOR,
    PLAYER_COLOR,
    START_COLOR,
    EXIT_COLOR,
    TEXT_COLOR,
)
from src.grid import Grid
from src.state import GameState
from src.rules import scan_tile, step_to_tile


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quantum Minesweeper: Safe Routes")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)

        self.running = True
        self.reset_game()

    def reset_game(self):
        self.state = GameState()
        self.grid = Grid(GRID_ROWS, GRID_COLS, default_danger_prob=0.22)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
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

        elif key == pygame.K_r:
            self.reset_game()

        elif self.state.mode == "STEP" and not self.state.game_over:
            current_row, current_col = self.state.player_pos

            target_row, target_col = current_row, current_col

            if key == pygame.K_UP:
                target_row -= 1
            elif key == pygame.K_DOWN:
                target_row += 1
            elif key == pygame.K_LEFT:
                target_col -= 1
            elif key == pygame.K_RIGHT:
                target_col += 1
            else:
                return

            if self.grid.in_bounds(target_row, target_col):
                tile = self.grid.get_tile(target_row, target_col)
                step_to_tile(self.state, tile)

    def handle_left_click(self, mouse_pos):
        if self.state.mode != "SCAN" or self.state.game_over:
            return

        row, col = self.mouse_to_grid(mouse_pos)
        if row is None or col is None:
            return

        tile = self.grid.get_tile(row, col)
        if tile is not None:
            scan_tile(self.state, tile)

    def mouse_to_grid(self, mouse_pos):
        mx, my = mouse_pos

        if mx < GRID_OFFSET_X or my < GRID_OFFSET_Y:
            return None, None

        col = (mx - GRID_OFFSET_X) // TILE_SIZE
        row = (my - GRID_OFFSET_Y) // TILE_SIZE

        if not self.grid.in_bounds(row, col):
            return None, None

        return row, col

    def draw(self):
        self.screen.fill(BG_COLOR)

        self.draw_hud()
        self.draw_grid()
        self.draw_player()
        self.draw_endgame_message()

        pygame.display.flip()

    def draw_hud(self):
        lines = [
            f"Mode: {self.state.mode}  (TAB to switch)",
            f"Trust: {self.state.trust}",
            f"Scans left: {self.state.scans_left}",
            f"Casualties: {self.state.casualties}/{self.state.max_casualties}",
            "Controls: TAB = switch mode | Arrows = move | Mouse = scan | R = restart",
        ]

        y = 20
        for line in lines:
            text_surface = self.font.render(line, True, TEXT_COLOR)
            self.screen.blit(text_surface, (40, y))
            y += 28

    def draw_grid(self):
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                tile = self.grid.get_tile(row, col)

                x = GRID_OFFSET_X + col * TILE_SIZE
                y = GRID_OFFSET_Y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                color = UNKNOWN_COLOR
                if tile.collapsed:
                    color = SAFE_COLOR if tile.real_state == "SAFE" else DANGER_COLOR

                if (row, col) == self.state.start_pos:
                    color = START_COLOR if not tile.collapsed else color

                if (row, col) == self.state.exit_pos:
                    color = EXIT_COLOR if not tile.collapsed else color

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, 2)

                if tile.collapsed:
                    label = "S" if tile.real_state == "SAFE" else "D"
                    text_surface = self.font.render(label, True, (20, 20, 20))
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)

    def draw_player(self):
        row, col = self.state.player_pos

        center_x = GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        center_y = GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2

        pygame.draw.circle(self.screen, PLAYER_COLOR, (center_x, center_y), TILE_SIZE // 4)

    def draw_endgame_message(self):
        if not self.state.game_over:
            return

        message = "YOU WIN" if self.state.win else "YOU LOSE"
        text_surface = self.big_font.render(message, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(text_surface, text_rect)