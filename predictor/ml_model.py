"""Loads the trained model and makes predictions for Django."""
import sys
from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.preprocessing import FEATURES, DatasetError  # noqa: E402

MODEL_PATH = BASE_DIR / "ml" / "model.pkl"
_bundle = None


class ModelUnavailable(Exception):
    """Raised when the model cannot be loaded (shown as a friendly message)."""


def _retrain():
    from ml.train_model import train
    try:
        bundle, _ = train()
    except DatasetError as exc:
        raise ModelUnavailable(f"The dataset is not available ({exc}).") from exc
    return bundle


def get_bundle():
    """Load model.pkl once. If it is missing/incompatible, retrain once."""
    global _bundle
    if _bundle is not None:
        return _bundle
    try:
        _bundle = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else _retrain()
    except ModelUnavailable:
        raise
    except Exception:                      # e.g. saved with another scikit-learn version
        try:
            _bundle = _retrain()
        except Exception as exc:
            raise ModelUnavailable(
                "The trained model could not be loaded. "
                "Run:  python ml/train_model.py") from exc
    return _bundle


def reset_cache():
    global _bundle
    _bundle = None


def predict(data):
    """data uses form field names (g1, g2, ...). Returns (percentage, pass_probability)."""
    bundle = get_bundle()
    row = dict(data)
    row["G1"], row["G2"] = row.pop("g1"), row.pop("g2")
    frame = pd.DataFrame([row])[FEATURES]
    try:
        grade = float(bundle["regressor"].predict(frame)[0])
        grade = min(max(grade, 0.0), 20.0)
        prob = float(bundle["classifier"].predict_proba(frame)[0][1])
    except Exception as exc:
        raise ModelUnavailable("The model failed to make a prediction.") from exc
    return round(grade * 5, 1), round(prob * 100, 1)   # grade/20 -> percentage
