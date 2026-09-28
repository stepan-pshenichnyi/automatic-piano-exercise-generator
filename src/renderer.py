import random

from music21 import stream, note, meter, key, clef, dynamics, expressions, layout, spanner, bar
from music21 import chord as m21chord
from .keys import KEY_SETTINGS
from .articulations import ARTICULATION_PROBABILITIES, ARTICULATION_FUNCTIONS

def assign_offsets(bar, start_offset=0):

    new_bar = []
    current_offset = start_offset

    for pitch, dur in bar:
        new_bar.append((pitch, dur, current_offset))
        current_offset += dur

    return new_bar

def render_exercise(exercise, params):

    key_name = params["key"]
    time_signature = params["time_signature"]

    settings = KEY_SETTINGS[key_name]
    tonic, mode = settings["music21_key"]

    score = stream.Score()

    for hand, bars in exercise.items():

        part = stream.Part()
      

        for i, bar_data in enumerate(bars):

            m = stream.Measure(number=i + 1)

            # ----- First measure setup -----
            if i == 0:

                if hand == "RH":
                    m.insert(0, clef.TrebleClef())
                else:
                    m.insert(0, clef.BassClef())

                m.insert(0, key.Key(tonic, mode))
                m.insert(0, meter.TimeSignature(time_signature))

                if hand == "RH":
                    dyn = dynamics.Dynamic(params["dynamic"])

                    expr = expressions.TextExpression(
                        params["expression"]
                    )
                    expr.placement = "above"

                    m.insert(0, dyn)
                    m.insert(0, expr)

            # ----- Notes -----
            for note_index, note_data in enumerate(bar_data):

                if len(note_data) == 3:
                    pitch, dur, offset = note_data
                else:
                    pitch, dur = note_data
                    offset = None

                if pitch == "rest":
                    n = note.Rest()

                elif isinstance(pitch, (tuple, list)):
                    n = m21chord.Chord(list(pitch))

                else:
                    n = note.Note()
                    n.pitch.midi = pitch

                n.quarterLength = dur

               

                # grade = params["grade"]

                # probs = ARTICULATION_PROBABILITIES[grade]

                # if not isinstance(n, note.Rest):

                #     if (dur in (0.5, 1.0) and random.random() < probs["staccato"]):
                #         n.articulations.append(articulations.Staccato())
                #     elif grade in (1, 2, 3, 4) and dur >= 1.0 and random.random() < probs["accent"]:
                #         n.articulations.append(articulations.Accent())
                #     elif grade == 4 and  dur >= 1.0 and random.random() < probs["tenuto"]:
                #         n.articulations.append(articulations.Tenuto())

        
        

                if offset is None:
                    m.append(n)
                else:
                    m.insert(offset, n)

            if (
                i == 0
                and params.get("pickup") is not None
            ):
                m.padAsAnacrusis()

            part.append(m)
    
        part.makeNotation(inPlace=True)

        for ch in part.recurse().getElementsByClass(m21chord.Chord):
            for n in ch.notes:
                acc = n.pitch.accidental
                if acc is not None and acc.name == "natural":
                    n.pitch.accidental = None


        if hand == "RH":

            for measure_idx, measure in enumerate(
                part.getElementsByClass(stream.Measure)
            ):

                if measure_idx >= len(params["bar_articulations"]):
                    continue

                articulation = params["bar_articulations"][measure_idx]

                if articulation is None:
                    continue

                notes = list(
                    measure.recurse().getElementsByClass(
                        (note.Note, m21chord.Chord)
                    )
                )

                func = ARTICULATION_FUNCTIONS.get(articulation)

                if func:
                    func(notes)

        grade = params["grade"]
        probs = ARTICULATION_PROBABILITIES[grade]

        if grade in (1, 2, 3, 4):

            notes = [
                n
                for n in part.recurse().notes
                if isinstance(n, note.Note)
            ]

            if len(notes) >= 4 and random.random() < probs["slur"]:

                start = random.randint(
                    0,
                    len(notes)-4
                )

                end = min(
                    start + random.randint(2,5),
                    len(notes)-1
                )

                sl = spanner.Slur(
                    notes[start:end+1]
                )

                part.insert(0, sl)

        #fermata
        if grade == 4:

            notes = list(part.recurse().notes)

            if notes and random.random() < probs["fermata"]:

                notes[-1].expressions.append(
                    expressions.Fermata()
                )

        #cresc/dim (hairpin)

        if grade in (1,2,3,4):

            notes = list(part.recurse().notes)

            if len(notes) >= 6 and random.random() < probs["hairpin"]:

                start = random.randint(
                    0,
                    len(notes)-5
                )

                end = min(
                    start+4,
                    len(notes)-1
                )

                if random.random() < 0.5:
                    hp = dynamics.Crescendo()
                else:
                    hp = dynamics.Diminuendo()

                hp.addSpannedElements(notes[start:end+1])
                part.insert(0, hp)
                
        last_measure = part.getElementsByClass(stream.Measure).last()
        if last_measure is not None:
            last_measure.rightBarline = bar.Barline("final")
        score.append(part)

    score.insert(
        0,
        layout.StaffGroup(
            score.parts,
            symbol="brace"
        )
    )

    score.show()