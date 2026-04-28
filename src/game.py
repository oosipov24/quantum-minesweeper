import pygame
import math

from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    TILE_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y,
    SIDEBAR_X, SIDEBAR_W,
    CARDS_Y, CARDS_H, LEVEL_BAR_Y,
    LEVEL_PANEL_X, LEVEL_PANEL_Y, LEVEL_PANEL_W, LEVEL_PANEL_H,
    BG_COLOR, PANEL_COLOR, PANEL_BORDER_COLOR, GRID_LINE_COLOR,
    UNKNOWN_LOW_COLOR, UNKNOWN_MID_COLOR, UNKNOWN_HIGH_COLOR,
    SAFE_COLOR, DANGER_COLOR, PLAYER_COLOR, PLAYER_OUTLINE_COLOR,
    START_COLOR, EXIT_COLOR, ENTANGLED_COLOR, HOVER_COLOR,
    INTERFERENCE_POS_COLOR, INTERFERENCE_NEG_COLOR,
    TEXT_COLOR, MUTED_TEXT_COLOR, WARNING_TEXT_COLOR,
    BAD_TEXT_COLOR, GOOD_TEXT_COLOR,
    CARD_TRUST_COLOR, CARD_CAS_COLOR, CARD_SCAN_COLOR, CARD_STEP_COLOR,
)
from src.grid import Grid
from src.levels import LEVELS
from src.state import GameState
from src.rules import scan_tile, step_to_tile


# ── tiny helpers ──────────────────────────────────────────────────────────────

def _surf(w, h, color, alpha=255):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*color[:3], alpha))
    return s

def _rounded_rect(surface, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)

