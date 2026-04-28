class Tile:
    def __init__(self, row, col, danger_prob=0.2):
        self.row = row
        self.col = col
        self.danger_prob = danger_prob
        self.initial_danger_prob = danger_prob
        self.collapsed = False
        self.real_state = None
        self.entangled_with = None
        self.entanglement_id = None
        self.revealed_by = None
        self.interference_delta = 0.0
        self.is_start = False
        self.is_exit = False

    @property
    def is_entangled(self):
        return self.entangled_with is not None

    def force_collapse(self, state, revealed_by="SYSTEM"):
        self.real_state = state
        self.collapsed = True
        self.revealed_by = revealed_by
