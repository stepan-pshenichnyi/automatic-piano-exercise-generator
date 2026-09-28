import random
import pickle

from .utils import weighted_sample

with open('data/hand_patterns_grade1.pkl', 'rb') as f:
    transition_patterns = pickle.load(f)

def sample_hand_pattern(time_signature, bars):

    ts_patterns = transition_patterns.get(time_signature, {})

    # if bars not in ts_patterns:
    #     raise ValueError("No transition patterns for this structure")

    if bars not in ts_patterns:
        # fallback patterns
        if bars == 8:
            return generate_hand_pattern(bars)

        # fallback for unsupported structures
        return ["R"] * bars

    pattern_dict = ts_patterns[bars]

    pattern = weighted_sample(pattern_dict)

    return list(pattern)

def generate_hand_pattern(bars, grade=None):
    if grade == 3:
        choices = ["R", "L", "LR", "RL", "BOTH"]
        weights = [0.22, 0.22, 0.18, 0.18, 0.20]
        return random.choices(choices, weights=weights, k=bars)

    rule = random.random()

    if rule < 0.50:
        hand = random.choice(["R", "L"])
        pattern = [hand] * bars

    elif rule < 0.80:
        first = random.choice(["R", "L"])
        second = "L" if first == "R" else "R"
        split = bars // 2
        pattern = [first] * split + [second] * (bars - split)

    elif rule < 0.95:
        first = random.choice(["R", "L"])
        second = "L" if first == "R" else "R"
        switch_bar = random.randint(max(1, bars - 2), bars - 1)
        pattern = [first] * switch_bar + [second] * (bars - switch_bar)

    else:
        first = random.choice(["R", "L"])
        second = "L" if first == "R" else "R"
        pattern = [first if i % 2 == 0 else second for i in range(bars)]

    return pattern

def build_lh_bar(bar, prev_lh_note, difficulty):

    low, high = difficulty["staff_limits"]["LH"]
    max_interval = difficulty["max_interval"]

    new_bar = []

    for pitch, dur in bar:

        if pitch == "rest":
            new_bar.append(("rest", dur))
            continue

        p = transpose_to_lh_range(pitch)

        # constrain LH motion
        if prev_lh_note is not None:
            if abs(p - prev_lh_note) > max_interval:
                # pull toward previous note
                direction = 1 if p > prev_lh_note else -1
                p = prev_lh_note + direction * max_interval

        # clamp to staff
        p = max(low, min(high, p))

        new_bar.append((p, dur))
        prev_lh_note = p

    return new_bar, prev_lh_note

def transpose_to_lh_range(pitch):

    if pitch == "rest":
        return pitch

    while pitch >= 60:
        pitch -= 12

    return pitch