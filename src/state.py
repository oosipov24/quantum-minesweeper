class GameState:
    def __init__(self):
        self.mode = "SCAN"
        self.trust = 100
        self.scans_left = 10
        self.casualties = 0
        self.max_casualties = 3
        self.player_pos = (0, 0)
        self.start_pos = (0, 0)
        self.exit_pos = (7, 7)
        self.game_over = False
        self.win = False