# ── Screen ────────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 860
FPS           = 60

# ── Grid ──────────────────────────────────────────────────────────────────────
GRID_ROWS     = 8
GRID_COLS     = 8
TILE_SIZE     = 58

# Layout: left sidebar (260px) | gap (16px) | grid (8*58+7*3=485px) | right gap
SIDEBAR_X     = 16
SIDEBAR_W     = 258
GRID_OFFSET_X = 292          # SIDEBAR_X + SIDEBAR_W + 18
GRID_OFFSET_Y = 248          # below header cards; old level bar removed

# Stats cards row
CARDS_Y       = 96
CARDS_H       = 72

# Old level bar kept only for backward compatibility.
# Level information is now drawn in the mission panel to the right of the grid.
LEVEL_BAR_Y   = 156

# Right-side mission panel
LEVEL_PANEL_X = 804
LEVEL_PANEL_Y = GRID_OFFSET_Y
LEVEL_PANEL_W = SCREEN_WIDTH - LEVEL_PANEL_X - 24
LEVEL_PANEL_H = 510

# Kept for backward-compat (not used for panel layout anymore)
PANEL_X       = 292
PANEL_Y       = 248
PANEL_WIDTH   = 258

# ── Colours ───────────────────────────────────────────────────────────────────
BG_COLOR           = (10,  14,  26)
PANEL_COLOR        = (15,  22,  44)
PANEL_BORDER_COLOR = (28,  44,  80)
GRID_LINE_COLOR    = (20,  32,  56)

UNKNOWN_LOW_COLOR  = (16,  28,  52)
UNKNOWN_MID_COLOR  = (42,  32,  16)
UNKNOWN_HIGH_COLOR = (56,  14,  14)

SAFE_COLOR    = (10,  46,  32)
DANGER_COLOR  = (52,  12,  12)
START_COLOR   = (22,  18,  54)
EXIT_COLOR    = (10,  34,  56)

PLAYER_COLOR         = (  0, 212, 170)
PLAYER_OUTLINE_COLOR = (  0,  80,  64)

ENTANGLED_COLOR        = (168,  85, 247)
HOVER_COLOR            = (  0, 191, 255)
INTERFERENCE_POS_COLOR = (255, 100,  80)
INTERFERENCE_NEG_COLOR = ( 80, 210, 140)

TEXT_COLOR         = (200, 214, 244)
MUTED_TEXT_COLOR   = ( 88, 104, 140)
WARNING_TEXT_COLOR = (255, 165,   0)
BAD_TEXT_COLOR     = (255,  71,  87)
GOOD_TEXT_COLOR    = ( 46, 213, 115)

# ── Accent colours for stat cards top-borders ─────────────────────────────────
CARD_TRUST_COLOR = (  0, 191, 255)   # cyan
CARD_CAS_COLOR   = (255,  71,  87)   # red
CARD_SCAN_COLOR  = (255, 165,   0)   # amber
CARD_STEP_COLOR  = (  0, 212, 170)   # teal

# ── Game logic (unchanged) ────────────────────────────────────────────────────
MIN_DANGER_PROB         = 0.05
MAX_DANGER_PROB         = 0.85
SCAN_TRUST_COST         = 2
STEP_UNKNOWN_TRUST_COST = 5
INTERFERENCE_STRENGTH   = 0.06