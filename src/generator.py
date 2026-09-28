import random
from collections import Counter
import pickle

from .expressions import sample_expression
from .rhythm import get_valid_rhythms, sample_distinct_rhythms, build_rhythm_plan, rest_probability, balance_bar, split_bar_by_duration, get_pickup_candidates
from .hands import sample_hand_pattern, generate_hand_pattern, build_lh_bar
from .config import GRADE_SETTINGS, DIFFICULTY_PROFILES, TIME_SIGNATURE_BEATS
from .keys import (KEY_SETTINGS,
    RH_POSITIONS,
    build_five_finger_position,
    build_extended_position,
    build_scale
)
from .harmony import generate_harmonic_plan, realize_lh_grade3_from_chord, realize_lh_from_chord, rh_is_one_note, lh_is_one_note
from .renderer import assign_offsets
from .melody import decorate_bar_with_two_note_chords, bar_is_repetitive, generate_bar
from .articulations import assign_motif_articulations

with open('data/expressive_marks_grade1.pkl', 'rb') as f:
    expressive_dict = pickle.load(f)

def sample_grade_parameters(grade):

    settings = GRADE_SETTINGS[grade]

    structure = random.choice(settings["structures"])

    difficulty = DIFFICULTY_PROFILES[grade]

    params = {
        "bars": structure["bars"],
        "time_signature": structure["time_signature"],
        "key": random.choice(settings["keys"]),
        "position": settings["position"],
        "max_interval": difficulty["max_interval"],
        "allowed_durations": difficulty["allowed_durations"]
    }

    # Initial grade uses one hand only
    if grade == "initial":
        params["hand"] = random.choice(["RH", "LH"])

    return params

def choose_position(params, settings):

    if params["position"] == "5_finger":
        return RH_POSITIONS[params["key"]]

    if params["position"] == "any_5_finger":
        return build_five_finger_position(
            settings["tonic_midi"],
            settings["scale_type"]
        )
    
    if params["position"] == "extended":
        return build_extended_position(
            settings["tonic_midi"],
            settings["scale_type"]
        )


