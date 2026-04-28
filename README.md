# Quantum Minesweeper: Safe Routes

Second Prototype of a grid-based humanitarian logistics game built with **Python + Pygame**.

## Goal

Guide the evacuation marker from **START** to **EXIT** while keeping:

- Trust above 0
- casualties within the allowed limit
- scans under control

The game is not about checking every tile. It is about finding a sustainable route under uncertainty.

## Controls

| Key / Action | Meaning |
|---|---|
| `TAB` | Switch between SCAN and STEP |
| `1` | SCAN mode |
| `2` | STEP mode |
| Mouse left click | Scan a tile in SCAN mode |
| Arrow keys / WASD | Move in STEP mode |
| `R` | Restart current level |
| `N` | Next level |
| `P` | Previous level |

## Quantum concepts in the second prototype

### 1. Superposition / Uncertainty

Unknown tiles do not store a fixed safe/danger result. They store a danger probability. The actual state is resolved only when the player scans or steps onto the tile.

### 2. Measurement and Collapse

SCAN or STEP triggers measurement. The tile collapses into either `SAFE` or `DANGER`.

### 3. Observer Cost

Observation is not free. Scanning reduces Trust, and stepping into unknown space reduces Trust more strongly. This makes information a costly resource.

### 4. Entanglement

Some tiles are linked as Q-pairs. When one tile in the pair collapses, the other collapses immediately with the opposite result. This makes tiles non-independent and moves the game beyond ordinary Minesweeper logic.

### 5. Interference

After a measurement, nearby unresolved tiles have their risk probabilities shifted. A dangerous collapse increases nearby uncertainty; a safe collapse slightly calms the local probability field.

## Levels

The game currently contains 3 levels:

1. **First Corridor** — introduces basic route planning and Q-pairs.
2. **Metro Interference** — stronger local probability shifts.
3. **Trust Collapse** — fewer resources and a stricter casualty limit.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

On PowerShell, activation may require:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Project structure

```text
main.py
src/
  config.py
  game.py
  grid.py
  levels.py
  rules.py
  state.py
  tile.py
```