def _blit_c(surface, surf, cx, cy):
    surface.blit(surf, surf.get_rect(center=(cx, cy)))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quantum Minesweeper: Safe Routes")
        self.clock  = pygame.time.Clock()

        # fonts
        mono = "couriernew,consolas,dejavusansmono"
        sans = "segoeui,helveticaneue,arial"
        self.f_title        = pygame.font.SysFont(sans,  26, bold=True)   # Main title
        self.f_sub          = pygame.font.SysFont(mono,  13)               # Subtitle
        self.f_card_l       = pygame.font.SysFont(mono,  11)               # Card label
        self.f_card_v       = pygame.font.SysFont(sans,  28, bold=True)    # Card value

        # Larger sidebar fonts for readability.
        self.f_side_h       = pygame.font.SysFont(mono,  13)               # Sidebar headings
        self.f_mode_l       = pygame.font.SysFont(mono,  15)               # Mode button label
        self.f_leg          = pygame.font.SysFont(mono,  15)               # Legend labels
        self.f_log          = pygame.font.SysFont(mono,  13)               # Event log text

        # Right mission panel fonts.
        self.f_level        = pygame.font.SysFont(sans,  24, bold=True)    # Level title
        self.f_mission_h    = pygame.font.SysFont(mono,  16, bold=True)    # Mission heading
        self.f_mission_body = pygame.font.SysFont(mono,  15)               # Mission text

        self.f_tile         = pygame.font.SysFont(mono,  12)               # Tile %
        self.f_tile_sm      = pygame.font.SysFont(mono,  10)               # q-label / delta
        self.f_hint         = pygame.font.SysFont(mono,  11)               # Bottom hint
        self.f_ov_big       = pygame.font.SysFont(sans,  44, bold=True)    # Overlay title
        self.f_ov_msg       = pygame.font.SysFont(mono,  14)               # Overlay reason

        self.running      = True
        self.level_index  = 0
        self.hovered_cell = None
        self._tick        = 0
        self.reset_game(self.level_index)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def reset_game(self, level_index=None):
        if level_index is not None:
            self.level_index = level_index % len(LEVELS)
        self.state = GameState(self.level_index)
        self.grid  = Grid(self.state.level)

    def run(self):
        while self.running:
            self._tick += 1
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    # ── input ─────────────────────────────────────────────────────────────────

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
            cr, cc = self.state.player_pos
            tr, tc = cr, cc
            if   key in (pygame.K_UP,    pygame.K_w): tr -= 1
            elif key in (pygame.K_DOWN,  pygame.K_s): tr += 1
            elif key in (pygame.K_LEFT,  pygame.K_a): tc -= 1
            elif key in (pygame.K_RIGHT, pygame.K_d): tc += 1
            else: return
            if self.grid.in_bounds(tr, tc):
                step_to_tile(self.state, self.grid, self.grid.get_tile(tr, tc))

    def handle_left_click(self, pos):
        if self.state.mode != "SCAN" or self.state.game_over:
            return
        cell = self.mouse_to_grid(pos)
        if cell:
            tile = self.grid.get_tile(*cell)
            if tile:
                scan_tile(self.state, self.grid, tile)

    def mouse_to_grid(self, pos):
        mx, my = pos
        if mx < GRID_OFFSET_X or my < GRID_OFFSET_Y:
            return None
        col = (mx - GRID_OFFSET_X) // TILE_SIZE
        row = (my - GRID_OFFSET_Y) // TILE_SIZE
        if not self.grid.in_bounds(row, col):
            return None
        return row, col

    # ── master draw ───────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_header()
        self._draw_stat_cards()
        self._draw_sidebar()
        self._draw_level_panel()
        self._draw_grid()
        self._draw_entanglement_links()
        self._draw_player()
        self._draw_hint()
        self._draw_endgame()
        pygame.display.flip()

    # ── header: title + subtitle ──────────────────────────────────────────────

    def _draw_header(self):
        cx = SCREEN_WIDTH // 2

        # "QUANTUM " (white) + "MINESWEEPER" (teal)
        part1 = self.f_title.render("QUANTUM ", True, (230, 240, 255))
        part2 = self.f_title.render("MINESWEEPER", True, (0, 212, 170))
        total_w = part1.get_width() + part2.get_width()
        x0 = cx - total_w // 2
        y0 = 14
        self.screen.blit(part1, (x0, y0))
        self.screen.blit(part2, (x0 + part1.get_width(), y0))

        sub = self.f_sub.render("SAFE ROUTES — HUMANITARIAN LOGISTICS", True, MUTED_TEXT_COLOR)
        self.screen.blit(sub, sub.get_rect(centerx=cx, top=y0 + part1.get_height() + 4))

    # ── four stat cards ───────────────────────────────────────────────────────

    def _draw_stat_cards(self):
        s   = self.state
        cas_str = f"{s.casualties} / {s.max_casualties}"
        cards = [
            ("PUBLIC TRUST",       str(s.trust),      CARD_TRUST_COLOR,
             self._value_color(s.trust, 100)),
            ("CIVILIAN CASUALTIES",  cas_str,            CARD_CAS_COLOR,
             BAD_TEXT_COLOR if s.casualties else TEXT_COLOR),
            ("SCANS LEFT",  str(s.scans_left),  CARD_SCAN_COLOR, TEXT_COLOR),
            ("STEPS",       str(s.turn_count),  CARD_STEP_COLOR, MUTED_TEXT_COLOR),
        ]

        margin = 16
        total_w = SCREEN_WIDTH - margin * 2
        card_w  = (total_w - 12 * 3) // 4   # 3 gaps between 4 cards
        card_x  = margin

        for label, value, accent, val_color in cards:
            rect = pygame.Rect(card_x, CARDS_Y, card_w, CARDS_H)
            # background
            _rounded_rect(self.screen, PANEL_COLOR, rect, radius=8,
                          border=1, border_color=PANEL_BORDER_COLOR)
            # top accent bar
            top_bar = pygame.Rect(card_x, CARDS_Y, card_w, 3)
            pygame.draw.rect(self.screen, accent, top_bar,
                             border_top_left_radius=8, border_top_right_radius=8)
            # label
            lsurf = self.f_card_l.render(label, True, MUTED_TEXT_COLOR)
            self.screen.blit(lsurf, lsurf.get_rect(centerx=rect.centerx, top=rect.top + 12))
            # value
            vsurf = self.f_card_v.render(value, True, val_color)
            # pulse red when critical
            if label == "TRUST" and s.trust < 25:
                alpha = int(180 + 75 * math.sin(self._tick * 0.15))
                vsurf.set_alpha(alpha)
            _blit_c(self.screen, vsurf, rect.centerx, rect.top + 48)
            card_x += card_w + 12

    # ── right-side level / mission panel ───────────────────────────────────────

    def _draw_level_panel(self):
        rect = pygame.Rect(LEVEL_PANEL_X, LEVEL_PANEL_Y, LEVEL_PANEL_W, LEVEL_PANEL_H)

        # Subtle translucent background layer.
        panel_s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        panel_s.fill((*PANEL_COLOR[:3], 218))
        self.screen.blit(panel_s, rect.topleft)

        # Main panel border and cyber-style corner accents.
        pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, rect, 1, border_radius=10)
        self._draw_panel_corners(rect, HOVER_COLOR)

        # Level dots are moved out of the old horizontal bar.
        self._draw_level_dots(rect.right - 12, rect.top - 28)

        pad_x = 26
        y = rect.top + 34

        name = self.state.level.get("name", f"Level {self.level_index + 1}").upper()
        title = self.f_level.render(name, True, HOVER_COLOR)
        self.screen.blit(title, (rect.x + pad_x, y))
        y += title.get_height() + 34

        heading = self.f_mission_h.render("MISSION BRIEF", True, HOVER_COLOR)
        self.screen.blit(heading, (rect.x + pad_x, y))
        y += heading.get_height() + 18

        pygame.draw.line(self.screen, HOVER_COLOR,
                         (rect.x + pad_x, y), (rect.right - pad_x, y), 1)
        pygame.draw.circle(self.screen, HOVER_COLOR, (rect.x + pad_x, y), 2)
        y += 28

        brief = self._level_brief()
        for line in self.wrap_text(brief, self.f_mission_body, rect.w - pad_x * 2):
            body = self.f_mission_body.render(line, True, (145, 175, 225))
            self.screen.blit(body, (rect.x + pad_x, y))
            y += 28

        # Bottom divider + small decorative marker.
        bottom_y = rect.bottom - 70
        pygame.draw.line(self.screen, (40, 70, 120),
                         (rect.x + pad_x, bottom_y), (rect.right - pad_x, bottom_y), 1)
        cx = rect.centerx
        pygame.draw.line(self.screen, HOVER_COLOR, (cx - 24, rect.bottom - 42), (cx, rect.bottom - 22), 2)
        pygame.draw.line(self.screen, HOVER_COLOR, (cx + 24, rect.bottom - 42), (cx, rect.bottom - 22), 2)
        pygame.draw.line(self.screen, HOVER_COLOR, (cx - 14, rect.bottom - 42), (cx + 14, rect.bottom - 42), 2)

    def _draw_panel_corners(self, rect, color):
        corner = 22
        width = 2

        # Top-left
        pygame.draw.line(self.screen, color, (rect.left, rect.top + corner), (rect.left, rect.top + 8), width)
        pygame.draw.line(self.screen, color, (rect.left + 8, rect.top), (rect.left + corner, rect.top), width)

        # Top-right
        pygame.draw.line(self.screen, color, (rect.right, rect.top + corner), (rect.right, rect.top + 8), width)
        pygame.draw.line(self.screen, color, (rect.right - 8, rect.top), (rect.right - corner, rect.top), width)

        # Bottom-left
        pygame.draw.line(self.screen, color, (rect.left, rect.bottom - corner), (rect.left, rect.bottom - 8), width)
        pygame.draw.line(self.screen, color, (rect.left + 8, rect.bottom), (rect.left + corner, rect.bottom), width)

        # Bottom-right
        pygame.draw.line(self.screen, color, (rect.right, rect.bottom - corner), (rect.right, rect.bottom - 8), width)
        pygame.draw.line(self.screen, color, (rect.right - 8, rect.bottom), (rect.right - corner, rect.bottom), width)

    def _draw_level_dots(self, right_x, cy):
        dot_r = 5
        dx = right_x
        for i in range(len(LEVELS) - 1, -1, -1):
            color = (0, 212, 170) if i == self.level_index else (30, 50, 90)
            pygame.draw.circle(self.screen, color, (dx, cy), dot_r)
            if i == self.level_index:
                pygame.draw.circle(self.screen, (0, 150, 120), (dx, cy), dot_r, 1)
            dx -= dot_r * 2 + 6

    def _level_brief(self):
        return self.state.level.get(
            "brief",
            "A damaged evacuation corridor cuts through the aid zone. "
            "Civilian signals are unstable, and several tiles may collapse "
            "into danger states when observed or crossed. Your task is to "
            "scan the route, identify the safest path, and guide survivors "
            "to the exit with minimum losses."
        )

    # Kept for old call sites. The old horizontal level bar is intentionally gone.
    def _draw_level_bar(self):
        self._draw_level_panel()

    # ── left sidebar ──────────────────────────────────────────────────────────

    def _draw_sidebar(self):
        x  = SIDEBAR_X
        w  = SIDEBAR_W
        y0 = GRID_OFFSET_Y

        # ── Mode section ──────────────────────────────────────────────────────
        y = y0
        self._sidebar_heading("MODE", x, y)
        y += 28

        for mode_key, icon, color in [("SCAN", "S", (0, 191, 255)),
                                       ("STEP", "M", (0, 212, 170))]:
            active = self.state.mode == mode_key
            btn_h  = 40
            btn    = pygame.Rect(x, y, w, btn_h)
            bc     = color if active else PANEL_BORDER_COLOR

            s_btn = pygame.Surface((w, btn_h), pygame.SRCALPHA)
            s_btn.fill((*PANEL_COLOR, 255) if not active else (*color[:3], 30))
            self.screen.blit(s_btn, (x, y))
            pygame.draw.rect(self.screen, bc, btn, 1, border_radius=7)

            # Icon badge.
            ibadge = pygame.Rect(x + 9, y + 8, 24, 24)
            pygame.draw.rect(self.screen, (*color[:3], 42 if active else 20),
                             ibadge, border_radius=5)
            isurf = self.f_mode_l.render(icon, True, color)
            _blit_c(self.screen, isurf, ibadge.centerx, ibadge.centery)

            label_mode = "SCAN tile" if mode_key == "SCAN" else "MOVE marker"
            lsurf = self.f_mode_l.render(label_mode, True,
                                          color if active else MUTED_TEXT_COLOR)
            self.screen.blit(lsurf, (x + 42, y + 10))
            y += btn_h + 8

        y += 10

        # ── Legend section ────────────────────────────────────────────────────
        self._sidebar_heading("LEGEND", x, y)
        y += 28

        legend_items = [
            ("P", "Player",  PLAYER_COLOR,    (0, 70, 56)),
            ("E", "Exit",    (0, 191, 255),   (0, 30, 60)),
            ("✓", "Safe",    (46, 213, 115),  (10, 46, 32)),
            ("✕", "Danger",  (255, 71, 87),   (52, 12, 12)),
            ("Q", "Q-pair",  ENTANGLED_COLOR, PANEL_COLOR),
        ]
        for icon, label, col, bg in legend_items:
            cell_r = pygame.Rect(x + 4, y + 1, 23, 23)
            pygame.draw.rect(self.screen, bg,  cell_r, border_radius=5)
            pygame.draw.rect(self.screen, col, cell_r, 1, border_radius=5)

            isurf = self.f_leg.render(icon, True, col)
            _blit_c(self.screen, isurf, cell_r.centerx, cell_r.centery)

            lsurf = self.f_leg.render(label, True, (145, 175, 225))
            self.screen.blit(lsurf, (x + 36, y + 2))
            y += 30

        y += 12

        # ── Event log section ─────────────────────────────────────────────────
        self._sidebar_heading("EVENT LOG", x, y)
        y += 28

        log_h    = SCREEN_HEIGHT - y - 48
        log_rect = pygame.Rect(x, y, w, log_h)
        pygame.draw.rect(self.screen, BG_COLOR, log_rect, border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, log_rect, 1, border_radius=6)

        # Clip log text inside the box.
        log_clip = pygame.Rect(x + 2, y + 4, w - 4, log_h - 8)
        messages = self.state.event_log[-12:]

        # Draw from bottom up.
        ly = log_rect.bottom - 12
        for msg in reversed(messages):
            color = (46, 213, 115)  if "safe"    in msg.lower() else \
                    (255, 71, 87)   if "danger"  in msg.lower() or "casualty" in msg.lower() else \
                    (168, 85, 247)  if "entangl" in msg.lower() or "q-pair"   in msg.lower() else \
                    (255, 165, 0)   if "warning" in msg.lower() else \
                    (145, 175, 225)
            for line in reversed(self.wrap_text(msg, self.f_log, w - 20)):
                ly -= 20
                if ly < log_clip.top:
                    break
                lsurf = self.f_log.render(line, True, color)
                self.screen.blit(lsurf, (x + 10, ly))

    def _sidebar_heading(self, text, x, y):
        surf = self.f_side_h.render(text, True, MUTED_TEXT_COLOR)
        self.screen.blit(surf, (x + 4, y))
        line_y = y + surf.get_height() + 4
        pygame.draw.line(self.screen, PANEL_BORDER_COLOR,
                         (x, line_y), (x + SIDEBAR_W, line_y))

    # ── grid ──────────────────────────────────────────────────────────────────

    def _draw_grid(self):
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                tile  = self.grid.get_tile(row, col)
                rect  = self._tile_rect(row, col)
                color = self._tile_color(tile)

                pygame.draw.rect(self.screen, color, rect, border_radius=5)

                # probability bar at bottom
                if not tile.collapsed and not tile.is_start and not tile.is_exit:
                    bw = int(rect.width * tile.danger_prob)
                    bc = self._prob_color(tile.danger_prob)
                    bar = pygame.Rect(rect.x, rect.bottom - 3, bw, 3)
                    pygame.draw.rect(self.screen, bc, bar,
                                     border_bottom_left_radius=5,
                                     border_bottom_right_radius=5 if bw >= rect.width else 0)

                # entangled inner ring
                if tile.is_entangled:
                    pygame.draw.rect(self.screen, ENTANGLED_COLOR,
                                     rect.inflate(-6, -6), 1, border_radius=4)

                # border
                is_hover = self.hovered_cell == (row, col)
                bc2   = HOVER_COLOR if is_hover else GRID_LINE_COLOR
                bw2   = 2 if is_hover else 1
                pygame.draw.rect(self.screen, bc2, rect, bw2, border_radius=5)

                self._draw_tile_label(tile, rect)

    def _draw_tile_label(self, tile, rect):
        cx, cy = rect.centerx, rect.centery

        if tile.is_start:
            self._bc(self.f_tile_sm, "START", (100, 180, 255), cx, cy)
        elif tile.is_exit:
            self._bc(self.f_tile_sm, "EXIT",  (0, 212, 170),   cx, cy)
        elif tile.collapsed:
            if tile.real_state == "SAFE":
                self._bc(self.f_tile, "SAFE",   (46, 213, 115), cx, cy)
            else:
                self._bc(self.f_tile, "DANGER", (255, 71, 87),  cx, cy)
        else:
            pct   = f"{int(tile.danger_prob * 100)}%"
            pcol  = self._prob_color(tile.danger_prob)
            self._bc(self.f_tile, pct, pcol, cx, cy - 3)

        if tile.entanglement_id:
            qs = self.f_tile_sm.render(f"Q{tile.entanglement_id}", True, ENTANGLED_COLOR)
            self.screen.blit(qs, (rect.x + 4, rect.y + 3))

        if not tile.collapsed and abs(tile.interference_delta) > 0.005:
            sign = "+" if tile.interference_delta > 0 else ""
            wc   = INTERFERENCE_POS_COLOR if tile.interference_delta > 0 else INTERFERENCE_NEG_COLOR
            ws   = self.f_tile_sm.render(
                f"{sign}{int(tile.interference_delta * 100)}", True, wc)
            self.screen.blit(ws, (rect.x + 4, rect.bottom - 14))

    def _bc(self, font, text, color, cx, cy):
        s = font.render(text, True, color)
        self.screen.blit(s, s.get_rect(center=(cx, cy)))

    # ── entanglement links ────────────────────────────────────────────────────

    def _draw_entanglement_links(self):
        drawn = set()
        hi_id = None
        if self.hovered_cell:
            ht = self.grid.get_tile(*self.hovered_cell)
            if ht and ht.entanglement_id:
                hi_id = ht.entanglement_id

        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                tile = self.grid.get_tile(row, col)
                if not tile.is_entangled or tile.entanglement_id in drawn:
                    continue
                other = self.grid.get_tile(*tile.entangled_with)
                if other is None:
                    continue
                p1 = self._tile_center(tile.row,  tile.col)
                p2 = self._tile_center(other.row, other.col)
                w  = 3 if tile.entanglement_id == hi_id else 1
                self._dashed_line(ENTANGLED_COLOR, p1, p2, width=w, dash=9, gap=5)
                drawn.add(tile.entanglement_id)

    def _dashed_line(self, color, p1, p2, width=1, dash=8, gap=5):
        dx, dy = p2[0]-p1[0], p2[1]-p1[1]
        L = math.hypot(dx, dy)
        if L == 0: return
        ux, uy = dx/L, dy/L
        pos = 0
        while pos < L:
            x0 = p1[0] + ux * pos
            y0 = p1[1] + uy * pos
            x1 = p1[0] + ux * min(pos+dash, L)
            y1 = p1[1] + uy * min(pos+dash, L)
            pygame.draw.line(self.screen, color, (int(x0),int(y0)), (int(x1),int(y1)), width)
            pos += dash + gap

    # ── player ────────────────────────────────────────────────────────────────

    def _draw_player(self):
        row, col = self.state.player_pos
        cx, cy   = self._tile_center(row, col)
        r        = TILE_SIZE // 4

        # animated pulse ring
        pulse = math.sin(self._tick * 0.09) * 2
        ring_r = int(r + 5 + pulse)
        ring_s = pygame.Surface((ring_r*2+4, ring_r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring_s, (*PLAYER_COLOR[:3], 80),
                           (ring_r+2, ring_r+2), ring_r, 2)
        self.screen.blit(ring_s, (cx - ring_r - 2, cy - ring_r - 2))

        # glow layers
        for i in range(4, 0, -1):
            gr = r + i*3
            gs = pygame.Surface((gr*2+2, gr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*PLAYER_COLOR[:3], 18),
                               (gr+1, gr+1), gr)
            self.screen.blit(gs, (cx-gr-1, cy-gr-1))

        pygame.draw.circle(self.screen, PLAYER_COLOR, (cx, cy), r)

    # ── hint bar ──────────────────────────────────────────────────────────────

    def _draw_hint(self):
        if self.state.game_over:
            return
        mode = self.state.mode
        if mode == "SCAN":
            txt = "SCAN mode: click any unknown tile to measure it"
        else:
            txt = "MOVE mode: click adjacent tile  or  use Arrow keys / WASD"
        surf = self.f_hint.render(txt, True, (55, 75, 115))
        bary = GRID_OFFSET_Y + self.grid.rows * TILE_SIZE + 10
        grid_center_x = GRID_OFFSET_X + (self.grid.cols * TILE_SIZE) // 2 - 1
        self.screen.blit(surf, surf.get_rect(centerx=grid_center_x, top=bary))

    # ── end-game overlay ──────────────────────────────────────────────────────

    def _draw_endgame(self):
        if not self.state.game_over:
            return

        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((5, 8, 18, 195))
        self.screen.blit(ov, (0, 0))

        win    = self.state.win
        accent = GOOD_TEXT_COLOR if win else BAD_TEXT_COLOR
        bw, bh = 600, 250
        bx     = (SCREEN_WIDTH  - bw) // 2
        by     = (SCREEN_HEIGHT - bh) // 2

        box_s = pygame.Surface((bw, bh), pygame.SRCALPHA)
        box_s.fill((15, 22, 44, 235))
        self.screen.blit(box_s, (bx, by))
        pygame.draw.rect(self.screen, accent,
                         pygame.Rect(bx, by, bw, bh), 2, border_radius=12)
        pygame.draw.rect(self.screen, accent,
                         pygame.Rect(bx, by, bw, 3), border_radius=12)

        msg   = "MISSION SUCCESS" if win else "MISSION FAILED"
        tsurf = self.f_ov_big.render(msg, True, accent)
        _blit_c(self.screen, tsurf, SCREEN_WIDTH//2, by + 68)

        for i, line in enumerate(self.wrap_text(self.state.end_reason, self.f_ov_msg, bw-60)):
            ls = self.f_ov_msg.render(line, True, TEXT_COLOR)
            _blit_c(self.screen, ls, SCREEN_WIDTH//2, by + 128 + i*24)

        hint  = "R  restart    N  next level    P  previous level"
        hs    = self.f_hint.render(hint, True, MUTED_TEXT_COLOR)
        _blit_c(self.screen, hs, SCREEN_WIDTH//2, by + bh - 28)

    # ── geometry helpers ──────────────────────────────────────────────────────

    def _tile_rect(self, row, col):
        x = GRID_OFFSET_X + col * TILE_SIZE
        y = GRID_OFFSET_Y + row * TILE_SIZE
        return pygame.Rect(x, y, TILE_SIZE - 3, TILE_SIZE - 3)

    def _tile_center(self, row, col):
        return (GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2 - 1,
                GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2 - 1)

    def _tile_color(self, tile):
        if tile.collapsed:
            if tile.real_state == "SAFE":
                if tile.is_start: return START_COLOR
                if tile.is_exit:  return EXIT_COLOR
                return SAFE_COLOR
            return DANGER_COLOR
        return self._risk_color(tile.danger_prob)

    def _risk_color(self, p):
        if p < 0.35:
            return self._blend(UNKNOWN_LOW_COLOR, UNKNOWN_MID_COLOR, p / 0.35)
        return     self._blend(UNKNOWN_MID_COLOR, UNKNOWN_HIGH_COLOR, (p-0.35)/0.50)

    def _prob_color(self, p):
        if p < 0.40: return (46, 213, 115)
        if p < 0.65: return (255, 165,  0)
        return             (255,  71, 87)

    def _blend(self, a, b, t):
        t = max(0.0, min(1.0, t))
        return tuple(int(x + (y-x)*t) for x, y in zip(a, b))

    def _value_color(self, value, max_value):
        r = value / max_value if max_value else 0
        if r > 0.6: return GOOD_TEXT_COLOR
        if r > 0.3: return WARNING_TEXT_COLOR
        return BAD_TEXT_COLOR

    def wrap_text(self, text, font, max_width):
        words = text.split()
        if not words: return [""]
        lines, cur = [], words[0]
        for w in words[1:]:
            cand = cur + " " + w
            if font.size(cand)[0] <= max_width:
                cur = cand
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        return lines

    # ── kept for compatibility with old call sites ────────────────────────────
    def draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_header()
        self._draw_stat_cards()
        self._draw_sidebar()
        self._draw_level_panel()
        self._draw_grid()
        self._draw_entanglement_links()
        self._draw_player()
        self._draw_hint()
        self._draw_endgame()
        pygame.display.flip()

    def draw_header(self):           self._draw_header()
    def draw_grid(self):             self._draw_grid()
    def draw_entanglement_links(self): self._draw_entanglement_links()
    def draw_player(self):           self._draw_player()
    def draw_side_panel(self):       self._draw_sidebar()
    def draw_endgame_message(self):  self._draw_endgame()