def generate_exercise(pitch_markov_prob, rhythm_dict, grade="initial"):

    params = sample_grade_parameters(grade)
    params["grade"] = grade

    # anacrusis

    params["pickup"] = None

    if grade == 4 and random.random() < 0.25:
        if params["time_signature"] == "6/8":
            params["pickup"] = random.choice([0.5, 1.0, 1.5])
        else:
            params["pickup"] = random.choice([0.5, 1.0])


    dynamic, expression = sample_expression(expressive_dict)

    bars = params["bars"]
    time_signature = params["time_signature"]
    key_name = params["key"]
    params["dynamic"] = dynamic
    params["expression"] = expression
    params["bar_articulations"] = []

    difficulty = DIFFICULTY_PROFILES[grade]
    settings = KEY_SETTINGS[key_name]

    tonic_midi = settings["tonic_midi"]
    scale_type = settings["scale_type"]

    prev_lh_note = None

    # Hand selection
    # Hand pattern
    if grade == "initial":
        hand = random.choice(["R", "L"])
        hand_pattern = [hand] * bars
    elif grade == 1:
        hand_pattern = sample_hand_pattern(time_signature, bars)
    elif grade >= 3:
        hand_pattern = generate_hand_pattern(bars, grade=3)
    else:
        hand_pattern = generate_hand_pattern(bars)   

    #print("Hand pattern:", hand_pattern)

    # Valid rhythms
    valid_rhythms = get_valid_rhythms(
        rhythm_dict,
        time_signature,
        difficulty
    )

    if not valid_rhythms:
        raise ValueError("No valid rhythms for this grade/time signature")

    # Make 3/8 more flowing. 3/8 melodies usually benefit from more motion and fewer long notes.
    if time_signature == "3/8":
        valid_rhythms = {
            p: c * (1.5 if len(p) >= 3 else 1.0) #if three or more notes in the pattern, the prob is multiplied by 1.5
            for p, c in valid_rhythms.items()
        }

    # Motifs
    motif_A, motif_B, motif_C = sample_distinct_rhythms(valid_rhythms)


    motif_articulations = assign_motif_articulations(
        [motif_A, motif_B, motif_C],
        grade
    )

    rhythm_plan = build_rhythm_plan(
        bars,
        motif_A,
        motif_B,
        motif_C,
        valid_rhythms
    )

    #print("rhythm_plan:", rhythm_plan)

    # Optional rest
    include_rest = (
        grade == "initial"
        and random.random() < rest_probability(bars)
    )

    rest_bar = None
    if include_rest and bars > 2:
        rest_bar = random.randint(2, bars - 1)

    exercise = {}

    exercise = {"RH": [], "LH": []}
    previous_melody_bar = None

    position_notes = choose_position(params, settings)

    #print(f"generate_exercise: position_notes:{position_notes}")

    low, high = difficulty["staff_limits"]["RH"]

    filtered_notes = [
        n for n in position_notes
        if low <= n <= high
    ]

    if not filtered_notes:
        filtered_notes = position_notes

    scale_pcs = {n % 12 for n in build_scale(tonic_midi, scale_type)}

    full_scale_notes = [
        n for n in range(low, high + 1)
        if (n % 12) in scale_pcs
    ]

    if grade == "initial":
        allowed_notes = filtered_notes

    elif grade in (1, 2):
        allowed_notes = filtered_notes

    elif grade >= 3:
        allowed_notes = full_scale_notes

    #print(f"generate_exercise: allowed_notes:{allowed_notes}")

    scale_pcs = {n % 12 for n in build_scale(tonic_midi, scale_type)}
    full_scale_notes = [n for n in range(low, high + 1) if (n % 12) in scale_pcs]


    start_notes = [position_notes[0], position_notes[2], position_notes[4]]
    cadences = {bars: position_notes[0]}

    if isinstance(grade, int) and grade >= 2:
        harmonic_plan = generate_harmonic_plan(key_name, bars)
        #print(f"generate_exercise: harmonic_plan: {harmonic_plan}")
        cadences = {bars: settings["tonic_midi"]}

    prev_note = random.choices(
        start_notes,
        weights=[3,1,1]
    )[0]

    highest_note = prev_note

    # ---- add a global pitch usage counter to avoid collapse to one pitch ----
    pitch_counter = Counter()

    #anacrusis

    pickup_rhythm = None
    ending_rhythm = None

    if params["pickup"] is not None:

        candidates = get_pickup_candidates(
            rhythm_dict,
            time_signature,
            params["pickup"],
            difficulty
        )

        if not candidates:
            raise ValueError(
                f"No pickup candidates for {time_signature} "
                f"with pickup {params['pickup']}"
            )

        pickup_rhythm, ending_rhythm, _ = random.choices(
            candidates,
            weights=[c[2] for c in candidates],
            k=1
        )[0]

    
    for bar_number in range(1, bars + 1):

        beats = TIME_SIGNATURE_BEATS[time_signature]
        if (
            params["pickup"] is not None
            and bar_number == 1
        ):
            current_beats = params["pickup"]

        elif (
            params["pickup"] is not None
            and bar_number == bars
        ):
            current_beats = beats - params["pickup"]

        else:
            current_beats = beats

        #anacrusis

        if params["pickup"] is not None:
            
            if bar_number == 1:
                rhythm = pickup_rhythm

            elif bar_number == bars:
                rhythm = ending_rhythm

            else:
                rhythm = rhythm_plan[bar_number - 1]
                bar_articulation = motif_articulations.get(rhythm)
                params["bar_articulations"].append(bar_articulation)

        else:
            rhythm = (
                motif_A
                if bar_number == bars
                else rhythm_plan[bar_number - 1]
            )

            bar_articulation = motif_articulations.get(rhythm)
            params["bar_articulations"].append(bar_articulation)



        max_attempts = 6
        for attempt in range(max_attempts):
            #print(f"bar {bar_number}, attemt number {attempt}")

            current_chord = (
                harmonic_plan[bar_number - 1]
                if isinstance(grade, int) and grade >= 2
                else None
            )
            current_chord_pcs = {n % 12 for n in current_chord} if current_chord else None

           #print(f"bar_number = {bar_number}")
           #print(f"rhythm = {rhythm}")
           #print(f"type(rhythm) = {type(rhythm)}")
           #print(f"rhythm_plan = {rhythm_plan}")

            bar, new_prev, new_highest = generate_bar(
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
                current_chord_pcs=current_chord_pcs
            )

            if not (
                previous_melody_bar
                and bar_is_repetitive(previous_melody_bar)
                and bar_is_repetitive(bar)
            ):
                break
        
        prev_note = new_prev
        highest_note = new_highest
        previous_melody_bar = bar

        beats = TIME_SIGNATURE_BEATS[time_signature] #replaced int(time_signature.split("/")[0])

        if grade == 2:
            rh_bar = balance_bar(bar, current_beats)
            lh_bar = realize_lh_from_chord(
                harmonic_plan[bar_number - 1],
                beats
            )

            exercise["RH"].append(rh_bar)
            exercise["LH"].append(balance_bar(lh_bar, current_beats))

        elif isinstance(grade, int) and grade >= 3:
            rh_bar = balance_bar(bar, current_beats)
            rh_bar = decorate_bar_with_two_note_chords(
                rh_bar,
                harmonic_plan[bar_number - 1],
                *difficulty["staff_limits"]["RH"],
                prob=0.15
            )
            
            if params["pickup"] is not None:

                if bar_number == 1:
                    # LH rests during pickup
                    lh_bar = [
                        ("rest", current_beats)
                    ]

                elif bar_number == bars:
                    # Sustain bass note only
                    root, _, _ = harmonic_plan[bar_number - 1]

                    lh_bar = [
                        (root - 12, current_beats)
                    ]

                else:
                    lh_bar = realize_lh_grade3_from_chord(
                        harmonic_plan[bar_number - 1],
                        beats
                    )

            else:
                lh_bar = realize_lh_grade3_from_chord(
                    harmonic_plan[bar_number - 1],
                    beats
                )

            exercise["RH"].append(rh_bar)
            exercise["LH"].append(balance_bar(lh_bar, current_beats))


        else:
            # ORIGINAL Initial / Grade 1 logic

            pattern = hand_pattern[bar_number - 1]
            rest_bar = [("rest", beats)]

            if pattern == "R":
                exercise["RH"].append(balance_bar(bar, beats))
                exercise["LH"].append(rest_bar)

            elif pattern == "L":
                lh_bar, prev_lh_note = build_lh_bar(
                    bar,
                    prev_lh_note,
                    difficulty
                )

                exercise["RH"].append(rest_bar)
                exercise["LH"].append(balance_bar(lh_bar, current_beats))

            elif pattern == "LR":
                first, second = split_bar_by_duration(
                    bar,
                    beats / 2
                )

                lh_bar, prev_lh_note = build_lh_bar(
                    first,
                    prev_lh_note,
                    difficulty
                )

                rh_bar = second

                lh_bar = assign_offsets(lh_bar, 0)
                rh_bar = assign_offsets(rh_bar, beats / 2)

                exercise["RH"].append(rh_bar)
                exercise["LH"].append(lh_bar)

            elif pattern == "RL":
                first, second = split_bar_by_duration(
                    bar,
                    beats / 2
                )

                rh_bar = first

                lh_bar, prev_lh_note = build_lh_bar(
                    second,
                    prev_lh_note,
                    difficulty
                )

                rh_bar = assign_offsets(rh_bar, 0)
                lh_bar = assign_offsets(lh_bar, beats / 2)

                exercise["RH"].append(balance_bar(rh_bar, beats))
                exercise["LH"].append(balance_bar(lh_bar, current_beats))
            

    #print('Printin exercise["RH"][0]:', exercise["RH"][0])
    #print('Printin exercise["RH"][1]:', exercise["RH"][1])

    if (
        grade == 1
        and rh_is_one_note(exercise)
        and lh_is_one_note(exercise)
    ):
        return generate_exercise(
            pitch_markov_prob,
            rhythm_dict,
            grade
        )
    
    elif (
        grade == 2
        and rh_is_one_note(exercise)
    ):
        return generate_exercise(
            pitch_markov_prob,
            rhythm_dict,
            grade
        )

    return exercise, params
