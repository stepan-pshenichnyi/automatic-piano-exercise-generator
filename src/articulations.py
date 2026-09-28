import random
from music21 import articulations

ARTICULATION_WEIGHTS = {
    "initial": [0.90, 0.10, 0.00, 0.00],
    1:         [0.75, 0.20, 0.05, 0.00],
    2:         [0.65, 0.25, 0.10, 0.00],
    3:         [0.55, 0.30, 0.10, 0.05],
    4:         [0.45, 0.35, 0.10, 0.10],
}

ARTICULATIONS = [
    None,
    "staccato",
    "accent",
    "tenuto"
]

def assign_motif_articulations(motifs, grade):
    weights = ARTICULATION_WEIGHTS[grade]

    return {
        motif: random.choices(
            ARTICULATIONS,
            weights=weights,
            k=1
        )[0]
        for motif in motifs
    }


def apply_staccato(notes):

    eligible = [
        n
        for n in notes
        if 0.5 <= n.quarterLength <= 1.0
    ]

    if len(eligible) <= 4:
        targets = eligible
    else:
        targets = eligible[:4]

    for n in targets:
        n.articulations.append(
            articulations.Staccato()
        )

def apply_accent(notes):

    if not notes:
        return

    target = max(
        notes,
        key=lambda n: (
            n.beatStrength,
            n.quarterLength
        )
    )

    target.articulations.append(
        articulations.Accent()
    )

def apply_tenuto(notes):

    eligible = [
        n
        for n in notes
        if n.quarterLength >= 1
    ]

    if eligible:
        eligible[0].articulations.append(
            articulations.Tenuto()
        )

ARTICULATION_FUNCTIONS = {
    "staccato": apply_staccato,
    "accent": apply_accent,
    "tenuto": apply_tenuto,
}

ARTICULATION_PROBABILITIES = {

    "initial": {
        "staccato": 0.10,
        "slur": 0.20,
    },

    1: {
        "staccato": 0.12,
        "slur": 0.25,
        "accent": 0.08,
        "hairpin": 0.15,
    },

    2: {
        "staccato": 0.15,
        "slur": 0.30,
        "accent": 0.10,
        "hairpin": 0.20,
    },

    3: {
        "staccato": 0.18,
        "slur": 0.35,
        "accent": 0.12,
        "hairpin": 0.25,
    },

    4: {
        "staccato": 0.20,
        "slur": 0.40,
        "accent": 0.15,
        "hairpin": 0.30,
        "tenuto": 0.15,
        "fermata": 0.15,
    }
}
