"""
Generate a SYNTHETIC demo dataset that follows the column layout of the public
UCI "Student Performance" dataset (Cortez & Silva, 2008).

WHY: so the project runs immediately without a download. The rows are NOT real
students. For your final submission, replace ml/dataset.csv with the real UCI
file (see README -> "Using the real UCI dataset").

Run:  python ml/generate_demo_dataset.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parent


def generate(n=600, seed=42):
    rng = np.random.default_rng(seed)
    ability = rng.normal(11, 3.0, n)                       # hidden "ability"
    age = rng.choice([15, 16, 17, 18, 19, 20], n, p=[.20, .25, .25, .20, .07, .03])
    sex = rng.choice(["F", "M"], n)
    studytime = rng.choice([1, 2, 3, 4], n, p=[.20, .45, .25, .10])
    failures = rng.choice([0, 1, 2, 3], n, p=[.78, .14, .05, .03])
    absences = np.clip(np.round(rng.gamma(1.5, 3.5, n)), 0, 60).astype(int)
    schoolsup = rng.choice(["yes", "no"], n, p=[.13, .87])
    famsup = rng.choice(["yes", "no"], n, p=[.60, .40])
    activities = rng.choice(["yes", "no"], n, p=[.50, .50])
    internet = rng.choice(["yes", "no"], n, p=[.83, .17])
    freetime = rng.integers(1, 6, n)
    goout = rng.integers(1, 6, n)

    base = ability + 0.6 * (studytime - 2) - 1.2 * failures - 0.05 * absences
    g1 = np.clip(np.round(base + rng.normal(0, 1.2, n)), 0, 20)
    g2 = np.clip(np.round(0.6 * g1 + 0.4 * base + rng.normal(0, 1.2, n)), 0, 20)
    g3 = np.clip(np.round(0.25 * g1 + 0.65 * g2 + 0.10 * base
                          + 0.25 * (studytime - 2) - 0.04 * absences
                          - 0.10 * (goout - 3) + rng.normal(0, 1.1, n)), 0, 20)

    return pd.DataFrame({
        "age": age, "sex": sex, "studytime": studytime, "failures": failures,
        "absences": absences, "G1": g1.astype(int), "G2": g2.astype(int),
        "schoolsup": schoolsup, "famsup": famsup, "activities": activities,
        "internet": internet, "freetime": freetime, "goout": goout,
        "G3": g3.astype(int),
    })


if __name__ == "__main__":
    df = generate()
    df.to_csv(ML_DIR / "dataset.csv", index=False)
    (ML_DIR / "dataset_info.json").write_text(json.dumps({
        "source": "Synthetic demo data (UCI-style columns)",
        "synthetic": True,
    }, indent=2))
    print(f"Saved {len(df)} rows x {df.shape[1]} columns to ml/dataset.csv")
