import random
import pandas as pd

from .utils import weighted_sample

def load_expression_matrix(path):
    df = pd.read_csv(path, sep=";", index_col=0)
    # remove empty column if present
    df = df.dropna(axis=1, how="all")
    return df

def sample_expression(expr_probs):
    dynamic = random.choice(list(expr_probs.keys()))
    expression = weighted_sample(expr_probs[dynamic])
    return dynamic, expression