from src.tile import Tile


class Grid:
    def __init__(self, rows, cols, default_danger_prob=0.2):
        self.rows = rows
        self.cols = cols
        self.tiles = [
            [Tile(row, col, default_danger_prob) for col in range(cols)]
            for row in range(rows)
        ]

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_tile(self, row, col):
        if not self.in_bounds(row, col):
            return None
        return self.tiles[row][col]