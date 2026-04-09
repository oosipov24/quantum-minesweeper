class Tile:
    def __init__(self, row, col, danger_prob=0.2):
        self.row = row
        self.col = col
        self.danger_prob = danger_prob
        self.collapsed = False
        self.real_state = None
        self.entangled_with = None
        self.revealed_by = None