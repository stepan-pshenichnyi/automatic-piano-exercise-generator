import random
import numpy as np

from .config import DIFFICULTY_PROFILES
from .keys import KEY_SETTINGS

from .utils import normalize, weighted_sample
from .harmony import build_grade3_dyad

def phrase_direction(bar_number, bars):

    if bars == 4:
        if bar_number == 1:
            return "up"

        if bar_number == 2:
            return "peak"

        if bar_number == 3:
            return "down"

        return "cadence"

    if bars == 6:
        if bar_number in [1, 4]:
            return "up"

        if bar_number in [2, 5]:
            return "peak"

        if bar_number == 3:
            return "down"

        return "cadence"

    return "neutral"

def pedagogical_bias(prev_note, candidates, bar_number, bars, highest_note, difficulty, i, recent_notes, key_settings):

    step_bias = difficulty["step_bias"]
    leap_penalty = difficulty["leap_penalty"]
    preferred = difficulty["preferred_interval"]
    tonic_midi = key_settings["tonic_midi"]

    for nxt in list(candidates.keys()):

        interval = abs(nxt - prev_note)

        #discourage repeated notes
        if len(recent_notes) >= 2:
            if recent_notes[-1] == recent_notes[-2] == nxt:
                candidates[nxt] *= 0.1

        # # encourage motion at the start of a bar
        # if i == 0 and nxt != prev_note:
        #     candidates[nxt] *= 1.3

        # discourage repeating the same note
        if nxt == prev_note:
            candidates[nxt] *= 0.5

        # encourage stepwise motion
        if interval <= preferred:
            candidates[nxt] *= (step_bias * 1.3)

        if bar_number == bars: #last bar
            # strong tonic pull at end
            if nxt == tonic_midi:
                candidates[nxt] *= 3

        # discourage big jumps
        elif interval >= preferred + 2:
            candidates[nxt] *= leap_penalty

        # phrase direction
        direction = phrase_direction(bar_number, bars)

        if direction == "up" and nxt > prev_note:
            candidates[nxt] *= 1.4

        if direction == "down" and nxt < prev_note:
            candidates[nxt] *= 1.4

        if direction == "peak" and nxt > prev_note:
            candidates[nxt] *= 1.2

        if direction == "cadence" and nxt < prev_note:
            candidates[nxt] *= 1.5

        # discourage repeating the highest note
        if prev_note == highest_note and nxt >= prev_note:
            candidates[nxt] *= 0.3

    return candidates

def constrained_transitions(prev_note, pitch_markov_prob, allowed_notes, difficulty):

    raw = pitch_markov_prob.get(prev_note, {})
    filtered = {}

    max_interval = difficulty["max_interval"]
    #print(f"constrained_transitions: max_interval = {max_interval}")
    #print(f"constrained_transitions: allowed_notes = {allowed_notes}")

    for nxt, prob in raw.items():

        if nxt not in allowed_notes:
            continue

        interval = abs(nxt - prev_note)

        if interval > max_interval:
            continue

        #soft constraint instead of hard jump rejection
        weight = 1 / (1 + interval)

        filtered[nxt] = prob * weight
    
    #print(f"constrained_transitions: filtered after loop:{filtered}")

    # fallback 1
    if not filtered:
        #print("constrained_transitions: fallback 1")
        filtered = {
            n: prob for n, prob in raw.items()
            if n in allowed_notes
        }

    # fallback 2 (guarantee non-empty)
    if not filtered:
        #print("constrained_transitions: fallback 2")
        filtered = {n: 1 for n in allowed_notes}

    return filtered

def decorate_with_chromatic_notes(
    bar,
    allowed_scale_pcs,
    probability=0.08
):
    new_bar = []

    for pitch, dur in bar:

        if pitch == "rest":
            new_bar.append((pitch, dur))
            continue

        if isinstance(pitch, tuple):
            new_bar.append((pitch, dur))
            continue

        if random.random() > probability:
            new_bar.append((pitch, dur))
            continue

        direction = random.choice([-1, 1])
        candidate = pitch + direction

        # only if candidate is outside the scale
        if candidate % 12 not in allowed_scale_pcs:
            new_bar.append((candidate, dur))
        else:
            new_bar.append((pitch, dur))

    return new_bar

def decorate_bar_with_two_note_chords(
    bar,
    current_chord,
    low,
    high,
    prob=0.15
):

    new_bar = []

    for pitch, dur in bar:

        if pitch == "rest":
            new_bar.append((pitch, dur))
            continue

        if random.random() > prob:
            new_bar.append((pitch, dur))
            continue

        other = build_grade3_dyad(
            pitch,
            current_chord,
            low,
            high
        )

        if other is None:
            new_bar.append((pitch, dur))
        else:
            new_bar.append(
                (tuple(sorted((pitch, other))), dur)
            )

    return new_bar

