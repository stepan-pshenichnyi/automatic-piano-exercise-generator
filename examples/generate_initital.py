from src.generator import generate_exercise
from src.renderer import render_exercise

import pickle


with open('data/rhythm_dict_with_cleanup_20dec25.pkl', 'rb') as f:
    rhythm_dict = pickle.load(f)

with open('data/pitch_markov_restrictedG3E6.pkl', 'rb') as f:
    pitch_markov_prob = pickle.load(f)

with open('data/hand_patterns_grade1.pkl', 'rb') as f:
    transition_patterns = pickle.load(f)



exercise, params = generate_exercise(
    pitch_markov_prob,
    rhythm_dict,
    grade="initial"
)

render_exercise(exercise, params)