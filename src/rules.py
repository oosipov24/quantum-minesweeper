import random

from src.config import (
    MIN_DANGER_PROB,
    MAX_DANGER_PROB,
    SCAN_TRUST_COST,
    STEP_UNKNOWN_TRUST_COST,
)


def clamp(value, low, high):
    return max(low, min(high, value))


def add_log(game_state, message):
    game_state.event_log.append(message)
    game_state.event_log = game_state.event_log[-7:]


def collapse_tile(game_state, grid, tile, revealed_by):
    if tile.collapsed:
        return tile.real_state

    tile.real_state = "DANGER" if random.random() < tile.danger_prob else "SAFE"
    tile.collapsed = True
    tile.revealed_by = revealed_by

    add_log(
        game_state,
        f"{revealed_by}: ({tile.row},{tile.col}) collapsed to {tile.real_state}.",
    )

    resolve_entanglement(game_state, grid, tile)
    apply_interference(game_state, grid, tile)
    return tile.real_state


def resolve_entanglement(game_state, grid, tile):
    if tile.entangled_with is None:
        return

    other = grid.get_tile(*tile.entangled_with)
    if other is None or other.collapsed:
        return

    # Simple anti-correlation: one member resolves SAFE, the partner resolves DANGER.
    # This makes the state of the pair non-independent.
    other.real_state = "DANGER" if tile.real_state == "SAFE" else "SAFE"
    other.collapsed = True
    other.revealed_by = "ENTANGLED"

    add_log(
        game_state,
        f"Entanglement Q{tile.entanglement_id}: ({other.row},{other.col}) collapsed to {other.real_state}.",
    )


def apply_interference(game_state, grid, source_tile):
    # Measurement disturbs the local probability field around the measured tile.
    # SAFE slightly calms neighboring risk; DANGER raises neighboring uncertainty.
    strength = game_state.interference_strength
    delta = strength if source_tile.real_state == "DANGER" else -strength * 0.65

    changed = 0
    for neighbor in grid.neighbors_4(source_tile.row, source_tile.col):
        if neighbor.collapsed:
            continue
        old_prob = neighbor.danger_prob
        neighbor.danger_prob = clamp(old_prob + delta, MIN_DANGER_PROB, MAX_DANGER_PROB)
        neighbor.interference_delta += neighbor.danger_prob - old_prob
        changed += 1

    if changed:
        sign = "+" if delta > 0 else ""
        add_log(game_state, f"Interference wave: {changed} nearby probabilities shifted ({sign}{delta:.2f}).")


def scan_tile(game_state, grid, tile):
    if game_state.game_over:
        return

    if game_state.scans_left <= 0:
        add_log(game_state, "No scans left.")
        return

    if tile.collapsed:
        add_log(game_state, f"Tile ({tile.row},{tile.col}) is already known.")
        return

    game_state.turn_count += 1
    game_state.scans_left -= 1
    game_state.trust -= SCAN_TRUST_COST
    collapse_tile(game_state, grid, tile, "SCAN")
    check_game_status(game_state)


def step_to_tile(game_state, grid, tile):
    if game_state.game_over:
        return

    game_state.turn_count += 1
    result = tile.real_state

    if not tile.collapsed:
        game_state.trust -= STEP_UNKNOWN_TRUST_COST
        result = collapse_tile(game_state, grid, tile, "STEP")

    if result == "DANGER":
        game_state.casualties += 1
        add_log(game_state, f"Casualties increased to {game_state.casualties}.")

    game_state.player_pos = (tile.row, tile.col)
    check_game_status(game_state)


def check_game_status(game_state):
    row, col = game_state.player_pos

    if game_state.trust <= 0:
        game_state.trust = 0
        game_state.game_over = True
        game_state.win = False
        game_state.end_reason = "Trust collapsed. The evacuation network stopped cooperating."
        return

    if game_state.casualties > game_state.max_casualties:
        game_state.game_over = True
        game_state.win = False
        game_state.end_reason = "Casualty limit exceeded. The corridor is no longer acceptable."
        return

    if (row, col) == game_state.exit_pos:
        game_state.game_over = True
        game_state.win = True
        game_state.end_reason = "Exit reached while keeping the mission within limits."