def bar_is_repetitive(bar):


    pitches = [p for p, d in bar if p != "rest"]

    if len(pitches) <= 1:
        return False

    return len(set(pitches)) == 1


def generate_bar(
    prev_note,
    bar_number,
    bars,
    highest_note,
    rhythm,
    pitch_markov_prob,
    allowed_notes,
    cadences,
    difficulty,
    pitch_counter,
    settings,
    current_chord_pcs=None #new
):

    bar_notes = []
    recent_notes = [prev_note]
    previous_melody_bar = None

    for i, dur in enumerate(rhythm):

        highest_note = max(highest_note, prev_note)

        # Get candidate transitions
        candidates = constrained_transitions(
            prev_note,
            pitch_markov_prob,
            allowed_notes,
            difficulty
        )
        #print(candidates)

        #print(f"candidates after constrained_transitions: {candidates}")


        #Apply pedagogical musical bias
        candidates = pedagogical_bias(
            prev_note,
            candidates,
            bar_number,
            bars,
            highest_note,
            difficulty,
            i,
            recent_notes,
            settings
        )

        #NEW grade 2: melody favors chord tones on strong notes
        is_strong_note = (i == 0 or i == len(rhythm) - 1)

        if current_chord_pcs and is_strong_note:
            for k in list(candidates.keys()):
                if k % 12 in current_chord_pcs:
                    candidates[k] *= 2.0



        total = sum(candidates.values())
        if total > 0:
            candidates = {k: v / total for k, v in candidates.items()}

        #print(f"candidates after pedagogical_bias: {candidates}")
        # Cadence bias on final note of the bar
        is_last_note = (i == len(rhythm) - 1)

        if is_last_note and bar_number in cadences:

            target = cadences[bar_number]

            if isinstance(target, list):
                for t in target:
                    candidates[t] = candidates.get(t, 0) * difficulty["cadence_strength"]
            else:
                candidates[target] = candidates.get(target, 0) * difficulty["cadence_strength"]

        # ----- apply extra anti-collapse penalties (local + global) -----
        # make a copy to mutate weights
        for k in list(candidates.keys()):
            # strongly discourage repeating the same pitch immediately
            if k == prev_note:
                candidates[k] *= 0.25   # stronger than previous 0.5

            # penalize globally overused pitches (reduce probability progressively)
            # threshold controls how quickly a pitch is downweighted;.
            usage = pitch_counter.get(k, 0)
            if usage >= 6:
                # drop weight more aggressively once used a pitch many times
                candidates[k] *= max(0.05, 1.0 - (usage - 5) * 0.15)

        # Normalize after penalties
        candidates = normalize(candidates)


        # Safety fallback or weighted sample
        if not candidates:
            alternatives = [n for n in allowed_notes if n != prev_note]

            if alternatives:
                next_note = min(alternatives, key=lambda x: abs(x - prev_note))
            else:
                next_note = prev_note
        else:
            next_note = weighted_sample(candidates)

        # prevent huge leaps
        if abs(next_note - prev_note) > difficulty["max_interval"]:
            # pull it back toward previous note
            step_options = [
                n for n in allowed_notes
                if abs(n - prev_note) <= difficulty["preferred_interval"]
            ]

            if step_options:
                next_note = min(step_options, key=lambda x: abs(x - prev_note))
            else:
                next_note = prev_note

        low, high = difficulty["staff_limits"]["RH"]
        next_note = max(low, min(high, next_note))          

        # If this pitch is already extremely overused globally, try a nearby alternative
        if pitch_counter.get(next_note, 0) >= 10:
            alternatives = [
                n for n in allowed_notes
                if n != next_note and abs(n - prev_note) <= difficulty["preferred_interval"] + 1
            ]

            if not alternatives:
                alternatives = [
                    n for n in allowed_notes
                    if n != next_note and abs(n - prev_note) <= difficulty["max_interval"]
                ]

            alternatives = sorted(
                alternatives,
                key=lambda x: (pitch_counter.get(x, 0), abs(x - prev_note))
            )
            if alternatives:
                next_note = alternatives[0]

        # record usage
        if next_note != "rest":
            pitch_counter[next_note] += 1

        bar_notes.append((next_note, dur))

        recent_notes.append(next_note)
        if len(recent_notes) > 3:
            recent_notes.pop(0)

        prev_note = next_note

    return bar_notes, prev_note, highest_note
