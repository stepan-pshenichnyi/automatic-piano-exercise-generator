import random

SCALE_PATTERNS = { #semitone distances from the tonic
    "major": [0, 2, 4, 5, 7, 9, 11],
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11]
} 


RH_POSITIONS = {
    "C_major": [60, 62, 64, 65, 67],  # C D E F G
    "D_minor": [62, 64, 65, 67, 69]   # D E F G A
}


def build_scale(tonic_midi, scale_type, octaves=3):

    intervals = SCALE_PATTERNS[scale_type]

    notes = set()

    for o in range(-1, octaves):
        for i in intervals:
            notes.add(tonic_midi + i + 12*o)

    return notes

def build_triad(tonic_midi, scale_type): #builds tonic triad
    scale = sorted(build_scale(tonic_midi, scale_type))
    return [scale[0], scale[2], scale[4]]

def build_key_settings(tonic_midi, scale_type, music21_name):
    notes = build_scale(tonic_midi, scale_type)
    triad = build_triad(tonic_midi, scale_type)

    return {
        "notes": notes,
        "start": triad,
        "music21_key": music21_name,
        "scale_type": scale_type,
        "tonic_midi": tonic_midi
    }

KEY_SETTINGS = {

    #initial
    "C_major": build_key_settings(60,"major",("C","major")),
    "D_minor": build_key_settings(62,"natural_minor",("D","minor")),

    #grade1
    "G_major": build_key_settings(67,"major",("G","major")),
    "F_major": build_key_settings(65,"major",("F","major")),
    "A_minor": build_key_settings(69,"natural_minor",("A","minor")),

    #grade2
    "D_major": build_key_settings(62, "major", ("D", "major")), #new
    "E_minor": build_key_settings(64, "harmonic_minor", ("E", "minor")), #new
    "G_minor": build_key_settings(67, "harmonic_minor", ("G", "minor")), #new


    #grade3
    "B_flat_major": build_key_settings(70, "major", ("B-", "major")),
    "E_flat_major": build_key_settings(63, "major", ("E-", "major")),
    "B_minor": build_key_settings(71, "harmonic_minor", ("B", "minor")),


}

def build_extended_position(tonic_midi, scale_type, width=7): #Extended position for grades 3+

    scale = sorted(build_scale(tonic_midi, scale_type))

    start = random.randint(0, len(scale) - width)

    return scale[start:start + width]

def build_five_finger_position(tonic_midi, scale_type):
    scale = sorted(build_scale(tonic_midi, scale_type))

    # choose 5 consecutive scale notes
    start = random.randint(0, len(scale) - 5)

    return scale[start:start + 5]


