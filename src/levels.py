LEVELS = [
    {
        "name": "Level 1 — First Corridor",
        "subtitle": "Training evacuation route",
        "story": (
            "A small district lost power after an infrastructure failure. "
            "Your team must open the first safe corridor for civilians."
        ),
        "size": (8, 8),
        "start": (0, 0),
        "exit": (7, 7),
        "trust": 100,
        "scans": 13,
        "max_casualties": 2,
        "interference_strength": 0.04,
        "danger_probs": [
            [0.00, 0.12, 0.16, 0.22, 0.28, 0.25, 0.20, 0.18],
            [0.10, 0.16, 0.24, 0.34, 0.30, 0.26, 0.22, 0.20],
            [0.14, 0.20, 0.32, 0.42, 0.38, 0.30, 0.24, 0.20],
            [0.16, 0.22, 0.30, 0.36, 0.40, 0.34, 0.28, 0.22],
            [0.18, 0.20, 0.24, 0.32, 0.38, 0.44, 0.32, 0.24],
            [0.20, 0.22, 0.26, 0.30, 0.34, 0.42, 0.36, 0.26],
            [0.18, 0.20, 0.22, 0.24, 0.28, 0.34, 0.30, 0.22],
            [0.16, 0.18, 0.20, 0.22, 0.24, 0.28, 0.22, 0.00],
        ],
        "entangled_pairs": [((1, 2), (4, 5)), ((2, 6), (6, 3))],
    },
    {
        "name": "Level 2 — Metro Interference",
        "subtitle": "Underground access route",
        "story": (
            "A damaged metro tunnel creates unstable sensor readings. "
            "Measurements now disturb nearby risk values more strongly."
        ),
        "size": (8, 8),
        "start": (0, 0),
        "exit": (7, 7),
        "trust": 95,
        "scans": 11,
        "max_casualties": 2,
        "interference_strength": 0.07,
        "danger_probs": [
            [0.00, 0.18, 0.22, 0.26, 0.30, 0.26, 0.22, 0.18],
            [0.14, 0.22, 0.36, 0.46, 0.42, 0.38, 0.30, 0.22],
            [0.18, 0.28, 0.48, 0.58, 0.52, 0.44, 0.34, 0.24],
            [0.20, 0.34, 0.50, 0.62, 0.54, 0.46, 0.38, 0.28],
            [0.22, 0.32, 0.42, 0.50, 0.58, 0.54, 0.42, 0.30],
            [0.20, 0.28, 0.34, 0.40, 0.48, 0.52, 0.44, 0.32],
            [0.18, 0.22, 0.28, 0.34, 0.40, 0.44, 0.36, 0.26],
            [0.14, 0.18, 0.22, 0.26, 0.30, 0.34, 0.24, 0.00],
        ],
        "entangled_pairs": [((0, 5), (5, 1)), ((2, 2), (6, 6)), ((3, 4), (4, 7))],
    },
    {
        "name": "Level 3 — Trust Collapse",
        "subtitle": "Dense urban evacuation",
        "story": (
            "The city is tense. Every inspection delays evacuation and reduces cooperation. "
            "The safest route is not the one with the most scans."
        ),
        "size": (8, 8),
        "start": (0, 0),
        "exit": (7, 7),
        "trust": 80,
        "scans": 9,
        "max_casualties": 1,
        "interference_strength": 0.06,
        "danger_probs": [
            [0.00, 0.16, 0.24, 0.30, 0.40, 0.34, 0.28, 0.22],
            [0.18, 0.26, 0.36, 0.48, 0.58, 0.46, 0.36, 0.28],
            [0.22, 0.32, 0.46, 0.60, 0.66, 0.56, 0.42, 0.32],
            [0.24, 0.36, 0.50, 0.64, 0.70, 0.60, 0.48, 0.36],
            [0.22, 0.32, 0.44, 0.56, 0.64, 0.66, 0.54, 0.40],
            [0.20, 0.28, 0.38, 0.46, 0.56, 0.62, 0.52, 0.36],
            [0.18, 0.24, 0.30, 0.38, 0.46, 0.52, 0.44, 0.30],
            [0.14, 0.18, 0.24, 0.28, 0.34, 0.38, 0.28, 0.00],
        ],
        "entangled_pairs": [((1, 1), (3, 5)), ((2, 6), (6, 2)), ((4, 1), (5, 6)), ((0, 6), (7, 1))],
    },
]
