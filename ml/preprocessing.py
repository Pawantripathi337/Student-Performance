"""Data loading, cleaning and preprocessing shared by training and Django."""
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ML_DIR = Path(__file__).resolve().parent
DATASET_PATH = ML_DIR / "dataset.csv"

TARGET = "G3"                                            # final grade (0-20)
NUMERIC = ["age", "studytime", "failures", "absences", "G1", "G2", "freetime", "goout"]
CATEGORICAL = ["sex", "schoolsup", "famsup", "activities", "internet"]
FEATURES = NUMERIC + CATEGORICAL

PASS_MARK = 10                                           # G3 >= 10 -> "pass"
VALID_RANGES = {"age": (10, 30), "studytime": (1, 4), "failures": (0, 4),
                "absences": (0, 100), "G1": (0, 20), "G2": (0, 20),
                "freetime": (1, 5), "goout": (1, 5), TARGET: (0, 20)}


class DatasetError(Exception):
    """Raised when the dataset is missing or invalid (shown as a friendly message)."""


def load_and_clean(path=None):
    """Load the CSV and return a cleaned DataFrame."""
    path = Path(path) if path else DATASET_PATH
    if not path.exists():
        raise DatasetError(f"Dataset file not found: {path}")
    try:
        header = path.read_text(encoding="utf-8-sig").splitlines()[0]
        sep = ";" if header.count(";") > header.count(",") else ","   # UCI files use ;
        df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
    except Exception as exc:
        raise DatasetError(f"Could not read dataset: {exc}") from exc

    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise DatasetError(f"Dataset is missing required columns: {missing}")

    df = df[FEATURES + [TARGET]].copy()
    for col in CATEGORICAL:                                  # tidy text values
        df[col] = df[col].astype(str).str.strip()
    df["sex"] = df["sex"].str.upper()
    for col in ["schoolsup", "famsup", "activities", "internet"]:
        df[col] = df[col].str.lower()
    for col in NUMERIC + [TARGET]:                           # force numbers
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().drop_duplicates()                       # missing + duplicates
    for col, (lo, hi) in VALID_RANGES.items():               # drop impossible rows
        df = df[df[col].between(lo, hi)]
    if len(df) < 50:
        raise DatasetError("Dataset has too few valid rows after cleaning.")
    return df.reset_index(drop=True)


def make_preprocessor(features=None):
    """Scale numeric columns, one-hot encode categorical columns."""
    features = features or FEATURES
    num = [c for c in NUMERIC if c in features]
    cat = [c for c in CATEGORICAL if c in features]
    return ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])
