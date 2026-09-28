from .config import TIME_SIGNATURE_BEATS
from .utils import weighted_sample, normalize

def is_valid_rhythm(pattern, beats_per_bar, difficulty):

    if abs(sum(pattern) - beats_per_bar) > 1e-6:
        return False

    allowed = difficulty["allowed_durations"]

    return all(d in allowed for d in pattern)

def get_valid_rhythms(rhythm_dict, time_signature, difficulty):

    beats = TIME_SIGNATURE_BEATS[time_signature] #replaced int(time_signature.split("/")[0])

    patterns = rhythm_dict.get(time_signature, {})

    # for p, c in patterns.items():
    #     if is_valid_rhythm(p, beats, difficulty):
    #        #print(p, c)

    return {
        p: c
        for p, c in patterns.items()
        if is_valid_rhythm(p, beats, difficulty)
    }

def sample_rhythm(initial_rhythms):
    probs = normalize(initial_rhythms)
    return weighted_sample(probs)

def get_rhythms_of_length(
    rhythm_dict,
    time_signature,
    target_length,
    difficulty
):

    valid = get_valid_rhythms(
        rhythm_dict,
        time_signature,
        difficulty
    )

    return {
        p: c
        for p, c in valid.items()
        if abs(sum(p) - target_length) < 1e-6
    }

def sample_distinct_rhythms(valid_rhythms):

    A = sample_rhythm(valid_rhythms)

    B = A
    while B == A:
        B = sample_rhythm(valid_rhythms)

    C = A
    while C in (A, B):
        C = sample_rhythm(valid_rhythms)

    return A, B, C

def build_rhythm_plan(bars, A, B, C, valid_rhythms): #musical repetition and structure


    if bars == 4:
        return [A, A, B, A]

    if bars == 6:
        return [A, A, B, B, A, C]

    return [sample_rhythm(valid_rhythms) for _ in range(bars)]

def rest_probability(bars):
    if bars == 4:
        return 0.20   # 20% chance
    if bars == 6:
        return 0.30   # 30% chance
    return 0.20

def split_bar_by_duration(bar, split_point):

    first = []
    second = []

    duration_sum = 0

    for pitch, dur in bar:

        if duration_sum + dur <= split_point:
            first.append((pitch, dur))
        else:
            second.append((pitch, dur))

        duration_sum += dur

    return first, second

def balance_bar(bar, beats):

    # support both (p, d) and (p, d, offset)
    total = sum(note_data[1] for note_data in bar)

    if total >= beats:
        return bar

    missing = beats - total

    # preserve structure (2-tuple or 3-tuple)
    if bar and len(bar[0]) == 3:
        bar.append(("rest", missing, total))
    else:
        bar.append(("rest", missing))

    return bar


def split_rhythm(full_rhythm, pickup_length):
    """
    Split a rhythm pattern into
    pickup + ending.
    """

    total = 0.0
    split = 0

    for i, dur in enumerate(full_rhythm):
        total += dur

        if abs(total - pickup_length) < 1e-6:
            split = i + 1
            break

        elif total > pickup_length:
            return None

    return (
        full_rhythm[:split],
        full_rhythm[split:]
    )

def get_pickup_candidates(
    rhythm_dict,
    time_signature,
    pickup_length,
    difficulty
):
    valid = get_valid_rhythms(
        rhythm_dict,
        time_signature,
        difficulty
    )

    candidates = []

    for rhythm, weight in valid.items():

        result = split_rhythm(
            rhythm,
            pickup_length
        )

        if result is not None:
            pickup, ending = result

            candidates.append(
                (
                    pickup,
                    ending,
                    weight
                )
            )

    return candidates
