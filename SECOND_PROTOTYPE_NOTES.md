# Second Prototype Notes

## What changed from the first prototype

The first prototype implemented a playable core loop: grid, SCAN/STEP, collapse, Trust, scans, casualties, and win/lose conditions.

The second prototype strengthens the quantum concept and improves presentation:

| Area | Added in Second Prototype |
|---|---|
| Quantum gameplay | Entangled Q-pairs and interference waves |
| Strategy | One measurement can affect several cells and future probabilities |
| Visuals | Risk-colored unknown tiles, Q-pair borders, entanglement links, event log, side panel |
| Content | Three handcrafted levels |
| Lore | Humanitarian evacuation framing for each level |

## Why this is more quantum than ordinary Minesweeper

In classical Minesweeper, the board is fixed from the beginning. The player reveals a hidden but already determined state.

In this prototype, unknown tiles are represented by probabilities and collapse during interaction. More importantly, some states are linked through entanglement: measuring one tile can immediately resolve another tile. This means the board is not a set of independent hidden cells.

The interference system further strengthens the observer effect. Measurement changes the local probability field, so observing the system affects future outcomes.

## Suggested explanation for presentation

> The first version was close to probabilistic Minesweeper because each tile behaved independently. In the second prototype, I added coupled state collapse through entanglement and local probability interference. Now a measurement does not only reveal one tile; it can also resolve a linked tile and disturb nearby unresolved probabilities. This makes observation an active gameplay event instead of passive information gathering.

## Core design message

The player should not scan everything. The player must decide where information is worth the cost, because every measurement consumes resources and can change the system.
