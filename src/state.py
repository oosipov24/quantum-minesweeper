from src.levels import LEVELS


class GameState:
    def __init__(self, level_index=0):
        self.level_index = level_index % len(LEVELS)
        self.level = LEVELS[self.level_index]
        self.mode = "SCAN"
        self.trust = self.level["trust"]
        self.scans_left = self.level["scans"]
        self.casualties = 0
        self.max_casualties = self.level["max_casualties"]
        self.player_pos = self.level["start"]
        self.start_pos = self.level["start"]
        self.exit_pos = self.level["exit"]
        self.game_over = False
        self.win = False
        self.end_reason = ""
        self.turn_count = 0
        self.event_log = [
            "Mission started.",
            "Tiles are uncertain until SCAN or STEP collapses them.",
        ]

    @property
    def level_name(self):
        return self.level["name"]

    @property
    def level_story(self):
        return self.level["story"]

    @property
    def interference_strength(self):
        return self.level.get("interference_strength", 0.05)
