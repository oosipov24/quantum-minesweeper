import random


def collapse_tile(tile):
    if tile.collapsed:
        return tile.real_state

    tile.real_state = "DANGER" if random.random() < tile.danger_prob else "SAFE"
    tile.collapsed = True
    return tile.real_state


def scan_tile(game_state, tile):
    if game_state.game_over:
        return

    if game_state.scans_left <= 0:
        return

    if tile.collapsed:
        return

    game_state.scans_left -= 1
    game_state.trust -= 2
    tile.revealed_by = "SCAN"
    collapse_tile(tile)

    check_game_status(game_state)


def step_to_tile(game_state, tile):
    if game_state.game_over:
        return

    if not tile.collapsed:
        game_state.trust -= 5
        tile.revealed_by = "STEP"
        result = collapse_tile(tile)
    else:
        result = tile.real_state

    if result == "DANGER":
        game_state.casualties += 1

    game_state.player_pos = (tile.row, tile.col)
    check_game_status(game_state)


def check_game_status(game_state):
    row, col = game_state.player_pos

    if game_state.trust <= 0:
        game_state.game_over = True
        game_state.win = False
        return

    if game_state.casualties > game_state.max_casualties:
        game_state.game_over = True
        game_state.win = False
        return

    if (row, col) == game_state.exit_pos:
        game_state.game_over = True
        game_state.win = True