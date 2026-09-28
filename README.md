# Grade-Conditioned Piano Sight-Reading Exercise Generator

An automatic music generation system that creates piano sight-reading exercises aligned with ABRSM grade levels. The project combines **statistical music modeling** with **rule-based pedagogical constraints** to generate controllable exercises with varying levels of musical difficulty.

## Overview

Sight-reading is an essential musical skill that requires performers to interpret and play unfamiliar notation in real time. Developing this skill relies on regular practice with exercises that are appropriately challenging for the learner.

This project explores the automatic generation of piano sight-reading exercises conditioned on a target difficulty level. Rather than relying exclusively on random generation or purely data-driven models, it adopts a hybrid approach that combines patterns learned from a symbolic music corpus with explicit constraints derived from musical and pedagogical considerations.

The generator models several dimensions of musical difficulty, including:

* **Rhythmic complexity:** the variety and frequency of rhythmic patterns.
* **Melodic intervals:** the size and distribution of pitch transitions.
* **Pitch range:** the register and range of notes used.
* **Hand position:** the positioning and movement requirements for each hand.
* **Hand coordination:** the interaction between right- and left-hand material.
* **Harmonic complexity:** the harmonic progressions and tonal relationships.
* **Chordal texture:** the use of dyads, chords, and other grade-specific features.

The system currently supports grade-conditioned generation up to ABRSM Grade 4.

## Quick Start

The easiest way to generate an exercise is to run one of the example scripts from the project root directory:

```bash
python -m examples.generate_initial
python -m examples.generate_grade_1
python -m examples.generate_grade_2
python -m examples.generate_grade_3
python -m examples.generate_grade_4
```

Each command generates a new piano sight-reading exercise and opens the resulting score in MuseScore.

**Requirements:**

* Python 3.x and the dependencies listed in `requirements.txt`.
* MuseScore installed on your system.

Run the commands from the repository root to ensure that the scripts can locate the source modules and data files correctly.

## Methodology

The generator follows a hybrid statistical and rule-based approach.

### Statistical modeling

Patterns extracted from a symbolic music corpus are used to construct statistical representations of musical material.

A Markov model is employed for melodic generation, using transition probabilities to sample successive pitches based on preceding musical context. Rhythmic patterns are represented through frequency-based dictionaries, allowing the system to sample patterns according to their observed occurrence.

### Pedagogical constraints

Statistical sampling alone does not guarantee that generated material is musically coherent or appropriate for a particular grade. Therefore, the generator incorporates explicit constraints to control the resulting exercises.

These constraints influence aspects such as:

* Permitted pitch ranges and melodic intervals.
* Rhythmic vocabulary and pattern selection.
* Hand positions and coordination requirements.
* Harmonic structure and chordal material.
* Grade-specific musical features.

The combination of statistical probabilities and rule-based validation allows the system to balance variation with controllability.

## Generation Pipeline

The exercise generation process consists of the following stages:

1. Select the target ABRSM grade.
2. Sample structural parameters for the exercise.
3. Select a key.
4. Load the corresponding difficulty profile.
5. Construct the rhythmic vocabulary.
6. Sample rhythmic motifs and construct the rhythm plan.
7. Generate a harmonic plan.
8. Select the initial melodic pitch.
9. Generate the melody using the Markov model.
10. Adjust melodic probabilities according to pedagogical constraints.
11. Construct left-hand material.
12. Introduce grade-specific chordal and notational features.
13. Validate the generated exercise.
14. Return the final symbolic representation.

The resulting exercise can then be rendered as musical notation.

## Project Structure

```text
piano-sight-reading-generator/
│
├── data/                              # Precomputed statistical data
│   ├── expressive_marks_grade1.pkl
│   ├── hand_patterns_grade.pkl
│   ├── pitch_markov_restricted3GE.pkl
│   └── rhythm_dict_with_clean_20dec25.pkl
│
├── examples/                          # Ready-to-run generation scripts
│   ├── generate_initial.py
│   ├── generate_grade_1.py
│   ├── generate_grade_2.py
│   ├── generate_grade_3.py
│   └── generate_grade_4.py
│
└── src/                               # Core generation modules
    ├── articulations.py               # Articulation generation
    ├── config.py                      # Grade settings and difficulty profiles
    ├── expressions.py                 # Expressive markings
    ├── generator.py                   # Main exercise generation pipeline
    ├── hands.py                       # Hand patterns and coordination
    ├── harmony.py                     # Harmonic planning and left-hand material
    ├── keys.py                        # Key and scale-related logic
    ├── melody.py                      # Melodic generation
    ├── render.py                      # Score rendering and export
    ├── rhythm.py                      # Rhythmic pattern generation
    └── utils.py                       # Shared utility functions
```

The project is organized into three main directories:

* **`data/`** contains precomputed statistical representations used during generation, including melodic transition probabilities, rhythmic patterns, hand-position information, and expressive markings.
* **`examples/`** provides standalone scripts for generating exercises at different ABRSM grade levels. These serve as the primary entry point for users.
* **`src/`** contains the core implementation, separating the generation pipeline into specialized modules for melody, rhythm, harmony, hand coordination, expression, and rendering.

## Getting Started

### Prerequisites

* Python 3.x
* [MuseScore](https://musescore.org/) installed on your system
* Required Python packages listed in `requirements.txt`

### Installation

Clone the repository:

```bash
git clone https://github.com/stepan-pshenichnyi/piano-sight-reading-generator.git
cd piano-sight-reading-generator
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Generating Exercises

The project provides ready-to-use example scripts for generating exercises at different ABRSM grade levels.

From the project root directory, run:

```bash
python -m examples.generate_grade_2
```

The script automatically generates a Grade 2 piano sight-reading exercise, exports it as a score, and opens it in MuseScore for viewing and practice.

To generate exercises at other levels, simply replace the grade number:

```bash
python -m examples.generate_initial
python -m examples.generate_grade_1
python -m examples.generate_grade_2
python -m examples.generate_grade_3
python -m examples.generate_grade_4
```

Each script generates a new exercise, so running the same command multiple times can produce different results.

**Note:** MuseScore must be installed for the generated score to open automatically. Run these commands from the repository root directory.

## Example Output

The generated exercises are exported as musical scores and opened in MuseScore, allowing users to inspect the notation and use the exercises for sight-reading practice.

![Generated Grade 2 piano exercise in MuseScore](docs/images/2.2.png)

## Design Principles

The project is guided by three main design objectives:

* **Controllability:** Generation is conditioned on explicit difficulty profiles, allowing the musical characteristics of an exercise to be adjusted.
* **Musical coherence:** Statistical models capture patterns from existing musical material, while constraints help maintain consistency.
* **Modularity:** The architecture separates musical concepts and generation stages, making the system easier to maintain, test, and extend.

## Limitations and Future Work

Potential directions for further development include:

* Extending support to higher ABRSM grades.
* Improving the representation of musical context in the statistical models.
* Expanding the symbolic music corpus.
* Introducing more sophisticated methods for evaluating pedagogical difficulty.
* Developing automated evaluation methods for musical coherence and exercise quality.
* Providing an interactive interface for configuring and generating exercises.

## Background

This project originated as a Master's thesis in Applied Informatics, with a specialization in Artificial Intelligence, at Vrije Universiteit Brussel (VUB).

It investigates how statistical music generation techniques can be combined with explicit pedagogical constraints to produce controllable piano sight-reading exercises.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
