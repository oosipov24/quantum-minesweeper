from src.tile import Tile


class Grid:
    def __init__(self, level):
        rows, cols = level["size"]
        self.rows = rows
        self.cols = cols
        danger_probs = level["danger_probs"]
        self.tiles = [
            [Tile(row, col, danger_probs[row][col]) for col in range(cols)]
            for row in range(rows)
        ]
        self.apply_start_exit(level["start"], level["exit"])
        self.apply_entanglement(level.get("entangled_pairs", []))

    def apply_start_exit(self, start_pos, exit_pos):
        start = self.get_tile(*start_pos)
        exit_tile = self.get_tile(*exit_pos)

        if start:
            start.is_start = True
            start.danger_prob = 0.0
            start.initial_danger_prob = 0.0
            start.force_collapse("SAFE", "SYSTEM")

        if exit_tile:
            exit_tile.is_exit = True
            exit_tile.danger_prob = 0.0
            exit_tile.initial_danger_prob = 0.0
            exit_tile.force_collapse("SAFE", "SYSTEM")

    def apply_entanglement(self, pairs):
        for index, (a_pos, b_pos) in enumerate(pairs, start=1):
            a = self.get_tile(*a_pos)
            b = self.get_tile(*b_pos)
            if not a or not b:
                continue
            a.entangled_with = b_pos
            b.entangled_with = a_pos
            a.entanglement_id = index
            b.entanglement_id = index

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_tile(self, row, col):
        if not self.in_bounds(row, col):
            return None
        return self.tiles[row][col]

    def neighbors_4(self, row, col):
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n_row = row + d_row
            n_col = col + d_col
            if self.in_bounds(n_row, n_col):
                yield self.get_tile(n_row, n_col)
