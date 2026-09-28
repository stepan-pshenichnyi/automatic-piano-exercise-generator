import random
from .keys import KEY_SETTINGS, SCALE_PATTERNS


GRADE3_DYAD_RULES = {

    # Melody is the root
    "root": {
        "targets": ["third", "fifth"],
        "weights": [0.80, 0.20]
    },

    # Melody is the third
    "third": {
        "targets": ["root", "fifth"],
        "weights": [0.50, 0.50]
    },

    # Melody is the fifth
    "fifth": {
        "targets": ["third", "root"],
        "weights": [0.80, 0.20]
    }

}

GRADE3_LH_PATTERNS = {

    4: [

        # Grade 2 pattern
        [
            ("R", 1.0),
            ("F", 1.0),
            ("T", 1.0),
            ("F", 1.0)
        ],

        # Broken chord
        [
            ("R", 1.0),
            ("T", 1.0),
            ("F", 1.0),
            ("T", 1.0)
        ],

        # Dyad on beat 3
        [
            ("R", 1.0),
            ("F", 1.0),
            (("T", "F"), 2.0)
        ],

        # Dyads on beats 1 and 3
        [
            (("R", "F"), 1.0),
            ("T", 1.0),
            (("R", "F"), 2.0)
        ]
    ],

    3: [

        [
            ("R", 1.0),
            ("T", 1.0),
            ("F", 1.0)
        ],

        [
            (("R", "F"), 1.0),
            ("T", 1.0),
            ("F", 1.0)
        ]
    ],

    2: [

        [
            ("R", 1.0),
            ("F", 1.0)
        ],

        [
            (("R", "F"), 2.0)
        ]
    ],
    
    1.5: [

        [
            ("R", 0.5),
            ("F", 0.5),
            ("T", 0.5)
        ],

        [
            ("R", 1.0),
            ("F", 0.5)
        ],

        [
            ("R", 0.5),
            (("T", "F"), 1.0)
        ],

        [
            (("R", "F"), 1.5)
        ]
    ]
}

PROGRESSION_LIBRARY = {
    "major": {
        4: [
            [1, 6, 2, 5],
            [1, 4, 5, 1],
            [1, 2, 5, 1],
        ],
        6: [
            [1, 1, 4, 5, 2, 1],
            [1, 6, 4, 5, 1, 1],
        ]
    },
    "minor": {
        4: [
            [1, 4, 5, 1],
            [1, 6, 5, 1],
            [1, 2, 5, 1],
        ],
        6: [
            [1, 4, 6, 5, 1, 1],
            [1, 6, 4, 5, 1, 1],
        ]
    }
}

def nearest_note_with_pc(pc, low, high, target):
    candidates = [n for n in range(low, high + 1) if n % 12 == pc]
    if not candidates:
        return target
    return min(candidates, key=lambda n: abs(n - target))


def realize_lh_pattern(pattern, chord):

    root, third, fifth = chord

    mapping = {
        "R": root - 12,
        "T": third - 12,
        "F": fifth - 12
    }
    realized = []

    for symbol, dur in pattern:
        if isinstance(symbol, tuple):
            realized.append((tuple(mapping[s] for s in symbol), dur))

        else:
            realized.append((mapping[symbol], dur))

    return realized

def build_grade3_dyad(
    melody_pitch,
    current_chord,
    low,
    high
):
    """
    Given a melody note and the current chord,
    return a second note to form a Grade 3 dyad.

    Returns None if the melody note is not
    part of the current harmony.
    """

    root, third, fifth = current_chord

    chord = {
        "root": root,
        "third": third,
        "fifth": fifth
    }

    melody_pc = melody_pitch % 12

    degree_map = {
        root % 12: "root",
        third % 12: "third",
        fifth % 12: "fifth"
    }

    melody_degree = degree_map.get(melody_pc)

    if melody_degree is None:
        return None

    rule = GRADE3_DYAD_RULES[melody_degree]

    candidates = [
        nearest_note_with_pc(
            chord[target] % 12,
            low,
            high,
            melody_pitch
        )
        for target in rule["targets"]
    ]

    return random.choices(
        candidates,
        weights=rule["weights"],
        k=1
    )[0]

def build_diatonic_chord(tonic_midi, scale_type, degree, low=48, high=64):
    scale = SCALE_PATTERNS[scale_type]
    idx = (degree - 1) % 7

    pcs = [
        (tonic_midi + scale[idx]) % 12,
        (tonic_midi + scale[(idx + 2) % 7]) % 12,
        (tonic_midi + scale[(idx + 4) % 7]) % 12,
    ]

    targets = [low + 2, low + 6, low + 10]
    return [nearest_note_with_pc(pc, low, high, target) for pc, target in zip(pcs, targets)]





def generate_harmonic_plan(key_name, bars):
    settings = KEY_SETTINGS[key_name]
    mode = "minor" if "minor" in key_name else "major"
    degree_plan = random.choice(PROGRESSION_LIBRARY[mode].get(bars, [[1] * bars]))
    #print(f"generate_harmonic_plan: degree_plan: {degree_plan}")

    return [
        build_diatonic_chord(
            settings["tonic_midi"],
            settings["scale_type"],
            degree
        )
        for degree in degree_plan
    ]


def realize_lh_from_chord(chord, beats):
    root, third, fifth = chord

    # very simple grade-2 accompaniment
    if beats == 2:
        return [(root - 12, 1.0), (fifth - 12, 1.0)]
    if beats == 3:
        return [(root - 12, 1.0), (third - 12, 1.0), (fifth - 12, 1.0)]

    return [
        (root - 12, 1.0),
        (fifth - 12, 1.0),
        (third - 12, 1.0),
        (fifth - 12, 1.0),
    ]



def realize_lh_grade3_from_chord(chord, beats):

    patterns = GRADE3_LH_PATTERNS.get(beats)

    if patterns is None:
        raise ValueError(
            f"No Grade 3 LH patterns for beats={beats}"
        )

    pattern = random.choice(patterns)

    return realize_lh_pattern(pattern, chord)


def rh_is_one_note(exercise):
    pitches = set()

    for bar in exercise["RH"]:
        for note_data in bar:
            pitch = note_data[0]

            if pitch == "rest":
                continue

            pitches.add(pitch)

    # don't reject exercises with no RH notes
    if not pitches:
        return False

    return len(pitches) == 1


def lh_is_one_note(exercise):
    pitches = set()

    for bar in exercise["LH"]:
        for note_data in bar:
            pitch = note_data[0]

            if pitch == "rest":
                continue

            pitches.add(pitch)

    # don't reject exercises with no LH notes
    if not pitches:
        return False

    return len(pitches) == 1
